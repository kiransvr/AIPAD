"""Financial inclusion metrics routes."""

from fastapi import APIRouter, Depends

from src.controllers.inclusion_controller import (
    demographic_breakdown,
    inclusion_index,
    inclusion_summary,
    regional_inclusion,
)
from src.auth import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/summary")
async def get_inclusion_summary(session = Depends(lambda: None)):
    """Get financial inclusion summary"""
    _ = session
    return inclusion_summary()


@router.get("/demographic-breakdown")
async def get_demographic_breakdown(session = Depends(lambda: None)):
    """Get demographic breakdown"""
    _ = session
    return demographic_breakdown()


@router.get("/regional-inclusion")
async def get_regional_inclusion(session = Depends(lambda: None)):
    """Get regional inclusion metrics"""
    _ = session
    return regional_inclusion()


@router.get("/inclusion-index")
async def get_inclusion_index(session = Depends(lambda: None)):
    """Get inclusion index trend"""
    _ = session
    return inclusion_index()
