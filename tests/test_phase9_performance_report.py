from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from middleware.src.metrics.queue_monitor import fetch_queue_depth
from scripts.performance_report import (
    find_latest_metrics,
    generate_plots,
    load_metrics,
    load_queue_samples,
    metrics_have_pipeline_data,
    resolve_metrics,
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


def test_resolve_metrics_uses_json_snapshot(tmp_path: Path) -> None:
    metrics_file = tmp_path / "e2e_metrics.json"
    metrics_file.write_text(
        json.dumps(
            {
                "consumed_total": 100,
                "processed_total": 40,
                "dropped_total": 60,
                "processing_latency_seconds": {"p50": 0.001, "p95": 0.002, "p99": 0.003},
            }
        ),
        encoding="utf-8",
    )
    resolved = resolve_metrics(None, tmp_path, metrics_url="http://127.0.0.1:1")
    assert resolved["consumed_total"] == 100
    assert metrics_have_pipeline_data(resolved)


def test_generate_plots_renders_bars_with_metrics(tmp_path: Path) -> None:
    metrics = {
        "consumed_total": 300,
        "processed_total": 120,
        "dropped_total": 180,
        "errors_total": 0,
        "processing_latency_seconds": {"p50": 0.0003, "p95": 0.0008, "p99": 0.0012},
    }
    samples = [{"elapsed_s": 0, "depth": 5}, {"elapsed_s": 2, "depth": 1}]
    plot_files = generate_plots(tmp_path, metrics, queue_depth=None, queue_samples=samples)
    assert len(plot_files) == 3
    counts_png = tmp_path / "plots" / "pipeline_counts.png"
    assert counts_png.stat().st_size > 8_000
