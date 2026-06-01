from __future__ import annotations

from middleware.src.pipeline.pipeline_builder import build_pipeline
from shared.log_schema import LogLevel, LogRecord, LogType, UserRole


def _build_log(
    *,
    level: LogLevel,
    source: str,
    role: UserRole,
    log_type: LogType = LogType.LOG,
) -> LogRecord:
    return LogRecord(
        level=level,
        type=log_type,
        role=role,
        source=source,
        message="raw message",
        payload={"producer_id": "producer-test"},
    )


def test_pipeline_filters_info_warning_and_docker_logs() -> None:
    pipeline = build_pipeline()

    info_log = _build_log(level=LogLevel.INFO, source="trade.api", role=UserRole.security)
    warning_log = _build_log(level=LogLevel.WARNING, source="trade.api", role=UserRole.developer)
    docker_log = _build_log(level=LogLevel.ERROR, source="docker.engine", role=UserRole.sysadmin)

    assert pipeline.handle(info_log) is None
    assert pipeline.handle(warning_log) is None
    assert pipeline.handle(docker_log) is None


def test_pipeline_enriches_critical_security_log() -> None:
    pipeline = build_pipeline()
    log = _build_log(level=LogLevel.CRITICAL, source="auth.gateway", role=UserRole.security)

    output = pipeline.handle(log)
    assert output is not None
    assert output.message.startswith("<") and output.message.endswith(">")
    assert output.payload["sender_id"] == "producer-test"
    assert output.payload["criticality"] == "critical"


def test_pipeline_adds_transaction_number_for_transaction_type() -> None:
    pipeline = build_pipeline()
    log = _build_log(
        level=LogLevel.ERROR,
        source="trade.api",
        role=UserRole.developer,
        log_type=LogType.TRANSACTION,
    )

    output = pipeline.handle(log)
    assert output is not None
    assert "transaction_no" in output.payload
    assert output.message.startswith("{") and output.message.endswith("}")
