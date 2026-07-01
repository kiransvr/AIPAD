"""Upload controller wrappers."""
from typing import Any

from fastapi import UploadFile

from src.services.upload_service import (
    get_sample_template,
    get_upload_status,
    reset_uploaded_data,
    upload_portfolio_data,
)

async def upload(
    file: UploadFile,
    uploader_username: str | None = None,
    uploader_role: str | None = None,
) -> dict[str, Any]:
    return await upload_portfolio_data(
        file,
        uploader_username=uploader_username,
        uploader_role=uploader_role,
    )


def upload_status() -> dict[str, Any]:
    return get_upload_status()


def sample_template() -> dict[str, Any]:
    return get_sample_template()


def reset_upload() -> dict[str, str]:
    return reset_uploaded_data()
