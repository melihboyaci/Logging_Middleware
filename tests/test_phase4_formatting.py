from __future__ import annotations

from pathlib import Path

from middleware.src.sinks.role_router import RoleRouter
from shared.log_schema import LogLevel, LogRecord, LogType, UserRole


def _sample_log(role: UserRole, message: str = "hello") -> LogRecord:
    return LogRecord(
        level=LogLevel.ERROR,
        type=LogType.LOG,
        role=role,
        source="test.source",
        message=message,
        payload={"k": "v"},
    )


def test_role_router_writes_role_specific_files(tmp_path: Path) -> None:
    router = RoleRouter(output_dir=str(tmp_path))

    p_sys = router.route(_sample_log(UserRole.sysadmin))
    p_dev = router.route(_sample_log(UserRole.developer))
    p_sec = router.route(_sample_log(UserRole.security))

    assert p_sys.exists() and p_sys.suffix == ".md"
    assert p_dev.exists() and p_dev.suffix == ".json"
    assert p_sec.exists() and p_sec.suffix == ".csv"


def test_json_output_contains_serialized_log(tmp_path: Path) -> None:
    router = RoleRouter(output_dir=str(tmp_path))
    target = router.route(_sample_log(UserRole.developer, message="dev-msg"))

    content = target.read_text(encoding="utf-8")
    assert '"role":"developer"' in content
    assert '"message":"dev-msg"' in content
