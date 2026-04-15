"""Response schemas for the server monitoring API."""

from typing import List, Optional

from pydantic import BaseModel, Field


class CpuStats(BaseModel):
    percent: float = Field(description="Current CPU utilization percentage visible to the runtime.")
    count: int = Field(description="Visible CPU core count.")
    load_avg_1m: Optional[float] = Field(default=None, description="One-minute system load average when available.")
    load_avg_5m: Optional[float] = Field(default=None, description="Five-minute system load average when available.")
    load_avg_15m: Optional[float] = Field(default=None, description="Fifteen-minute system load average when available.")


class MemoryStats(BaseModel):
    total: int = Field(description="Total visible memory in bytes.")
    available: int = Field(description="Currently available memory in bytes.")
    used: int = Field(description="Currently used memory in bytes.")
    percent: float = Field(description="Current memory utilization percentage.")


class DiskStats(BaseModel):
    mountpoint: str = Field(description="Mounted filesystem path.")
    total: int = Field(description="Total disk capacity in bytes.")
    used: int = Field(description="Used disk capacity in bytes.")
    free: int = Field(description="Free disk capacity in bytes.")
    percent: float = Field(description="Disk utilization percentage.")


class NetworkStats(BaseModel):
    bytes_sent: int = Field(description="Bytes sent since process/runtime start visibility window.")
    bytes_recv: int = Field(description="Bytes received since process/runtime start visibility window.")
    packets_sent: int = Field(description="Packets sent since process/runtime start visibility window.")
    packets_recv: int = Field(description="Packets received since process/runtime start visibility window.")


class ProcessSummary(BaseModel):
    total_processes: int = Field(description="Visible process count in the current runtime scope.")
    top_cpu: List[str] = Field(description="Top CPU-consuming visible processes.")
    top_memory: List[str] = Field(description="Top memory-consuming visible processes.")


class MetaInfo(BaseModel):
    scope: str = Field(description="Observability scope for this monitoring payload.")
    notes: List[str] = Field(description="Important caveats or runtime notes for interpreting the payload.")


class TelemetrySnapshotResponse(BaseModel):
    created_at: str = Field(description="Timestamp when the snapshot was persisted.")
    hostname: str = Field(description="Visible hostname at the time of capture.")
    cpu_percent: float = Field(description="Captured CPU utilization percentage.")
    memory_percent: float = Field(description="Captured memory utilization percentage.")
    disk_count: int = Field(description="Number of visible disks in the snapshot.")
    total_processes: int = Field(description="Visible process count in the snapshot.")
    bytes_sent: int = Field(description="Captured transmitted bytes counter.")
    bytes_recv: int = Field(description="Captured received bytes counter.")
    scope: str = Field(description="Observability scope for the snapshot.")


class TelemetryHistoryResponse(BaseModel):
    items: List[TelemetrySnapshotResponse] = Field(description="Recent persisted telemetry snapshots.")


class SystemSummaryResponse(BaseModel):
    hostname: str = Field(description="Visible hostname for the running container or host context.")
    platform: str = Field(description="Operating system and kernel/platform descriptor.")
    uptime_seconds: float = Field(description="Runtime uptime in seconds.")
    cpu_percent: float = Field(description="Current CPU utilization percentage.")
    memory_percent: float = Field(description="Current memory utilization percentage.")
    disk_count: int = Field(description="Number of visible disk mountpoints included in detailed telemetry.")
    scope: str = Field(description="Observability scope for the summary payload.")


class ErrorResponse(BaseModel):
    detail: str = Field(description="Machine-readable or operator-readable error message.")


class SystemStatsResponse(BaseModel):
    hostname: str = Field(description="Visible hostname for the running container or host context.")
    platform: str = Field(description="Operating system and kernel/platform descriptor.")
    uptime_seconds: float = Field(description="Runtime uptime in seconds.")
    cpu: CpuStats
    memory: MemoryStats
    disks: List[DiskStats]
    network: NetworkStats
    processes: ProcessSummary
    meta: MetaInfo
