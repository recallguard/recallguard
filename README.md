# RecallGuard

[![CI](https://github.com/recallguard/recallguard/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/recallguard/recallguard/actions/workflows/ci-cd.yml)

RecallGuard tracks U.S. product recalls and notifies subscribed users by e-mail and Slack. A lightweight React dashboard lets users manage alert subscriptions.

## 🚀 Quick-start
```bash
# clone and enter repo
cd recallguard
# start database and dependencies
docker compose up --build -d
# run migrations and seed demo data
make db-up
# run backend + frontend
uvicorn backend.api.app:app &
npm install && npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) for the dashboard.

## 🔧 Config
See [.env.example](./.env.example) for all environment variables. They include database credentials, SendGrid and Slack keys and deployment tokens.

## Operations
- Health check: `/healthz`
- Prometheus metrics: `/metrics`
- Docker compose spins up API, worker, Postgres and Redis

## Deployment
Pushing to `main` runs tests then deploys to Fly.io and Vercel via GitHub Actions.
