# Quick Reference Guide

## TL;DR - Get Started in 5 Minutes

### Development (SQLite - No Docker)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run dashboard/app.py

# 3. Open browser to http://localhost:8501
```

### Development (PostgreSQL + Docker)
```bash
# 1. Start Docker services
docker-compose -f docker-compose.staging.yml up

# 2. App will be at http://localhost:8501
# 3. PostgreSQL at localhost:5432
# 4. pgAdmin at http://localhost:5050
```

### Production (Managed PostgreSQL)
```bash
# 1. Get PostgreSQL URL from provider (Neon, Supabase, Railway, etc.)
# 2. Set environment variable
export DATABASE_URL="postgresql+psycopg://user:pass@host:5432/dbname"

# 3. Deploy (Docker or Streamlit Cloud)
docker run -e DATABASE_URL="..." -p 8501:8501 storage-forecaster
```

---

## Where to Find Things

| Need | Location | Command |
|------|----------|---------|
| View recent reviews | Streamlit app → Reviews & Deploy tab | N/A |
| Export reviews to CSV | Streamlit app → Reviews & Deploy → Export button | `python scripts/view_reviews.py --all` |
| Check database status | Terminal | `python scripts/init_db.py health` |
| Create database tables | Terminal | `python scripts/init_db.py setup` |
| View database schema | Terminal | `python scripts/init_db.py export-schema` |
| Analyze predictions | Terminal | `python scripts/view_reviews.py --predictions` |
| Manage database (UI) | http://localhost:5050 (when using docker-compose.prod.yml) | pgAdmin interface |

---

## Understanding User Data

### What gets captured when user submits review?

```python
{
    "name": "User's name",           # Optional, max 120 chars
    "role": "User's role/team",      # Optional, max 120 chars
    "rating": 5,                     # 1-5 scale
    "model_used": "XGBoost",         # Which model they tested
    "comment": "Their feedback...",  # The actual review text
    "user_hash": "a1b2c3d4...",     # Anonymized ID (SHA256)
    "created_at": "2026-06-10T14:30:00+00:00"  # When submitted
}
```

### What gets captured when user runs forecast?

```python
{
    "model_used": "XGBoost",         # Which model made prediction
    "source": "sample_user",         # "sample_user" or "uploaded_csv"
    "user_hash": "a1b2c3d4...",     # Anonymized user ID
    "horizon_days": 30,              # 30, 60, or 90 days
    "predicted_used_gb": 42.5,       # Storage usage prediction
    "predicted_used_pct": 78.2,      # Percentage of capacity
    "created_at": "2026-06-10T14:30:00+00:00"
}
```

---

## Database Options Explained

### SQLite (Development Default)
- **File**: `data/app_reviews.db`
- **Setup**: None required
- **Use when**: Local development only
- **Pros**: No dependencies, portable
- **Cons**: Single-user, not for production

### PostgreSQL Local (Docker)
- **Setup**: `docker-compose -f docker-compose.staging.yml up`
- **Connection**: `postgresql+psycopg://app_user:app_password@localhost:5432/storage_forecaster`
- **Use when**: Testing production-like setup locally
- **Pros**: Production-like, persistent data
- **Cons**: Requires Docker

### PostgreSQL Managed - Neon
- **Sign up**: https://neon.tech
- **Free tier**: Yes
- **Connection**: Copy from project dashboard
- **Use when**: Production, want zero maintenance
- **Pros**: Free tier, auto-scaling, serverless
- **Cons**: External dependency

### PostgreSQL Managed - Supabase
- **Sign up**: https://supabase.com
- **Free tier**: Yes (limited)
- **Connection**: Copy from project settings
- **Use when**: Production, need auth/extras
- **Pros**: PostgreSQL + auth + storage + realtime
- **Cons**: Overkill if just need reviews

### PostgreSQL Managed - Railway
- **Sign up**: https://railway.app
- **Free tier**: $5 credit
- **Connection**: Auto-set as `DATABASE_URL`
- **Use when**: Full app deployment
- **Pros**: One-click deploy, auto-scaling
- **Cons**: Paid after trial

---

## Common Tasks

### View reviews submitted by users
```bash
# Recent 20 reviews
python scripts/view_reviews.py

# All reviews (can be many)
python scripts/view_reviews.py --all

# Statistics
python scripts/view_reviews.py --stats

# Download via Streamlit
# Go to app → Reviews & Deploy → Download CSV button
```

### View prediction logs
```bash
# Export all predictions to CSV
python scripts/view_reviews.py --predictions
```

### Analyze review data in Pandas
```python
import pandas as pd
from src.review_store import load_reviews

reviews = load_reviews(limit=1000)
df = pd.DataFrame(reviews)

# Average rating by model
print(df.groupby('model_used')['rating'].mean())

# Review count by day
print(df.groupby(df['created_at'].dt.date).size())

# Save to CSV
df.to_csv('reviews_analysis.csv', index=False)
```

### Deploy to production
```bash
# Option 1: Docker to custom server
docker build -t storage-forecaster .
docker tag storage-forecaster:latest myregistry/storage-forecaster:latest
docker push myregistry/storage-forecaster:latest
# Then deploy to server with: docker run -e DATABASE_URL=... -p 8501:8501 myregistry/storage-forecaster

# Option 2: Streamlit Cloud
# Push to GitHub, connect at streamlit.io, set DATABASE_URL secret

# Option 3: Railway
# Connect GitHub repo, Railway auto-detects Streamlit, set DATABASE_URL
```

### Database backup & restore
```bash
# Backup (PostgreSQL)
pg_dump -U app_user -h localhost storage_forecaster > backup.sql

# Restore
psql -U app_user -h localhost storage_forecaster < backup.sql

# Backup all reviews to CSV
python scripts/view_reviews.py --all --output=reviews_backup.csv
```

### Check what database you're using
```python
from src.settings import get_settings
from src.review_store import backend_label, healthcheck

settings = get_settings()
print(f"Database URL: {settings.database_url}")
print(f"Backend: {backend_label()}")
health = healthcheck()
print(f"Status: {'✓ Connected' if health.get('ok') else '✗ Error'}")
```

---

## Troubleshooting

### "No such table: reviews"
```bash
# Initialize database tables
python scripts/init_db.py setup
```

### "Can't connect to database"
```bash
# Check database status
python scripts/init_db.py health

# Verify DATABASE_URL is set correctly
python -c "from src.settings import get_settings; print(get_settings().database_url)"

# For Docker Compose: check containers running
docker-compose -f docker-compose.staging.yml ps
```

### "ModuleNotFoundError" when running scripts
```bash
# Make sure you're in the right directory
cd /path/to/storage-forecaster

# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Install requirements again
pip install -r requirements.txt
```

### Reviews not appearing in Streamlit
```bash
# Clear Streamlit cache
streamlit cache clear

# Reload the app
# Then refresh browser
```

### Docker Compose fails to start
```bash
# Check if ports are already in use
# Port 8501 = Streamlit
# Port 5432 = PostgreSQL
# Port 5050 = pgAdmin

# Stop existing containers
docker-compose down

# Restart
docker-compose -f docker-compose.staging.yml up
```

---

## Architecture Overview

```
Your Application
    ↓
Streamlit Dashboard (dashboard/app.py)
    ↓
Review/Prediction Store (src/review_store.py)
    ↓
Database (Choose one):
  • SQLite (local dev)
  • PostgreSQL Local (docker-compose)
  • PostgreSQL Managed (Neon/Supabase/Railway/Render)
    ↓
Stored Data:
  • reviews table (user feedback)
  • prediction_logs table (forecast events)
```

---

## File Structure for Data Access

```
dashboard/
  └── app.py                 # Main UI - Reviews & Deploy tab
                            # Shows reviews, export button
scripts/
  ├── view_reviews.py       # CLI tool to view/export reviews
  ├── view_reviews.py       # Access prediction logs
  ├── init_db.py            # Database management
  └── setup_wizard.py       # Initial setup
src/
  ├── review_store.py       # Database layer
  │   ├── save_review()     # Save user review
  │   ├── load_reviews()    # Get reviews from DB
  │   ├── log_predictions() # Save forecast events
  │   └── review_summary()  # Stats
  └── settings.py           # Config (DATABASE_URL)
```

---

## Environment Variables

Set in `.env` or shell:

```bash
# Which database to use
DATABASE_URL=sqlite:///data/app_reviews.db
# OR
DATABASE_URL=postgresql+psycopg://user:pass@host/dbname

# App configuration
APP_ENV=development          # development, staging, production
APP_BASE_URL=http://localhost:8501

# Docker Compose (only needed if using docker-compose)
POSTGRES_USER=app_user
POSTGRES_PASSWORD=app_password
POSTGRES_DB=storage_forecaster
```

---

## Key Concepts

### User Hash
- **What**: Anonymized identifier for users
- **Why**: Privacy - don't store raw email/username
- **How**: SHA256 hash of seed value
- **Access**: Shows in reviews as "user_hash" field

### Reviews Table
- Stores user feedback on model performance
- Manual submissions via dashboard form
- Query with: `python scripts/view_reviews.py`

### Prediction Logs Table
- Auto-logged when users run forecasts
- Tracks which model, input source, predicted values
- Helps understand product usage patterns

### Backend Label
- "SQLite (local fallback)" = using local file
- "PostgreSQL (managed)" = using remote database
- Check with: `python scripts/init_db.py health`

---

## Support Resources

| Topic | Location |
|-------|----------|
| Project overview | `README.md` |
| Docker & PostgreSQL integration | `DOCKER_POSTGRES_GUIDE.md` (just created!) |
| Deployment options | `DEPLOYMENT.md` |
| Architecture decisions | `PRODUCTION_ARCHITECTURE.md` |
| Data access code | `src/review_store.py` |
| Database queries | Use `scripts/view_reviews.py` or `scripts/init_db.py` |

---

## Next Steps

1. **Test locally**: `streamlit run dashboard/app.py`
2. **Submit review**: Go to Reviews & Deploy tab
3. **Export data**: `python scripts/view_reviews.py --all`
4. **Choose database**: SQLite (dev) or PostgreSQL (prod)
5. **Deploy**: Follow steps in `DEPLOYMENT.md`
