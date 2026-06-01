from __future__ import annotations

from pathlib import Path


def test_ci_workflow_exists_and_contains_jobs() -> None:
    workflow = Path(".github/workflows/ci.yml")
    assert workflow.exists()
    content = workflow.read_text(encoding="utf-8")

    assert "name: CI" in content
    assert "tests:" in content
    assert "e2e-smoke:" in content
    assert "python -m pytest -q" in content
    assert "python scripts/e2e_smoke.py" in content
