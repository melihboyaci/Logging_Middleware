from __future__ import annotations

from abc import ABC, abstractmethod

from shared.log_schema import LogRecord


class AbstractHandler(ABC):
    def __init__(self) -> None:
        self._next: AbstractHandler | None = None

    def set_next(self, handler: AbstractHandler) -> AbstractHandler:
        self._next = handler
        return handler

    def handle(self, log: LogRecord) -> LogRecord | None:
        current = self.process(log)
        if current is None:
            return None
        if self._next is None:
            return current
        return self._next.handle(current)

    @abstractmethod
    def process(self, log: LogRecord) -> LogRecord | None:
        raise NotImplementedError
