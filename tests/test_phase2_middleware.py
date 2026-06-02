from __future__ import annotations

from middleware.src.api.routes import health, metrics
from middleware.src.metrics.collector import METRICS
from middleware.src.pipeline.anonymization_handler import AnonymizationHandler
from shared.log_schema import LogLevel, LogRecord, LogType, UserRole


def test_anonymization_handler_masks_sensitive_values() -> None:
    log = LogRecord(
        level=LogLevel.ERROR,
        type=LogType.TRANSACTION,
        role=UserRole.security,
        source="trade.api",
        message="User mail melih@example.com tc 12345678901",
        payload={
            "tc": "12345678901",
            "iban": "TR123456789012345678901234",
            "credit_card": "5235123412341234",
            "swift": "GARBTRIS",
            "email": "melih@example.com",
        },
    )

    output = AnonymizationHandler().handle(log)
    assert output is not None
    assert "12xxxxxxxx1" in output.message
    assert output.payload["tc"] == "12xxxxxxxx1"
    assert output.payload["credit_card"] == "5235 xxxxxx 1234"
    assert output.payload["swift"] == "***SWIFT***"
    assert output.payload["email"] == "m***@example.com"
    assert output.payload["iban"].startswith("TR12")
    assert output.payload["iban"].endswith("1234")


def test_anonymizer_is_idempotent_for_already_masked_values() -> None:
    log = LogRecord(
        level=LogLevel.ERROR,
        type=LogType.TRANSACTION,
        role=UserRole.security,
        source="trade.api",
        message="masked tc 12xxxxxxxx1",
        payload={"tc": "12xxxxxxxx1", "email": "m***@example.com"},
    )

    output = AnonymizationHandler().handle(log)
    assert output is not None
    assert output.payload["tc"] == "12xxxxxxxx1"
    assert output.payload["email"] == "m***@example.com"


def test_health_route_returns_ok() -> None:
    assert health() == {"status": "ok"}


def test_metrics_route_returns_nested_latency_summary() -> None:
    METRICS.record_processing_latency(0.01)
    METRICS.record_processing_latency(0.02)

    payload = metrics()
    assert payload["consumed_total"] >= 0
    assert "processing_latency_seconds" in payload
    assert "p50" in payload["processing_latency_seconds"]
