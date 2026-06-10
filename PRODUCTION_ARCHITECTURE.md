# Production Architecture

## Recommended architecture
1. **Streamlit web app** serves the UI and product workflows.
2. **Managed PostgreSQL** stores user reviews and forecast event logs.
3. **Saved XGBoost artifacts** are loaded at startup for low-latency inference.
4. **Object storage / Git repo** holds datasets, reports, and model versions.
5. **Observability** captures app health, database health, and usage metrics.
6. **Retraining workflow** periodically regenerates data, retrains models, and publishes new artifacts.

## Managed review storage
Use a managed Postgres provider such as Neon, Supabase, Render Postgres, Railway Postgres, or Cloud SQL.

The app reads `DATABASE_URL` and automatically switches from local SQLite to PostgreSQL when that variable is set.

## Deployment tiers
### Tier 1: Public beta
- Streamlit Community Cloud
- Managed Postgres for reviews
- Manual model refresh from Git pushes

### Tier 2: Production MVP
- Docker deployment on Render / Railway / VM / Kubernetes
- Managed Postgres
- Centralized secrets management
- Error monitoring + uptime checks
- Nightly export of reviews and prediction logs

### Tier 3: Scaled architecture
- Streamlit frontend or separate React frontend
- FastAPI inference service for model serving
- Background queue for async jobs
- Feature store / warehouse for telemetry and retraining

## Core hardening decisions already added
- Non-root Docker container
- Healthcheck endpoint in container
- Secret-driven DB configuration
- Structured review table and prediction log table
- Upload validation for forecast files
- Model artifact persistence in `models/`

## Recommended next hardening moves
- Add authentication for staff/admin paths
- Add database migrations with Alembic
- Add Sentry or OpenTelemetry
- Add CI checks for tests, linting, and app startup
- Add scheduled retraining and model registry metadata
