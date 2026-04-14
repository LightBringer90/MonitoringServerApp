from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "server-monitor-api")
    port: int = int(os.getenv("PORT", "7000"))
    monitor_username: str = os.getenv("MONITOR_USERNAME", "LightB")
    monitor_password: str = os.getenv("MONITOR_PASSWORD", "changeme")
    monitor_token: str = os.getenv("MONITOR_TOKEN", "change-me-token")


settings = Settings()
