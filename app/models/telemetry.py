"""Persistence model for telemetry snapshots."""

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TelemetrySnapshot(Base):
    __tablename__ = "telemetry_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    hostname: Mapped[str] = mapped_column(String(255))
    cpu_percent: Mapped[float] = mapped_column(Float)
    memory_percent: Mapped[float] = mapped_column(Float)
    disk_count: Mapped[int] = mapped_column(Integer)
    total_processes: Mapped[int] = mapped_column(Integer)
    bytes_sent: Mapped[int] = mapped_column(Integer)
    bytes_recv: Mapped[int] = mapped_column(Integer)
    scope: Mapped[str] = mapped_column(String(64))
