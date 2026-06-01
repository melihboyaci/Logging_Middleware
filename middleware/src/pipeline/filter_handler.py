from __future__ import annotations

import re

from middleware.src.pipeline.handler import AbstractHandler
from shared.log_schema import LogLevel, LogRecord

DOCKER_SOURCE_RE = re.compile(r"^docker\.")


class FilterHandler(AbstractHandler):
    def process(self, log: LogRecord) -> LogRecord | None:
        if log.level in {LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING}:
            return None
        if DOCKER_SOURCE_RE.match(log.source):
            return None
        return log
