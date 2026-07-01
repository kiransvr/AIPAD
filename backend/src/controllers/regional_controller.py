"""Regional controller orchestrating regional analytics use-cases."""
from typing import Any

from src.services.regional_service import get_map_data, get_region_detail, get_risk_heatmap, get_risk_zones


def risk_heatmap() -> dict[str, Any]:
    return get_risk_heatmap()


def risk_zones() -> dict[str, Any]:
    return get_risk_zones()


def region_detail(region_id: str) -> dict[str, Any]:
    return get_region_detail(region_id)


def map_data() -> dict[str, Any]:
    return get_map_data()
