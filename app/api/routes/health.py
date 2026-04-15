"""Health and readiness endpoints for the monitoring API."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness probe", description="Simple endpoint confirming that the API process is up.")
def health():
    return {"status": "ok", "service": "server-monitor-api"}


@router.get("/health/ready", summary="Readiness probe", description="Endpoint confirming that the API is ready to serve requests.")
def ready():
    return {"status": "ready", "service": "server-monitor-api"}
