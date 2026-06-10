from src.evaluation.metrics import regression_metrics


def test_regression_metrics_keys():
    result = regression_metrics([1, 2, 3], [1, 2, 3])
    assert set(result.keys()) == {'mae', 'rmse', 'mape'}
