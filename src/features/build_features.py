from __future__ import annotations

import pandas as pd


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out['date'] = pd.to_datetime(out['date'])
    out['day_of_week'] = out['date'].dt.dayofweek
    out['month'] = out['date'].dt.month
    out['day_of_month'] = out['date'].dt.day
    out['day_of_year'] = out['date'].dt.dayofyear
    out['week_of_year'] = out['date'].dt.isocalendar().week.astype(int)
    out['is_weekend'] = out['day_of_week'].isin([5, 6]).astype(int)
    return out


def add_lag_features(df: pd.DataFrame, lags=(1, 7, 14, 30), value_col='used_gb', group_col='user_id') -> pd.DataFrame:
    out = df.sort_values([group_col, 'date']).copy()
    for lag in lags:
        out[f'{value_col}_lag_{lag}'] = out.groupby(group_col)[value_col].shift(lag)
    return out


def add_rolling_features(df: pd.DataFrame, windows=(7, 30), value_col='used_gb', group_col='user_id') -> pd.DataFrame:
    out = df.sort_values([group_col, 'date']).copy()
    grouped = out.groupby(group_col)[value_col]
    for window in windows:
        out[f'{value_col}_roll_mean_{window}'] = grouped.transform(lambda s: s.shift(1).rolling(window).mean())
        out[f'{value_col}_roll_std_{window}'] = grouped.transform(lambda s: s.shift(1).rolling(window).std())
    return out


def add_supervised_targets(df: pd.DataFrame, horizons=(30, 60, 90), value_col='used_gb', group_col='user_id') -> pd.DataFrame:
    out = df.sort_values([group_col, 'date']).copy()
    for horizon in horizons:
        out[f'target_t_plus_{horizon}'] = out.groupby(group_col)[value_col].shift(-horizon)
    return out
