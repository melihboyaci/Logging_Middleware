from __future__ import annotations

from collections.abc import Callable
from time import perf_counter

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from middleware.src.config import MiddlewareConfig
from middleware.src.metrics.collector import METRICS
from shared.log_schema import LogRecord


class RabbitConsumer:
    def __init__(self, config: MiddlewareConfig, process_log: Callable[[LogRecord], LogRecord | None]) -> None:
        self._config = config
        self._process_log = process_log
        self._connection: aio_pika.RobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None
        self._queue: aio_pika.abc.AbstractQueue | None = None

    async def start(self) -> None:
        self._connection = await aio_pika.connect_robust(self._config.amqp_url)
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=self._config.prefetch_count)

        exchange = await self._channel.declare_exchange(
            self._config.exchange_name,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        self._queue = await self._channel.declare_queue(self._config.queue_name, durable=True)
        await self._queue.bind(exchange, routing_key=self._config.queue_name)
        await self._queue.consume(self._on_message)

    async def stop(self) -> None:
        if self._connection is not None:
            await self._connection.close()
            self._connection = None

    async def _on_message(self, message: AbstractIncomingMessage) -> None:
        async with message.process(requeue=False):
            METRICS.consumed_total += 1
            started = perf_counter()
            try:
                log = LogRecord.model_validate_json(message.body.decode("utf-8"))
                result = self._process_log(log)
                if result is None:
                    METRICS.dropped_total += 1
            except Exception:
                METRICS.errors_total += 1
                raise
            finally:
                METRICS.record_processing_latency(perf_counter() - started)
