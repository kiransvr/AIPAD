"""
Main entry point for the AI Portfolio Analytics Dashboard API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging

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
