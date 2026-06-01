from __future__ import annotations

import json

from shared.log_schema import LogRecord

from middleware.src.formatting.formatter import Formatter


class HtmlFormatter(Formatter):
    def format(self, log: LogRecord) -> str:
        payload = json.dumps(log.payload, ensure_ascii=False, indent=2)
        return (
            "<article>"
            f"<h3>Log {log.id}</h3>"
            f"<p><strong>timestamp:</strong> {log.timestamp.isoformat()}</p>"
            f"<p><strong>level:</strong> {log.level.value}</p>"
            f"<p><strong>type:</strong> {log.type.value}</p>"
            f"<p><strong>role:</strong> {log.role.value}</p>"
            f"<p><strong>source:</strong> {log.source}</p>"
            f"<p><strong>message:</strong> {log.message}</p>"
            f"<pre>{payload}</pre>"
            "</article>"
        )
