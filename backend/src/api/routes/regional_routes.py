"""Regional heatmap routes."""

from fastapi import APIRouter, Depends

from src.controllers.regional_controller import map_data, region_detail, risk_heatmap, risk_zones
from src.auth import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/heatmap")
async def get_risk_heatmap(session = Depends(lambda: None)):
    """Get regional risk heatmap data"""
    _ = session
    return risk_heatmap()


@router.get("/risk-zones")
async def get_risk_zones(session = Depends(lambda: None)):
    """Get risk zone classifications"""
    _ = session
    return risk_zones()


@router.get("/map-data")
async def get_map_data(session = Depends(lambda: None)):
    """Get map points derived from uploaded regional data."""
    _ = session
    return map_data()


@router.get("/region/{region_id}")
async def get_region_detail(
    region_id: str,
    session = Depends(lambda: None)
):
    """Get specific region details"""
    _ = session
    return region_detail(region_id)
