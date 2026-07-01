"""Growth controller orchestrating growth analytics use-cases."""
from typing import Any

from src.services.growth_service import get_growth_forecast, get_growth_summary, get_growth_trend, get_product_mix


def growth_summary() -> dict[str, Any]:
    return get_growth_summary()


def growth_trend(period: str = "monthly") -> dict[str, Any]:
    return get_growth_trend(period)


def growth_forecast(months: int = 12) -> dict[str, Any]:
    return get_growth_forecast(months)


def product_mix() -> dict[str, Any]:
    return get_product_mix()
