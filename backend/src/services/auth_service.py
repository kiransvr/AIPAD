"""Authentication service logic."""
from datetime import timedelta
from typing import Any

from src.auth import authenticate_user, create_access_token
from src.config import settings


def login_user(username: str, password: str) -> dict[str, Any] | None:
    """Authenticate and return token payload for API responses."""
    user = authenticate_user(username, password)
    if not user:
        return None

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
        },
    }
