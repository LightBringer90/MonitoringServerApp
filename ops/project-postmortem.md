# Project Postmortem: server-monitor-api

Project: server-monitor-api
Date: 2026-04-14
Phase reached: functional backend monitoring service with persisted telemetry

## What worked
- modular FastAPI structure was established cleanly
- auth, health, and system metrics endpoints worked
- persisted telemetry and history endpoints improved usefulness
- project ran successfully through Docker Compose
- dashboard-consumer endpoints supported the monitoring UI integration well

## What failed or was weaker than expected
- disk monitoring logic needed refinement in container context
- observability scope was initially too easy to misread as host-wide
- smoke testing started lighter than it should have
- richer trend and analytics capability is still limited

## Operational issues found
- container-visible metrics are not the same as host-wide observability
- runtime configuration had to be tightened as the service became richer
- persistence and retention behavior needed explicit operational handling

## Documentation issues found
- observability scope needed clearer explanation
- deploy notes had to catch up with the richer persisted-monitoring shape
- endpoint/auth behavior needed clearer operator-facing explanation

## Next improvements for this project
- add deeper automated tests beyond smoke-path checks
- improve trend and aggregation capabilities
- consider a stronger migration story if persistence complexity grows
- continue improving operational clarity around scope and runtime assumptions
