"""Branch controller orchestrating branch analytics use-cases."""
from typing import Any

from src.services.branch_service import get_branch_detail, get_branch_ranking, get_branch_summary


def branch_summary() -> dict[str, Any]:
    return get_branch_summary()


def branch_detail(branch_id: int) -> dict[str, Any]:
    return get_branch_detail(branch_id)


def branch_ranking() -> dict[str, Any]:
    return get_branch_ranking()
