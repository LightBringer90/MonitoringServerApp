# server-monitor-api

A modular FastAPI-based server monitoring backend built inside the backend factory.

## Features
- `/`
- `/health`
- `/health/ready`
- `/api/system` protected with token auth
- `/api/system/summary` protected with token auth
- `/api/system/basic` protected with HTTP Basic auth
- CPU, memory, disk, network, and process summary metrics
- explicit metadata about monitoring scope in container runtime

## Run

```bash
cp .env.example .env
docker compose up -d --build
```

## Dashboard-facing endpoints

- `GET /health`
- `GET /health/ready`
- `GET /api/system/summary`
- `GET /api/system`

Recommended auth for dashboards:
- `X-Monitor-Token: <token>`

Legacy/basic-auth endpoint:
- `GET /api/system/basic`

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
