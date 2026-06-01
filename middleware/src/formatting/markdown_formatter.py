from __future__ import annotations

import json

from shared.log_schema import LogRecord

from middleware.src.formatting.formatter import Formatter


class MarkdownFormatter(Formatter):
    def format(self, log: LogRecord) -> str:
        payload = json.dumps(log.payload, ensure_ascii=False, indent=2)
        return (
            f"## Log {log.id}\n"
            f"- timestamp: {log.timestamp.isoformat()}\n"
            f"- level: {log.level.value}\n"
            f"- type: {log.type.value}\n"
            f"- role: {log.role.value}\n"
            f"- source: {log.source}\n"
            f"- message: {log.message}\n"
            f"- payload:\n```json\n{payload}\n```\n"
        )
