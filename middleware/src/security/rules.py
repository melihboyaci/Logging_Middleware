from __future__ import annotations

import re

TC_PATTERN = re.compile(r"\b[1-9]\d{10}\b")
CARD_PATTERN = re.compile(r"\b(?:\d[ -]?){13,19}\b")
IBAN_PATTERN = re.compile(r"\bTR\d{24}\b")
SWIFT_PATTERN = re.compile(r"\b[A-Z]{6}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b")
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
