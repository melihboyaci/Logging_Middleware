from __future__ import annotations

from dataclasses import dataclass, field
from statistics import quantiles


@dataclass
class MetricsCollector:
    published_total: int = 0
    consumed_total: int = 0
    processed_total: int = 0
    dropped_total: int = 0
    errors_total: int = 0
    processing_latency_seconds: list[float] = field(default_factory=list)

    def record_processing_latency(self, seconds: float) -> None:
        if seconds >= 0:
            self.processing_latency_seconds.append(seconds)

    def _latency_summary(self) -> dict[str, float]:
        if not self.processing_latency_seconds:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}
        values = sorted(self.processing_latency_seconds)
        if len(values) < 20:
            p50 = values[len(values) // 2]
            p95 = values[max(0, int(len(values) * 0.95) - 1)]
            p99 = values[-1]
            return {"p50": p50, "p95": p95, "p99": p99}
        q = quantiles(values, n=100, method="inclusive")
        p50, p95, p99 = q[49], q[94], q[98]
        return {"p50": p50, "p95": p95, "p99": p99}

    def snapshot(self) -> dict[str, int | float | dict[str, float]]:
        return {
            "published_total": self.published_total,
            "consumed_total": self.consumed_total,
            "processed_total": self.processed_total,
            "dropped_total": self.dropped_total,
            "errors_total": self.errors_total,
            "processing_latency_seconds": self._latency_summary(),
        }


METRICS = MetricsCollector()
