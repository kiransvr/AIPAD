"""Loan officer productivity routes."""

from fastapi import APIRouter, Depends

from src.controllers.officer_controller import officer_detail, officer_leaderboard, officer_summary
from src.auth import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/summary")
async def get_officer_summary(session = Depends(lambda: None)):
    """Get loan officer productivity summary"""
    _ = session
    return officer_summary()


@router.get("/{officer_id}")
async def get_officer_detail(
    officer_id: int,
    session = Depends(lambda: None)
):
    """Get specific officer details"""
    _ = session
    return officer_detail(officer_id)


@router.get("/leaderboard/productivity")
async def get_officer_leaderboard(
    session = Depends(lambda: None)
):
    """Get officer productivity leaderboard"""
    _ = session
    return officer_leaderboard()
