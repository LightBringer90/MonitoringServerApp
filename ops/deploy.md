# Deploy

## Runtime shape
- Service runs in Docker Compose
- API port: 7000
- Local persisted telemetry path: `./data/monitor.db`

## Pre-deploy checklist
- Review `.env` values
- Confirm monitor token is set to a non-placeholder value
- Confirm `data/` volume path is writable
- Build and start the stack
- Verify `/health`
- Verify `/health/ready`
- Confirm readiness does not report placeholder-secret issues
- Verify `POST /api/system/snapshot`
- Verify `GET /api/system/history`
- Verify `GET /api/system/trends`

## Rollback notes
- If the upgraded service fails, restore the prior image/build and preserve `./data/`
- Validate token-auth endpoints after rollback
- Validate dashboard compatibility after rollback

## Post-deploy verification
- Check `/health`
- Check `/health/ready`
- Capture a snapshot
- Verify history returns recent persisted data
- Verify trend summaries return recent aggregate data
- Verify dashboard on port 4280 can read summary/history/trends and capture snapshots
