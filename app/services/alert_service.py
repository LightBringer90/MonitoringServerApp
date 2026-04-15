"""Email alert helpers for monitor failures and threshold breaches."""

from email.message import EmailMessage
import smtplib

from app.core.config import settings
from app.schemas.system import SystemStatsResponse


def alerts_enabled() -> bool:
    return settings.alert_email_enabled


def _send_email(subject: str, body: str) -> None:
    if not alerts_enabled():
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.alert_email_from
    message["To"] = settings.alert_email_to
    message.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
        smtp.send_message(message)


def send_failure_report(error_text: str) -> None:
    _send_email(
        subject="Monitor failure report",
        body=(
            "The server monitor snapshot worker encountered an error.\n\n"
            f"Error: {error_text}\n"
        ),
    )


def send_threshold_report(stats: SystemStatsResponse, reasons: list[str]) -> None:
    _send_email(
        subject="Monitor threshold alert",
        body=(
            "The server monitor detected threshold breaches.\n\n"
            f"Hostname: {stats.hostname}\n"
            f"Platform: {stats.platform}\n"
            f"CPU: {stats.cpu.percent:.1f}%\n"
            f"Memory: {stats.memory.percent:.1f}%\n"
            f"Reasons: {', '.join(reasons)}\n"
            f"Scope: {stats.meta.scope}\n"
        ),
    )


def threshold_reasons(stats: SystemStatsResponse) -> list[str]:
    reasons: list[str] = []
    if stats.cpu.percent >= settings.cpu_alert_threshold:
        reasons.append(f"cpu >= {settings.cpu_alert_threshold:.1f}%")
    if stats.memory.percent >= settings.memory_alert_threshold:
        reasons.append(f"memory >= {settings.memory_alert_threshold:.1f}%")
    return reasons
