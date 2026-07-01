"""NPL (Non-Performing Loans) routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.analytics_controller import npl_by_stage, npl_collections, npl_summary
from src.auth import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/summary")
async def get_npl_summary(
    session: AsyncSession = Depends(lambda: None)
):
    """Get NPL summary metrics"""
    _ = session
    return npl_summary()


@router.get("/by-stage")
async def get_npl_by_stage(
    session: AsyncSession = Depends(lambda: None)
):
    """Get NPL by stage (PL, SL, DL)"""
    _ = session
    return npl_by_stage()


@router.get("/collections")
async def get_collections_pipeline(
    session: AsyncSession = Depends(lambda: None)
):
    """Get collections pipeline data"""
    _ = session
    return npl_collections()
