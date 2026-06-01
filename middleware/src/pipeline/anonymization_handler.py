from __future__ import annotations

from middleware.src.pipeline.handler import AbstractHandler
from middleware.src.security.anonymizer import anonymize_payload, anonymize_text
from shared.log_schema import LogRecord


class AnonymizationHandler(AbstractHandler):
    def process(self, log: LogRecord) -> LogRecord:
        return log.model_copy(
            update={
                "message": anonymize_text(log.message),
                "payload": anonymize_payload(log.payload),
            }
        )
