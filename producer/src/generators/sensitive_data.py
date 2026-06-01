from __future__ import annotations

from random import Random


def generate_tckn(rng: Random) -> str:
    first = rng.randint(1, 9)
    remaining = "".join(str(rng.randint(0, 9)) for _ in range(10))
    return f"{first}{remaining}"


def generate_credit_card(rng: Random) -> str:
    prefix = "5235"
    middle = "".join(str(rng.randint(0, 9)) for _ in range(8))
    suffix = "".join(str(rng.randint(0, 9)) for _ in range(4))
    return f"{prefix}{middle}{suffix}"


def generate_email(rng: Random) -> str:
    local = f"user{rng.randint(1000, 9999)}"
    domain = rng.choice(["example.com", "mail.net", "corp.org"])
    return f"{local}@{domain}"


def generate_iban(rng: Random) -> str:
    digits = "".join(str(rng.randint(0, 9)) for _ in range(24))
    return f"TR{digits}"


def generate_swift(rng: Random) -> str:
    bank = "".join(rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(4))
    country = "TR"
    location = "".join(rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(2))
    return f"{bank}{country}{location}"


def generate_amount(rng: Random) -> float:
    raw = rng.uniform(100.0, 250000.0)
    return round(raw, 2)
