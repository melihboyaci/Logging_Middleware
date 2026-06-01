from __future__ import annotations

from typing import Any

from middleware.src.security.rules import (
    CARD_PATTERN,
    EMAIL_PATTERN,
    IBAN_PATTERN,
    SWIFT_PATTERN,
    TC_PATTERN,
)


def _mask_tc(text: str) -> str:
    return TC_PATTERN.sub(lambda m: f"{m.group(0)[:2]}xxxxxxxx{m.group(0)[-1]}", text)


def _mask_card(text: str) -> str:
    def replace(match: Any) -> str:
        raw = "".join(ch for ch in match.group(0) if ch.isdigit())
        if len(raw) < 13 or len(raw) > 19:
            return match.group(0)
        return f"{raw[:4]} xxxxxx {raw[-4:]}"

    return CARD_PATTERN.sub(replace, text)


def _mask_iban(text: str) -> str:
    return IBAN_PATTERN.sub(lambda m: f"{m.group(0)[:4]}xxxxxxxxxxxxxxxxxxxx{m.group(0)[-4:]}", text)


def _mask_swift(text: str) -> str:
    return SWIFT_PATTERN.sub("***SWIFT***", text)


def _mask_email(text: str) -> str:
    def replace(match: Any) -> str:
        email = match.group(0)
        local, domain = email.split("@", 1)
        lead = local[0] if local else "x"
        return f"{lead}***@{domain}"

    return EMAIL_PATTERN.sub(replace, text)


def anonymize_text(text: str) -> str:
    text = _mask_tc(text)
    text = _mask_card(text)
    text = _mask_iban(text)
    text = _mask_swift(text)
    text = _mask_email(text)
    return text


def anonymize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    safe: dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, str):
            safe[key] = anonymize_text(value)
        else:
            safe[key] = value
    return safe
