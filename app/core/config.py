"""Application configuration for server-monitor-api.

This module centralizes environment-driven settings and validates critical
security/runtime expectations early so misconfiguration fails fast.
"""

import os
from typing import Iterable

from pydantic import BaseModel, Field, field_validator


PLACEHOLDER_SECRET_VALUES = {
    "change-me-token",
    "changeme",
    "change-me",
    "example-token",
}


class Settings(BaseModel):
    """Validated runtime settings for the monitoring API."""

    app_name: str = Field(default=os.getenv("APP_NAME", "server-monitor-api"))
    port: int = Field(default=int(os.getenv("PORT", "7000")))
    monitor_username: str = Field(default=os.getenv("MONITOR_USERNAME", "LightB"))
    monitor_password: str = Field(default=os.getenv("MONITOR_PASSWORD", "changeme"))
    monitor_token: str = Field(default=os.getenv("MONITOR_TOKEN", "change-me-token"))
    database_url: str = Field(default=os.getenv("DATABASE_URL", "sqlite:///./data/monitor.db"))
    history_limit_default: int = Field(default=int(os.getenv("HISTORY_LIMIT_DEFAULT", "50")))
    snapshot_interval_seconds: int = Field(default=int(os.getenv("SNAPSHOT_INTERVAL_SECONDS", "60")))
    snapshot_retention_limit: int = Field(default=int(os.getenv("SNAPSHOT_RETENTION_LIMIT", "500")))
    telemetry_stale_after_seconds: int = Field(default=int(os.getenv("TELEMETRY_STALE_AFTER_SECONDS", "180")))
    alert_email_enabled: bool = Field(default=os.getenv("ALERT_EMAIL_ENABLED", "false").lower() == "true")
    smtp_host: str = Field(default=os.getenv("SMTP_HOST", "mailpit"))
    smtp_port: int = Field(default=int(os.getenv("SMTP_PORT", "1025")))
    alert_email_from: str = Field(default=os.getenv("ALERT_EMAIL_FROM", "monitor@local.test"))
    alert_email_to: str = Field(default=os.getenv("ALERT_EMAIL_TO", "alerts@local.test"))
    cpu_alert_threshold: float = Field(default=float(os.getenv("CPU_ALERT_THRESHOLD", "95")))
    memory_alert_threshold: float = Field(default=float(os.getenv("MEMORY_ALERT_THRESHOLD", "95")))

    @field_validator("port")
    @classmethod
    def validate_port(cls, value: int) -> int:
        if value <= 0 or value > 65535:
            raise ValueError("PORT must be between 1 and 65535")
        return value

    @field_validator("history_limit_default")
    @classmethod
    def validate_history_limit_default(cls, value: int) -> int:
        if value <= 0 or value > 500:
            raise ValueError("HISTORY_LIMIT_DEFAULT must be between 1 and 500")
        return value

    @field_validator("snapshot_interval_seconds")
    @classmethod
    def validate_snapshot_interval_seconds(cls, value: int) -> int:
        if value < 10 or value > 3600:
            raise ValueError("SNAPSHOT_INTERVAL_SECONDS must be between 10 and 3600")
        return value

    @field_validator("snapshot_retention_limit")
    @classmethod
    def validate_snapshot_retention_limit(cls, value: int) -> int:
        if value < 10 or value > 10000:
            raise ValueError("SNAPSHOT_RETENTION_LIMIT must be between 10 and 10000")
        return value

    @field_validator("telemetry_stale_after_seconds")
    @classmethod
    def validate_telemetry_stale_after_seconds(cls, value: int) -> int:
        if value < 30 or value > 86400:
            raise ValueError("TELEMETRY_STALE_AFTER_SECONDS must be between 30 and 86400")
        return value

    @field_validator("smtp_port")
    @classmethod
    def validate_smtp_port(cls, value: int) -> int:
        if value <= 0 or value > 65535:
            raise ValueError("SMTP_PORT must be between 1 and 65535")
        return value

    @field_validator("cpu_alert_threshold", "memory_alert_threshold")
    @classmethod
    def validate_threshold_percentages(cls, value: float) -> float:
        if value <= 0 or value > 100:
            raise ValueError("Alert thresholds must be between 0 and 100")
        return value

    @field_validator("monitor_username", "monitor_password", "monitor_token", "database_url", "smtp_host", "alert_email_from", "alert_email_to")
    @classmethod
    def validate_non_empty_secret_fields(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Authentication and persistence settings must not be empty")
        return value

    def placeholder_secret_fields(self) -> list[str]:
        placeholders: list[str] = []
        for field_name in ("monitor_password", "monitor_token"):
            value = getattr(self, field_name, "")
            if value.strip().lower() in PLACEHOLDER_SECRET_VALUES:
                placeholders.append(field_name)
        return placeholders

    def readiness_issues(self) -> list[str]:
        issues: list[str] = []
        placeholder_fields = self.placeholder_secret_fields()
        if placeholder_fields:
            issues.append(
                "Placeholder secrets are still configured for: " + ", ".join(sorted(placeholder_fields))
            )
        if self.database_url.strip().lower() == "sqlite:///./data/monitor.db" and not os.path.isdir("./data"):
            issues.append("Expected local data directory ./data is missing for the default SQLite configuration")
        return issues


settings = Settings()
