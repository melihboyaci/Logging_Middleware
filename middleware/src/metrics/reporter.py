from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from middleware.src.metrics.collector import METRICS


class MetricsReporter:
    def __init__(self, reports_dir: str = "reports") -> None:
        self._reports_dir = Path(reports_dir)
        self._reports_dir.mkdir(parents=True, exist_ok=True)

    def write_snapshot(self, name: str = "metrics_snapshot") -> Path:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        target = self._reports_dir / f"{name}_{ts}.json"
        target.write_text(json.dumps(METRICS.snapshot(), indent=2), encoding="utf-8")
        return target
