from fastapi import FastAPI

from app.api.routes.root import router as root_router
from app.api.routes.health import router as health_router
from app.api.routes.system import router as system_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(root_router)
app.include_router(health_router)
app.include_router(system_router)
