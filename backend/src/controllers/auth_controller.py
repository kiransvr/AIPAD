"""Auth controller to bridge HTTP layer and services."""
from typing import Any

from src.services.auth_service import login_user


def login(username: str, password: str) -> dict[str, Any] | None:
    """Return login response payload or None for invalid credentials."""
    return login_user(username, password)
