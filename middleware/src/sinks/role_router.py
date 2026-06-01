from __future__ import annotations

from pathlib import Path

from middleware.src.config import FORMAT_FILE_EXT, OUTPUT_DIR, ROLE_FORMAT_MAP
from middleware.src.formatting.formatter_factory import formatter_for_role
from shared.log_schema import LogRecord


class RoleRouter:
    def __init__(self, output_dir: str = OUTPUT_DIR) -> None:
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._formatters = {}

    def route(self, log: LogRecord) -> Path:
        role_name = log.role.value
        formatter = self._formatters.setdefault(role_name, formatter_for_role(log.role))
        format_name = ROLE_FORMAT_MAP.get(role_name, "json")
        extension = FORMAT_FILE_EXT.get(format_name, "json")
        target = self._output_dir / f"{role_name}.{extension}"

        line = formatter.format(log)
        with target.open("a", encoding="utf-8") as f:
            f.write(line)
            if not line.endswith("\n"):
                f.write("\n")
        return target
