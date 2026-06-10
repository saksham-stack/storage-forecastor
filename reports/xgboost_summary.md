# XGBoost Results

Direct multi-horizon XGBoost forecasting using lag, rolling, calendar, state, and profile features.

|     mae |    rmse |     mape | model          |   horizon_days |   train_rows |   test_rows |
|--------:|--------:|---------:|:---------------|---------------:|-------------:|------------:|
| 19.631  | 42.3032 |  9.50685 | xgboost_direct |             30 |        12480 |        3840 |
| 24.8166 | 51.3152 | 12.1856  | xgboost_direct |             60 |        10560 |        4800 |
| 25.2648 | 47.8979 | 14.1117  | xgboost_direct |             90 |         8640 |        5760 |