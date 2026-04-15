"""Persistence helpers for telemetry history."""

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.telemetry import TelemetrySnapshot
from app.schemas.system import (
    SystemStatsResponse,
    TelemetryHistoryResponse,
    TelemetrySnapshotResponse,
    TelemetryTrendPoint,
    TelemetryTrendWindow,
)


def prune_old_snapshots(db: Session, retention_limit: int) -> None:
    rows = db.execute(
        select(TelemetrySnapshot.id).order_by(TelemetrySnapshot.created_at.desc()).offset(retention_limit)
    ).scalars().all()
    if rows:
        db.execute(delete(TelemetrySnapshot).where(TelemetrySnapshot.id.in_(rows)))
        db.commit()



def record_snapshot(db: Session, stats: SystemStatsResponse, retention_limit: int) -> TelemetrySnapshot:
    snapshot = TelemetrySnapshot(
        hostname=stats.hostname,
        cpu_percent=stats.cpu.percent,
        memory_percent=stats.memory.percent,
        disk_count=len(stats.disks),
        total_processes=stats.processes.total_processes,
        bytes_sent=stats.network.bytes_sent,
        bytes_recv=stats.network.bytes_recv,
        scope=stats.meta.scope,
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    prune_old_snapshots(db, retention_limit)
    return snapshot



def get_recent_history(db: Session, limit: int) -> TelemetryHistoryResponse:
    rows = db.execute(
        select(TelemetrySnapshot).order_by(TelemetrySnapshot.created_at.desc()).limit(limit)
    ).scalars().all()

    return TelemetryHistoryResponse(
        items=[
            TelemetrySnapshotResponse(
                created_at=row.created_at.isoformat(),
                hostname=row.hostname,
                cpu_percent=row.cpu_percent,
                memory_percent=row.memory_percent,
                disk_count=row.disk_count,
                total_processes=row.total_processes,
                bytes_sent=row.bytes_sent,
                bytes_recv=row.bytes_recv,
                scope=row.scope,
            )
            for row in rows
        ]
    )



def get_trend_window(db: Session, limit: int) -> TelemetryTrendWindow:
    rows = db.execute(
        select(TelemetrySnapshot).order_by(TelemetrySnapshot.created_at.desc()).limit(limit)
    ).scalars().all()
    chronological_rows = list(reversed(rows))

    if not chronological_rows:
        return TelemetryTrendWindow(
            points=[],
            cpu_average=0.0,
            cpu_peak=0.0,
            memory_average=0.0,
            memory_peak=0.0,
            process_average=0.0,
            latest_created_at=None,
        )

    cpu_values = [row.cpu_percent for row in chronological_rows]
    memory_values = [row.memory_percent for row in chronological_rows]
    process_values = [row.total_processes for row in chronological_rows]

    return TelemetryTrendWindow(
        points=[
            TelemetryTrendPoint(
                created_at=row.created_at.isoformat(),
                cpu_percent=row.cpu_percent,
                memory_percent=row.memory_percent,
                total_processes=row.total_processes,
            )
            for row in chronological_rows
        ],
        cpu_average=sum(cpu_values) / len(cpu_values),
        cpu_peak=max(cpu_values),
        memory_average=sum(memory_values) / len(memory_values),
        memory_peak=max(memory_values),
        process_average=sum(process_values) / len(process_values),
        latest_created_at=chronological_rows[-1].created_at.isoformat(),
    )
