"""Security middleware and error envelope tests."""

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
import httpx
import pytest

from src.config import settings
from src.main import (
    _request_history,
    http_exception_handler,
    rate_limit_middleware,
    request_validation_exception_handler,
    security_headers_middleware,
    unhandled_exception_handler,
)


def _make_test_app() -> FastAPI:
    app = FastAPI()

    app.middleware("http")(security_headers_middleware)
    app.middleware("http")(rate_limit_middleware)

    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)

    @app.get("/ok")
    async def ok() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/boom")
    async def boom() -> None:
        raise HTTPException(status_code=400, detail="Bad input")

    return app


@pytest.mark.asyncio
async def test_security_headers_are_attached() -> None:
    app = _make_test_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/ok")

        assert response.status_code == 200
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
        assert response.headers.get("Permissions-Policy") == "geolocation=(), camera=(), microphone=()"
        assert response.headers.get("X-Request-ID")


@pytest.mark.asyncio
async def test_http_error_response_uses_standard_envelope() -> None:
    app = _make_test_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/boom")
        body = response.json()

        assert response.status_code == 400
        assert body["error"]["code"] == "http_error"
        assert body["error"]["message"] == "Bad input"
        assert body["error"]["status"] == 400
        assert body["request_id"]


@pytest.mark.asyncio
async def test_rate_limiter_returns_429_after_limit() -> None:
    app = _make_test_app()

    # Isolate test state from other tests sharing module-level limiter history.
    _request_history.clear()

    original_enabled = settings.RATE_LIMIT_ENABLED
    original_max_requests = settings.RATE_LIMIT_MAX_REQUESTS
    original_window = settings.RATE_LIMIT_WINDOW_SECONDS

    try:
        settings.RATE_LIMIT_ENABLED = True
        settings.RATE_LIMIT_MAX_REQUESTS = 2
        settings.RATE_LIMIT_WINDOW_SECONDS = 60

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            first = await client.get("/ok")
            second = await client.get("/ok")
            third = await client.get("/ok")

            assert first.status_code == 200
            assert second.status_code == 200
            assert third.status_code == 429
            assert third.json()["error"]["code"] == "rate_limit_exceeded"
            assert third.headers.get("Retry-After")
    finally:
        settings.RATE_LIMIT_ENABLED = original_enabled
        settings.RATE_LIMIT_MAX_REQUESTS = original_max_requests
        settings.RATE_LIMIT_WINDOW_SECONDS = original_window
        _request_history.clear()
