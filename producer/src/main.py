from __future__ import annotations

import argparse
import asyncio
from collections.abc import Iterator
from typing import Any

from producer.src.config import ProducerConfig
from producer.src.generators.log_factory import LogFactory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CENG302 data middleware producer")
    parser.add_argument("--total", type=int, default=None, help="Total log count")
    parser.add_argument("--batch", type=int, default=None, help="Batch size")
    parser.add_argument("--rate", type=int, default=None, help="Publish rate per second")
    parser.add_argument("--amqp-url", type=str, default=None, help="AMQP URL")
    parser.add_argument("--dry-run", action="store_true", help="Generate logs without publishing")
    return parser.parse_args()


def build_stream(factory: LogFactory, total: int) -> Iterator[Any]:
    for _ in range(total):
        yield factory.create_log()


async def run() -> None:
    args = parse_args()
    base = ProducerConfig()
    config = ProducerConfig(
        amqp_url=args.amqp_url or base.amqp_url,
        exchange_name=base.exchange_name,
        routing_key=base.routing_key,
        total=args.total or base.total,
        batch_size=args.batch or base.batch_size,
        rate_per_second=args.rate or base.rate_per_second,
        scenario_seed=base.scenario_seed,
        producer_id=base.producer_id,
    )

    factory = LogFactory(seed=config.scenario_seed, producer_id=config.producer_id)
    stream = build_stream(factory, config.total)

    if args.dry_run:
        generated = sum(1 for _ in stream)
        print(f"Dry run completed. Generated {generated} logs.")
        return

    from producer.src.transport.publisher import RabbitPublisher

    publisher = RabbitPublisher(
        amqp_url=config.amqp_url,
        exchange_name=config.exchange_name,
        routing_key=config.routing_key,
    )
    stats = await publisher.publish_stream(
        stream=stream,
        batch_size=config.batch_size,
        rate_per_second=config.rate_per_second,
    )
    print(
        "Publish done. "
        f"published={int(stats['published'])} "
        f"elapsed={stats['elapsed']:.2f}s "
        f"throughput={stats['throughput']:.2f} log/s"
    )


if __name__ == "__main__":
    asyncio.run(run())
