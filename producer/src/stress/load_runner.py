from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from producer.src.config import ProducerConfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stress profile writer for producer")
    parser.add_argument("--profile", choices=["ramp", "burst"], default="ramp")
    parser.add_argument("--reports-dir", default="reports")
    parser.add_argument("--max-total", type=int, default=100000)
    return parser.parse_args()


def ramp_profile(max_total: int) -> list[dict[str, int]]:
    points = [1000, 10000, 50000, max_total]
    return [{"total": p, "rate": min(p, 10000), "batch": 200} for p in points]


def burst_profile(max_total: int) -> list[dict[str, int]]:
    return [
        {"total": max_total // 2, "rate": 15000, "batch": 500},
        {"total": max_total, "rate": 20000, "batch": 500},
    ]


def main() -> None:
    args = parse_args()
    reports = Path(args.reports_dir)
    reports.mkdir(parents=True, exist_ok=True)
    config = ProducerConfig()

    if args.profile == "ramp":
        profile = ramp_profile(args.max_total)
    else:
        profile = burst_profile(args.max_total)

    payload = {
        "profile": args.profile,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "amqp_url": config.amqp_url,
        "exchange_name": config.exchange_name,
        "routing_key": config.routing_key,
        "steps": profile,
    }
    target = reports / f"load_profile_{args.profile}.json"
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Load profile saved to {target}")


if __name__ == "__main__":
    main()
