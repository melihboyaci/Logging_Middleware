from __future__ import annotations

import asyncio
from collections.abc import Iterable
from time import perf_counter

import aio_pika
from aio_pika import DeliveryMode, Message

from shared.log_schema import LogRecord


class RabbitPublisher:
    def __init__(self, amqp_url: str, exchange_name: str, routing_key: str) -> None:
        self._amqp_url = amqp_url
        self._exchange_name = exchange_name
        self._routing_key = routing_key
        self.published_total = 0

    async def publish_batch(self, logs: Iterable[LogRecord]) -> int:
        log_list = list(logs)
        if not log_list:
            return 0

        connection = await aio_pika.connect_robust(self._amqp_url)
        try:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=500)
            exchange = await channel.declare_exchange(
                self._exchange_name,
                aio_pika.ExchangeType.TOPIC,
                durable=True,
            )
            queue = await channel.declare_queue(self._routing_key, durable=True)
            await queue.bind(exchange, routing_key=self._routing_key)

            for log in log_list:
                body = log.model_dump_json().encode("utf-8")
                message = Message(
                    body=body,
                    delivery_mode=DeliveryMode.PERSISTENT,
                    content_type="application/json",
                )
                await exchange.publish(message, routing_key=self._routing_key)
                self.published_total += 1
            return len(log_list)
        finally:
            await connection.close()

    async def publish_stream(
        self,
        stream: Iterable[LogRecord],
        batch_size: int,
        rate_per_second: int,
    ) -> dict[str, float]:
        if batch_size <= 0:
            raise ValueError("batch_size must be > 0")
        if rate_per_second <= 0:
            raise ValueError("rate_per_second must be > 0")

        start = perf_counter()
        batch: list[LogRecord] = []
        published = 0

        for log in stream:
            batch.append(log)
            if len(batch) >= batch_size:
                published += await self.publish_batch(batch)
                batch.clear()
                await asyncio.sleep(batch_size / rate_per_second)

        if batch:
            published += await self.publish_batch(batch)

        elapsed = perf_counter() - start
        throughput = published / elapsed if elapsed > 0 else 0.0
        return {"published": float(published), "elapsed": elapsed, "throughput": throughput}
