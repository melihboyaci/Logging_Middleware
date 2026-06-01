from __future__ import annotations

from pathlib import Path
import subprocess
import sys


def test_e2e_script_has_help_text() -> None:
    script = Path("scripts/e2e_smoke.py")
    assert script.exists()
    content = script.read_text(encoding="utf-8")
    assert "E2E smoke" in content
    assert "docker" in content


def test_stress_runner_burst_profile(tmp_path: Path) -> None:
    cmd = [
        sys.executable,
        "-m",
        "producer.src.stress.load_runner",
        "--profile",
        "burst",
        "--reports-dir",
        str(tmp_path),
        "--max-total",
        "3000",
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    assert "Load profile saved to" in result.stdout
    assert (tmp_path / "load_profile_burst.json").exists()
