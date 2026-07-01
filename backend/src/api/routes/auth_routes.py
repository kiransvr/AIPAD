"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.auth import User, get_current_user
from src.controllers.auth_controller import login as login_controller


router = APIRouter()


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return access token."""
    response = login_controller(form_data.username, form_data.password)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return response


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    """Return current user profile."""
    return current_user
