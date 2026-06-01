from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Any

from shared.log_schema import LogLevel, LogType, UserRole

from .sensitive_data import (
    generate_amount,
    generate_credit_card,
    generate_email,
    generate_iban,
    generate_swift,
    generate_tckn,
)


@dataclass(frozen=True)
class ScenarioOutput:
    name: str
    level: LogLevel
    log_type: LogType
    role: UserRole
    source: str
    message: str
    payload: dict[str, Any]


SCENARIO_WEIGHTS: dict[str, int] = {
    "kvkk_transaction": 20,
    "failed_login_burst": 12,
    "dev_404": 14,
    "sysadmin_datetime_mismatch": 10,
    "noise_info_warning": 28,
    "docker_internal_noise": 8,
    "card_purchase": 8,
}


def generate_scenario(name: str, rng: Random) -> ScenarioOutput:
    if name == "kvkk_transaction":
        return ScenarioOutput(
            name=name,
            level=LogLevel.ERROR,
            log_type=LogType.TRANSACTION,
            role=UserRole.security,
            source="trade.api",
            message="Suspicious transfer detected for customer",
            payload={
                "tc": generate_tckn(rng),
                "iban": generate_iban(rng),
                "swift": generate_swift(rng),
                "amount": generate_amount(rng),
            },
        )

    if name == "failed_login_burst":
        return ScenarioOutput(
            name=name,
            level=LogLevel.ERROR,
            log_type=LogType.ACCESS,
            role=UserRole.security,
            source="auth.gateway",
            message="3 failed login attempts from same ip",
            payload={"ip": f"10.0.{rng.randint(1, 250)}.{rng.randint(1, 250)}"},
        )

    if name == "dev_404":
        return ScenarioOutput(
            name=name,
            level=LogLevel.ERROR,
            log_type=LogType.ACCESS,
            role=UserRole.developer,
            source="web.api",
            message="404 GET /v1/orders/{id}",
            payload={"request_id": f"req-{rng.randint(10000, 99999)}"},
        )

    if name == "sysadmin_datetime_mismatch":
        return ScenarioOutput(
            name=name,
            level=LogLevel.CRITICAL,
            log_type=LogType.LOG,
            role=UserRole.sysadmin,
            source="scheduler.core",
            message="datetime mismatch between nodes",
            payload={"node_a": "srv-a", "node_b": "srv-b"},
        )

    if name == "noise_info_warning":
        level = rng.choice([LogLevel.INFO, LogLevel.WARNING])
        return ScenarioOutput(
            name=name,
            level=level,
            log_type=LogType.LOG,
            role=rng.choice([UserRole.sysadmin, UserRole.developer, UserRole.security]),
            source="app.noise",
            message="non-critical informational noise",
            payload={"note": "can be filtered"},
        )

    if name == "docker_internal_noise":
        return ScenarioOutput(
            name=name,
            level=LogLevel.INFO,
            log_type=LogType.LOG,
            role=UserRole.sysadmin,
            source="docker.engine",
            message="container healthcheck output",
            payload={"container": f"ctr-{rng.randint(100, 999)}"},
        )

    if name == "card_purchase":
        return ScenarioOutput(
            name=name,
            level=LogLevel.ERROR,
            log_type=LogType.TRANSACTION,
            role=UserRole.security,
            source="payment.gateway",
            message="Card payment anomaly triggered",
            payload={
                "credit_card": generate_credit_card(rng),
                "email": generate_email(rng),
                "amount": generate_amount(rng),
            },
        )

    raise ValueError(f"Unknown scenario: {name}")


def weighted_scenario_name(rng: Random) -> str:
    names = list(SCENARIO_WEIGHTS.keys())
    weights = list(SCENARIO_WEIGHTS.values())
    return rng.choices(names, weights=weights, k=1)[0]
