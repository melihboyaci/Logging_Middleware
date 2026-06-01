from __future__ import annotations

import json

from shared.log_schema import LogRecord

from middleware.src.formatting.formatter import Formatter


class CsvFormatter(Formatter):
    def __init__(self) -> None:
        self._header = "id,timestamp,level,type,role,source,message,payload"
        self._header_written = False

    def format(self, log: LogRecord) -> str:
        payload = json.dumps(log.payload, ensure_ascii=False).replace('"', '""')
        row = (
            f"{log.id},{log.timestamp.isoformat()},{log.level.value},"
            f"{log.type.value},{log.role.value},{log.source},\"{log.message}\",\"{payload}\""
        )
        if not self._header_written:
            self._header_written = True
            return f"{self._header}\n{row}"
        return row
