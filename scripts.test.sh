#!/usr/bin/env bash
set -euo pipefail
cp .env.example .env

docker compose down --remove-orphans >/dev/null 2>&1 || true
docker compose up -d --build
sleep 10
curl -fsS http://127.0.0.1:7000/health >/dev/null
curl -fsS -X POST -H 'X-Monitor-Token: change-me-token' http://127.0.0.1:7000/api/system/snapshot >/dev/null
curl -fsS -H 'X-Monitor-Token: change-me-token' 'http://127.0.0.1:7000/api/system/history?limit=3' >/dev/null
docker compose down --remove-orphans
