from __future__ import annotations

from dataclasses import dataclass
from os import getenv

ROLE_FORMAT_MAP = {
    "sysadmin": getenv("FORMAT_SYSADMIN", "markdown"),
    "developer": getenv("FORMAT_DEVELOPER", "json"),
    "security": getenv("FORMAT_SECURITY", "csv"),
}

FORMAT_FILE_EXT = {
    "markdown": "md",
    "json": "json",
    "csv": "csv",
    "html": "html",
}

OUTPUT_DIR = getenv("OUTPUT_DIR", "output")


@dataclass(frozen=True)
class MiddlewareConfig:
    amqp_url: str = getenv("AMQP_URL", "amqp://guest:guest@127.0.0.1:5672/")
    exchange_name: str = getenv("EXCHANGE_NAME", "logs")
    queue_name: str = getenv("QUEUE_NAME", "logs.raw")
    prefetch_count: int = int(getenv("PREFETCH_COUNT", "50"))

    host: str = getenv("MIDDLEWARE_HOST", "0.0.0.0")
    port: int = int(getenv("MIDDLEWARE_PORT", "8000"))
