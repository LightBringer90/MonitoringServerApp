from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

from app.core.config import settings

security = HTTPBasic()


def require_auth(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    correct_user = secrets.compare_digest(credentials.username, settings.monitor_username)
    correct_pass = secrets.compare_digest(credentials.password, settings.monitor_password)
    if not (correct_user and correct_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def require_token(x_monitor_token: str | None = Header(default=None)) -> str:
    if not x_monitor_token or not secrets.compare_digest(x_monitor_token, settings.monitor_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing monitor token",
        )
    return x_monitor_token
