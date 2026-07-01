"""Data upload routes for portfolio data."""

from fastapi import APIRouter, Depends, File, UploadFile

from src.auth import User, get_current_user, require_roles
from src.controllers.upload_controller import (
    reset_upload,
    sample_template,
    upload,
    upload_status,
)
from src.services.upload_service import get_uploaded_dataframe, get_uploaded_summary

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("")
async def upload_portfolio_data(
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles("admin", "risk", "branch-manager", "loan-officer")),
):
    """Upload loan portfolio data (Excel or CSV)."""
    return await upload(file, uploader_username=current_user.username, uploader_role=current_user.role)


@router.get("/status")
async def get_upload_status():
    """Get status of last uploaded data."""
    return upload_status()


@router.get("/sample")
async def get_sample_template():
    """Get sample data template for portfolio upload."""
    return sample_template()


@router.post("/reset")
async def reset_uploaded_data(current_user: User = Depends(require_roles("admin", "risk"))):
    """Reset uploaded data (for testing/admin purposes)."""
    _ = current_user
    return reset_upload()


__all__ = ["router", "get_uploaded_dataframe", "get_uploaded_summary"]
