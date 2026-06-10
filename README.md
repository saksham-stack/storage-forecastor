# Device Storage Growth Forecaster

A machine learning portfolio project that forecasts laptop/phone storage usage over the next **30, 60, and 90 days**.

## Project Goal
Predict how end-user device storage fills over time, then compare forecasting approaches such as:
- Baseline trend models
- Prophet
- XGBoost with lag features
- Optional LSTM (stretch goal)

## Project Structure

```text
storage_forecaster_v2/
├── configs/                  # Config files
├── dashboard/                # Streamlit app
├── data/
│   ├── raw/                  # Real raw device logs (future)
│   ├── processed/            # Cleaned/model-ready datasets
│   └── synthetic/            # Synthetic training data
├── models/                   # Saved trained models
├── notebooks/                # EDA and experimentation notebooks
├── reports/
│   └── figures/              # Exported plots for README/report
├── scripts/                  # CLI scripts for data generation/training
├── src/
│   ├── data/                 # Data loading and preprocessing
│   ├── evaluation/           # Metrics and backtesting
│   ├── features/             # Feature engineering
│   ├── models/               # Model training/inference code
│   └── visualization/        # Plotting utilities
└── tests/                    # Unit tests
```

## Quick Start on Windows (VS Code + venv)

### 1) Open terminal in the project folder
Use **Command Prompt** or the **VS Code terminal**.

### 2) Create a virtual environment
```bat
python -m venv .venv
```

### 3) Activate it
```bat
.venv\Scripts\activate
```

### 4) Install dependencies
```bat
pip install --upgrade pip
pip install -r requirements.txt
```

### 5) Run the synthetic data generator
```bat
python scripts\generate_synthetic_data.py
```

### 6) Run the visualization script
```bat
python scripts\visualize_data.py
```

### 7) Launch the dashboard! 🚀
```bat
streamlit run dashboard\app.py
```

## Using the Dashboard

### Test with Sample Data
The dashboard comes with synthetic sample data - just run it and explore!

### **Test with Your Own Data** 📋
New in the dashboard: **Data Builder tab** makes it super easy!

1. Open the dashboard
2. Click the **"Data Builder"** tab
3. Choose one of three methods:
   - **📊 See Example Data** - View a real example (no download)
   - **🔨 Generate Template** - Create a blank CSV template in 30 seconds
   - **📥 Download Real Example** - Get sample data to test immediately

4. For your own data:
   - Use **"Generate Template"** to create a pre-formatted CSV
   - Fill in your device's storage data (7-30 days minimum)
   - Upload to **Forecast Lab** tab
   - Get predictions! 🎉

**See `DATA_BUILDER_GUIDE.md` for detailed instructions.**

## Recommended VS Code Setup
Install these extensions:
- Python
- Pylance
- Jupyter

Then in VS Code:
1. Open the folder
2. Press `Ctrl+Shift+P`
3. Select **Python: Select Interpreter**
4. Choose the interpreter inside `.venv`

## First Milestones
- [x] Create synthetic dataset
- [x] Visualize storage behavior by profile
- [ ] Build EDA notebook
- [ ] Train baseline forecasting model
- [x] Train Prophet model
- [x] Train XGBoost model
- [x] Evaluate 30/60/90-day forecasts
- [x] Build upgraded Streamlit dashboard

## Synthetic User Profiles
- **Media-heavy**: steady photo/video growth
- **Gamer**: occasional large app/game installs
- **Office user**: slow, linear document-heavy growth
- **Cleaner**: periodic cleanup cycles

## Example Commands
### Train simple baseline model
```bat
python scripts\train_baseline.py
```

### Train improved baseline (multi-horizon Ridge with lag features)
```bat
python scripts\train_baseline_v2.py
```

### Train Prophet forecasts
```bat
python scripts\train_prophet.py
```

### Train XGBoost forecasts
```bat
python scripts\train_xgboost.py
```

### Initialize the review store
```bat
python scripts\init_review_store.py
```

### Export reviews to CSV
```bat
python scripts\export_reviews.py
```

### Compare model metrics
```bat
python scripts\compare_model_metrics.py
```

### Launch dashboard
```bat
streamlit run dashboard\app.py
```

## Notes
- The synthetic dataset is intended for prototyping and portfolio work.
- You can later add a real device logging script for Windows to collect actual usage data.
- Use time-based validation instead of random train/test splits.
- Reviews can use local SQLite in development or managed PostgreSQL in deployment via `DATABASE_URL`.
- See `DEPLOYMENT.md`, `PRODUCTION_ARCHITECTURE.md`, and `.env.example` before public launch.

## Current recommended production path
1. Train or refresh models.
2. Configure a managed PostgreSQL database.
3. Set `DATABASE_URL` in your deployment secrets.
4. Deploy the Streamlit app via Community Cloud or Docker.
5. Collect real user reviews and forecast logs for iteration.
