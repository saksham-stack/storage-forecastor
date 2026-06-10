# Baseline V2 Results

Direct multi-horizon Ridge regression using lag/rolling/time/profile features.

|     mae |    rmse |    mape | model             |   horizon_days |   train_rows |   test_rows |
|--------:|--------:|--------:|:------------------|---------------:|-------------:|------------:|
| 19.3256 | 35.8019 | 11.0338 | baseline_v2_ridge |             30 |        12480 |        3840 |
| 28.2714 | 47.4837 | 18.345  | baseline_v2_ridge |             60 |        10560 |        4800 |
| 40.7252 | 70.0969 | 30.3951 | baseline_v2_ridge |             90 |         8640 |        5760 |