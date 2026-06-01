from __future__ import annotations

from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True)
class ProducerConfig:
    amqp_url: str = getenv("AMQP_URL", "amqp://guest:guest@localhost:5672/")
    exchange_name: str = getenv("EXCHANGE_NAME", "logs")
    routing_key: str = getenv("ROUTING_KEY", "logs.raw")

    total: int = int(getenv("TOTAL_LOGS", "100"))
    batch_size: int = int(getenv("BATCH_SIZE", "50"))
    rate_per_second: int = int(getenv("RATE_PER_SECOND", "200"))

    scenario_seed: int = int(getenv("SCENARIO_SEED", "302"))
    producer_id: str = getenv("PRODUCER_ID", "producer-1")
