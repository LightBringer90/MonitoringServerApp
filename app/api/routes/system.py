from fastapi import APIRouter, Depends

from app.core.auth import require_auth, require_token
from app.schemas.system import SystemStatsResponse
from app.services.system_service import get_system_stats

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("", response_model=SystemStatsResponse)
def system_stats(_token: str = Depends(require_token)) -> SystemStatsResponse:
    return get_system_stats()


@router.get("/summary")
def system_summary(_token: str = Depends(require_token)):
    stats = get_system_stats()
    return {
        "hostname": stats.hostname,
        "platform": stats.platform,
        "uptime_seconds": stats.uptime_seconds,
        "cpu_percent": stats.cpu.percent,
        "memory_percent": stats.memory.percent,
        "disk_count": len(stats.disks),
        "scope": stats.meta.scope,
    }


@router.get("/basic", response_model=SystemStatsResponse)
def system_stats_basic(_user: str = Depends(require_auth)) -> SystemStatsResponse:
    return get_system_stats()
