# Accessing User Data - Complete Reference

## Overview

Your application captures two types of user data:

1. **Reviews** - User feedback and ratings on model performance
2. **Predictions** - Log of forecasts made by users for analysis

This guide explains how to access both types of data.

---

## Method 1: Via Streamlit Dashboard (Easiest)

### View Recent Reviews
1. Run app: `streamlit run dashboard/app.py`
2. Navigate to **"Reviews & Deploy"** tab
3. You'll see:
   - Total reviews counter
   - Average rating
   - Recent reviews table
   - Export button

### Export Reviews as CSV
1. Go to **"Reviews & Deploy"** tab
2. Click **"📥 Export reviews to CSV"** button
3. Browser will download `reviews_YYYY-MM-DD.csv`

### View Database Status
In the same tab, sidebar shows:
- Review backend type (SQLite vs PostgreSQL)
- Total reviews count
- Average rating
- XGBoost models status

---

## Method 2: Via Command Line Scripts

### View Recent Reviews
```bash
# Show last 20 reviews
python scripts/view_reviews.py

# Show last 50 reviews
python scripts/view_reviews.py --limit 50
```

Output:
```
====================================================================================================
RECENT REVIEWS (Last 20)
====================================================================================================

             created_at             name           role  rating  model_used                                              comment
 2026-06-10 14:35:22.123456+00:00   John Doe   Engineer        5     XGBoost  Excellent forecast accuracy. Would use in production.
 2026-06-10 14:20:11.987654+00:00   Jane Smith  Manager        4  Prophet  Good for medium-term forecasts. Easy to interpret.
```

### Export All Reviews to CSV
```bash
# Export all reviews (up to 50,000)
python scripts/view_reviews.py --all

# Export to specific file
python scripts/view_reviews.py --all --output my_reviews.csv
```

Output: File saved to `reports/reviews_export_20260610_143522.csv`

### View Statistics
```bash
python scripts/view_reviews.py --stats
```

Output:
```
====================================================================================================
REVIEW STATISTICS
====================================================================================================

Total Reviews:          42
Average Rating:         4.52
Total Predictions:      156

Breakdown by Model:
                 Count  Avg Rating  Total
model_used                               
Baseline V2         14        3.86     14
Prophet             13        4.69     13
XGBoost             15        4.80     15
```

### Export Prediction Logs
```bash
# Export all prediction logs (forecasts made by users)
python scripts/view_reviews.py --predictions

# Export to specific file
python scripts/view_reviews.py --predictions --output predictions.csv
```

---

## Method 3: Via Python (Programmatic)

### Load and Display Reviews
```python
from src.review_store import load_reviews

# Get last 100 reviews
reviews = load_reviews(limit=100)

# Print them
for review in reviews:
    print(f"{review['name']} ({review['rating']}/5)")
    print(f"  Model: {review['model_used']}")
    print(f"  Comment: {review['comment']}")
    print(f"  Submitted: {review['created_at']}")
    print()
```

### Get Summary Statistics
```python
from src.review_store import review_summary

summary = review_summary()

print(f"Total reviews: {summary['total_reviews']}")
print(f"Average rating: {summary['avg_rating']:.2f}")
print(f"Predictions logged: {summary['total_predictions_logged']}")
```

### DataFrame Analysis (Pandas)
```python
import pandas as pd
from src.review_store import load_reviews

reviews = load_reviews(limit=10000)
df = pd.DataFrame(reviews)

# Average rating by model
print(df.groupby('model_used')['rating'].mean())

# Reviews by date
print(df.groupby(df['created_at'].dt.date).size())

# Ratings distribution
print(df['rating'].value_counts().sort_index())

# Export to CSV
df.to_csv('reviews.csv', index=False)
```

### Query Prediction Logs
```python
from src.review_store import get_engine
from sqlalchemy import text
import pandas as pd

engine = get_engine()

# Get all predictions
query = """
SELECT created_at, model_used, source, horizon_days, 
       predicted_used_gb, predicted_used_pct
FROM prediction_logs
ORDER BY created_at DESC
"""

df = pd.read_sql(text(query), engine)

# Analysis
print(f"Total predictions: {len(df)}")
print(f"Models used: {df['model_used'].unique()}")
print(f"Average prediction: {df['predicted_used_gb'].astype(float).mean():.2f} GB")

# Export
df.to_csv('predictions.csv', index=False)
```

---

## Method 4: Direct Database Queries

### Connect to Database

#### SQLite (Local)
```python
from src.review_store import get_engine

engine = get_engine()  # Automatically connects to data/app_reviews.db

with engine.connect() as conn:
    # Run queries
    pass
```

#### PostgreSQL (Local or Remote)
```python
import os
from sqlalchemy import create_engine

# Set DATABASE_URL environment variable first
db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url)

with engine.connect() as conn:
    # Run queries
    pass
```

### Query Examples

#### Get all reviews
```python
from src.review_store import get_engine, reviews_table
from sqlalchemy import select

engine = get_engine()

stmt = select(reviews_table).order_by(reviews_table.c.created_at.desc())

with engine.connect() as conn:
    results = conn.execute(stmt).mappings().all()
    for row in results:
        print(row)
```

#### Get reviews by model
```python
from sqlalchemy import select, text

engine = get_engine()

with engine.connect() as conn:
    result = conn.execute(
        text("""
        SELECT model_used, COUNT(*) as count, AVG(rating) as avg_rating
        FROM reviews
        GROUP BY model_used
        ORDER BY count DESC
        """)
    )
    
    for row in result:
        print(f"{row[0]}: {row[1]} reviews, avg rating {row[2]:.2f}")
```

#### Get high-rated reviews (4+ stars)
```python
from sqlalchemy import select, text

engine = get_engine()

with engine.connect() as conn:
    result = conn.execute(
        text("""
        SELECT name, rating, model_used, comment, created_at
        FROM reviews
        WHERE rating >= 4
        ORDER BY rating DESC, created_at DESC
        LIMIT 20
        """)
    )
    
    for row in result:
        print(f"⭐ {row[2]} - {row[0]}: {row[3]}")
```

#### Get prediction statistics by model
```python
engine = get_engine()

with engine.connect() as conn:
    result = conn.execute(
        text("""
        SELECT 
            model_used,
            COUNT(*) as total_predictions,
            AVG(CAST(predicted_used_gb AS FLOAT)) as avg_predicted_gb,
            AVG(CAST(predicted_used_pct AS FLOAT)) as avg_predicted_pct
        FROM prediction_logs
        GROUP BY model_used
        """)
    )
    
    for row in result:
        print(f"{row[0]}: {row[1]} predictions, avg {row[2]:.2f}GB ({row[3]:.1f}%)")
```

---

## Database Schema

### Reviews Table
```sql
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    name VARCHAR(120),
    role VARCHAR(120),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    model_used VARCHAR(60),
    comment TEXT,
    user_hash VARCHAR(120)
);
```

**Columns**:
- `id`: Unique identifier
- `created_at`: When review was submitted
- `name`: User's name (optional)
- `role`: User's role/team (optional)
- `rating`: 1-5 star rating
- `model_used`: Which model tested ("XGBoost", "Prophet", "Baseline V2")
- `comment`: Review text (max 4000 chars)
- `user_hash`: Anonymized user ID (SHA256 hash)

### Prediction Logs Table
```sql
CREATE TABLE prediction_logs (
    id INTEGER PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_used VARCHAR(60),
    source VARCHAR(40),
    user_hash VARCHAR(120),
    horizon_days INTEGER,
    predicted_used_gb VARCHAR(32),
    predicted_used_pct VARCHAR(32)
);
```

**Columns**:
- `id`: Unique identifier
- `created_at`: When prediction was made
- `model_used`: Model name ("XGBoost", etc.)
- `source`: "sample_user" or "uploaded_csv"
- `user_hash`: Anonymized user ID
- `horizon_days`: Forecast horizon (30, 60, 90)
- `predicted_used_gb`: Predicted storage in GB
- `predicted_used_pct`: Predicted storage percentage

---

## Data Privacy & Anonymization

### User Hash
Your app anonymizes users to protect privacy:

```python
import hashlib

def make_user_hash(seed: str) -> str:
    """Create a consistent, one-way hash for anonymization."""
    return hashlib.sha256(seed.encode('utf-8')).hexdigest()[:24]

# Example
user_hash = make_user_hash('john.doe@company.com')
# Output: 'a4e0f91f4c5e3b6d2a8c1e9d'
# Same input always produces same hash
# Can't reverse-engineer to get original email
```

### What's Stored
- `name` and `role` are **optional** - users can submit anonymously
- `user_hash` is **always included** - allows tracking patterns without PII
- All timestamps are in UTC

### GDPR Considerations
- No passwords or sensitive data stored
- All user identification is anonymized via hash
- Data stored encrypted (if using managed PostgreSQL with SSL)
- Can export all reviews for GDPR data requests
- Can delete all records by table reset

---

## Exporting Data

### Export Reviews as CSV
```python
import pandas as pd
from src.review_store import load_reviews

reviews = load_reviews(limit=10000)
df = pd.DataFrame(reviews)
df.to_csv('all_reviews.csv', index=False)
print(f"Exported {len(df)} reviews")
```

### Export Predictions as JSON
```python
import json
from src.review_store import get_engine
from sqlalchemy import text

engine = get_engine()

with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM prediction_logs LIMIT 1000"))
    predictions = [dict(row._mapping) for row in result]

with open('predictions.json', 'w') as f:
    json.dump(predictions, f, indent=2, default=str)
```

### Scheduled Daily Export
```bash
# Create a daily export script
# save as: export_daily.sh

#!/bin/bash
python /path/to/storage-forecaster/scripts/view_reviews.py --all \
  --output=/backups/reviews_$(date +%Y%m%d).csv

python /path/to/storage-forecaster/scripts/view_reviews.py --predictions \
  --output=/backups/predictions_$(date +%Y%m%d).csv
```

Then add to crontab:
```bash
0 2 * * * /path/to/export_daily.sh
```

---

## Connecting BI Tools

### Connect Power BI
1. Get PostgreSQL connection string
2. In Power BI: Get Data → PostgreSQL Database
3. Enter server, database, username, password
4. Select `reviews` and `prediction_logs` tables
5. Load and create visualizations

### Connect Tableau
1. Get PostgreSQL connection string
2. In Tableau: Connect → PostgreSQL
3. Enter server, database, username, password
4. Drag tables to canvas
5. Create dashboards

### Connect Google Sheets
```python
# Export to CSV, then upload to Google Drive
python scripts/view_reviews.py --all --output=/tmp/reviews.csv

# Or use Google Sheets API directly
from google.colab import auth
import gspread

auth.authenticate_user()
gc = gspread.authorize(creds)

# Import reviews and append
df = pd.read_csv('reviews.csv')
# ... append to sheet
```

---

## Backup & Recovery

### Backup Reviews
```bash
# SQLite backup
cp data/app_reviews.db data/app_reviews_backup.db

# PostgreSQL backup
pg_dump -U app_user -h localhost storage_forecaster > backup.sql

# CSV backup (all methods)
python scripts/view_reviews.py --all --output=backup_$(date +%Y%m%d).csv
```

### Restore from CSV
```python
import pandas as pd
from src.review_store import save_review

df = pd.read_csv('backup.csv')

for _, row in df.iterrows():
    save_review(
        name=row['name'],
        role=row['role'],
        rating=int(row['rating']),
        model_used=row['model_used'],
        comment=row['comment'],
        user_hash=row.get('user_hash')
    )
```

---

## Troubleshooting Data Access

### Problem: "No data appearing"
```bash
# Check database is initialized
python scripts/init_db.py health

# If not working, initialize
python scripts/init_db.py setup

# Then test by submitting a review in the app
```

### Problem: "Can't read CSV export"
```python
# Check encoding
import pandas as pd
df = pd.read_csv('reviews.csv', encoding='utf-8')

# If encoding error, try
df = pd.read_csv('reviews.csv', encoding='latin-1')
```

### Problem: "SQL query not working"
```python
# Check database connection
from src.review_store import healthcheck
print(healthcheck())

# Verify table exists
from src.review_store import get_engine
from sqlalchemy import inspect
inspector = inspect(get_engine())
print(inspector.get_table_names())
```

### Problem: "Performance is slow"
```bash
# For large datasets, limit results
python scripts/view_reviews.py --limit 1000

# Add indexes (PostgreSQL)
CREATE INDEX idx_reviews_created_at ON reviews(created_at);
CREATE INDEX idx_reviews_model_used ON reviews(model_used);
CREATE INDEX idx_prediction_logs_model_used ON prediction_logs(model_used);
```

---

## Summary Table

| Task | Method | Command |
|------|--------|---------|
| View recent reviews | Streamlit dashboard | Go to Reviews & Deploy tab |
| Export reviews CSV | Streamlit or CLI | Dashboard button or `view_reviews.py --all` |
| View statistics | CLI | `view_reviews.py --stats` |
| Query database | Python | Use `load_reviews()` or SQLAlchemy |
| Direct SQL query | Python | Use `get_engine()` with SQLAlchemy |
| Backup data | Any | `view_reviews.py --all` or `pg_dump` |
| BI tool access | PostgreSQL | Use managed database connection string |

---

## Getting Help

- **Quick reference**: `QUICK_START.md`
- **Docker & PostgreSQL**: `DOCKER_POSTGRES_GUIDE.md`
- **Database code**: `src/review_store.py`
- **Example scripts**: `scripts/view_reviews.py`, `scripts/init_db.py`
- **Settings**: `src/settings.py`
