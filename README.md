# RecallGuard

[![CI](https://github.com/recallguard/recallguard/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/recallguard/recallguard/actions/workflows/ci-cd.yml)





RecallGuard tracks U.S. product recalls and notifies subscribed users by e-mail and Slack. A lightweight React dashboard lets users manage alert subscriptions.


## 🚀 Quick-start


RecallGuard monitors product recalls and alerts users across web and mobile
interfaces. This repository now includes a small sample backend with tests and
a front‑end skeleton using React. Mobile apps can be built using React Native
on top of the same API endpoints.



RecallGuard monitors product recalls and alerts users. This repository
contains a minimal prototype skeleton.



## Setup
Install dependencies with `pip install -r requirements.txt`.

Run tests with `pytest`. The suite uses an in-memory SQLite database so no
external service is required. In CI a Postgres service is started
automatically.

Sample recall data used for tests is located under `tests/data`.

### Running locally with Postgres
Start a database via Docker and run migrations:

```bash
docker compose up -d db
make db-up
```

To process alert notifications, also start Redis and a Celery worker:

```bash
docker compose up -d redis
celery -A backend.tasks worker
```

## Auth & running locally
Set a JWT secret and recreate the dev database:


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


## Local development via Docker
Run all services with:
```bash
docker compose up --build
```
The API will be available at http://localhost:5000 and the dashboard at http://localhost:3000.

## Notifications & Alerts
Set `SENDGRID_API_KEY`, `ALERTS_FROM_EMAIL`, and `SLACK_WEBHOOK_URL` in your environment to enable e-mails and Slack messages when new recalls match user subscriptions. Users can opt in to e-mail notifications from the dashboard.


## Deployment
The project ships with a GitHub Actions workflow that builds Docker images and deploys to Fly.io and Vercel whenever `main` passes all tests. Set the following repository secrets:
- `FLY_API_TOKEN`
- `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`
- `PG_URL`, `JWT_SECRET`, `SENDGRID_API_KEY`, `SLACK_WEBHOOK_URL`

## Additional Recall Sources

The ingest pipeline also fetches drug and device enforcement data from openFDA:

- `https://api.fda.gov/drug/enforcement.json?search=status:"Ongoing"&limit=100`
- `https://api.fda.gov/device/enforcement.json?search=status:"Ongoing"&limit=100`

Vehicle owners can look up recalls by VIN via the authenticated endpoint:

```
GET /api/recalls/vin/<vin>
```

Provide a 17 character alphanumeric VIN. The route returns any matching recalls
but does not automatically generate alerts.


## Scan & Check

Visit `/scan` in the frontend to open a barcode or QR scanner using your
camera. When a code is detected, the browser calls
`GET /api/check/<upc>` to verify if the product has an active recall. A
JSON response of `{ status: "safe" }` indicates no recall. If a recall is
found, the response includes the recall ID, product name, hazard and link
to more details.

## My Stuff Locker

Authenticated users can save products they own via the `/api/items` endpoints.

- `GET /api/items` – list saved items with recall status
- `POST /api/items` – add an item `{ upc, label?, profile? }`
- `DELETE /api/items/<id>` – remove an item

Visit `/mystuff` in the frontend to view and manage these items. Products are
grouped by profile (Me, My Kids, My Pets) and each entry shows whether the UPC
is currently recalled.



