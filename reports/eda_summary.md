# EDA Summary

## Dataset snapshot
- Rows: **17,280**
- Users: **32**
- Profiles: **4**
- Days per user: **540**
- Date range: **2024-01-01** to **2025-06-23**

## Profile summary

| profile | users | avg_capacity_gb | avg_used_gb | avg_used_pct | avg_daily_delta_gb | cleanup_rate |
|---|---:|---:|---:|---:|---:|---:|
| media_heavy | 8 | 320.000 | 177.052 | 59.491 | 0.215 | 0.011 |
| gamer | 8 | 672.000 | 275.651 | 40.224 | 0.215 | 0.019 |
| office_user | 8 | 336.000 | 88.442 | 33.266 | 0.086 | 0.002 |
| cleaner | 8 | 224.000 | 47.807 | 22.730 | -0.015 | 0.062 |


## Key takeaways
1. **Fastest growth profile:** `media_heavy` based on average daily storage increase.
2. **Highest average utilization:** `media_heavy` based on average used percentage.
3. **Most frequent cleanup behavior:** `cleaner` based on cleanup event rate.
4. **Modeling note:** profile-level behavior differs strongly, so a single global linear model is likely underfit.
5. **Feature note:** lag features and profile-aware modeling should help more than using day index alone.

## Generated figures
- `reports/figures/eda_capacity_distribution.png`
- `reports/figures/eda_daily_delta_boxplot.png`
- `reports/figures/eda_monthly_cleanup_rate.png`
- `reports/figures/eda_correlation_heatmap.png`
- `reports/figures/eda_growth_curves.png`
