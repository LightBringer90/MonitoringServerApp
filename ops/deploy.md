# Deploy

- Target server: not-set
- Deployment mode: docker-compose
- Reverse proxy domain: not-set
- TLS: not-set
- Base port: 7000
- App port: 7000

## Firewall suggestions
- direct app access: ufw allow 7000/tcp
- reverse proxy only: ufw allow 80/tcp and ufw allow 443/tcp
