# RecallGuard

> Unified recall intelligence and alert platform that protects consumers and businesses from unsafe products.

## Table of Contents

* [Overview](#overview)
* [Key Features](#key-features)
* [Architecture](#architecture)
* [Tech Stack](#tech-stack)
* [Quickstart](#quickstart)
* [Configuration](#configuration)
* [Development Workflow](#development-workflow)
* [Testing](#testing)
* [Deployment](#deployment)
* [Contributing](#contributing)
* [License](#license)
* [Acknowledgements](#acknowledgements)

## Overview

RecallGuard aggregates product‑safety recalls from multiple U.S. regulatory agencies (CPSC, FDA, USDA, NHTSA) and cross‑references them with the items your household or organisation owns. When a match is found, RecallGuard sends a concise, plain‑English alert so you can act before it’s too late.

> **Mission**: Make product‑safety intelligence effortless, actionable and accessible to everyone.

## Key Features

* **Multi‑agency data ingestion**: scheduled scrapers pull and normalise recall data from CPSC, FDA, USDA, NHTSA and vetted news feeds.
* **Product matching engine**: VIN decoding, barcode scanning, email parsing and computer‑vision recognition to map user items to official recall IDs.
* **Custom alerts & reports**: email/SMS/push notifications, weekly digest, CSV/PDF export for enterprise users.
* **AI‑powered insights**: GPT‑generated human‑readable summaries, risk scores and legal guidance snippets.
* **B2B toolkit**: role‑based dashboards, SLA monitoring, API access and webhooks for supply‑chain partners.
* **Privacy‑first**: end‑to‑end encryption of sensitive user data and compliance with GDPR/CCPA.

## Architecture

```
backend/       # FastAPI micro‑services, Celery workers, utils
frontend/      # React 18 + Vite SPA, Tailwind UI components
ai/            # Prompt templates, summariser & legal qualifier helpers
cli_tools/     # One‑off maintenance & data‑import scripts
docker‑compose # Local orchestration
```

A PostgreSQL database backs transactional data; Redis powers job queues and cache; Celery schedules scraping and alert tasks. Both backend and frontend are containerised for parity between dev and prod.

## Tech Stack

| Layer           | Tech                                      |
| --------------- | ----------------------------------------- |
| API             | **FastAPI**, Pydantic, Uvicorn            |
| Background jobs | **Celery** + Redis                        |
| Database        | **PostgreSQL** w/ SQLAlchemy ORM          |
| Front‑end       | **React 18**, Vite, Tailwind CSS          |
| AI              | OpenAI GPT‑4o, HuggingFace Transformers   |
| DevOps          | Docker, Docker Compose, GitHub Actions CI |

## Quickstart

```bash
# 1. Clone
$ git clone https://github.com/your-org/recallguard.git && cd recallguard

# 2. Configure
$ cp .env.example .env   # then edit secrets & API keys

# 3. Launch (all services)
$ docker compose up --build

# Frontend: http://localhost:5173
# Backend : http://localhost:8000/docs (Swagger)
```

## Configuration

Environment variables are loaded from `.env` in the project root. See `.env.example` for required keys:

| Key                     | Description                       |
| ----------------------- | --------------------------------- |
| `OPENAI_API_KEY`        | API key for GPT‑powered summaries |
| `POSTGRES_PASSWORD`     | PostgreSQL superuser password     |
| `REDIS_URL`             | Redis connection string           |
| `EMAIL_FROM` / `SMTP_*` | Outgoing mail credentials         |
| ...                     | ...                               |

## Development Workflow

```bash
# backend
$ poetry install
$ uvicorn backend.api.main:app --reload

# frontend
$ cd frontend && npm i && npm run dev

# tests
$ pytest -q
```

Pre‑commit hooks run **ruff**, **black** and **prettier** to keep code clean.

## Testing

`pytest` covers API routes, business logic and scrapers; Cypress covers critical frontend flows.

## Deployment

1. Push images to a registry (GHCR, ECR).
2. Provision a PostgreSQL & Redis service.
3. Use the provided `docker-compose.prod.yml` or Helm charts.
4. Configure a CDN + HTTPS (Cloudflare, AWS ALB).

## Contributing

1. Fork & create a feature branch.
2. Write clear, descriptive commits.
3. Ensure `pre-commit run --all-files` passes.
4. Submit a pull request; maintainers will review.

## License

This project is licensed under the **MIT License** – see `LICENSE` for details.

## Acknowledgements

* U.S. Consumer Product Safety Commission (CPSC)
* Food & Drug Administration (FDA)
* National Highway Traffic Safety Administration (NHTSA)
* U.S. Department of Agriculture (USDA)
* OpenAI & HuggingFace communities
