# RecallGuard

[![CI](https://github.com/recallguard/recallguard/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/recallguard/recallguard/actions/workflows/ci-cd.yml)




RecallGuard monitors product recalls and alerts users across web and mobile
interfaces. This repository now includes a small sample backend with tests and
a front‑end skeleton using React. Mobile apps can be built using React Native
on top of the same API endpoints.



RecallGuard monitors product recalls and alerts users. This repository
contains a minimal prototype skeleton.



## Setup
Install dependencies with `pip install -r requirements.txt`.

Run tests with `pytest`.

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
export JWT_SECRET=change-me
python -m backend.db      # creates dev.db with demo user
python run.py             # start API + scheduler
```

Login via:

```bash
curl -X POST -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"password"}' \
  localhost:5000/api/auth/login
```

## Running the scheduler
```bash
export SQLALCHEMY_DATABASE_URL=sqlite:///dev.db
python -m backend.db      # (re)create + seed
python run.py             # starts API + scheduler
```

Trigger a manual refresh:

```bash
curl -X POST -H "X-Admin: true" localhost:5000/api/recalls/refresh
```

## Running the dashboard
1. Install Python and Node dependencies (Chakra UI will be installed via npm):
   ```bash
   pip install -r requirements.txt
   npm install
   ```
2. Start the Flask API and scheduler:
   ```bash
   python run.py
   ```
3. In another terminal, run the React/Next dashboard:
   ```bash
   npm run dev
   ```

   Dark mode is available using the toggle in the navbar. The responsive card
   grid is built with Chakra UI and styled with Tailwind accents.


## Auth & running locally
Set a JWT secret and recreate the dev database:

```bash
export JWT_SECRET=change-me
python -m backend.db      # creates dev.db with demo user
python run.py             # start API + scheduler
```

Login via:

```bash
curl -X POST -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"password"}' \
  localhost:5000/api/auth/login
```

## Running the scheduler
```bash
export SQLALCHEMY_DATABASE_URL=sqlite:///dev.db
python -m backend.db      # (re)create + seed
python run.py             # starts API + scheduler
```

Trigger a manual refresh:

```bash
curl -X POST -H "X-Admin: true" localhost:5000/api/recalls/refresh
```



## Running the dashboard
1. Install Python and Node dependencies:
   ```bash
   pip install -r requirements.txt
   npm install
   ```
e
2. Start the Flask API and scheduler:

2. Start the Flask API:

   ```bash
   python run.py
   ```
3. In another terminal, run the React/Next dashboard:
   ```bash

   npm run dev
=======
   npx next dev frontend

   ```



Sample recall data used for tests is located under `tests/data`.



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

