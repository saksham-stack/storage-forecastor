# Architecture & Data Flow Diagrams

## 1. Application Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     STREAMLIT DASHBOARD                          │
│                     (dashboard/app.py)                           │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │  Overview    │  Forecast    │  Benchmarks  │  Reviews &   │  │
│  │  Behavior    │  Lab         │  Center      │  Deploy ⭐   │  │
│  │  Explorer    │              │              │              │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              REVIEW STORE LAYER                                  │
│              (src/review_store.py)                              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  save_review()                                             │ │
│  │  load_reviews()                                            │ │
│  │  log_predictions()                                         │ │
│  │  review_summary()                                          │ │
│  │  healthcheck()                                             │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│            DATABASE LAYER (Abstracted)                          │
│  ┌─────────────────┬──────────────────┬───────────────────────┐ │
│  │   SQLite        │   PostgreSQL     │   PostgreSQL Managed  │ │
│  │  (Local Dev)    │   (Local Docker) │   (Production)        │ │
│  │                 │                  │                       │ │
│  │ data/           │ localhost:5432   │ neon.tech             │ │
│  │ app_reviews.db  │ docker-compose   │ supabase.com          │ │
│  │                 │                  │ railway.app           │ │
│  │                 │                  │ render.com            │ │
│  └─────────────────┴──────────────────┴───────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Data Flow - User Review Submission

```
User in Streamlit App
       ↓
Review Form Submitted
│ name
│ role
│ rating (1-5)
│ model_used
│ comment
       ↓
save_review() function
       ↓
Generate user_hash (anonymization)
       ↓
Database INSERT
       ↓
reviews table
├─ id (auto increment)
├─ created_at (auto timestamp)
├─ name
├─ role
├─ rating
├─ model_used
├─ comment
└─ user_hash ← Anonymized
       ↓
Success message shown in UI
```

## 3. Data Flow - Forecast Prediction

```
User runs XGBoost forecast
       ↓
Prepare features (lag, rolling, time)
       ↓
Make prediction for 30/60/90 days
       ↓
log_predictions() function
       ↓
Insert prediction log
       ↓
prediction_logs table
├─ id (auto increment)
├─ created_at (auto timestamp)
├─ model_used ("XGBoost")
├─ source ("sample_user" or "uploaded_csv")
├─ user_hash ← Anonymized
├─ horizon_days (30, 60, or 90)
├─ predicted_used_gb
└─ predicted_used_pct
       ↓
Chart displayed to user
```

## 4. Database Deployment Options

```
                    DATABASE_URL Environment Variable
                           ↓
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                  ↓
    SQLite           PostgreSQL        PostgreSQL
   (Local)           (Docker)          (Managed)
     │                  │                 │
     ├─ development     ├─ staging        ├─ Neon
     ├─ no setup        ├─ docker-compose ├─ Supabase
     ├─ portable        ├─ persistent     ├─ Railway
     └─ single user     └─ multi-user     ├─ Render
                                          ├─ free tier
                                          ├─ auto-scaling
                                          └─ production-ready
```

## 5. Data Access Methods

```
                        REVIEWS DATA
                           ↓
          ┌────────────────┼────────────────┐
          ↓                ↓                ↓
    Streamlit         Command Line       Python
    Dashboard         CLI Scripts        Scripts
        │                 │                │
        │            ┌────┴────┐          │
        ├─ View      │          │          │
        ├─ Export    │    ┌─────┴─────┐   │
        └─ Stats   view_reviews.py  pd.read_sql()
               ├─ --all          │
               ├─ --stats        │
               └─ --predictions  └─→ DataFrame
                                      │
                    ┌─────────────────┼──────────────┐
                    ↓                 ↓              ↓
                CSV Export         JSON           BI Tools
                            pandas  Database Query Power BI
                                  sqlalchemy     Tableau
```

## 6. Docker Compose Architecture

```
┌─────────────────────────────────────────────────────────────┐
│         Docker Network: storage-net (bridge)                │
│                                                              │
│  ┌──────────────────────┐    ┌──────────────────────────┐  │
│  │  storage-forecaster  │    │  postgres:5432           │  │
│  │  (Streamlit App)     │◄──►│  (PostgreSQL Database)   │  │
│  │                      │    │                          │  │
│  │  :8501 → 8501        │    │  :5432 → 5432            │  │
│  └──────────────────────┘    └──────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  pgAdmin (Database UI)                               │  │
│  │  :5050 → 80                                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Volumes:                                                   │
│  • postgres_data:/var/lib/postgresql/data                  │
│  • ./models ↔ /app/models                                  │
│  • ./reports ↔ /app/reports                                │
│  • ./data ↔ /app/data                                      │
└─────────────────────────────────────────────────────────────┘

Access Points:
- App:     http://localhost:8501
- PgAdmin: http://localhost:5050 (admin@admin.com / admin)
- DB:      psql -h localhost -U app_user -d storage_forecaster
```

## 7. User Data Privacy Flow

```
User Input (name, email, ID, etc.)
        ↓
make_user_hash(input)
        ├─ SHA256 hash
        ├─ One-way encryption
        └─ First 24 characters
        ↓
user_hash: "a4e0f91f4c5e3b6d2a8c1e9d"
        ↓
Stored in Database (anonymized)
        ├─ Can't reverse to original
        ├─ Consistent (same input = same hash)
        ├─ GDPR compliant
        └─ Privacy preserved
        ↓
Analysis & Export
├─ See patterns without PII
├─ Export for data science
└─ Share publicly safely
```

## 8. Configuration Flow

```
                    Environment Configuration
                           ↓
          ┌────────────────┼────────────────┐
          ↓                ↓                ↓
    .env file        Environment          Secrets
    (Development)    Variables            (Streamlit Cloud)
         │           (Production)              │
         │                │                    │
         └────┬───────────┴────────────────┬───┘
              ↓
         Settings object
         (src/settings.py)
              ├─ database_url
              ├─ environment
              ├─ app_base_url
              ├─ model_registry_dir
              └─ review_export_dir
              ↓
         Application uses
         configuration
```

## 9. Scripts & Tools Overview

```
┌─────────────────────────────────────────────────────────┐
│                   YOUR TOOLBOX                          │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  scripts/view_reviews.py                        │   │
│  │  • View recent reviews                          │   │
│  │  • Export all reviews to CSV                    │   │
│  │  • Show statistics                              │   │
│  │  • Export prediction logs                       │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  scripts/init_db.py                             │   │
│  │  • Setup database tables                        │   │
│  │  • Check database health                        │   │
│  │  • Reset database                               │   │
│  │  • Export database schema                       │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  scripts/setup_wizard.py                        │   │
│  │  • Interactive setup                            │   │
│  │  • Create virtual environment                   │   │
│  │  • Install dependencies                         │   │
│  │  • Choose database option                       │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  dashboard/app.py                               │   │
│  │  • View reviews in UI                           │   │
│  │  • Export CSV via button                        │   │
│  │  • Submit reviews                               │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 10. Deployment Environments

```
LOCAL DEVELOPMENT              STAGING/TESTING           PRODUCTION
════════════════════════════════════════════════════════════════════

SQLite or                      PostgreSQL +              Managed
PostgreSQL                     Docker                    PostgreSQL
  │                              │                         │
  ├─ Machine                  ├─ Docker Host           ├─ Cloud Provider
  ├─ :8501                    ├─ :8501                 ├─ HTTPS
  ├─ localhost                ├─ localhost             ├─ Custom Domain
  ├─ No HTTPS                 ├─ Container Logs        ├─ Monitoring
  ├─ Manual testing           ├─ Health Checks         ├─ Auto-backups
  ├─ data/app_reviews.db      ├─ docker-compose        ├─ Auto-scaling
  └─ Persistent data          ├─ pgAdmin UI            ├─ SSL/TLS
                              └─ postgres_data volume  ├─ Secrets Manager
                                                       └─ CI/CD Pipeline
```

## 11. Complete Data Journey

```
┌──────────────────────────────────────────────────────────────────────┐
│                      DATA LIFECYCLE                                   │
└──────────────────────────────────────────────────────────────────────┘

1. COLLECTION
   User submits review in Streamlit app
         ↓

2. PROCESSING
   • Anonymize user (make_user_hash)
   • Validate input (max lengths, constraints)
   • Add timestamp
         ↓

3. STORAGE
   Insert into appropriate table:
   • reviews table (feedback)
   • prediction_logs table (forecasts)
         ↓

4. PERSISTENCE
   Choose database:
   • SQLite (dev)
   • PostgreSQL (Docker/production)
         ↓

5. ACCESS
   Multiple methods:
   • Streamlit Dashboard UI
   • CLI scripts (view_reviews.py)
   • Python code (sqlalchemy)
   • Direct SQL queries
         ↓

6. ANALYSIS
   • Pandas DataFrames
   • SQL aggregations
   • BI tools (Power BI, Tableau)
         ↓

7. EXPORT
   • CSV files
   • JSON
   • Custom formats
         ↓

8. BACKUP
   • Automated exports
   • Database snapshots
   • Version control
         ↓

9. COMPLIANCE
   • GDPR: anonymized data
   • Privacy: user hashes
   • Retention: manual deletion available
   • Audit: timestamps preserved
```

## Quick Reference: Which Command For What?

```
┌─────────────────────────────────┬──────────────────────────────────┐
│ What I Need                     │ Command                          │
├─────────────────────────────────┼──────────────────────────────────┤
│ See last 20 reviews             │ python scripts/view_reviews.py   │
│ Download all reviews            │ python scripts/view_reviews.py   │
│                                 │ --all --output=reviews.csv       │
│ Show statistics                 │ python scripts/view_reviews.py   │
│                                 │ --stats                          │
│ Export predictions              │ python scripts/view_reviews.py   │
│                                 │ --predictions                    │
│ Check database health           │ python scripts/init_db.py health │
│ Setup database tables           │ python scripts/init_db.py setup  │
│ Start app locally (SQLite)      │ streamlit run dashboard/app.py   │
│ Start with Docker Compose       │ docker-compose -f                │
│                                 │ docker-compose.staging.yml up    │
│ View database via UI            │ http://localhost:5050            │
│ Read full guide                 │ DOCKER_POSTGRES_GUIDE.md         │
│ Quick reference                 │ QUICK_START.md                   │
│ How to access data              │ ACCESS_USER_DATA.md              │
└─────────────────────────────────┴──────────────────────────────────┘
```

This diagram file helps visualize your entire system architecture!
