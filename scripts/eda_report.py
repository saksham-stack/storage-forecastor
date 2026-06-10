import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='whitegrid')

DATA_PATH = Path('data/synthetic/synthetic_storage_usage.csv')
FIG_DIR = Path('reports/figures')
SUMMARY_PATH = Path('reports/eda_summary.md')


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f'Missing dataset: {DATA_PATH}')

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_PATH, parse_dates=['date'])

    profile_order = ['media_heavy', 'gamer', 'office_user', 'cleaner']
    colors = {
        'media_heavy': '#E63946',
        'gamer': '#457B9D',
        'office_user': '#2A9D8F',
        'cleaner': '#F4A261',
    }

    # Basic summaries
    rows = len(df)
    users = df['user_id'].nunique()
    profiles = df['profile'].nunique()
    days = df['day_index'].nunique()
    date_min = df['date'].min().date()
    date_max = df['date'].max().date()

    profile_summary = (
        df.groupby('profile')
          .agg(
              users=('user_id', 'nunique'),
              avg_capacity_gb=('total_capacity_gb', 'mean'),
              avg_used_gb=('used_gb', 'mean'),
              avg_used_pct=('used_pct', 'mean'),
              avg_daily_delta_gb=('daily_delta_gb', 'mean'),
              cleanup_rate=('cleanup_event', 'mean')
          )
          .round(3)
          .reindex(profile_order)
    )
    profile_summary.to_csv('reports/profile_summary.csv')

    # Figure 1: capacity distribution by profile
    plt.figure(figsize=(10, 5))
    sns.countplot(data=df.drop_duplicates(['user_id']), x='total_capacity_gb', hue='profile', palette=colors)
    plt.title('Device Capacity Distribution by Profile')
    plt.xlabel('Total Capacity (GB)')
    plt.ylabel('Number of users')
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'eda_capacity_distribution.png', dpi=140)
    plt.close()

    # Figure 2: daily delta distribution
    plt.figure(figsize=(10, 5))
    subset = df[(df['daily_delta_gb'] > -50) & (df['daily_delta_gb'] < 80)].copy()
    sns.boxplot(data=subset, x='profile', y='daily_delta_gb', order=profile_order, hue='profile', palette=colors, legend=False)
    plt.title('Daily Storage Change by Profile')
    plt.xlabel('Profile')
    plt.ylabel('Daily delta (GB)')
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'eda_daily_delta_boxplot.png', dpi=140)
    plt.close()

    # Figure 3: cleanup rate by month
    monthly = (df.assign(month=df['date'].dt.to_period('M').astype(str))
                 .groupby(['month', 'profile'])['cleanup_event']
                 .mean()
                 .reset_index())
    plt.figure(figsize=(12, 5))
    sns.lineplot(data=monthly, x='month', y='cleanup_event', hue='profile', hue_order=profile_order, palette=colors)
    plt.title('Monthly Cleanup Event Rate by Profile')
    plt.xlabel('Month')
    plt.ylabel('Cleanup event rate')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'eda_monthly_cleanup_rate.png', dpi=140)
    plt.close()

    # Figure 4: correlation heatmap for numeric variables
    cols = ['used_gb', 'free_gb', 'used_pct', 'photos_gb', 'videos_gb', 'apps_gb', 'documents_gb', 'system_gb', 'other_gb', 'daily_delta_gb', 'cleanup_event']
    corr = df[cols].corr(numeric_only=True)
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, cmap='coolwarm', center=0, annot=False)
    plt.title('Correlation Heatmap of Core Numeric Features')
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'eda_correlation_heatmap.png', dpi=140)
    plt.close()

    # Figure 5: mean growth curve by profile (EDA view)
    growth = df.groupby(['profile', 'day_index'])['used_gb'].mean().reset_index()
    plt.figure(figsize=(11, 5))
    for profile in profile_order:
        sub = growth[growth['profile'] == profile]
        plt.plot(sub['day_index'], sub['used_gb'], label=profile, color=colors[profile], linewidth=2)
    plt.title('Average Used Storage Over Time by Profile')
    plt.xlabel('Day index')
    plt.ylabel('Used GB')
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'eda_growth_curves.png', dpi=140)
    plt.close()

    # Simple textual insights
    top_cleanup = profile_summary['cleanup_rate'].idxmax()
    top_growth = profile_summary['avg_daily_delta_gb'].idxmax()
    top_util = profile_summary['avg_used_pct'].idxmax()

    profile_table_md = '| profile | users | avg_capacity_gb | avg_used_gb | avg_used_pct | avg_daily_delta_gb | cleanup_rate |\n'
    profile_table_md += '|---|---:|---:|---:|---:|---:|---:|\n'
    for profile_name, row in profile_summary.iterrows():
        profile_table_md += f"| {profile_name} | {int(row['users'])} | {row['avg_capacity_gb']:.3f} | {row['avg_used_gb']:.3f} | {row['avg_used_pct']:.3f} | {row['avg_daily_delta_gb']:.3f} | {row['cleanup_rate']:.3f} |\n"

    summary_md = f'''# EDA Summary

## Dataset snapshot
- Rows: **{rows:,}**
- Users: **{users}**
- Profiles: **{profiles}**
- Days per user: **{days}**
- Date range: **{date_min}** to **{date_max}**

## Profile summary

{profile_table_md}

## Key takeaways
1. **Fastest growth profile:** `{top_growth}` based on average daily storage increase.
2. **Highest average utilization:** `{top_util}` based on average used percentage.
3. **Most frequent cleanup behavior:** `{top_cleanup}` based on cleanup event rate.
4. **Modeling note:** profile-level behavior differs strongly, so a single global linear model is likely underfit.
5. **Feature note:** lag features and profile-aware modeling should help more than using day index alone.

## Generated figures
- `reports/figures/eda_capacity_distribution.png`
- `reports/figures/eda_daily_delta_boxplot.png`
- `reports/figures/eda_monthly_cleanup_rate.png`
- `reports/figures/eda_correlation_heatmap.png`
- `reports/figures/eda_growth_curves.png`
'''
    SUMMARY_PATH.write_text(summary_md, encoding='utf-8')

    print('EDA complete')
    print(summary_md)


if __name__ == '__main__':
    main()
