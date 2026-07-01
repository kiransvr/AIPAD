"""
Main entry point for the AI Portfolio Analytics Dashboard API
"""
from fastapi import FastAPI
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import uuid
from collections import defaultdict, deque
from time import monotonic

from src.config import settings
from src.database.core import init_db, close_db
from src.api.routes.auth_routes import router as auth_router
from src.api.routes import (
    par_routes,
    npl_routes,
    branch_routes,
    officer_routes,
    regional_routes,
    growth_routes,
    gender_routes,
    inclusion_routes,
    health_routes,
    upload_routes
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory rate limiter storage (per-process)
_request_history: dict[str, deque[float]] = defaultdict(deque)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages app startup and shutdown events
    """
    logger.info("Starting AI Portfolio Analytics Dashboard")
    await init_db()
    yield
    logger.info("Shutting down AI Portfolio Analytics Dashboard")
    await close_db()


# Initialize FastAPI app
app = FastAPI(
    title="AI Portfolio Analytics Dashboard",
    description="Data-as-a-Service (DAaaS) solution for portfolio risk analysis and operational intelligence",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Attach request id and security headers to every response."""
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

    if settings.ENVIRONMENT.lower() != "development":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Simple IP-based sliding-window rate limiter."""
    if not settings.RATE_LIMIT_ENABLED:
        return await call_next(request)

    # Keep preflight and docs discovery routes unthrottled for UX.
    if request.method == "OPTIONS" or request.url.path in {"/", "/docs", "/redoc", "/openapi.json"}:
        return await call_next(request)

    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = request_id

    client_ip = request.client.host if request.client else "unknown"
    window_seconds = max(settings.RATE_LIMIT_WINDOW_SECONDS, 1)
    max_requests = max(settings.RATE_LIMIT_MAX_REQUESTS, 1)
    now = monotonic()

    history = _request_history[client_ip]
    window_start = now - window_seconds
    while history and history[0] < window_start:
        history.popleft()

    if len(history) >= max_requests:
        retry_after = 1
        if history:
            retry_after = max(1, int(window_seconds - (now - history[0])))

        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "code": "rate_limit_exceeded",
                    "message": "Too many requests. Please retry shortly.",
                    "status": 429,
                },
                "request_id": request_id,
            },
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(max_requests),
                "X-RateLimit-Remaining": "0",
            },
        )

    history.append(now)
    response = await call_next(request)
    remaining = max(0, max_requests - len(history))
    response.headers["X-RateLimit-Limit"] = str(max_requests)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Standardized HTTP error response format."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    if isinstance(exc.detail, str):
        message = exc.detail
        details = None
    elif isinstance(exc.detail, dict):
        message = str(exc.detail.get("message") or exc.detail.get("error") or "Request failed")
        details = exc.detail
    else:
        message = "Request failed"
        details = exc.detail

    error_payload = {
        "code": "http_error",
        "message": message,
        "status": exc.status_code,
    }
    if details is not None:
        error_payload["details"] = details

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": error_payload,
            "request_id": request_id,
        },
    )


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    """Centralized validation error response."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed.",
                "status": 422,
                "details": exc.errors(),
            },
            "request_id": request_id,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all error handler for unhandled server exceptions."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.exception("Unhandled error. request_id=%s", request_id, exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_server_error",
                "message": "An unexpected server error occurred.",
                "status": 500,
            },
            "request_id": request_id,
        },
    )


# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(health_routes.router, prefix="/api/v1/health", tags=["health"])
app.include_router(par_routes.router, prefix="/api/v1/par", tags=["par"])
app.include_router(npl_routes.router, prefix="/api/v1/npl", tags=["npl"])
app.include_router(branch_routes.router, prefix="/api/v1/branches", tags=["branches"])
app.include_router(officer_routes.router, prefix="/api/v1/officers", tags=["officers"])
app.include_router(regional_routes.router, prefix="/api/v1/regional", tags=["regional"])
app.include_router(growth_routes.router, prefix="/api/v1/growth", tags=["growth"])
app.include_router(gender_routes.router, prefix="/api/v1/gender", tags=["gender"])
app.include_router(inclusion_routes.router, prefix="/api/v1/inclusion", tags=["inclusion"])
app.include_router(upload_routes.router, prefix="/api/v1/upload", tags=["upload"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to AI Portfolio Analytics Dashboard",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
