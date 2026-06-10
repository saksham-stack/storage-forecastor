import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
from pathlib import Path

DATA_PATH = Path('data/synthetic/synthetic_storage_usage.csv')


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f'Missing dataset: {DATA_PATH}')

    df = pd.read_csv(DATA_PATH)
    df = df.sort_values(['user_id', 'day_index']).copy()

    # Very simple baseline: predict used_gb from day_index per profile
    train = df[df['day_index'] < df['day_index'].max() - 90]
    test = df[df['day_index'] >= df['day_index'].max() - 90]

    X_train = train[['day_index']]
    y_train = train['used_gb']
    X_test = test[['day_index']]
    y_test = test['used_gb']

    model = LinearRegression()
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))

    print('Baseline model complete')
    print(f'MAE:  {mae:.3f}')
    print(f'RMSE: {rmse:.3f}')


if __name__ == '__main__':
    main()
