from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.evaluation.metrics import regression_metrics
from src.features.build_features import (
    add_lag_features,
    add_rolling_features,
    add_supervised_targets,
    add_time_features,
)

DATA_PATH = Path('data/synthetic/synthetic_storage_usage.csv')
REPORTS_DIR = Path('reports')
MODELS_DIR = Path('models')
HORIZONS = [30, 60, 90]


def build_dataset() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=['date'])
    df = df.sort_values(['user_id', 'date']).copy()
    df = add_time_features(df)
    df = add_lag_features(df, lags=(1, 7, 14, 30))
    df = add_rolling_features(df, windows=(7, 30))
    df = add_supervised_targets(df, horizons=HORIZONS)
    return df


def train_for_horizon(df: pd.DataFrame, horizon: int) -> tuple[dict, pd.DataFrame]:
    target_col = f'target_t_plus_{horizon}'
    working = df.dropna(subset=[target_col]).copy()

    max_day = int(working['day_index'].max())
    test_anchor_start = max_day - horizon - 89
    train = working[working['day_index'] < test_anchor_start].copy()
    test = working[working['day_index'] >= test_anchor_start].copy()

    feature_cols_num = [
        'used_gb', 'free_gb', 'used_pct', 'daily_delta_gb', 'cleanup_event',
        'total_capacity_gb', 'day_index', 'day_of_week', 'month', 'day_of_month', 'day_of_year', 'week_of_year', 'is_weekend',
        'used_gb_lag_1', 'used_gb_lag_7', 'used_gb_lag_14', 'used_gb_lag_30',
        'used_gb_roll_mean_7', 'used_gb_roll_std_7', 'used_gb_roll_mean_30', 'used_gb_roll_std_30'
    ]
    feature_cols_cat = ['profile']
    used_cols = feature_cols_num + feature_cols_cat

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', Pipeline([
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler()),
            ]), feature_cols_num),
            ('cat', Pipeline([
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('onehot', OneHotEncoder(handle_unknown='ignore')),
            ]), feature_cols_cat),
        ]
    )

    model = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', Ridge(alpha=1.0)),
    ])

    model.fit(train[used_cols], train[target_col])
    preds = model.predict(test[used_cols])
    preds = np.minimum(preds, test['total_capacity_gb'].values * 0.985)
    preds = np.maximum(preds, 0.0)

    overall = regression_metrics(test[target_col], preds)
    overall.update({
        'model': 'baseline_v2_ridge',
        'horizon_days': horizon,
        'train_rows': int(len(train)),
        'test_rows': int(len(test)),
    })

    prediction_frame = test[['user_id', 'profile', 'date', 'day_index', 'total_capacity_gb', target_col]].copy()
    prediction_frame['prediction'] = preds
    prediction_frame['horizon_days'] = horizon
    prediction_frame = prediction_frame.rename(columns={target_col: 'actual'})
    return overall, prediction_frame


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f'Missing dataset: {DATA_PATH}')

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    df = build_dataset()
    all_metrics = []
    all_predictions = []

    for horizon in HORIZONS:
        metrics, preds = train_for_horizon(df, horizon)
        all_metrics.append(metrics)
        all_predictions.append(preds)

    metrics_df = pd.DataFrame(all_metrics)
    preds_df = pd.concat(all_predictions, ignore_index=True)

    metrics_path = REPORTS_DIR / 'baseline_v2_metrics.csv'
    preds_path = REPORTS_DIR / 'baseline_v2_predictions.csv'
    metrics_df.to_csv(metrics_path, index=False)
    preds_df.to_csv(preds_path, index=False)

    summary_md = ['# Baseline V2 Results', '', 'Direct multi-horizon Ridge regression using lag/rolling/time/profile features.', '', metrics_df.to_markdown(index=False)]
    (REPORTS_DIR / 'baseline_v2_summary.md').write_text('\n'.join(summary_md), encoding='utf-8')

    print('Baseline V2 complete')
    print(metrics_df.to_string(index=False))
    print(f'Saved metrics to: {metrics_path}')
    print(f'Saved predictions to: {preds_path}')


if __name__ == '__main__':
    main()
