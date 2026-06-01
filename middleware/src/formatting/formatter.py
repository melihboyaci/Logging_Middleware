from __future__ import annotations

from abc import ABC, abstractmethod

from shared.log_schema import LogRecord


class Formatter(ABC):
    @abstractmethod
    def format(self, log: LogRecord) -> str:
        raise NotImplementedError
