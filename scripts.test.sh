#!/usr/bin/env bash
set -euo pipefail
TEST_ENV_FILE=.env.test
cp .env.example "$TEST_ENV_FILE"
trap 'rm -f "$TEST_ENV_FILE"; docker compose --env-file "$TEST_ENV_FILE" down --remove-orphans >/dev/null 2>&1 || true' EXIT

docker compose --env-file "$TEST_ENV_FILE" down --remove-orphans >/dev/null 2>&1 || true
docker compose --env-file "$TEST_ENV_FILE" up -d --build
sleep 10
curl -fsS http://127.0.0.1:7000/health >/dev/null
curl -fsS -X POST -H 'X-Monitor-Token: change-me-token' http://127.0.0.1:7000/api/system/snapshot >/dev/null
curl -fsS -H 'X-Monitor-Token: change-me-token' 'http://127.0.0.1:7000/api/system/history?limit=3' >/dev/null
curl -fsS -H 'X-Monitor-Token: change-me-token' 'http://127.0.0.1:7000/api/system/trends?limit=3' >/dev/null
