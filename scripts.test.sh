#!/usr/bin/env bash
set -euo pipefail
TEST_ENV_FILE=.env.test
TEST_PROJECT_NAME=server-monitor-api-test
TEST_APP_PORT=17000
TEST_MAILPIT_UI_PORT=18025
TEST_MAILPIT_SMTP_PORT=11025
TEST_DATA_DIR=.test-data
cp .env.example "$TEST_ENV_FILE"
mkdir -p "$TEST_DATA_DIR"
python3 - <<'PY'
from pathlib import Path
path = Path('.env.test')
replacements = {
    'PORT': '7000',
    'MONITOR_PASSWORD': 'monitor-test-password-01',
    'MONITOR_TOKEN': 'monitor-test-token-01',
    'DATABASE_URL': 'sqlite:///./data/monitor-test.db',
    'ALERT_EMAIL_ENABLED': 'true',
    'SMTP_HOST': 'mailpit',
    'SMTP_PORT': '1025',
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
trap 'rm -f "$TEST_ENV_FILE"; docker compose -p "$TEST_PROJECT_NAME" --env-file "$TEST_ENV_FILE" down --remove-orphans >/dev/null 2>&1 || true' EXIT

docker compose -p "$TEST_PROJECT_NAME" --env-file "$TEST_ENV_FILE" down --remove-orphans >/dev/null 2>&1 || true
MONITOR_ENV_FILE="$TEST_ENV_FILE" \
MONITOR_APP_PORT="$TEST_APP_PORT" \
MONITOR_MAILPIT_UI_PORT="$TEST_MAILPIT_UI_PORT" \
MONITOR_MAILPIT_SMTP_PORT="$TEST_MAILPIT_SMTP_PORT" \
MONITOR_DATA_DIR="$TEST_DATA_DIR" \
docker compose -p "$TEST_PROJECT_NAME" --env-file "$TEST_ENV_FILE" up -d --build
for _ in $(seq 1 60); do
  if curl -fsS "http://127.0.0.1:${TEST_APP_PORT}/health" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
curl -fsS "http://127.0.0.1:${TEST_APP_PORT}/health" >/dev/null
curl -fsS "http://127.0.0.1:${TEST_APP_PORT}/health/ready" >/dev/null
curl -fsS -X POST -H 'X-Monitor-Token: monitor-test-token-01' "http://127.0.0.1:${TEST_APP_PORT}/api/system/snapshot" >/dev/null
curl -fsS "http://127.0.0.1:${TEST_APP_PORT}/health/ready" >/dev/null
curl -fsS -H 'X-Monitor-Token: monitor-test-token-01' "http://127.0.0.1:${TEST_APP_PORT}/api/system/history?limit=3" >/dev/null
curl -fsS -H 'X-Monitor-Token: monitor-test-token-01' "http://127.0.0.1:${TEST_APP_PORT}/api/system/trends?limit=3" >/dev/null
FRESHNESS_JSON=$(curl -fsS -H 'X-Monitor-Token: monitor-test-token-01' "http://127.0.0.1:${TEST_APP_PORT}/api/system/freshness")
FRESHNESS_JSON="$FRESHNESS_JSON" python3 - <<'PY'
import json
import os
payload = json.loads(os.environ['FRESHNESS_JSON'])
if payload.get('status') not in {'fresh', 'stale', 'missing'}:
    raise SystemExit('unexpected freshness payload')
if payload.get('status') != 'fresh':
    raise SystemExit('expected fresh telemetry after snapshot capture')
print('freshness smoke ok')
PY
ALERT_STATUS_JSON=$(curl -fsS -H 'X-Monitor-Token: monitor-test-token-01' "http://127.0.0.1:${TEST_APP_PORT}/api/system/alerts/status")
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
curl -fsS -X POST -H 'X-Monitor-Token: monitor-test-token-01' "http://127.0.0.1:${TEST_APP_PORT}/api/system/alerts/test" >/dev/null
sleep 2
MAILPIT_MESSAGES_JSON=$(curl -fsS "http://127.0.0.1:${TEST_MAILPIT_UI_PORT}/api/v1/messages")
MAILPIT_MESSAGES_JSON="$MAILPIT_MESSAGES_JSON" python3 - <<'PY'
import json
import os
payload = json.loads(os.environ['MAILPIT_MESSAGES_JSON'])
messages = payload.get('messages', [])
if not any('Monitor failure report' in (message.get('Subject') or '') for message in messages):
    raise SystemExit('expected test alert email in Mailpit inbox')
print('mailpit alert smoke ok')
PY
