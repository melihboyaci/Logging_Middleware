from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from shared.log_schema import LogLevel, LogRecord, LogType, UserRole


@dataclass
class SenderIdDecorator:
    def apply(self, log: LogRecord) -> LogRecord:
        payload = dict(log.payload)
        payload.setdefault("sender_id", payload.get("producer_id", "unknown-sender"))
        return log.model_copy(update={"payload": payload})


@dataclass
class TransactionInfoDecorator:
    def apply(self, log: LogRecord) -> LogRecord:
        if log.type != LogType.TRANSACTION:
            return log
        payload = dict(log.payload)
        payload.setdefault("transaction_no", f"txn-{uuid4().hex[:12]}")
        return log.model_copy(update={"payload": payload})


@dataclass
class CriticalityDecorator:
    def apply(self, log: LogRecord) -> LogRecord:
        if log.level == LogLevel.CRITICAL:
            criticality = "critical"
        elif log.level == LogLevel.ERROR:
            criticality = "high"
        elif log.level == LogLevel.WARNING:
            criticality = "med"
        else:
            criticality = "low"
        payload = dict(log.payload)
        payload["criticality"] = criticality
        return log.model_copy(update={"payload": payload})


@dataclass
class RoleTagDecorator:
    def apply(self, log: LogRecord) -> LogRecord:
        if log.role == UserRole.security:
            message = f"<{log.message}>"
        elif log.role == UserRole.developer:
            message = f"{{{log.message}}}"
        else:
            message = f"{{~{log.message}~}}"
        return log.model_copy(update={"message": message})


@dataclass
class DebugDecorator:
    def apply(self, log: LogRecord) -> LogRecord:
        if log.level != LogLevel.DEBUG:
            return log
        payload = dict(log.payload)
        payload["debug"] = True
        return log.model_copy(update={"payload": payload})


def apply_enrichment(log: LogRecord) -> LogRecord:
    decorators = [
        SenderIdDecorator(),
        TransactionInfoDecorator(),
        CriticalityDecorator(),
        RoleTagDecorator(),
        DebugDecorator(),
    ]
    current = log
    for decorator in decorators:
        current = decorator.apply(current)
    return current
