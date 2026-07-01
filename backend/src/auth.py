"""
Authentication and authorization helpers.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from src.config import settings


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class User(BaseModel):
    """Public user profile returned to clients."""

    username: str
    full_name: str
    role: str
    disabled: bool = False


class UserInDB(User):
    """Internal representation that includes password hash."""

    hashed_password: str


def _hash_password(raw_password: str) -> str:
    return pwd_context.hash(raw_password)


_DEMO_USERS: dict[str, UserInDB] = {
    "admin": UserInDB(
        username="admin",
        full_name="Platform Admin",
        role="admin",
        hashed_password=_hash_password("admin123"),
    ),
    "risk": UserInDB(
        username="risk",
        full_name="Risk Analyst",
        role="risk",
        hashed_password=_hash_password("risk123"),
    ),
    "branchmgr": UserInDB(
        username="branchmgr",
        full_name="Branch Manager",
        role="branch-manager",
        hashed_password=_hash_password("branch123"),
    ),
    "loanofficer": UserInDB(
        username="loanofficer",
        full_name="Loan Officer",
        role="loan-officer",
        hashed_password=_hash_password("officer123"),
    ),
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Validate a plain password against the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str) -> UserInDB | None:
    """Authenticate a user from the in-memory user store."""
    user = _DEMO_USERS.get(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Decode JWT and return the authenticated user context."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        if not username or not role:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    user = _DEMO_USERS.get(username)
    if not user or user.disabled:
        raise credentials_exception
    return User(username=user.username, full_name=user.full_name, role=user.role, disabled=user.disabled)


def require_roles(*allowed_roles: str) -> Callable[[User], User]:
    """Dependency factory to enforce role-level route access."""

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' is not allowed for this endpoint",
            )
        return current_user

    return role_checker
