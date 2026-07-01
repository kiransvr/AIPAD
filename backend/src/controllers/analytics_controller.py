"""Analytics controller entry points."""
from datetime import datetime
from typing import Any

from src.services.npl_service import get_collections_pipeline, get_npl_by_stage, get_npl_summary
from src.services.par_service import get_par_by_branch, get_par_by_region, get_par_summary, get_par_trend


def par_summary(start_date: datetime | None = None, end_date: datetime | None = None) -> dict[str, Any]:
    return get_par_summary(start_date=start_date, end_date=end_date)


def par_by_region() -> dict[str, Any]:
    return get_par_by_region()


def par_by_branch() -> dict[str, Any]:
    return get_par_by_branch()


def par_trend(days: int = 90) -> dict[str, Any]:
    return get_par_trend(days=days)


def npl_summary() -> dict[str, Any]:
    return get_npl_summary()


def npl_by_stage() -> dict[str, Any]:
    return get_npl_by_stage()


def npl_collections() -> dict[str, Any]:
    return get_collections_pipeline()
