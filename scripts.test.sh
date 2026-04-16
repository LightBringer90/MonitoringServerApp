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
    'ALERT_EMAIL_ENABLED': 'true',
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
ALERT_STATUS_JSON=$(curl -fsS -H 'X-Monitor-Token: monitor-test-token-01' http://127.0.0.1:7000/api/system/alerts/status)
ALERT_STATUS_JSON="$ALERT_STATUS_JSON" python3 - <<'PY'
import json
import os
payload = json.loads(os.environ['ALERT_STATUS_JSON'])
if payload.get('status') not in {'ok', 'warning'}:
    raise SystemExit('unexpected alert status payload')
if 'alert_email_enabled' not in payload:
    raise SystemExit('missing alert status field')
print('alert status smoke ok')
PY
curl -fsS -X POST -H 'X-Monitor-Token: monitor-test-token-01' http://127.0.0.1:7000/api/system/alerts/test >/dev/null
sleep 2
MAILPIT_MESSAGES_JSON=$(curl -fsS http://127.0.0.1:8025/api/v1/messages)
MAILPIT_MESSAGES_JSON="$MAILPIT_MESSAGES_JSON" python3 - <<'PY'
import json
import os
payload = json.loads(os.environ['MAILPIT_MESSAGES_JSON'])
messages = payload.get('messages', [])
if not any('Monitor failure report' in (message.get('Subject') or '') for message in messages):
    raise SystemExit('expected test alert email in Mailpit inbox')
print('mailpit alert smoke ok')
PY
