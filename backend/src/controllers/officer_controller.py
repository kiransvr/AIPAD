"""Officer controller orchestrating officer productivity use-cases."""
from typing import Any

from src.services.officer_service import get_officer_detail, get_officer_leaderboard, get_officer_summary


def officer_summary() -> dict[str, Any]:
    return get_officer_summary()


def officer_detail(officer_id: int) -> dict[str, Any]:
    return get_officer_detail(officer_id)


def officer_leaderboard() -> dict[str, Any]:
    return get_officer_leaderboard()
