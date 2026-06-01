from __future__ import annotations

from random import Random

from shared.log_schema import LogRecord

from .scenarios import generate_scenario, weighted_scenario_name


class LogFactory:
    def __init__(self, seed: int, producer_id: str) -> None:
        self._rng = Random(seed)
        self._producer_id = producer_id

    def create_log(self) -> LogRecord:
        scenario_name = weighted_scenario_name(self._rng)
        scenario = generate_scenario(scenario_name, self._rng)

        payload = dict(scenario.payload)
        payload["scenario"] = scenario.name
        payload["producer_id"] = self._producer_id

        return LogRecord(
            level=scenario.level,
            type=scenario.log_type,
            role=scenario.role,
            source=scenario.source,
            message=scenario.message,
            payload=payload,
        )
