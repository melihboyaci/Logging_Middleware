from __future__ import annotations

from middleware.src.enrichment.enrichers import apply_enrichment
from middleware.src.pipeline.handler import AbstractHandler
from shared.log_schema import LogRecord


class EnrichmentHandler(AbstractHandler):
    def process(self, log: LogRecord) -> LogRecord:
        return apply_enrichment(log)
