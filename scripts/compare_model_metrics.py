from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

REPORTS_DIR = Path('reports')
FIG_DIR = REPORTS_DIR / 'figures'
METRIC_FILES = [
    REPORTS_DIR / 'baseline_v2_metrics.csv',
    REPORTS_DIR / 'prophet_metrics.csv',
    REPORTS_DIR / 'xgboost_metrics.csv',
]


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    frames = [pd.read_csv(path) for path in METRIC_FILES if path.exists()]
    if not frames:
        raise FileNotFoundError('No metrics files found in reports/.')
    df = pd.concat(frames, ignore_index=True)

    plot_df = df.melt(id_vars=['model', 'horizon_days'], value_vars=['mae', 'rmse', 'mape'], var_name='metric', value_name='value')
    sns.set_theme(style='whitegrid')
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    for i, metric in enumerate(['mae', 'rmse', 'mape']):
        ax = axes[i]
        sub = plot_df[plot_df['metric'] == metric]
        sns.barplot(data=sub, x='horizon_days', y='value', hue='model', ax=ax)
        ax.set_title(metric.upper())
        ax.set_xlabel('Forecast horizon (days)')
        ax.set_ylabel(metric.upper())
        if i > 0:
            ax.get_legend().remove()
    axes[0].legend(title='Model')
    plt.tight_layout()
    fig_path = FIG_DIR / 'model_comparison_metrics.png'
    plt.savefig(fig_path, dpi=140, bbox_inches='tight')
    plt.close()

    best_by_mae = df.loc[df.groupby('horizon_days')['mae'].idxmin(), ['horizon_days', 'model', 'mae']]
    summary_lines = ['# Model Comparison', '', df.to_markdown(index=False), '', '## Lowest-MAE model by horizon', '', best_by_mae.to_markdown(index=False)]
    (REPORTS_DIR / 'model_comparison_summary.md').write_text('\n'.join(summary_lines), encoding='utf-8')

    print('Saved comparison figure to:', fig_path)
    print(df.to_string(index=False))


if __name__ == '__main__':
    main()
