from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from middleware.src.metrics.collector import METRICS
from middleware.src.metrics.reporter import MetricsReporter


def test_metrics_snapshot_contains_latency_quantiles() -> None:
    METRICS.processing_latency_seconds.clear()
    METRICS.record_processing_latency(0.01)
    METRICS.record_processing_latency(0.03)
    METRICS.record_processing_latency(0.02)

    snapshot = METRICS.snapshot()
    latency = snapshot["processing_latency_seconds"]
    assert isinstance(latency, dict)
    assert latency["p50"] >= 0.0
    assert latency["p95"] >= 0.0
    assert latency["p99"] >= 0.0


def test_metrics_reporter_writes_json_file(tmp_path: Path) -> None:
    METRICS.consumed_total = 5
    target = MetricsReporter(reports_dir=str(tmp_path)).write_snapshot("test_metrics")
    assert target.exists()
    content = json.loads(target.read_text(encoding="utf-8"))
    assert "consumed_total" in content


def test_load_runner_generates_ramp_profile_file(tmp_path: Path) -> None:
    cmd = [
        sys.executable,
        "-m",
        "producer.src.stress.load_runner",
        "--profile",
        "ramp",
        "--reports-dir",
        str(tmp_path),
        "--max-total",
        "2000",
    ]
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    assert "Load profile saved to" in completed.stdout
    target = tmp_path / "load_profile_ramp.json"
    assert target.exists()
    data = json.loads(target.read_text(encoding="utf-8"))
    assert data["profile"] == "ramp"
    assert data["steps"]
