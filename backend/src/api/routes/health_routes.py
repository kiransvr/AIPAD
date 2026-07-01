"""Health check routes."""

from fastapi import APIRouter

from src.controllers.health_controller import health_check as health_check_controller
from src.controllers.health_controller import liveness as liveness_controller
from src.controllers.health_controller import readiness as readiness_controller

router = APIRouter()


@router.get("/")
async def health_check():
    """Health check endpoint"""
    return health_check_controller()


@router.get("/live")
async def liveness():
    """Kubernetes liveness probe"""
    return liveness_controller()


@router.get("/ready")
async def readiness():
    """Kubernetes readiness probe"""
    return readiness_controller()
