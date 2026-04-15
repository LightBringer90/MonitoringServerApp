"""Health and readiness endpoints for the monitoring API."""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness probe", description="Simple endpoint confirming that the API process is up.")
def health():
    return {"status": "ok", "service": "server-monitor-api"}


@router.get("/health/ready", summary="Readiness probe", description="Endpoint confirming that the API is ready to serve requests.")
def ready():
    issues = settings.readiness_issues()
    if issues:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not-ready", "service": "server-monitor-api", "issues": issues},
        )
    return {"status": "ready", "service": "server-monitor-api"}
