# Deployment Guide

## What is hardened now
- Streamlit app upgraded for exploration, forecasting, benchmarking, and review capture
- XGBoost model artifacts saved under `models/`
- Review storage abstraction added through `DATABASE_URL`
- Local SQLite fallback for development, managed PostgreSQL for production
- Dockerfile uses a non-root user and includes a healthcheck
- `.env.example` and `.streamlit/config.toml` included for configuration
- `docker-compose.staging.yml` included for local staging tests

## Recommended production path

### Option 1: Streamlit Community Cloud + managed PostgreSQL
Best for the fastest public beta.

Steps:
1. Push the repository to GitHub.
2. Set the main file to `dashboard/app.py`.
3. Add dependencies from `requirements.txt`.
4. In Streamlit secrets or app environment settings, add `DATABASE_URL` pointing to managed Postgres.
5. Optionally add `APP_ENV=production` and `APP_BASE_URL`.
6. Run `python scripts/init_review_store.py` once if needed, or let the app auto-create tables.

### Option 2: Docker deployment on Render / Railway / VM / Kubernetes
Best for stronger operational control.

Steps:
1. Build the image locally: `docker build -t storage-forecaster .`
2. Run the container locally: `docker run -p 8501:8501 --env-file .env storage-forecaster`
3. Point `DATABASE_URL` at managed PostgreSQL.
4. Add HTTPS, monitoring, uptime checks, and platform secrets.
5. Roll out with health checks and persistent model artifacts.

## Managed review storage
The app now supports:
- `sqlite:///...` for local development
- `postgresql+psycopg://...` for production-grade managed PostgreSQL

Good managed PostgreSQL choices include Neon, Supabase Postgres, Render Postgres, Railway Postgres, and Cloud SQL.

## Production checklist
- managed Postgres configured
- secrets stored outside code
- app health endpoint monitored
- reviews and prediction logs persisted
- model artifacts versioned
- forecast upload validation enabled
- Docker image built from non-root user
- nightly export or backup of review data

## Suggested next operational upgrades
- add database migrations with Alembic
- add authentication for admin-only review analytics
- add Sentry / OpenTelemetry
- add CI pipeline for tests and startup checks
- add scheduled retraining and model promotion flow
