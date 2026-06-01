from __future__ import annotations

from middleware.src.pipeline.anonymization_handler import AnonymizationHandler
from middleware.src.pipeline.enrichment_handler import EnrichmentHandler
from middleware.src.pipeline.filter_handler import FilterHandler
from middleware.src.pipeline.handler import AbstractHandler
from middleware.src.pipeline.terminal_handler import TerminalHandler


def build_pipeline() -> AbstractHandler:
    anonymizer = AnonymizationHandler()
    filter_handler = FilterHandler()
    enrichment = EnrichmentHandler()
    terminal = TerminalHandler()
    anonymizer.set_next(filter_handler).set_next(enrichment).set_next(terminal)
    return anonymizer
