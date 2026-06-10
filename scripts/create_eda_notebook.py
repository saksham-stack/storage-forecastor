from pathlib import Path
import nbformat as nbf

nb = nbf.v4.new_notebook()

cells = []

cells.append(nbf.v4.new_markdown_cell(
"# Exploratory Data Analysis — Device Storage Growth Forecaster\n\n"
"This notebook explores the synthetic storage-usage dataset, checks data quality, studies user-profile behavior, and prepares ideas for forecasting models."
))

cells.append(nbf.v4.new_markdown_cell(
"## Goals\n"
"- Understand dataset shape and schema\n"
"- Compare storage behavior across profiles\n"
"- Inspect cleanup events and daily changes\n"
"- Identify useful forecasting features\n"
"- Build intuition for why the baseline model underfits"
))

cells.append(nbf.v4.new_code_cell(
"import pandas as pd\n"
"import numpy as np\n"
"import matplotlib.pyplot as plt\n"
"import seaborn as sns\n"
"from pathlib import Path\n\n"
"sns.set_theme(style='whitegrid')\n"
"DATA_PATH = Path('../data/synthetic/synthetic_storage_usage.csv')\n"
"df = pd.read_csv(DATA_PATH, parse_dates=['date'])\n"
"df.head()"
))

cells.append(nbf.v4.new_code_cell(
"print('Shape:', df.shape)\n"
"print('Users:', df['user_id'].nunique())\n"
"print('Profiles:', df['profile'].unique())\n"
"print('Date range:', df['date'].min(), 'to', df['date'].max())\n"
"df.info()"
))

cells.append(nbf.v4.new_markdown_cell("## Missing values and descriptive statistics"))

cells.append(nbf.v4.new_code_cell(
"missing = df.isna().sum().sort_values(ascending=False)\n"
"display(missing[missing > 0])\n"
"df.describe(numeric_only=True).T"
))

cells.append(nbf.v4.new_markdown_cell("## Profile-level summary"))

cells.append(nbf.v4.new_code_cell(
"profile_summary = (df.groupby('profile')\n"
"    .agg(users=('user_id', 'nunique'),\n"
"         avg_capacity_gb=('total_capacity_gb', 'mean'),\n"
"         avg_used_gb=('used_gb', 'mean'),\n"
"         avg_used_pct=('used_pct', 'mean'),\n"
"         avg_daily_delta_gb=('daily_delta_gb', 'mean'),\n"
"         cleanup_rate=('cleanup_event', 'mean'))\n"
"    .round(3))\n"
"profile_summary"
))

cells.append(nbf.v4.new_markdown_cell("## Average growth curves by profile"))

cells.append(nbf.v4.new_code_cell(
"growth = df.groupby(['profile', 'day_index'])['used_gb'].mean().reset_index()\n"
"plt.figure(figsize=(11,5))\n"
"for profile in growth['profile'].unique():\n"
"    sub = growth[growth['profile'] == profile]\n"
"    plt.plot(sub['day_index'], sub['used_gb'], label=profile, linewidth=2)\n"
"plt.title('Average Used Storage Over Time by Profile')\n"
"plt.xlabel('Day index')\n"
"plt.ylabel('Used GB')\n"
"plt.legend()\n"
"plt.show()"
))

cells.append(nbf.v4.new_markdown_cell("## Daily change distribution"))

cells.append(nbf.v4.new_code_cell(
"subset = df[(df['daily_delta_gb'] > -50) & (df['daily_delta_gb'] < 80)].copy()\n"
"plt.figure(figsize=(10,5))\n"
"sns.boxplot(data=subset, x='profile', y='daily_delta_gb')\n"
"plt.xticks(rotation=15)\n"
"plt.title('Daily Storage Change by Profile')\n"
"plt.show()"
))

cells.append(nbf.v4.new_markdown_cell("## Cleanup behavior over time"))

cells.append(nbf.v4.new_code_cell(
"monthly_cleanup = (df.assign(month=df['date'].dt.to_period('M').astype(str))\n"
"    .groupby(['month', 'profile'])['cleanup_event']\n"
"    .mean()\n"
"    .reset_index())\n"
"plt.figure(figsize=(12,5))\n"
"sns.lineplot(data=monthly_cleanup, x='month', y='cleanup_event', hue='profile')\n"
"plt.xticks(rotation=45, ha='right')\n"
"plt.title('Monthly Cleanup Event Rate by Profile')\n"
"plt.show()"
))

cells.append(nbf.v4.new_markdown_cell("## Correlation heatmap"))

cells.append(nbf.v4.new_code_cell(
"cols = ['used_gb','free_gb','used_pct','photos_gb','videos_gb','apps_gb','documents_gb','system_gb','other_gb','daily_delta_gb','cleanup_event']\n"
"corr = df[cols].corr(numeric_only=True)\n"
"plt.figure(figsize=(10,8))\n"
"sns.heatmap(corr, cmap='coolwarm', center=0)\n"
"plt.title('Correlation Heatmap')\n"
"plt.show()"
))

cells.append(nbf.v4.new_markdown_cell(
"## Forecasting takeaways\n"
"- A single global linear model is too simple for these different profile behaviors.\n"
"- Lag features like yesterday, 7-day, and 30-day used storage should be helpful.\n"
"- Cleanup events create abrupt drops, which simple trend models miss.\n"
"- Profile-aware models or profile-specific models are likely to perform better.\n"
"- Prophet and XGBoost are strong next candidates for comparison."
))

nb['cells'] = cells
nb['metadata'] = {
    'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
    'language_info': {'name': 'python', 'version': '3.x'}
}

out_path = Path('/home/user/storage_forecaster_v2/notebooks/01_eda.ipynb')
out_path.parent.mkdir(parents=True, exist_ok=True)
with out_path.open('w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f'Created notebook at {out_path}')
