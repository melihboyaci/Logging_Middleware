from __future__ import annotations

from middleware.src.metrics.collector import METRICS
from middleware.src.pipeline.handler import AbstractHandler
from middleware.src.sinks.role_router import RoleRouter
from shared.log_schema import LogRecord


class TerminalHandler(AbstractHandler):
    def __init__(self) -> None:
        super().__init__()
        self._router = RoleRouter()

    def process(self, log: LogRecord) -> LogRecord:
        self._router.route(log)
        METRICS.processed_total += 1
        return log
