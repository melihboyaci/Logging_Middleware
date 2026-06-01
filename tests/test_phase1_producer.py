from __future__ import annotations

from producer.src.generators.log_factory import LogFactory
from producer.src.generators.scenarios import SCENARIO_WEIGHTS, generate_scenario
from producer.src.generators.sensitive_data import (
    generate_credit_card,
    generate_email,
    generate_iban,
    generate_swift,
    generate_tckn,
)
from shared.log_schema import LogType


def test_sensitive_data_generators_shapes() -> None:
    from random import Random

    rng = Random(302)
    tc = generate_tckn(rng)
    card = generate_credit_card(rng)
    email = generate_email(rng)
    iban = generate_iban(rng)
    swift = generate_swift(rng)

    assert len(tc) == 11 and tc.isdigit()
    assert len(card) == 16 and card.isdigit()
    assert "@" in email
    assert iban.startswith("TR") and len(iban) == 26
    assert len(swift) == 8


def test_all_scenarios_producible() -> None:
    from random import Random

    rng = Random(302)
    for scenario_name in SCENARIO_WEIGHTS:
        output = generate_scenario(scenario_name, rng)
        assert output.name == scenario_name
        assert output.message
        assert output.source


def test_log_factory_produces_contract_fields() -> None:
    factory = LogFactory(seed=302, producer_id="producer-test")
    log = factory.create_log()

    assert log.source
    assert log.message
    assert "scenario" in log.payload
    assert log.payload["producer_id"] == "producer-test"
    assert log.type in {LogType.LOG, LogType.ERROR, LogType.TRANSACTION, LogType.ACCESS}
