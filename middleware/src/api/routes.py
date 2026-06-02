from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from middleware.src.metrics.collector import METRICS

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/metrics")
def metrics() -> dict[str, Any]:
    return METRICS.snapshot()
