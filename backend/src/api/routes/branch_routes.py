"""Branch performance routes."""

from fastapi import APIRouter, Depends

from src.controllers.branch_controller import branch_detail, branch_ranking, branch_summary
from src.auth import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/summary")
async def get_branch_summary(session = Depends(lambda: None)):
    """Get all branch performance summary"""
    _ = session
    return branch_summary()


@router.get("/{branch_id}")
async def get_branch_detail(
    branch_id: int,
    session = Depends(lambda: None)
):
    """Get specific branch details"""
    _ = session
    return branch_detail(branch_id)


@router.get("/ranking/performance")
async def get_branch_ranking(
    session = Depends(lambda: None)
):
    """Get branch performance ranking"""
    _ = session
    return branch_ranking()
