"""Gender analytics routes."""

from fastapi import APIRouter, Depends

from src.controllers.gender_controller import gender_performance, gender_summary, gender_trend
from src.auth import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/summary")
async def get_gender_summary(session = Depends(lambda: None)):
    """Get gender analytics summary"""
    _ = session
    return gender_summary()


@router.get("/performance-comparison")
async def get_gender_performance(session = Depends(lambda: None)):
    """Compare performance metrics by gender"""
    _ = session
    return gender_performance()


@router.get("/trend")
async def get_gender_trend(session = Depends(lambda: None)):
    """Get gender inclusion trend"""
    _ = session
    return gender_trend()
