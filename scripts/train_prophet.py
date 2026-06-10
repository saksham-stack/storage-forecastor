from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import numpy as np
import pandas as pd
from prophet import Prophet

from src.evaluation.metrics import regression_metrics

DATA_PATH = Path('data/synthetic/synthetic_storage_usage.csv')
REPORTS_DIR = Path('reports')
FIG_DIR = REPORTS_DIR / 'figures'
HORIZONS = [30, 60, 90]
TEST_DAYS = 90


def fit_one_user(user_df: pd.DataFrame) -> pd.DataFrame:
    user_df = user_df.sort_values('date').copy()
    capacity = float(user_df['total_capacity_gb'].iloc[0])
    train = user_df.iloc[:-TEST_DAYS].copy()
    test = user_df.iloc[-TEST_DAYS:].copy()

    train_prophet = train[['date', 'used_gb']].rename(columns={'date': 'ds', 'used_gb': 'y'})

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        changepoint_prior_scale=0.15,
        seasonality_prior_scale=8.0,
    )
    model.fit(train_prophet)

    future = model.make_future_dataframe(periods=TEST_DAYS, freq='D', include_history=False)
    forecast = model.predict(future)[['ds', 'yhat']].rename(columns={'ds': 'date'})

    merged = test[['user_id', 'profile', 'date', 'used_gb', 'total_capacity_gb']].merge(forecast, on='date', how='left')
    merged['prediction'] = np.clip(merged['yhat'], 0.0, capacity * 0.985)
    merged = merged.drop(columns=['yhat'])
    return merged.rename(columns={'used_gb': 'actual'})


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f'Missing dataset: {DATA_PATH}')

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATA_PATH, parse_dates=['date'])
    df = df.sort_values(['user_id', 'date']).copy()

    all_predictions = []
    for _, user_df in df.groupby('user_id'):
        all_predictions.append(fit_one_user(user_df))

    pred_df = pd.concat(all_predictions, ignore_index=True)
    pred_df['forecast_day'] = pred_df.groupby('user_id').cumcount() + 1

    metrics = []
    for horizon in HORIZONS:
        horizon_df = pred_df[pred_df['forecast_day'] <= horizon].copy()
        row = regression_metrics(horizon_df['actual'], horizon_df['prediction'])
        row.update({
            'model': 'prophet_per_user',
            'horizon_days': horizon,
            'train_rows_per_user': int(df.groupby('user_id').size().iloc[0] - TEST_DAYS),
            'test_rows': int(len(horizon_df)),
        })
        metrics.append(row)

    metrics_df = pd.DataFrame(metrics)
    metrics_path = REPORTS_DIR / 'prophet_metrics.csv'
    preds_path = REPORTS_DIR / 'prophet_predictions.csv'
    metrics_df.to_csv(metrics_path, index=False)
    pred_df.to_csv(preds_path, index=False)

    # Sample forecast chart: one representative user per profile.
    import matplotlib.pyplot as plt

    profiles = ['media_heavy', 'gamer', 'office_user', 'cleaner']
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), sharex=False)
    axes = axes.flatten()
    for i, profile in enumerate(profiles):
        ax = axes[i]
        sample_user = pred_df[pred_df['profile'] == profile]['user_id'].iloc[0]
        actual_all = df[df['user_id'] == sample_user].sort_values('date')
        pred_user = pred_df[pred_df['user_id'] == sample_user].sort_values('date')
        ax.plot(actual_all['date'], actual_all['used_gb'], label='Actual', linewidth=2)
        ax.plot(pred_user['date'], pred_user['prediction'], label='Prophet forecast', linewidth=2, linestyle='--')
        ax.axvline(actual_all['date'].iloc[-TEST_DAYS], color='gray', linestyle=':', alpha=0.8)
        ax.set_title(f'{profile} — {sample_user}')
        ax.set_ylabel('Used GB')
        ax.grid(alpha=0.3)
        if i == 0:
            ax.legend()
    plt.tight_layout()
    fig_path = FIG_DIR / 'prophet_sample_forecasts.png'
    plt.savefig(fig_path, dpi=140, bbox_inches='tight')
    plt.close()

    summary_md = ['# Prophet Results', '', 'Per-user Prophet forecasting on the final 90 days of each user time series.', '', metrics_df.to_markdown(index=False)]
    (REPORTS_DIR / 'prophet_summary.md').write_text('\n'.join(summary_md), encoding='utf-8')

    print('Prophet training complete')
    print(metrics_df.to_string(index=False))
    print(f'Saved metrics to: {metrics_path}')
    print(f'Saved predictions to: {preds_path}')
    print(f'Saved figure to: {fig_path}')


if __name__ == '__main__':
    main()
