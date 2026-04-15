#!/usr/bin/env bash
set -euo pipefail
TEST_ENV_FILE=.env.test
cp .env.example "$TEST_ENV_FILE"
mkdir -p data
python3 - <<'PY'
from pathlib import Path
path = Path('.env.test')
replacements = {
    'MONITOR_PASSWORD': 'monitor-test-password-01',
    'MONITOR_TOKEN': 'monitor-test-token-01',
}
lines = []
for line in path.read_text().splitlines():
    key, sep, value = line.partition('=')
    if key in replacements:
        lines.append(f'{key}={replacements[key]}')
    else:
        lines.append(line)
path.write_text('\n'.join(lines) + '\n')
PY
trap 'rm -f "$TEST_ENV_FILE"; docker compose --env-file "$TEST_ENV_FILE" down --remove-orphans >/dev/null 2>&1 || true' EXIT

MONITOR_ENV_FILE="$TEST_ENV_FILE" docker compose --env-file "$TEST_ENV_FILE" down --remove-orphans >/dev/null 2>&1 || true
MONITOR_ENV_FILE="$TEST_ENV_FILE" docker compose --env-file "$TEST_ENV_FILE" up -d --build
sleep 10
curl -fsS http://127.0.0.1:7000/health >/dev/null
curl -fsS http://127.0.0.1:7000/health/ready >/dev/null
curl -fsS -X POST -H 'X-Monitor-Token: monitor-test-token-01' http://127.0.0.1:7000/api/system/snapshot >/dev/null
curl -fsS -H 'X-Monitor-Token: monitor-test-token-01' 'http://127.0.0.1:7000/api/system/history?limit=3' >/dev/null
curl -fsS -H 'X-Monitor-Token: monitor-test-token-01' 'http://127.0.0.1:7000/api/system/trends?limit=3' >/dev/null
