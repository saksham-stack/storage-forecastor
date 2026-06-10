# Prophet Results

Per-user Prophet forecasting on the final 90 days of each user time series.

|     mae |    rmse |     mape | model            |   horizon_days |   train_rows_per_user |   test_rows |
|--------:|--------:|---------:|:-----------------|---------------:|----------------------:|------------:|
| 17.366  | 31.2555 |  9.78051 | prophet_per_user |             30 |                   450 |         960 |
| 28.7745 | 53.9266 | 15.1967  | prophet_per_user |             60 |                   450 |        1920 |
| 38.59   | 76.2224 | 19.0724  | prophet_per_user |             90 |                   450 |        2880 |