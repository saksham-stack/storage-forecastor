# Model Comparison

|     mae |    rmse |     mape | model             |   horizon_days |   train_rows |   test_rows |   train_rows_per_user |
|--------:|--------:|---------:|:------------------|---------------:|-------------:|------------:|----------------------:|
| 19.3256 | 35.8019 | 11.0338  | baseline_v2_ridge |             30 |        12480 |        3840 |                   nan |
| 28.2714 | 47.4837 | 18.345   | baseline_v2_ridge |             60 |        10560 |        4800 |                   nan |
| 40.7252 | 70.0969 | 30.3951  | baseline_v2_ridge |             90 |         8640 |        5760 |                   nan |
| 17.366  | 31.2555 |  9.78051 | prophet_per_user  |             30 |          nan |         960 |                   450 |
| 28.7745 | 53.9266 | 15.1967  | prophet_per_user  |             60 |          nan |        1920 |                   450 |
| 38.59   | 76.2224 | 19.0724  | prophet_per_user  |             90 |          nan |        2880 |                   450 |
| 19.2854 | 41.9007 |  9.41045 | xgboost_direct    |             30 |        12480 |        3840 |                   nan |
| 24.4786 | 50.3193 | 12.1666  | xgboost_direct    |             60 |        10560 |        4800 |                   nan |
| 25.7917 | 48.4473 | 14.1423  | xgboost_direct    |             90 |         8640 |        5760 |                   nan |

## Lowest-MAE model by horizon

|   horizon_days | model            |     mae |
|---------------:|:-----------------|--------:|
|             30 | prophet_per_user | 17.366  |
|             60 | xgboost_direct   | 24.4786 |
|             90 | xgboost_direct   | 25.7917 |