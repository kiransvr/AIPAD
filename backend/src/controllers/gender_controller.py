"""Gender controller orchestrating gender analytics use-cases."""
from typing import Any

from src.services.gender_service import get_gender_performance, get_gender_summary, get_gender_trend


def gender_summary() -> dict[str, Any]:
    return get_gender_summary()


def gender_performance() -> dict[str, Any]:
    return get_gender_performance()


def gender_trend() -> dict[str, Any]:
    return get_gender_trend()
