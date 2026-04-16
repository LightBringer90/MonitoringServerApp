"""Authenticated system telemetry endpoints for dashboard and operator use."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import require_auth, require_token
from app.core.config import settings
from app.core.database import get_db
from app.schemas.system import (
    AlertStatusResponse,
    ErrorResponse,
    SystemStatsResponse,
    SystemSummaryResponse,
    TelemetryHistoryResponse,
    TelemetryTrendWindow,
)
from app.services.alert_service import send_failure_report, threshold_reasons
from app.services.system_service import get_system_stats
from app.services.telemetry_service import get_recent_history, get_trend_window, record_snapshot

router = APIRouter(prefix="/api/system", tags=["system"])

common_error_responses = {
    status.HTTP_401_UNAUTHORIZED: {
        "model": ErrorResponse,
        "description": "Authentication failed or required credentials were missing.",
    }
}


@router.post(
    "/snapshot",
    response_model=SystemSummaryResponse,
    summary="Capture and persist a telemetry snapshot",
    description="Captures the current monitoring payload and stores a compact history record for dashboard trend views.",
    responses=common_error_responses,
)
def capture_snapshot(
    _token: str = Depends(require_token),
    db: Session = Depends(get_db),
) -> SystemSummaryResponse:
    stats = get_system_stats()
    record_snapshot(db, stats, settings.snapshot_retention_limit)
    return SystemSummaryResponse(
        hostname=stats.hostname,
        platform=stats.platform,
        uptime_seconds=stats.uptime_seconds,
        cpu_percent=stats.cpu.percent,
        memory_percent=stats.memory.percent,
        disk_count=len(stats.disks),
        scope=stats.meta.scope,
    )


@router.get(
    "/history",
    response_model=TelemetryHistoryResponse,
    summary="Read persisted telemetry history",
    description="Returns recent persisted telemetry snapshots for dashboard history and trend views.",
    responses=common_error_responses,
)
def telemetry_history(
    _token: str = Depends(require_token),
    limit: int = Query(default=settings.history_limit_default, ge=1, le=500),
    db: Session = Depends(get_db),
) -> TelemetryHistoryResponse:
    return get_recent_history(db, limit)


@router.get(
    "/trends",
    response_model=TelemetryTrendWindow,
    summary="Read telemetry trend window",
    description="Returns a compact trend window with aggregates that dashboards can use for recent CPU, memory, and process trend summaries.",
    responses=common_error_responses,
)
def telemetry_trends(
    _token: str = Depends(require_token),
    limit: int = Query(default=12, ge=1, le=120),
    db: Session = Depends(get_db),
) -> TelemetryTrendWindow:
    return get_trend_window(db, limit)


@router.get(
    "",
    response_model=SystemStatsResponse,
    summary="Full system telemetry",
    description="Returns the detailed monitoring payload intended for dashboards and internal tooling.",
    responses=common_error_responses,
)
def system_stats(_token: str = Depends(require_token)) -> SystemStatsResponse:
    return get_system_stats()


@router.get(
    "/summary",
    response_model=SystemSummaryResponse,
    summary="Compact system summary",
    description="Returns a lightweight summary payload suitable for frequent dashboard polling.",
    responses=common_error_responses,
)
def system_summary(_token: str = Depends(require_token)) -> SystemSummaryResponse:
    stats = get_system_stats()
    return SystemSummaryResponse(
        hostname=stats.hostname,
        platform=stats.platform,
        uptime_seconds=stats.uptime_seconds,
        cpu_percent=stats.cpu.percent,
        memory_percent=stats.memory.percent,
        disk_count=len(stats.disks),
        scope=stats.meta.scope,
    )


@router.get(
    "/alerts/status",
    response_model=AlertStatusResponse,
    summary="Read current alert status",
    description="Evaluates the current CPU and memory readings against configured thresholds and returns a compact operator-facing alert posture.",
    responses=common_error_responses,
)
def alert_status(_token: str = Depends(require_token)) -> AlertStatusResponse:
    stats = get_system_stats()
    reasons = threshold_reasons(stats)
    return AlertStatusResponse(
        status="warning" if reasons else "ok",
        hostname=stats.hostname,
        cpu_percent=stats.cpu.percent,
        memory_percent=stats.memory.percent,
        cpu_threshold=settings.cpu_alert_threshold,
        memory_threshold=settings.memory_alert_threshold,
        reasons=reasons,
        alert_email_enabled=settings.alert_email_enabled,
        scope=stats.meta.scope,
    )


@router.post(
    "/alerts/test",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger a test alert email",
    description="Sends a test alert email through the configured SMTP path so operators can verify end-to-end alert delivery.",
    responses=common_error_responses,
)
def trigger_test_alert(_token: str = Depends(require_token)) -> dict[str, str]:
    send_failure_report("Operator-triggered test alert")
    return {"status": "queued", "detail": "Test alert email sent"}


@router.get(
    "/basic",
    response_model=SystemStatsResponse,
    summary="Full system telemetry via HTTP Basic auth",
    description="Compatibility endpoint for manual access paths that still use HTTP Basic auth.",
    responses=common_error_responses,
)
def system_stats_basic(_user: str = Depends(require_auth)) -> SystemStatsResponse:
    return get_system_stats()
