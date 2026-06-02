from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from middleware.src.metrics.queue_monitor import fetch_queue_depth

OUTPUT = ROOT / "output"
REPORTS = ROOT / "reports"
QUEUE_SAMPLES = REPORTS / "queue_samples.jsonl"


def run(command: list[str], timeout: int = 180) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def wait_for_health(url: str, timeout_seconds: int = 120) -> None:
    started = time.time()
    while time.time() - started < timeout_seconds:
        try:
            with urlopen(url, timeout=5) as response:
                payload = json.loads(response.read().decode("utf-8"))
                if payload.get("status") == "ok":
                    return
        except Exception:
            time.sleep(2)
            continue
    raise TimeoutError("Middleware health endpoint did not become ready in time.")


def assert_outputs() -> None:
    expected = [OUTPUT / "sysadmin.md", OUTPUT / "developer.json", OUTPUT / "security.csv"]
    missing = [str(p) for p in expected if not p.exists()]
    if missing:
        raise AssertionError(f"Expected output files are missing: {missing}")


def assert_metrics() -> None:
    with urlopen("http://localhost:8000/metrics", timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if payload.get("consumed_total", 0) <= 0:
        raise AssertionError(f"consumed_total should be > 0, got: {payload}")
    if payload.get("processed_total", 0) <= 0:
        raise AssertionError(f"processed_total should be > 0, got: {payload}")


def clean_artifacts() -> None:
    for target in [OUTPUT / "sysadmin.md", OUTPUT / "developer.json", OUTPUT / "security.csv"]:
        if target.exists():
            target.unlink()
    if QUEUE_SAMPLES.exists():
        QUEUE_SAMPLES.unlink()


def sample_queue_depth(duration_seconds: int = 10, interval_seconds: float = 1.0) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    started = time.time()
    elapsed = 0.0
    while elapsed <= duration_seconds:
        try:
            depth = fetch_queue_depth("logs.raw")
            row = {"elapsed_s": round(elapsed, 2), "depth": depth}
            with QUEUE_SAMPLES.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row) + "\n")
        except RuntimeError:
            pass
        time.sleep(interval_seconds)
        elapsed = time.time() - started


def main() -> None:
    print("E2E smoke: cleaning old artifacts...")
    clean_artifacts()

    print("E2E smoke: starting compose services...")
    run(["docker", "compose", "up", "-d", "--build"])
    try:
        print("E2E smoke: waiting middleware health...")
        wait_for_health("http://localhost:8000/health")

        print("E2E smoke: sending sample load with producer publish...")
        run(
            [
                "python",
                "-m",
                "producer.src.main",
                "--total",
                "300",
                "--batch",
                "50",
                "--rate",
                "500",
            ],
            timeout=180,
        )

        print("E2E smoke: sampling queue depth...")
        sample_queue_depth(duration_seconds=8, interval_seconds=1.0)

        print("E2E smoke: validating outputs and metrics...")
        assert_outputs()
        assert_metrics()
        print("E2E smoke: PASSED")
    finally:
        print("E2E smoke: shutting down compose services...")
        run(["docker", "compose", "down"], timeout=180)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"E2E smoke: FAILED -> {exc}", file=sys.stderr)
        raise
