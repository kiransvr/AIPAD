"""Portfolio growth routes."""

from fastapi import APIRouter, Depends, Query

from src.controllers.growth_controller import (
    growth_forecast,
    growth_summary,
    growth_trend,
    product_mix,
)
from src.auth import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/summary")
async def get_growth_summary(
    session = Depends(lambda: None)
):
    """Get portfolio growth summary"""
    _ = session
    return growth_summary()


@router.get("/trend")
async def get_growth_trend(
    period: str = Query("monthly"),
    session = Depends(lambda: None)
):
    """Get portfolio growth trend"""
    _ = session
    return growth_trend(period=period)


@router.get("/forecast")
async def get_growth_forecast(
    months: int = Query(12),
    session = Depends(lambda: None)
):
    """Get portfolio growth forecast"""
    _ = session
    return growth_forecast(months=months)


@router.get("/product-mix")
async def get_product_mix(session = Depends(lambda: None)):
    """Get product mix analysis"""
    _ = session
    return product_mix()
