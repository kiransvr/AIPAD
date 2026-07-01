"""PAR (Portfolio at Risk) routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from src.controllers.analytics_controller import (
    par_by_branch,
    par_by_region,
    par_summary,
    par_trend,
)
from src.auth import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/summary")
async def get_par_summary(
    session: AsyncSession = Depends(lambda: None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
):
    """Get PAR summary metrics"""
    _ = session
    return par_summary(start_date=start_date, end_date=end_date)


@router.get("/by-region")
async def get_par_by_region(
    session: AsyncSession = Depends(lambda: None)
):
    """Get PAR by region"""
    _ = session
    return par_by_region()


@router.get("/by-branch")
async def get_par_by_branch(
    session: AsyncSession = Depends(lambda: None)
):
    """Get PAR by branch"""
    _ = session
    return par_by_branch()


@router.get("/trend")
async def get_par_trend(
    days: int = Query(90),
    session: AsyncSession = Depends(lambda: None)
):
    """Get PAR trend data"""
    _ = session
    return par_trend(days=days)
