"""Application entrypoint for the server-monitor-api service.

This module assembles the FastAPI application, registers routes, and defines
high-level API metadata so the service is easier to understand in OpenAPI and
for future maintainers.
"""

import threading
import time

from fastapi import FastAPI

from app.api.routes.root import router as root_router
from app.api.routes.health import router as health_router
from app.api.routes.system import router as system_router
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.services.system_service import get_system_stats
from app.services.telemetry_service import record_snapshot

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="Modular monitoring backend that exposes authenticated system telemetry for the dashboard client.",
    version="1.2.0",
)

app.include_router(root_router)
app.include_router(health_router)
app.include_router(system_router)



def snapshot_worker() -> None:
    while True:
        db = SessionLocal()
        try:
            stats = get_system_stats()
            record_snapshot(db, stats, settings.snapshot_retention_limit)
        except Exception:
            pass
        finally:
            db.close()
        time.sleep(settings.snapshot_interval_seconds)


@app.on_event("startup")
def start_snapshot_worker() -> None:
    thread = threading.Thread(target=snapshot_worker, daemon=True)
    thread.start()
