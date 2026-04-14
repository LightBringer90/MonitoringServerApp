import os
import platform
import socket
import time
from typing import List

import psutil

from app.schemas.system import CpuStats, DiskStats, MemoryStats, MetaInfo, NetworkStats, ProcessSummary, SystemStatsResponse

PSEUDO_MOUNT_EXACT = {
    "/etc/hosts",
    "/etc/hostname",
    "/etc/resolv.conf",
}

PSEUDO_MOUNT_PREFIXES = (
    "/proc",
    "/sys",
    "/dev",
)



def _should_keep_partition(mountpoint: str) -> bool:
    if mountpoint in PSEUDO_MOUNT_EXACT:
        return False
    return not any(mountpoint.startswith(prefix) for prefix in PSEUDO_MOUNT_PREFIXES)



def _load_average() -> tuple[float | None, float | None, float | None]:
    try:
        return os.getloadavg()
    except (AttributeError, OSError):
        return None, None, None



def _process_summary() -> ProcessSummary:
    processes = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = proc.info
            processes.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    top_cpu = sorted(processes, key=lambda p: p.get("cpu_percent") or 0, reverse=True)[:5]
    top_memory = sorted(processes, key=lambda p: p.get("memory_percent") or 0, reverse=True)[:5]

    return ProcessSummary(
        total_processes=len(processes),
        top_cpu=[f"{p.get('name','unknown')}:{p.get('cpu_percent',0)}" for p in top_cpu],
        top_memory=[f"{p.get('name','unknown')}:{round(p.get('memory_percent',0), 2)}" for p in top_memory],
    )



def get_system_stats() -> SystemStatsResponse:
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time

    disks: List[DiskStats] = []
    for part in psutil.disk_partitions(all=True):
        if not _should_keep_partition(part.mountpoint):
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disks.append(
                DiskStats(
                    mountpoint=part.mountpoint,
                    total=usage.total,
                    used=usage.used,
                    free=usage.free,
                    percent=usage.percent,
                )
            )
        except PermissionError:
            continue

    disks.sort(key=lambda d: d.mountpoint)
    net = psutil.net_io_counters()
    memory = psutil.virtual_memory()
    load_1m, load_5m, load_15m = _load_average()

    notes = [
        "This service runs inside Docker.",
        "CPU, memory, and network reflect container-visible runtime data.",
        "Process visibility is container-scoped in the current runtime mode.",
    ]
    if not disks:
        notes.append("Disk visibility is limited in the current container runtime scope.")

    return SystemStatsResponse(
        hostname=socket.gethostname(),
        platform=f"{platform.system()} {platform.release()}",
        uptime_seconds=uptime_seconds,
        cpu=CpuStats(
            percent=psutil.cpu_percent(interval=0.2),
            count=os.cpu_count() or 1,
            load_avg_1m=load_1m,
            load_avg_5m=load_5m,
            load_avg_15m=load_15m,
        ),
        memory=MemoryStats(
            total=memory.total,
            available=memory.available,
            used=memory.used,
            percent=memory.percent,
        ),
        disks=disks,
        network=NetworkStats(
            bytes_sent=net.bytes_sent,
            bytes_recv=net.bytes_recv,
            packets_sent=net.packets_sent,
            packets_recv=net.packets_recv,
        ),
        processes=_process_summary(),
        meta=MetaInfo(scope="container-runtime", notes=notes),
    )
