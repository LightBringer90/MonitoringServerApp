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
- Verify `POST /api/system/snapshot`
- Verify `GET /api/system/history`

## Rollback notes
- If the upgraded service fails, restore the prior image/build and preserve `./data/`
- Validate token-auth endpoints after rollback
- Validate dashboard compatibility after rollback

## Post-deploy verification
- Check `/health`
- Capture a snapshot
- Verify history returns recent persisted data
- Verify dashboard on port 4280 can read summary/history and capture snapshots
