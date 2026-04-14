# Project Postmortem: server-monitor-api

Project: server-monitor-api
Date: 2026-04-14
Phase reached: first real project through factory

## What worked
- Docker-native bootstrap and project creation worked
- modular FastAPI structure was established cleanly
- auth, health, and system metrics endpoints worked
- project ran successfully through Docker Compose
- this project proved the factory can produce a real backend service

## What failed or was weaker than expected
- disk monitoring logic did not behave as expected in container context
- earlier generated samples exposed timing and template polish gaps
- some Makefile/health assumptions needed correction once port allocation became real

## Which agent roles were exercised
- Senior API Architect
- Senior Backend Implementer
- Senior DevOps and Deployment Engineer
- Senior Documentation and Developer Experience Agent
- partial Senior QA and Test Engineer
- light Senior Security Reviewer

## Which agent roles should have done better
- Senior QA and Test Engineer should push harder on container-context behavior, not just happy-path startup
- Senior DevOps and Deployment Engineer should detect host-vs-container metric visibility issues earlier
- Senior API Architect should explicitly call out container observability constraints up front for host-monitoring tools

## Template or factory issues found
- Go template originally missed go.sum
- health checks initially assumed container default ports instead of allocated host ports
- older generated samples became stale relative to newer template standards

## Operational issues found
- Docker was a hard prerequisite for the factory and had to be installed later
- Telegram exec approvals required real configuration work before elevated commands flowed smoothly
- reboot exposed that the old host-side monitor was not properly persisted until systemd was fixed

## Documentation issues found
- early team-model docs were too layered and had to be consolidated to the single 11-agent model
- operator expectations needed to be clarified more explicitly in runbooks and standards

## What should be changed in the factory
- strengthen project postmortem and learning capture as standard behavior
- keep validating templates through real generated projects
- improve container-aware monitoring patterns for host-observability tools

## What should be changed in the team model
- elite agents should be measured by the quality of their judgment under real conditions, not just by role naming
- real projects should feed continuous upgrades to playbooks, gates, and templates
