from pathlib import Path
import pandas as pd


def load_synthetic_data(path: str = 'data/synthetic/synthetic_storage_usage.csv') -> pd.DataFrame:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f'Dataset not found: {csv_path}')
    return pd.read_csv(csv_path, parse_dates=['date'])
