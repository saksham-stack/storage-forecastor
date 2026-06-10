# Docker & PostgreSQL Integration Guide

## Overview
Your project is already set up for Docker and PostgreSQL integration! Here's how to use them effectively.

---

## Part 1: Local Development with Docker Compose

### 1.1 Running with PostgreSQL locally
You have `docker-compose.staging.yml` already configured. To run everything locally:

```bash
# Build and start both Streamlit app and PostgreSQL
docker-compose -f docker-compose.staging.yml up --build

# The app will be at: http://localhost:8501
# PostgreSQL will be at: localhost:5432
```

### 1.2 Running without Docker (Local SQLite - Default)
For quick local development without Docker:

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app (uses SQLite by default)
streamlit run dashboard/app.py
```

**Default database**: `data/app_reviews.db` (SQLite, local file)

### 1.3 Using PostgreSQL locally (without Docker)
If you have PostgreSQL installed locally:

```bash
# Set the environment variable
$env:DATABASE_URL = "postgresql+psycopg://postgres:password@localhost:5432/storage_forecaster"

# Create the database first
psql -U postgres -c "CREATE DATABASE storage_forecaster;"

# Initialize the tables
python scripts/init_review_store.py

# Run the app
streamlit run dashboard/app.py
```

---

## Part 2: Understanding User Data & Review Storage

### 2.1 What User Data is Captured?

When users submit a review in the dashboard, the following data is captured:

**Review Fields** (from `src/review_store.py`):
```python
- name: User's name (string, max 120 chars)
- role: User's role/team (string, max 120 chars)
- rating: Rating 1-5 (integer)
- model_used: Which model they tested (string, max 60 chars)
- comment: Their feedback/review (text, max 4000 chars)
- user_hash: Anonymized user identifier (string, max 120 chars)
- created_at: Timestamp when review was submitted (auto-set)
```

**Example of captured data**:
```
name: "John Doe"
role: "Senior Engineer"
rating: 5
model_used: "XGBoost"
comment: "Excellent forecast accuracy on our test data"
user_hash: "a1b2c3d4e5f6g7h8i9j0" (derived from user_id)
created_at: 2026-06-10 14:30:00 UTC
```

### 2.2 Accessing Review Data

You can view and export review data in several ways:

#### Option 1: Via Streamlit Dashboard (Reviews & Deploy tab)
```
- Total reviews: shown at top
- Average rating: shown at top
- Recent reviews: displayed in a table
```

#### Option 2: Programmatically
```python
from src.review_store import load_reviews, review_summary

# Get all reviews
reviews = load_reviews(limit=200)
for review in reviews:
    print(f"{review['name']} ({review['rating']}/5): {review['comment']}")

# Get summary stats
summary = review_summary()
print(f"Total reviews: {summary['total_reviews']}")
print(f"Average rating: {summary['avg_rating']}")
print(f"Predictions logged: {summary['total_predictions_logged']}")
```

#### Option 3: Direct database query
```python
from src.review_store import get_engine
from sqlalchemy import select, text

engine = get_engine()
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM reviews ORDER BY created_at DESC LIMIT 10;"))
    for row in result:
        print(row)
```

#### Option 4: Export to CSV
```python
import pandas as pd
from src.review_store import load_reviews

reviews = load_reviews(limit=1000)
df = pd.DataFrame(reviews)
df.to_csv('reports/reviews_export.csv', index=False)
print("Reviews exported to reports/reviews_export.csv")
```

### 2.3 Forecast Event Logging

When users run a forecast prediction, the event is also logged:

**Logged Fields** (from `src/review_store.py`):
```python
- model_used: Which model made the prediction (string)
- source: Where the input came from - "sample_user" or "uploaded_csv" (string)
- user_hash: Anonymized user identifier (string)
- horizon_days: Forecast horizon (30, 60, or 90 days)
- predicted_used_gb: The predicted storage usage in GB
- predicted_used_pct: The predicted storage percentage
- created_at: Timestamp (auto-set)
```

**Access prediction logs**:
```python
from src.review_store import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    result = conn.execute(
        text("SELECT * FROM prediction_logs ORDER BY created_at DESC LIMIT 50;")
    )
    for row in result:
        print(f"Model: {row[2]}, Horizon: {row[5]} days, Prediction: {row[6]} GB")
```

---

## Part 3: Database Schema

### 3.1 Reviews Table
```sql
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    name VARCHAR(120) NOT NULL,
    role VARCHAR(120) NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    model_used VARCHAR(60) NOT NULL,
    comment TEXT NOT NULL,
    user_hash VARCHAR(120)
);
```

### 3.2 Prediction Logs Table
```sql
CREATE TABLE prediction_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_used VARCHAR(60) NOT NULL,
    source VARCHAR(40) NOT NULL,
    user_hash VARCHAR(120),
    horizon_days INTEGER NOT NULL,
    predicted_used_gb VARCHAR(32) NOT NULL,
    predicted_used_pct VARCHAR(32) NOT NULL
);
```

---

## Part 4: Production Deployment

### 4.1 Using Managed PostgreSQL (Recommended)

Choose one of these providers:

#### **Neon** (recommended - free tier available)
1. Sign up at https://neon.tech
2. Create a project and database
3. Copy connection string:
   ```
   postgresql+psycopg://user:password@[host].neon.tech:5432/neondb
   ```

#### **Supabase** (PostgreSQL + extras)
1. Sign up at https://supabase.com
2. Create a new project
3. Copy connection string from project settings
4. Add `?sslmode=require` to the URL

#### **Railway** (simple deployment)
1. Deploy your app directly from Git
2. Add PostgreSQL plugin
3. Railway auto-sets `DATABASE_URL`

#### **Render** (alternative)
1. Deploy from GitHub
2. Attach Postgres database
3. Environment variable auto-configured

### 4.2 Docker Production Deployment

#### Local testing:
```bash
# Build image
docker build -t storage-forecaster:latest .

# Create .env file
echo 'DATABASE_URL=postgresql+psycopg://app_user:app_password@postgres:5432/storage_forecaster' > .env
echo 'APP_ENV=production' >> .env

# Run with docker-compose
docker-compose -f docker-compose.staging.yml up
```

#### Push to registry:
```bash
# Tag image
docker tag storage-forecaster:latest yourusername/storage-forecaster:latest

# Push to Docker Hub
docker push yourusername/storage-forecaster:latest
```

#### Deploy to production:
```bash
# On production server
docker pull yourusername/storage-forecaster:latest

docker run -d \
  -p 8501:8501 \
  -e DATABASE_URL="postgresql+psycopg://..." \
  -e APP_ENV=production \
  -e APP_BASE_URL=https://your-domain.com \
  --restart unless-stopped \
  yourusername/storage-forecaster:latest
```

### 4.3 Environment Variables for Production

Create `.env` file (do NOT commit to Git):
```bash
# Application
APP_ENV=production
APP_BASE_URL=https://your-app-domain.com

# Database (use managed PostgreSQL in production)
DATABASE_URL=postgresql+psycopg://user:password@host:5432/dbname

# Optional: Observability
# SENTRY_DSN=your-sentry-dsn
# POSTHOG_API_KEY=your-posthog-key
```

---

## Part 5: Accessing User Data in Production

### 5.1 View Reviews Dashboard
Go to the **"Reviews & Deploy"** tab in the Streamlit app to see all reviews and statistics in real-time.

### 5.2 Export Reviews via Dashboard
Add this feature to your app (enhancement):
```python
# In dashboard/app.py, Reviews & Deploy tab section
if st.button('📥 Export all reviews to CSV'):
    reviews = load_reviews(limit=10000)
    if reviews:
        df = pd.DataFrame(reviews)
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download reviews.csv",
            data=csv,
            file_name=f"reviews_{pd.Timestamp.now().date()}.csv",
            mime="text/csv"
        )
```

### 5.3 Admin Query Scripts
Create `scripts/export_reviews.py`:
```python
import pandas as pd
from datetime import datetime
from src.review_store import load_reviews, review_summary

summary = review_summary()
print(f"Summary: {summary['total_reviews']} total reviews")

reviews = load_reviews(limit=10000)
df = pd.DataFrame(reviews)

# Group by model
model_stats = df.groupby('model_used').agg({
    'rating': ['count', 'mean'],
    'comment': 'count'
}).round(2)
print("\nReviews by model:")
print(model_stats)

# Export
filename = f"reviews_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
df.to_csv(f"reports/{filename}", index=False)
print(f"\nExported to reports/{filename}")
```

Then run:
```bash
python scripts/export_reviews.py
```

### 5.4 Advanced: Connect Power BI / Tableau
Use connection string to connect BI tools directly to your PostgreSQL:
```
Host: [your-postgres-host]
Database: storage_forecaster
User: [your-user]
Password: [your-password]
Port: 5432
```

---

## Part 6: Data Privacy & Anonymization

### 6.1 How user_hash Works
Users are anonymized using SHA256:
```python
import hashlib

def make_user_hash(seed: str) -> str:
    return hashlib.sha256(seed.encode('utf-8')).hexdigest()[:24]

# Example
user_hash = make_user_hash('john_doe@example.com')
# Output: 'a4e0f91f4c5e3b6d2a8c1e9d'  # consistent but anonymous
```

### 6.2 GDPR/Privacy Considerations
- `name` and `role` are optional
- `user_hash` allows you to track feedback without storing PII
- Reviews table stores creation timestamp for audit trails
- Use HTTPS in production to encrypt data in transit
- Enable SSL on your PostgreSQL connection

---

## Quick Start Checklist

- [ ] **Local dev**: `streamlit run dashboard/app.py` (uses SQLite)
- [ ] **Local + Docker**: `docker-compose -f docker-compose.staging.yml up`
- [ ] **Managed Postgres**: Create account at Neon/Supabase
- [ ] **Set DATABASE_URL**: `export DATABASE_URL=postgresql+psycopg://...`
- [ ] **Test connection**: `python scripts/init_review_store.py`
- [ ] **Submit test review**: Use dashboard app
- [ ] **Export reviews**: `python scripts/export_reviews.py`
- [ ] **Deploy to production**: Use Railway/Render/Docker registry

---

## Troubleshooting

### PostgreSQL Connection Error
```bash
# Check if PostgreSQL is running
psql -U postgres -c "SELECT 1;"

# If using docker-compose
docker-compose -f docker-compose.staging.yml ps
```

### Tables not created
```bash
# Manually initialize tables
python scripts/init_review_store.py
```

### Can't see reviews
```bash
# Check DATABASE_URL is set correctly
python -c "from src.settings import get_settings; print(get_settings().database_url)"
```

### Data not persisting
```bash
# If using Docker, check volumes
docker volume ls
docker volume inspect storage-forecastor_postgres_data
```

---

## Next Steps
1. Choose your database (SQLite for dev, PostgreSQL for prod)
2. Test locally with Docker Compose
3. Set up managed PostgreSQL
4. Deploy app with proper environment variables
5. Monitor reviews and prediction logs
6. Export data regularly for analysis
