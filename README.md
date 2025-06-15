# RecallGuard

RecallGuard monitors product recalls and alerts users across web and mobile
interfaces. This repository now includes a small sample backend with tests and
a front‑end skeleton using React. Mobile apps can be built using React Native
on top of the same API endpoints.

## Setup
Install dependencies with `pip install -r requirements.txt`.
Initialize the SQLite database with `python -m backend.db`.
Install front-end deps with `npm install`.
Launch the Flask API with `flask run` and the React dashboard with `npm start` (port 3000).

Run tests with `pytest`.

Sample CPSC recall data is provided in `data/cpsc_sample.json` for local
development without external API access.

