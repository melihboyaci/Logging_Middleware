from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from middleware.src.metrics.queue_monitor import fetch_queue_depth
from scripts.performance_report import (
    find_latest_metrics,
    load_metrics,
    load_queue_samples,
    write_summary,
)


def test_fetch_queue_depth_parses_messages_field() -> None:
    payload = json.dumps({"messages": 42}).encode("utf-8")

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            return payload

    with patch("middleware.src.metrics.queue_monitor.urlopen", return_value=FakeResponse()):
        assert fetch_queue_depth("logs.raw") == 42


def test_write_summary_creates_markdown(tmp_path: Path) -> None:
    metrics = {
        "consumed_total": 10,
        "processed_total": 7,
        "dropped_total": 3,
        "errors_total": 0,
        "processing_latency_seconds": {"p50": 0.01, "p95": 0.02, "p99": 0.03},
    }
    target = write_summary(tmp_path, metrics, queue_depth=5, plot_files=["pipeline_counts.png"])
    content = target.read_text(encoding="utf-8")
    assert "consumed_total: 10" in content
    assert "queue_depth: 5" in content
    assert "pipeline_counts.png" in content


def test_load_metrics_and_queue_samples(tmp_path: Path) -> None:
    metrics_file = tmp_path / "phase5_metrics_test.json"
    metrics_file.write_text(
        json.dumps({"consumed_total": 1, "processed_total": 1, "dropped_total": 0}),
        encoding="utf-8",
    )
    samples = tmp_path / "queue_samples.jsonl"
    samples.write_text('{"elapsed_s": 0, "depth": 3}\n{"elapsed_s": 1, "depth": 1}\n', encoding="utf-8")

    loaded = load_metrics(metrics_file, tmp_path)
    assert loaded["consumed_total"] == 1
    assert find_latest_metrics(tmp_path) == metrics_file
    assert len(load_queue_samples(tmp_path)) == 2
