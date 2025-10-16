# Agent World — Flask Starter (Production-ready scaffold)

This is a working, containerized Flask app with authentication, a marketplace, BizReady endpoints, and basic pages.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # fill in values
python run.py
```

App runs at http://localhost:5000

## Docker

```bash
docker build -t agent-world .
docker run -p 5000:5000 --env-file .env agent-world
```

## Deploy (Render/Heroku/Railway/Fly)
- Use the Dockerfile or Procfile as needed. Set env vars from `.env.example`.

## Notes
- SQLite is used by default. Swap `SQLALCHEMY_DATABASE_URI` to your Postgres/MySQL URL for production.
- Seeders run automatically on landing page to populate marketplace and seats.
