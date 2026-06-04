from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from middleware.src.metrics.queue_monitor import fetch_queue_depth


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate performance plots and summary report")
    parser.add_argument("--reports-dir", default="reports")
    parser.add_argument("--metrics-file", default=None, help="Path to metrics JSON snapshot")
    parser.add_argument("--queue-name", default="logs.raw")
    parser.add_argument("--mgmt-url", default="http://127.0.0.1:15672")
    parser.add_argument("--skip-queue-fetch", action="store_true")
    parser.add_argument(
        "--metrics-url",
        default="http://127.0.0.1:8000/metrics",
        help="Fallback metrics endpoint when no JSON snapshot exists in reports/",
    )
    parser.add_argument(
        "--no-metrics-fetch",
        action="store_true",
        help="Do not call --metrics-url; use only reports/*.json or zeros",
    )
    return parser.parse_args()


def find_latest_metrics(reports_dir: Path) -> Path | None:
    candidates = sorted(reports_dir.glob("*metrics*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def empty_metrics() -> dict:
    return {
        "consumed_total": 0,
        "processed_total": 0,
        "dropped_total": 0,
        "errors_total": 0,
        "processing_latency_seconds": {"p50": 0.0, "p95": 0.0, "p99": 0.0},
    }


def fetch_metrics_from_url(url: str) -> dict | None:
    try:
        with urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except (URLError, OSError, json.JSONDecodeError, TimeoutError) as exc:
        print(f"Warning: could not fetch metrics from {url}: {exc}")
        return None


def metrics_have_pipeline_data(metrics: dict) -> bool:
    return any(int(metrics.get(key, 0)) > 0 for key in ("consumed_total", "processed_total", "dropped_total"))


def metrics_have_latency_data(metrics: dict) -> bool:
    latency = metrics.get("processing_latency_seconds", {})
    return any(float(latency.get(key, 0.0)) > 0.0 for key in ("p50", "p95", "p99"))


def load_metrics(path: Path | None, reports_dir: Path) -> dict:
    target = path or find_latest_metrics(reports_dir)
    if target is None or not target.exists():
        return empty_metrics()
    return json.loads(target.read_text(encoding="utf-8"))


def resolve_metrics(
    path: Path | None,
    reports_dir: Path,
    metrics_url: str | None,
) -> dict:
    metrics = load_metrics(path, reports_dir)
    if metrics_have_pipeline_data(metrics) or metrics_have_latency_data(metrics):
        return metrics
    if metrics_url:
        fetched = fetch_metrics_from_url(metrics_url)
        if fetched is not None:
            return fetched
    return metrics


def load_queue_samples(reports_dir: Path) -> list[dict[str, float | int]]:
    sample_file = reports_dir / "queue_samples.jsonl"
    if not sample_file.exists():
        return []
    rows: list[dict[str, float | int]] = []
    for line in sample_file.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_summary(
    reports_dir: Path,
    metrics: dict,
    queue_depth: int | None,
    plot_files: list[str],
) -> Path:
    latency = metrics.get("processing_latency_seconds", {})
    lines = [
        "# Performance Summary",
        "",
        f"Generated at: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Pipeline Counters",
        "",
        f"- consumed_total: {metrics.get('consumed_total', 0)}",
        f"- processed_total: {metrics.get('processed_total', 0)}",
        f"- dropped_total: {metrics.get('dropped_total', 0)}",
        f"- errors_total: {metrics.get('errors_total', 0)}",
        "",
        "## Latency (seconds)",
        "",
        f"- p50: {latency.get('p50', 0.0)}",
        f"- p95: {latency.get('p95', 0.0)}",
        f"- p99: {latency.get('p99', 0.0)}",
        "",
        "## RabbitMQ Queue",
        "",
        f"- queue_depth: {queue_depth if queue_depth is not None else 'n/a'}",
        "",
        "## Plots",
        "",
    ]
    if plot_files:
        lines.extend(f"- `{name}`" for name in plot_files)
    else:
        lines.append("- (no plots generated)")

    target = reports_dir / "performance_summary.md"
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def generate_plots(
    reports_dir: Path,
    metrics: dict,
    queue_depth: int | None,
    queue_samples: list[dict[str, float | int]],
) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plots_dir = reports_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    generated: list[str] = []

    fig, ax = plt.subplots(figsize=(7, 4))
    if metrics_have_pipeline_data(metrics):
        counts = {
            "consumed": int(metrics.get("consumed_total", 0)),
            "processed": int(metrics.get("processed_total", 0)),
            "dropped": int(metrics.get("dropped_total", 0)),
        }
        ax.bar(list(counts.keys()), list(counts.values()), color=["#4C78A8", "#59A14F", "#E15759"])
        ax.set_ylabel("count")
        ax.set_ylim(bottom=0)
    else:
        ax.text(
            0.5,
            0.5,
            "No metrics data\n(run e2e_smoke or pass --metrics-file)",
            ha="center",
            va="center",
            transform=ax.transAxes,
        )
        ax.set_axis_off()
    ax.set_title("Pipeline Counters")
    path_counts = plots_dir / "pipeline_counts.png"
    fig.tight_layout()
    fig.savefig(path_counts)
    plt.close(fig)
    generated.append(path_counts.name)

    fig, ax = plt.subplots(figsize=(7, 4))
    if metrics_have_latency_data(metrics):
        latency = metrics.get("processing_latency_seconds", {})
        labels = ["p50", "p95", "p99"]
        values = [float(latency.get(k, 0.0)) for k in labels]
        ax.bar(labels, values, color="#F28E2B")
        ax.set_ylabel("seconds")
        ax.set_ylim(bottom=0)
    else:
        ax.text(
            0.5,
            0.5,
            "No latency data\n(run e2e_smoke or pass --metrics-file)",
            ha="center",
            va="center",
            transform=ax.transAxes,
        )
        ax.set_axis_off()
    ax.set_title("Processing Latency Percentiles")
    path_latency = plots_dir / "latency_percentiles.png"
    fig.tight_layout()
    fig.savefig(path_latency)
    plt.close(fig)
    generated.append(path_latency.name)

    fig, ax = plt.subplots(figsize=(7, 4))
    if queue_samples:
        xs = [int(row.get("elapsed_s", idx)) for idx, row in enumerate(queue_samples)]
        ys = [int(row.get("depth", 0)) for row in queue_samples]
        ax.plot(xs, ys, marker="o")
        ax.set_xlabel("elapsed seconds")
        ax.set_title("Queue Depth Over Time")
    elif queue_depth is not None:
        ax.bar(["logs.raw"], [queue_depth], color="#76B7B2")
        ax.set_title("Current Queue Depth")
    else:
        ax.text(0.5, 0.5, "No queue data", ha="center", va="center")
        ax.set_axis_off()
    ax.set_ylabel("messages")
    path_queue = plots_dir / "queue_depth.png"
    fig.tight_layout()
    fig.savefig(path_queue)
    plt.close(fig)
    generated.append(path_queue.name)

    return generated


def main() -> None:
    args = parse_args()
    reports_dir = Path(args.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)

    metrics_path = Path(args.metrics_file) if args.metrics_file else None
    metrics_url = None if args.no_metrics_fetch else args.metrics_url
    metrics = resolve_metrics(metrics_path, reports_dir, metrics_url)
    queue_samples = load_queue_samples(reports_dir)

    queue_depth: int | None = None
    if not args.skip_queue_fetch:
        try:
            queue_depth = fetch_queue_depth(
                args.queue_name,
                mgmt_url=args.mgmt_url,
            )
        except RuntimeError as exc:
            print(f"Warning: {exc}")

    plot_files = generate_plots(reports_dir, metrics, queue_depth, queue_samples)
    summary_path = write_summary(reports_dir, metrics, queue_depth, plot_files)
    print(f"Performance summary: {summary_path}")
    print(f"Plots: {', '.join(plot_files)}")


if __name__ == "__main__":
    main()
