from __future__ import annotations

from shared.log_schema import LogRecord

from middleware.src.formatting.formatter import Formatter


class JsonFormatter(Formatter):
    def format(self, log: LogRecord) -> str:
        return log.model_dump_json()
