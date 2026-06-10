# Synthetic Data Generator Patch Validation

## Files updated
- `scripts/generate_synthetic_data.py`
- `scripts/visualize_data.py`

## Why the patch was needed
The previous EDA showed unrealistic behavior, especially for the `gamer` profile, whose average `used_pct` was **177.280%**, which is physically impossible for a storage device.

## Validation after patch
After regenerating the dataset and rerunning the pipeline:
- Output dataset path is now `data/synthetic/synthetic_storage_usage.csv`
- Rows generated: **17,280**
- Users: **32**
- Profiles: **4**
- Date range: **2024-01-01** to **2025-06-23**
- Maximum `used_pct`: **90.401%**
- Minimum `free_gb`: **12.287 GB**

## Updated profile summary
| profile | users | avg_capacity_gb | avg_used_gb | avg_used_pct | avg_daily_delta_gb | cleanup_rate |
|---|---:|---:|---:|---:|---:|---:|
| media_heavy | 8 | 320.000 | 177.052 | 59.491 | 0.215 | 0.011 |
| gamer | 8 | 672.000 | 275.651 | 40.224 | 0.215 | 0.019 |
| office_user | 8 | 336.000 | 88.442 | 33.266 | 0.086 | 0.002 |
| cleaner | 8 | 224.000 | 47.807 | 22.730 | -0.015 | 0.062 |

## Model sanity check
The simple baseline model still runs successfully after the patch.
