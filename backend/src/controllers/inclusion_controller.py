"""Inclusion controller orchestrating inclusion analytics use-cases."""
from typing import Any

from src.services.inclusion_service import (
    get_demographic_breakdown,
    get_inclusion_index,
    get_inclusion_summary,
    get_regional_inclusion,
)


def inclusion_summary() -> dict[str, Any]:
    return get_inclusion_summary()


def demographic_breakdown() -> dict[str, Any]:
    return get_demographic_breakdown()


def regional_inclusion() -> dict[str, Any]:
    return get_regional_inclusion()


def inclusion_index() -> dict[str, Any]:
    return get_inclusion_index()
