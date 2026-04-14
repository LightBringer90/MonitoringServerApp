from pydantic import BaseModel
from typing import List, Optional


class CpuStats(BaseModel):
    percent: float
    count: int
    load_avg_1m: Optional[float] = None
    load_avg_5m: Optional[float] = None
    load_avg_15m: Optional[float] = None


class MemoryStats(BaseModel):
    total: int
    available: int
    used: int
    percent: float


class DiskStats(BaseModel):
    mountpoint: str
    total: int
    used: int
    free: int
    percent: float


class NetworkStats(BaseModel):
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int


class ProcessSummary(BaseModel):
    total_processes: int
    top_cpu: List[str]
    top_memory: List[str]


class MetaInfo(BaseModel):
    scope: str
    notes: List[str]


class SystemStatsResponse(BaseModel):
    hostname: str
    platform: str
    uptime_seconds: float
    cpu: CpuStats
    memory: MemoryStats
    disks: List[DiskStats]
    network: NetworkStats
    processes: ProcessSummary
    meta: MetaInfo
