up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

health:
	curl -fsS http://127.0.0.1:7000/health

system:
	curl -fsS -u $$MONITOR_USERNAME:$$MONITOR_PASSWORD http://127.0.0.1:7000/api/system/basic

summary-token:
	curl -fsS -H "X-Monitor-Token: $$MONITOR_TOKEN" http://127.0.0.1:7000/api/system/summary

system-token:
	curl -fsS -H "X-Monitor-Token: $$MONITOR_TOKEN" http://127.0.0.1:7000/api/system
