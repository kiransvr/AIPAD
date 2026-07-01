"""Authentication and RBAC integration tests."""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.routes import auth_routes, health_routes, par_routes, upload_routes

app = FastAPI()
app.include_router(auth_routes.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(health_routes.router, prefix="/api/v1/health", tags=["health"])
app.include_router(par_routes.router, prefix="/api/v1/par", tags=["par"])
app.include_router(upload_routes.router, prefix="/api/v1/upload", tags=["upload"])

client = TestClient(app)


def _login(username: str, password: str) -> dict:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    return body


def test_health_endpoint_still_public() -> None:
    response = client.get("/api/v1/health/")
    assert response.status_code == 200


def test_login_returns_bearer_token_and_user_profile() -> None:
    body = _login("admin", "admin123")
    assert body["token_type"] == "bearer"
    assert body["user"]["username"] == "admin"
    assert body["user"]["role"] == "admin"


def test_protected_route_requires_token() -> None:
    response = client.get("/api/v1/par/summary")
    assert response.status_code == 401


def test_admin_can_access_par_and_upload_status() -> None:
    admin = _login("admin", "admin123")
    headers = {"Authorization": f"Bearer {admin['access_token']}"}

    par_response = client.get("/api/v1/par/summary", headers=headers)
    upload_response = client.get("/api/v1/upload/status", headers=headers)

    assert par_response.status_code == 200
    assert upload_response.status_code == 200


def test_branch_manager_cannot_access_upload_status() -> None:
    branch_manager = _login("branchmgr", "branch123")
    headers = {"Authorization": f"Bearer {branch_manager['access_token']}"}

    par_response = client.get("/api/v1/par/summary", headers=headers)
    upload_response = client.get("/api/v1/upload/status", headers=headers)

    assert par_response.status_code == 200
    assert upload_response.status_code == 403
