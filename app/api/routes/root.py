from fastapi import APIRouter

router = APIRouter(tags=["root"])


@router.get("/")
def root():
    return {
        "service": "server-monitor-api",
        "status": "ok",
        "endpoints": {
            "health": "/health",
            "system": "/api/system"
        }
    }
