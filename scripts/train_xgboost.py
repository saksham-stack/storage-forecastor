from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBRegressor

from src.evaluation.metrics import regression_metrics
from src.features.build_features import (
    add_lag_features,
    add_rolling_features,
    add_supervised_targets,
    add_time_features,
)

DATA_PATH = Path('data/synthetic/synthetic_storage_usage.csv')
REPORTS_DIR = Path('reports')
FIG_DIR = REPORTS_DIR / 'figures'
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


def feature_sets():
    num = [
        'used_gb', 'free_gb', 'used_pct', 'daily_delta_gb', 'cleanup_event',
        'total_capacity_gb', 'day_index', 'day_of_week', 'month', 'day_of_month', 'day_of_year', 'week_of_year', 'is_weekend',
        'used_gb_lag_1', 'used_gb_lag_7', 'used_gb_lag_14', 'used_gb_lag_30',
        'used_gb_roll_mean_7', 'used_gb_roll_std_7', 'used_gb_roll_mean_30', 'used_gb_roll_std_30'
    ]
    cat = ['profile']
    return num, cat


def build_model(num_cols, cat_cols):
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', SimpleImputer(strategy='median'), num_cols),
            ('cat', Pipeline([
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('onehot', OneHotEncoder(handle_unknown='ignore')),
            ]), cat_cols),
        ]
    )

    regressor = XGBRegressor(
        n_estimators=350,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_alpha=0.0,
        reg_lambda=1.0,
        objective='reg:squarederror',
        random_state=42,
        n_jobs=2,
    )

    model = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', regressor),
    ])
    return model


def train_for_horizon(df: pd.DataFrame, horizon: int):
    target_col = f'target_t_plus_{horizon}'
    working = df.dropna(subset=[target_col]).copy()

    max_day = int(working['day_index'].max())
    test_anchor_start = max_day - horizon - 89
    train = working[working['day_index'] < test_anchor_start].copy()
    test = working[working['day_index'] >= test_anchor_start].copy()

    num_cols, cat_cols = feature_sets()
    used_cols = num_cols + cat_cols

    model = build_model(num_cols, cat_cols)
    model.fit(train[used_cols], train[target_col])
    preds = model.predict(test[used_cols])
    preds = np.minimum(preds, test['total_capacity_gb'].values * 0.985)
    preds = np.maximum(preds, 0.0)

    metrics = regression_metrics(test[target_col], preds)
    metrics.update({
        'model': 'xgboost_direct',
        'horizon_days': horizon,
        'train_rows': int(len(train)),
        'test_rows': int(len(test)),
    })

    pred_df = test[['user_id', 'profile', 'date', 'day_index', 'total_capacity_gb', target_col]].copy()
    pred_df['prediction'] = preds
    pred_df['horizon_days'] = horizon
    pred_df = pred_df.rename(columns={target_col: 'actual'})

    model_path = MODELS_DIR / f'xgboost_h{horizon}.joblib'
    joblib.dump(model, model_path)
    return metrics, pred_df, model, used_cols, model_path


def export_feature_importance(model, out_csv: Path, out_png: Path):
    import matplotlib.pyplot as plt

    preprocessor = model.named_steps['preprocessor']
    regressor = model.named_steps['regressor']
    feature_names = preprocessor.get_feature_names_out()
    importances = pd.DataFrame({
        'feature': feature_names,
        'importance': regressor.feature_importances_,
    }).sort_values('importance', ascending=False)
    importances.to_csv(out_csv, index=False)

    top = importances.head(15).iloc[::-1]
    plt.figure(figsize=(9, 6))
    plt.barh(top['feature'], top['importance'])
    plt.title('Top XGBoost Feature Importances (30-day model)')
    plt.xlabel('Importance')
    plt.tight_layout()
    plt.savefig(out_png, dpi=140, bbox_inches='tight')
    plt.close()


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f'Missing dataset: {DATA_PATH}')

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    df = build_dataset()
    all_metrics = []
    all_predictions = []
    first_model = None

    for horizon in HORIZONS:
        metrics, preds, model, used_cols, model_path = train_for_horizon(df, horizon)
        all_metrics.append(metrics)
        all_predictions.append(preds)
        if horizon == 30:
            first_model = model
        print(f'Saved model: {model_path}')

    metrics_df = pd.DataFrame(all_metrics)
    preds_df = pd.concat(all_predictions, ignore_index=True)
    metrics_path = REPORTS_DIR / 'xgboost_metrics.csv'
    preds_path = REPORTS_DIR / 'xgboost_predictions.csv'
    metrics_df.to_csv(metrics_path, index=False)
    preds_df.to_csv(preds_path, index=False)

    export_feature_importance(
        first_model,
        REPORTS_DIR / 'xgboost_feature_importance.csv',
        FIG_DIR / 'xgboost_feature_importance.png',
    )

    try:
        table_md = metrics_df.to_markdown(index=False)
    except Exception:
        table_md = metrics_df.to_string(index=False)
    summary_md = ['# XGBoost Results', '', 'Direct multi-horizon XGBoost forecasting using lag, rolling, calendar, state, and profile features.', '', table_md]
    (REPORTS_DIR / 'xgboost_summary.md').write_text('\n'.join(summary_md), encoding='utf-8')

    print('XGBoost training complete')
    print(metrics_df.to_string(index=False))
    print(f'Saved metrics to: {metrics_path}')
    print(f'Saved predictions to: {preds_path}')


if __name__ == '__main__':
    main()
