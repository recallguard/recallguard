# RecallGuard




RecallGuard monitors product recalls and alerts users across web and mobile
interfaces. This repository now includes a small sample backend with tests and
a front‑end skeleton using React. Mobile apps can be built using React Native
on top of the same API endpoints.



RecallGuard monitors product recalls and alerts users. This repository
contains a minimal prototype skeleton.



## Setup
Install dependencies with `pip install -r requirements.txt`.

Run tests with `pytest`.


Sample CPSC recall data is provided in `data/cpsc_sample.json` for local
development without external API access.

## Running the dashboard
1. Install Python and Node dependencies:
   ```bash
   pip install -r requirements.txt
   npm install
   ```
2. Start the Flask API:
   ```bash
   python run.py
   ```
3. In another terminal, run the React/Next dashboard:
   ```bash
   npx next dev frontend
   ```



Sample CPSC recall data is provided in `data/cpsc_sample.json` for local
development without external API access.


