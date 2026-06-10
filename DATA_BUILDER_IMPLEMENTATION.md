# 🛠️ Data Builder Implementation Guide

## Overview

The **Data Builder** feature in the Streamlit dashboard makes it easy for users to:
1. See example storage data
2. Generate custom CSV templates
3. Download pre-filled sample data

This document explains how it works and how to maintain/extend it.

---

## Architecture

### Location
- **Main code:** `dashboard/app.py` (lines ~160-230)
- **Tab position:** 2nd tab in main tabs (after Overview)

### Components

```
data_builder_tab
├── Mode Selection (Radio button)
│   ├── 📊 See Example Data
│   ├── 🔨 Generate Template
│   └── 📥 Download Real Example
└── Implementation for each mode
```

---

## Code Structure

### Main Tab Creation
```python
overview_tab, data_builder_tab, forecast_tab, benchmark_tab, reviews_tab = st.tabs(
    ['Overview', 'Data Builder', 'Forecast Lab', 'Model Benchmarks', 'Reviews & Deploy']
)
```

### Inside `with data_builder_tab:`

#### Mode 1: See Example Data
```python
if builder_mode == '📊 See Example Data':
    # Read template
    example_df = pd.read_csv(ROOT / 'data' / 'storage_data_template.csv')
    
    # Display preview (15 rows)
    st.dataframe(example_df.head(15), use_container_width=True)
    
    # Show column meanings
    col_info = {
        'user_id': 'Your device ID (e.g., "my_phone_001")',
        'profile': 'Device type (e.g., "heavy_user", "light_user")',
        # ... more columns ...
    }
```

**Key Files:**
- Input: `data/storage_data_template.csv`
- Output: Visual display only

---

#### Mode 2: Generate Template
```python
elif builder_mode == '🔨 Generate Template':
    # User inputs
    device_id = st.text_input('Device ID', ...)
    days_of_data = st.number_input('Days of data', min_value=7, ...)
    profile = st.text_input('Device profile', ...)
    capacity = st.number_input('Storage capacity (GB)', ...)
    start_date = st.date_input('Start date', ...)
    
    # Template generation
    dates = pd.date_range(start=start_date, periods=int(days_of_data), freq='D')
    template_data = {
        'user_id': [device_id] * len(dates),
        'profile': [profile] * len(dates),
        'date': dates.strftime('%Y-%m-%d'),
        'day_index': range(len(dates)),
        'total_capacity_gb': [float(capacity)] * len(dates),
        # ... 11 more columns (all initialized to 0.0) ...
    }
    template_df = pd.DataFrame(template_data)
    
    # Download button
    st.download_button(
        label=f'📥 Download template ({len(template_df)} rows)',
        data=template_df.to_csv(index=False),
        file_name=f'storage_data_{device_id}_{start_date.strftime("%Y%m%d")}.csv',
        mime='text/csv',
    )
```

**Key Features:**
- Dynamic date generation
- All 16 columns present
- Automatic numbering (day_index)
- Pre-calculated free_gb and used_pct (as 0.0)

**Required Columns:**
```python
REQUIRED_UPLOAD_COLUMNS = [
    'user_id', 'profile', 'date', 'day_index', 
    'total_capacity_gb', 'used_gb', 'free_gb', 'used_pct',
    'photos_gb', 'videos_gb', 'apps_gb', 'documents_gb', 
    'system_gb', 'other_gb', 'daily_delta_gb', 'cleanup_event'
]
```

---

#### Mode 3: Download Real Example
```python
else:  # Download Real Example
    example_df = pd.read_csv(ROOT / 'data' / 'storage_data_template.csv')
    example_csv = example_df.to_csv(index=False)
    
    st.download_button(
        label='📥 Download example CSV',
        data=example_csv,
        file_name='storage_data_example.csv',
        mime='text/csv',
    )
```

**Key Files:**
- Input: `data/storage_data_template.csv`
- Output: CSV download

---

## File Dependencies

### Required Files
```
data/
└── storage_data_template.csv    # Example data (33 rows, device_001)
```

### Generated Files (Runtime)
- User downloads (not stored):
  - `storage_data_template.csv` (from Method 1 & 3)
  - `storage_data_{device_id}_{date}.csv` (from Method 2)

---

## Data Flow

```
User Request
    │
    ├─ Method 1: View Example
    │   └─→ Read storage_data_template.csv
    │       └─→ Display preview + column info
    │
    ├─ Method 2: Generate Template
    │   ├─→ Collect user inputs (form)
    │   ├─→ Generate dates
    │   ├─→ Create DataFrame with all columns
    │   └─→ Download button → to user's computer
    │
    └─ Method 3: Download Real Example
        └─→ Read storage_data_template.csv
            └─→ Download button → to user's computer

User's Computer
    │
    └─→ CSV file
        └─→ Opens in Excel/Sheets
            └─→ User fills in actual numbers
                └─→ User uploads to Forecast Lab
                    └─→ Predictions! 🎉
```

---

## Testing

### Test Mode 1: See Example Data
```python
# Should display:
# - 15 rows of sample data
# - All 16 columns visible
# - Column descriptions (16 items)
```

**Test:**
1. Click "Data Builder" tab
2. Select "📊 See Example Data"
3. Verify data displays correctly
4. Verify column meanings are clear

---

### Test Mode 2: Generate Template
```python
# Should create:
# - DataFrame with specified days
# - All columns present (16 total)
# - Dates correctly sequenced
# - Download button works
```

**Test:**
```python
device_id = "test_device"
days = 14
profile = "heavy_user"
capacity = 256
start_date = 2024-01-01

# Expected output:
# - 14 rows
# - day_index: 0-13
# - dates: 2024-01-01 to 2024-01-14
# - all GB columns = 0.0
# - filename: storage_data_test_device_20240101.csv
```

**Test:**
1. Click "Data Builder" tab
2. Select "🔨 Generate Template"
3. Enter test values
4. Click "Generate blank template"
5. Verify CSV shows correct structure
6. Download and verify file
7. Open in Excel - all columns present?

---

### Test Mode 3: Download Real Example
```python
# Should provide:
# - storage_data_example.csv
# - 31 rows (one month)
# - Realistic data values
# - Download works
```

**Test:**
1. Click "Data Builder" tab
2. Select "📥 Download Real Example"
3. Click download button
4. Verify file downloads
5. Open in Excel - is data realistic?

---

## Validation (Forecast Lab)

When users upload from Data Builder, the Forecast Lab validates:

```python
# In forecast_tab upload section:

uploaded_df = pd.read_csv(uploaded)

# Check 1: All columns present
missing_cols = [c for c in REQUIRED_UPLOAD_COLUMNS if c not in uploaded_df.columns]
if missing_cols:
    st.error(f'Missing required columns: {", ".join(missing_cols)}')

# Check 2: Row count
if len(uploaded_df) < 7:
    st.error(f'Need at least 7 days; you have {len(uploaded_df)} rows')

# Check 3: Date format
uploaded_df['date'] = pd.to_datetime(uploaded_df['date'])

# Check 4: Numeric columns
# ... check for negative values ...

# Check 5: Data integrity
if (uploaded_df['used_gb'] > uploaded_df['total_capacity_gb']).any():
    st.error('found rows where used_gb > capacity_gb')
```

---

## Extending the Feature

### Add New Generation Method

Example: Generate template with trend
```python
elif builder_mode == '📈 Generate with Trend':
    # New method: generate template with increasing storage usage
    
    daily_growth = st.number_input('Daily growth (GB)', 0.5)
    
    used_values = [capacity * 0.2 + (i * daily_growth) for i in range(days)]
    
    # Create template with trend
    template_data = {
        'used_gb': used_values,
        'free_gb': [capacity - u for u in used_values],
        'used_pct': [100 * u / capacity for u in used_values],
        # ... other columns ...
    }
```

### Add Column Help Text

```python
# Show field descriptions while filling form
device_id = st.text_input(
    'Device ID', 
    value='my_device_001',
    help='Unique identifier for your device (e.g., "Samsung_S23", "iPhone_Pro")'
)

days_of_data = st.number_input(
    'Days of data you have',
    min_value=7,
    max_value=365,
    value=30,
    help='More days = better forecasts. Minimum 7 days required.'
)
```

### Add CSV Validation Preview

```python
# After generating template, show validation
if generated_template is not None:
    st.success('✅ Template generated!')
    
    # Preview
    st.dataframe(generated_template.head())
    
    # Stats
    col1, col2, col3 = st.columns(3)
    col1.metric('Rows', len(generated_template))
    col2.metric('Date range', f"{days_of_data} days")
    col3.metric('Columns', 16)
```

---

## Troubleshooting

### Issue: Template generation is slow
**Solution:** Use vectorized operations (already done with list comprehensions)

### Issue: Dates are off by one day
**Solution:** Check `pd.date_range()` - it's inclusive on both ends
```python
dates = pd.date_range(start=start_date, periods=days, freq='D')
# This creates exactly `days` dates starting from start_date
```

### Issue: Download button doesn't work
**Solution:** Check:
1. `mime='text/csv'` is correct
2. `data` parameter is CSV string (use `.to_csv(index=False)`)
3. Button key is unique (use `key='download_gen_template'`)

### Issue: Column order is wrong
**Solution:** DataFrame preserves dict order (Python 3.7+), but to be safe:
```python
df = pd.DataFrame(template_data)
df = df[REQUIRED_UPLOAD_COLUMNS]  # Reorder explicitly
```

---

## Maintenance

### Regular Checks
- [ ] Verify `data/storage_data_template.csv` still exists
- [ ] Check template has realistic example data
- [ ] Ensure all 16 columns are present
- [ ] Test all three methods monthly

### Updates to Consider
- Add more profile types to dropdown
- Provide pre-filled templates for common devices
- Add capacity presets (common device sizes)
- Create multiple example files

---

## Files Reference

### Code Files
- `dashboard/app.py` - Main implementation (lines ~150-230)

### Data Files
- `data/storage_data_template.csv` - Example data

### Documentation Files
- `DATA_BUILDER_GUIDE.md` - User guide (detailed)
- `DATA_BUILDER_GUIDE.html` - Visual guide (browser-friendly)
- `CSV_QUICK_START.md` - Quick reference
- `DATA_BUILDER_FLOW.md` - Flow diagrams
- `DATA_BUILDER_IMPROVEMENTS.md` - Overview of changes

### Related Code
- `src/features/build_features.py` - Feature engineering (used in Forecast Lab)
- `src/evaluation/metrics.py` - Validation utilities

---

## Performance

### Generation Speed
- Template generation: < 100ms (even for 365 days)
- File download: Instant (handled by Streamlit)
- CSV size: ~15KB for 30 days

### Memory Usage
- Each template: ~1-2 MB for 365 days
- No persistent storage (downloads only)
- No database queries

---

## Security

### Input Validation
- Device ID: Text (no SQL injection risk)
- Days: Integer with min/max bounds
- Profile: Text input
- Capacity: Float with min/max bounds
- Date: Date widget (safe)

### Data Handling
- No user data stored permanently
- Files created on-demand, not saved
- Download triggers client-side save

---

## Summary

The Data Builder feature provides:
✅ Easy example viewing
✅ Quick template generation
✅ Sample data download
✅ Minimal code complexity
✅ User-friendly UI
✅ All in one tab

Maintain it by:
- Keeping template file up-to-date
- Testing methods monthly
- Monitoring user feedback
- Updating docs as needed
