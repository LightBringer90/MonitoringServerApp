from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {"status": "ok", "service": "server-monitor-api"}


@router.get("/health/ready")
def ready():
    return {"status": "ready", "service": "server-monitor-api"}
