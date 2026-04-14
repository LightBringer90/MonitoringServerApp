#!/usr/bin/env bash
set -euo pipefail
cp .env.example .env

docker build -t server-monitor-api-test .
