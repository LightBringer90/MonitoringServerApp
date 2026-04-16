# server-monitor-api

A modular FastAPI-based server monitoring backend.

## Features
- `/`
- `/health`
- `/health/ready` (fails when critical config is still using placeholder secrets)
- `/api/system` protected with token auth
- `/api/system/summary` protected with token auth
- `/api/system/history` protected with token auth
- `/api/system/trends` protected with token auth
- `/api/system/snapshot` protected with token auth
- `/api/system/basic` protected with HTTP Basic auth
- `/api/system/alerts/status` protected with token auth
- CPU, memory, disk, network, and process summary metrics
- persisted telemetry history stored in SQLite inside Docker volume-backed app data
- trend-window endpoint with CPU, memory, and process aggregates for dashboard summaries
- optional Mailpit-backed failure and threshold email reporting
- explicit metadata about monitoring scope in container runtime

## Run

```bash
cp .env.example .env
docker compose up -d --build
```

Mailpit UI is available at:
- `http://127.0.0.1:8025`

SMTP is exposed at:
- `127.0.0.1:1025`

## Dashboard-facing endpoints

- `GET /health`
- `GET /health/ready`
- `GET /api/system/summary`
- `GET /api/system`
- `GET /api/system/history`
- `GET /api/system/trends`
- `POST /api/system/snapshot`
- `GET /api/system/alerts/status`
- `POST /api/system/alerts/test`

Recommended auth for dashboards:
- `X-Monitor-Token: <token>`

Legacy/basic-auth endpoint:
- `GET /api/system/basic`

## Readiness behavior

The readiness endpoint is stricter than liveness.
It returns `503` when critical runtime configuration is still unsafe, for example when placeholder secrets such as `change-me-token` are still in use.

## Email alerts

The service can send failure reports and threshold alerts through Mailpit or another SMTP server.
A compact token-protected alert status endpoint is available for dashboards and operators:
- `GET /api/system/alerts/status`

A token-protected test endpoint is also available for end-to-end verification:
- `POST /api/system/alerts/test`

Set these values in `.env`:
- `ALERT_EMAIL_ENABLED=true`
- `SMTP_HOST`
- `SMTP_PORT`
- `ALERT_EMAIL_FROM`
- `ALERT_EMAIL_TO`
- `CPU_ALERT_THRESHOLD`
- `MEMORY_ALERT_THRESHOLD`

## Test health

```bash
make health
```

## Read protected system metrics

```bash
MONITOR_TOKEN=change-me-token make system-token
MONITOR_TOKEN=change-me-token make summary-token
```

## Notes
This service currently reports container-visible runtime metrics. Host-wide observability requires additional runtime design, such as explicit host mounts or different deployment scope.
