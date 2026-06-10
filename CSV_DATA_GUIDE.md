# CSV Data Format Guide for Storage Forecaster

## Overview

This guide explains the **CSV file format** required for uploading your own device storage data to the Storage Forecaster app.

---

## Required CSV Columns

Your CSV file must contain exactly these 16 columns in this order:

| # | Column Name | Type | Description | Example |
|---|------------|------|-------------|---------|
| 1 | `user_id` | String | Unique identifier for the device/user | "U001", "device_001" |
| 2 | `profile` | String | Device profile/category | "media_heavy", "gamer", "office_user" |
| 3 | `date` | Date | Measurement date (YYYY-MM-DD format) | "2024-01-01" |
| 4 | `day_index` | Integer | Sequential day number starting from 0 | 0, 1, 2, 3... |
| 5 | `total_capacity_gb` | Float | Total device storage capacity in GB | 256.0, 512.0, 1024.0 |
| 6 | `used_gb` | Float | Currently used storage in GB | 147.14, 256.32 |
| 7 | `free_gb` | Float | Free available storage in GB | 364.86, 256.68 |
| 8 | `used_pct` | Float | Percentage of storage used (0-100) | 28.74, 50.2 |
| 9 | `photos_gb` | Float | Storage used by photos in GB | 41.43, 25.5 |
| 10 | `videos_gb` | Float | Storage used by videos in GB | 33.68, 45.2 |
| 11 | `apps_gb` | Float | Storage used by apps in GB | 24.88, 30.1 |
| 12 | `documents_gb` | Float | Storage used by documents in GB | 8.50, 15.3 |
| 13 | `system_gb` | Float | Storage used by system files in GB | 25.10, 40.0 |
| 14 | `other_gb` | Float | Other storage usage in GB | 13.54, 20.1 |
| 15 | `daily_delta_gb` | Float | Daily change in used storage (GB) | 0.44, -2.5 |
| 16 | `cleanup_event` | Integer | Whether a cleanup occurred (0 or 1) | 0, 1 |

---

## Data Format Details

### Column Definitions & Constraints

#### `user_id` (String)
- **Purpose**: Identifies the device/user uniquely
- **Format**: Any text identifier (recommend "U001", "device_001", etc.)
- **Example Values**: "U001", "U002", "My_Phone", "Device_ABC"
- **Requirement**: Must be the same for all rows from the same device

#### `profile` (String)
- **Purpose**: Categorize the device type
- **Format**: Text describing device profile
- **Suggested Values**: 
  - "media_heavy" (for photo/video heavy users)
  - "gamer" (for game-heavy users)
  - "office_user" (for document-heavy users)
  - "cleaner" (for users with periodic cleanups)
- **Custom Values**: You can use any label

#### `date` (Date)
- **Format**: YYYY-MM-DD (ISO format)
- **Examples**: "2024-01-01", "2024-12-31"
- **Must Be**: Sequential dates, one entry per day per user
- **Range**: Any date range (can be past, present, or projected)

#### `day_index` (Integer)
- **Purpose**: Sequential counter for model features
- **Format**: Integer starting from 0
- **Example**: 0, 1, 2, 3... for first device, then restart at 0 for next device
- **Calculation**: `day_index = (date - first_date).days` for each user

#### `total_capacity_gb` (Float)
- **Format**: Decimal number
- **Range**: Typically 64, 128, 256, 512, 1024+ GB
- **Must Be**: Same for all rows of same device (or adjust if device storage changed)
- **Example**: 256.0, 512.0, 1024.0

#### `used_gb` (Float)
- **Format**: Decimal number
- **Must Be**: Always >= 0 and <= `total_capacity_gb`
- **Constraint**: `used_gb = photos_gb + videos_gb + apps_gb + documents_gb + system_gb + other_gb`
- **Example**: 147.14, 256.32, 512.0

#### `free_gb` (Float)
- **Format**: Decimal number
- **Calculation**: `free_gb = total_capacity_gb - used_gb`
- **Example**: 364.86, 256.68

#### `used_pct` (Float)
- **Format**: Percentage (0-100)
- **Calculation**: `used_pct = (used_gb / total_capacity_gb) * 100`
- **Range**: 0.0 to 100.0
- **Example**: 28.74, 50.2, 95.5

#### Storage Components (photos_gb, videos_gb, apps_gb, documents_gb, system_gb, other_gb)
- **Format**: All decimals
- **Must Be**: >= 0
- **Sum Requirement**: All 6 components must sum to `used_gb`
- **Accuracy**: More accurate breakdown = better forecasts

#### `daily_delta_gb` (Float)
- **Format**: Decimal (can be negative)
- **Purpose**: Daily storage change for trend detection
- **Calculation**: `daily_delta_gb = used_gb[today] - used_gb[yesterday]`
- **Range**: Typically -50 to +50 GB
- **Example**: 0.44 (growth), -2.5 (cleanup), 0.0 (no change)

#### `cleanup_event` (Integer)
- **Format**: 0 or 1
- **Meaning**: 1 = cleanup event occurred, 0 = no cleanup
- **Purpose**: Model learns cleanup patterns
- **Example**: 1 (user cleaned storage), 0 (normal day)

---

## CSV Format Specification

### Header Row
```csv
user_id,profile,date,day_index,total_capacity_gb,used_gb,free_gb,used_pct,photos_gb,videos_gb,apps_gb,documents_gb,system_gb,other_gb,daily_delta_gb,cleanup_event
```

### Data Row Example
```csv
U001,media_heavy,2024-01-01,0,512.0,147.14,364.86,28.74,41.43,33.68,24.88,8.50,25.10,13.54,0.0,0
U001,media_heavy,2024-01-02,1,512.0,147.58,364.42,28.82,41.60,33.89,24.90,8.51,25.10,13.57,0.44,0
U001,media_heavy,2024-01-03,2,512.0,148.14,363.86,28.93,41.89,34.10,24.91,8.52,25.11,13.60,0.56,0
```

### Multi-User Example
```csv
user_id,profile,date,day_index,total_capacity_gb,used_gb,free_gb,used_pct,photos_gb,videos_gb,apps_gb,documents_gb,system_gb,other_gb,daily_delta_gb,cleanup_event
U001,media_heavy,2024-01-01,0,512.0,147.14,364.86,28.74,41.43,33.68,24.88,8.50,25.10,13.54,0.0,0
U001,media_heavy,2024-01-02,1,512.0,147.58,364.42,28.82,41.60,33.89,24.90,8.51,25.10,13.57,0.44,0
U002,gamer,2024-01-01,0,256.0,200.50,55.50,78.32,10.00,120.50,50.00,5.00,10.00,5.00,0.0,0
U002,gamer,2024-01-02,1,256.0,205.20,50.80,80.16,10.20,125.00,51.00,5.10,10.50,5.40,4.7,0
```

---

## Data Validation Rules

Your CSV must pass these checks:

### ✅ Column Requirements
- [x] Exactly 16 columns
- [x] Column headers match exactly (case-sensitive)
- [x] Columns in correct order

### ✅ Data Type Requirements
- [x] `user_id`: String (no numbers only)
- [x] `profile`: String
- [x] `date`: YYYY-MM-DD format
- [x] `day_index`: Integer (0, 1, 2...)
- [x] All others: Numeric (decimal allowed)

### ✅ Value Constraints
- [x] `date` values must be valid dates
- [x] `total_capacity_gb` > 0
- [x] `0 <= used_gb <= total_capacity_gb`
- [x] `0 <= used_pct <= 100`
- [x] All GB values >= 0
- [x] `free_gb = total_capacity_gb - used_gb`
- [x] `used_pct = (used_gb / total_capacity_gb) * 100` (approximately)
- [x] Sum of components = `used_gb` (approximately)
- [x] `cleanup_event` is 0 or 1
- [x] Minimum 7 rows per device (1 week of data)
- [x] Ideally 30-90 rows per device (1-3 months)

### ✅ Sequence Requirements
- [x] Dates must be consecutive (one per day)
- [x] `day_index` restarts at 0 for each user
- [x] Data sorted by `user_id`, then `date`

---

## Common Mistakes to Avoid

❌ **WRONG** - Missing columns
```csv
user_id,date,used_gb,total_capacity_gb
```

✅ **RIGHT** - All 16 columns
```csv
user_id,profile,date,day_index,total_capacity_gb,used_gb,free_gb,used_pct,photos_gb,videos_gb,apps_gb,documents_gb,system_gb,other_gb,daily_delta_gb,cleanup_event
```

---

❌ **WRONG** - Wrong date format
```csv
date
01/01/2024
```

✅ **RIGHT** - ISO format
```csv
date
2024-01-01
```

---

❌ **WRONG** - Inconsistent calculations
```csv
total_capacity_gb,used_gb,used_pct
512.0,256.0,75.5
```
(should be 50%, not 75.5%)

✅ **RIGHT** - Consistent calculations
```csv
total_capacity_gb,used_gb,used_pct
512.0,256.0,50.0
```

---

❌ **WRONG** - Components don't sum to used_gb
```csv
used_gb,photos_gb,videos_gb,apps_gb,documents_gb,system_gb,other_gb
100.0,10.0,20.0,30.0,5.0,10.0,20.0
```
(sums to 95.0, not 100.0)

✅ **RIGHT** - Components sum correctly
```csv
used_gb,photos_gb,videos_gb,apps_gb,documents_gb,system_gb,other_gb
100.0,10.0,20.0,30.0,5.0,10.0,25.0
```

---

❌ **WRONG** - Not enough data
```csv
user_id,profile,date,...
U001,media_heavy,2024-01-01,...
U001,media_heavy,2024-01-02,...
```
(only 2 days)

✅ **RIGHT** - Sufficient data
```csv
user_id,profile,date,...
U001,media_heavy,2024-01-01,...
U001,media_heavy,2024-01-02,...
... (at least 30 rows)
U001,media_heavy,2024-01-30,...
```

---

## How to Create Your CSV

### Option 1: From Excel/Google Sheets
1. Create a spreadsheet with the 16 columns
2. Add your data (1 row per day per device)
3. Export as CSV (File → Export → CSV)
4. Upload to the app

### Option 2: From Python
```python
import pandas as pd

data = {
    'user_id': ['U001', 'U001', 'U001'],
    'profile': ['media_heavy', 'media_heavy', 'media_heavy'],
    'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
    'day_index': [0, 1, 2],
    'total_capacity_gb': [512.0, 512.0, 512.0],
    'used_gb': [147.14, 147.58, 148.14],
    'free_gb': [364.86, 364.42, 363.86],
    'used_pct': [28.74, 28.82, 28.93],
    'photos_gb': [41.43, 41.60, 41.89],
    'videos_gb': [33.68, 33.89, 34.10],
    'apps_gb': [24.88, 24.90, 24.91],
    'documents_gb': [8.50, 8.51, 8.52],
    'system_gb': [25.10, 25.10, 25.11],
    'other_gb': [13.54, 13.57, 13.60],
    'daily_delta_gb': [0.0, 0.44, 0.56],
    'cleanup_event': [0, 0, 0]
}

df = pd.DataFrame(data)
df.to_csv('my_storage_data.csv', index=False)
```

### Option 3: From a Template
- Download the template file: `storage_data_template.csv` (see below)
- Fill in with your actual data
- Save and upload

### Option 4: From Real Device Data
If you have device monitoring tools:
1. Export storage data from your monitoring tool
2. Format to match the 16 required columns
3. Calculate missing columns using formulas
4. Upload to app

---

## Getting Real Device Data

### For iPhone/iPad
1. Go to Settings → General → iPhone Storage (or iPad Storage)
2. Note the capacity and used storage
3. Collect daily snapshots and log in a spreadsheet
4. Include category breakdowns (Photos, Apps, Documents, etc.)

### For Android
1. Go to Settings → Storage
2. Note total, used, and free storage
3. Check individual app storage in Settings → Apps
4. Collect storage breakdown by category
5. Log daily in spreadsheet

### For Mac/Windows
1. Use built-in storage tools:
   - Mac: System Settings → General → Storage
   - Windows: Settings → System → Storage
2. Monitor with tools like:
   - DiskSight (Mac)
   - TreeSize (Windows)
   - WinDirStat (Windows)
3. Extract daily data to spreadsheet

### For Server/Cloud Storage
1. Use monitoring tools (CloudWatch, Prometheus, etc.)
2. Export metrics to CSV
3. Map to the 16 required columns
4. Upload to app

---

## CSV File Size Limits

- **Maximum file size**: 50 MB
- **Maximum rows**: 100,000 (about 273 years of daily data)
- **Recommended**: 30-500 rows (1 month to 1.5 years)
- **Optimal**: 60-180 rows (2-6 months)

---

## Example CSV Files

### Example 1: Single Device, 30 Days
```csv
user_id,profile,date,day_index,total_capacity_gb,used_gb,free_gb,used_pct,photos_gb,videos_gb,apps_gb,documents_gb,system_gb,other_gb,daily_delta_gb,cleanup_event
U001,media_heavy,2024-01-01,0,512.0,147.14,364.86,28.74,41.43,33.68,24.88,8.50,25.10,13.54,0.0,0
U001,media_heavy,2024-01-02,1,512.0,147.58,364.42,28.82,41.60,33.89,24.90,8.51,25.10,13.57,0.44,0
U001,media_heavy,2024-01-03,2,512.0,148.14,363.86,28.93,41.89,34.10,24.91,8.52,25.11,13.60,0.56,0
U001,media_heavy,2024-01-04,3,512.0,148.51,363.49,29.01,42.03,34.28,24.94,8.53,25.11,13.61,0.37,0
```

### Example 2: Multiple Devices, 7 Days
```csv
user_id,profile,date,day_index,total_capacity_gb,used_gb,free_gb,used_pct,photos_gb,videos_gb,apps_gb,documents_gb,system_gb,other_gb,daily_delta_gb,cleanup_event
U001,media_heavy,2024-01-01,0,512.0,147.14,364.86,28.74,41.43,33.68,24.88,8.50,25.10,13.54,0.0,0
U001,media_heavy,2024-01-02,1,512.0,147.58,364.42,28.82,41.60,33.89,24.90,8.51,25.10,13.57,0.44,0
U001,media_heavy,2024-01-03,2,512.0,148.14,363.86,28.93,41.89,34.10,24.91,8.52,25.11,13.60,0.56,0
U002,gamer,2024-01-01,0,256.0,200.50,55.50,78.32,10.00,120.50,50.00,5.00,10.00,5.00,0.0,0
U002,gamer,2024-01-02,1,256.0,205.20,50.80,80.16,10.20,125.00,51.00,5.10,10.50,5.40,4.7,0
```

---

## Troubleshooting

### Error: "Missing required columns"
- ✅ Check that all 16 column names are present
- ✅ Check spelling matches exactly (case-sensitive)
- ✅ No extra spaces in column names

### Error: "Date format invalid"
- ✅ Use YYYY-MM-DD format (e.g., 2024-01-31)
- ✅ Not MM/DD/YYYY or other formats

### Error: "used_gb exceeds total_capacity_gb"
- ✅ Ensure `used_gb <= total_capacity_gb`
- ✅ Check total_capacity_gb is correct

### Error: "Insufficient data (less than 7 rows)"
- ✅ Add more days of data
- ✅ Minimum 7 days per device

### Error: "Values don't match expected calculations"
- ✅ Verify: `free_gb = total_capacity_gb - used_gb`
- ✅ Verify: `used_pct = (used_gb / total_capacity_gb) * 100`
- ✅ Verify: sum of GB components ≈ `used_gb`

---

## Questions?

See the full guides:
- [CSV_DATA_GUIDE.md](CSV_DATA_GUIDE.md) (This file)
- [CSV_TEMPLATE_INSTRUCTIONS.md](CSV_TEMPLATE_INSTRUCTIONS.md)
- Access the template: Download from the app's "Forecast Lab" tab

Or check the app's help section in the "Forecast Lab" tab for more details.
