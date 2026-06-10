# CSV Template Instructions

## Quick Start

1. **Download the template**: `storage_data_template.csv` from `data/` folder
2. **Open in Excel or Google Sheets**
3. **Replace the example data** with your actual device storage data
4. **Save as CSV** (File → Save As → CSV format)
5. **Upload to the app** in the "Forecast Lab" tab

---

## What's in the Template?

The template includes:
- ✅ All 16 required columns in correct order
- ✅ 31 days (January 2024) of example data
- ✅ One example device (device_001) with media_heavy profile
- ✅ Realistic daily storage growth patterns
- ✅ All calculations pre-formatted

You can:
- **Keep this data** to test the app
- **Replace with your data** by editing each cell
- **Copy/paste your own rows** below the existing rows
- **Duplicate for multiple devices** (change user_id)

---

## Step-by-Step Instructions

### Step 1: Download & Open the Template

**Option A: From GitHub/Project Folder**
```
data/storage_data_template.csv
```

**Option B: From Streamlit App** (coming soon - download feature)
- Go to "Forecast Lab" tab
- Click "Download template" button (if available)

**Option C: Create Manually**
- Create new Excel/Google Sheet
- Copy headers from below
- Add your data rows

### Step 2: Edit the Data

#### Change the Device ID and Profile (Columns A & B)
```
OLD:  device_001, media_heavy
NEW:  my_phone, media_heavy
      your_device, gamer
      server_01, office_user
```

#### Enter Your Dates (Column C)
```
OLD:  2024-01-01, 2024-01-02, ...
NEW:  2024-03-15, 2024-03-16, ...
      (your actual dates in YYYY-MM-DD format)
```

#### Update Storage Values (Columns E-F)
```
OLD:  total_capacity_gb: 512.0, used_gb: 147.14
NEW:  total_capacity_gb: 256.0, used_gb: 198.5
      (your actual device capacity and current usage)
```

#### Fill in Component Breakdown (Columns I-N)
```
photos_gb, videos_gb, apps_gb, documents_gb, system_gb, other_gb

Example for a phone with 198.5 GB used:
photos_gb:      50.0 GB
videos_gb:      80.0 GB
apps_gb:        40.0 GB
documents_gb:   15.0 GB
system_gb:      10.0 GB
other_gb:        3.5 GB
TOTAL:         198.5 GB ✓
```

#### Enter Daily Changes (Column O)
```
daily_delta_gb: How much storage used changed each day

Example:
Day 1: +0.5 GB (grew by 500 MB)
Day 2: +0.3 GB (grew by 300 MB)
Day 3: -5.0 GB (cleanup happened, freed 5 GB)
Day 4: +0.2 GB (small growth)
```

#### Mark Cleanup Events (Column P)
```
cleanup_event: 0 = no cleanup, 1 = cleanup happened

Example:
Days 1-2: 0 (normal usage)
Day 3:    1 (user cleaned storage)
Days 4+:  0 (back to normal)
```

### Step 3: Update Calculated Columns

The template automatically calculates some columns. Update these:

**Column D: day_index**
- For each user, restart at 0
- Increment by 1 each day
- Example: 0, 1, 2, 3, 4, 5...

**Column G: free_gb**
- Formula: `free_gb = total_capacity_gb - used_gb`
- Excel: `=E2-F2` (then copy down)

**Column H: used_pct**
- Formula: `used_pct = (used_gb / total_capacity_gb) * 100`
- Excel: `=F2/E2*100` (then copy down)

### Step 4: Verify Your Data

Check these before uploading:

```
☐ 16 columns with correct headers
☐ Dates in YYYY-MM-DD format
☐ date values are consecutive (no gaps)
☐ day_index starts at 0 for each user
☐ total_capacity_gb is positive
☐ used_gb ≤ total_capacity_gb
☐ free_gb = total_capacity_gb - used_gb
☐ used_pct = (used_gb/total_capacity_gb)*100
☐ Component sum ≈ used_gb
☐ cleanup_event is 0 or 1
☐ At least 7 rows of data (1 week minimum)
☐ No empty cells
☐ No extra columns or rows
```

### Step 5: Save as CSV

**In Excel:**
1. Click "File" → "Save As"
2. Choose "CSV (Comma delimited) (*.csv)"
3. Click "Save"
4. Say "Yes" when asked about compatibility

**In Google Sheets:**
1. Click "File" → "Download" → "Comma-separated values (.csv)"
2. File downloads as `.csv`

**In Numbers (Mac):**
1. Click "File" → "Export To" → "CSV..."
2. Click "Export"

### Step 6: Upload to the App

1. Open Streamlit app
2. Go to **"Forecast Lab"** tab
3. Click **"Upload CSV"** radio button
4. Click **"Upload a CSV..."** button
5. Select your CSV file
6. App validates the data
7. Run the forecast!

---

## Example Workflows

### Scenario 1: One Month of iPhone Data

1. **Get your iPhone storage info:**
   - Settings → General → iPhone Storage
   - Note: Total capacity, Used space, Available space
   - Screenshot the storage breakdown by app/category

2. **Create spreadsheet:**
   - Row 1: Headers (use template)
   - Rows 2-32: 31 days of data (Jan 2024)
   - Fill columns with your data
   - Calculate: free_gb, used_pct from formulas

3. **Example values for iPhone 256GB with 198 GB used:**
   ```
   user_id: my_iphone
   profile: media_heavy
   date: 2024-01-01
   total_capacity_gb: 256.0
   used_gb: 198.0
   photos_gb: 50.0
   videos_gb: 80.0
   apps_gb: 40.0
   documents_gb: 15.0
   system_gb: 10.0
   other_gb: 3.0
   ```

4. **Save & upload** to the app

### Scenario 2: Multiple Devices (Phone + Laptop)

1. **Create two separate sections:**
   ```
   Rows 1-32: Device 1 (Phone) - user_id: iphone_01
   Rows 33-62: Device 2 (Laptop) - user_id: macbook_01
   ```

2. **For each device:**
   - Set unique user_id
   - Set appropriate profile (media_heavy, gamer, office_user, cleaner)
   - Fill in their storage values
   - Start day_index at 0 for each device

3. **Save & upload** - app will forecast for both

### Scenario 3: Historical Data (3+ Months)

1. **Collect historical snapshots:**
   - Export from monitoring tool
   - Gather from backup records
   - Reconstruct from backups/archives

2. **Format each day:**
   - One row per day per device
   - Fill all 16 columns
   - Ensure calculations match

3. **Upload longer history:**
   - More data = more accurate forecasts
   - 30-90 days optimal
   - Can use 180+ days

---

## Tips for Best Results

### ✅ Data Quality
- **Real data is better than estimates**
  - Use actual snapshots over estimations
  - Collect daily for most accuracy
  - More data = better forecasts (30+ days recommended)

### ✅ Component Breakdown
- **Be as detailed as possible**
  - Break down all storage categories
  - Don't leave large amounts in "other"
  - Get details from your device settings

### ✅ Cleanup Events
- **Mark cleanup events accurately**
  - Set cleanup_event = 1 when you manually cleaned
  - Model learns your cleanup patterns
  - Important for accurate forecasts

### ✅ Device Profile
- **Choose the right profile:**
  - media_heavy: Lots of photos/videos
  - gamer: Large games installed
  - office_user: Documents and work files
  - cleaner: Periodic manual cleanups
  - custom: Any other profile name

### ✅ Consistency
- **Collect consistently**
  - Same time each day (if possible)
  - Same measurement method
  - Helps model learn patterns

---

## Formulas Reference

If you need to create formulas in Excel/Sheets:

### Free GB Calculation
```
Excel: =E2-F2
Google Sheets: =E2-F2
```
Where E = total_capacity_gb, F = used_gb

### Used Percentage Calculation
```
Excel: =ROUND(F2/E2*100, 2)
Google Sheets: =ROUND(F2/E2*100, 2)
```

### Sum of Components
```
Excel: =I2+J2+K2+L2+M2+N2
Google Sheets: =I2+J2+K2+L2+M2+N2
```
Where I-N = the six component columns

### Daily Delta Calculation
```
Excel: =IF(ROW()=2, 0, F2-F1)
Google Sheets: =IF(ROW()=2, 0, F2-F1)
```
(0 for first row, otherwise difference from previous day)

---

## Common Template Issues

### Error: "Date format invalid"
**Problem:** Dates not in YYYY-MM-DD format
**Solution:** Convert all dates to YYYY-MM-DD
- Not: 01/01/2024 or January 1, 2024
- Yes: 2024-01-01

### Error: "Missing column"
**Problem:** A column header is misspelled or missing
**Solution:** Check all 16 headers match exactly:
```
user_id,profile,date,day_index,total_capacity_gb,used_gb,free_gb,used_pct,photos_gb,videos_gb,apps_gb,documents_gb,system_gb,other_gb,daily_delta_gb,cleanup_event
```

### Error: "Values don't match calculations"
**Problem:** free_gb or used_pct don't calculate correctly
**Solution:** Verify formulas:
- free_gb = total_capacity_gb - used_gb
- used_pct = (used_gb / total_capacity_gb) * 100

### Error: "Less than 7 rows"
**Problem:** Not enough data
**Solution:** Add more rows (at least 7 days, ideally 30-90)

### Error: "Components don't sum to used_gb"
**Problem:** Storage categories don't add up
**Solution:** Ensure: photos + videos + apps + documents + system + other = used_gb

---

## Data Collection Tools

### For Smartphones
- **iPhone**: Built-in Settings → Storage
- **Android**: Built-in Settings → Storage
- **Apps**: Storage Monitor apps from app store

### For Computers
- **Windows**: Built-in Settings → Storage (or WizTree)
- **Mac**: Disk Diag, DiskSight, or built-in System Settings
- **Linux**: `du -sh *` command or filelight GUI

### For Servers/Cloud
- **AWS**: CloudWatch metrics
- **Google Cloud**: Monitoring dashboard
- **Azure**: Azure Monitor
- **On-prem**: Prometheus, Grafana, or custom scripts

---

## Advanced: Python Helper Script

```python
import pandas as pd
from datetime import datetime, timedelta

# Create template data
def create_csv_template(
    user_id: str,
    profile: str,
    start_date: str,  # YYYY-MM-DD
    days: int,
    total_capacity_gb: float,
    starting_used_gb: float,
    daily_growth_gb: float = 0.5
):
    data = []
    
    start = datetime.strptime(start_date, "%Y-%m-%d")
    
    for i in range(days):
        date = start + timedelta(days=i)
        used_gb = starting_used_gb + (i * daily_growth_gb)
        used_gb = min(used_gb, total_capacity_gb * 0.95)  # Cap at 95%
        
        data.append({
            'user_id': user_id,
            'profile': profile,
            'date': date.strftime("%Y-%m-%d"),
            'day_index': i,
            'total_capacity_gb': total_capacity_gb,
            'used_gb': round(used_gb, 2),
            'free_gb': round(total_capacity_gb - used_gb, 2),
            'used_pct': round((used_gb / total_capacity_gb) * 100, 2),
            'photos_gb': round(used_gb * 0.3, 2),
            'videos_gb': round(used_gb * 0.35, 2),
            'apps_gb': round(used_gb * 0.2, 2),
            'documents_gb': round(used_gb * 0.08, 2),
            'system_gb': round(used_gb * 0.05, 2),
            'other_gb': round(used_gb * 0.02, 2),
            'daily_delta_gb': 0.0 if i == 0 else round(daily_growth_gb, 2),
            'cleanup_event': 1 if i % 14 == 0 and i > 0 else 0
        })
    
    df = pd.DataFrame(data)
    df.to_csv('my_storage_data.csv', index=False)
    print(f"Created {len(df)} rows")
    return df

# Example usage:
create_csv_template(
    user_id='my_phone',
    profile='media_heavy',
    start_date='2024-01-01',
    days=30,
    total_capacity_gb=256.0,
    starting_used_gb=150.0,
    daily_growth_gb=0.5
)
```

---

## Questions?

- **CSV format details**: See `CSV_DATA_GUIDE.md`
- **App won't accept my file**: Check "Common Template Issues" above
- **Need more examples**: See template file `storage_data_template.csv`
- **Technical help**: Check app's "Help" section or documentation

---

**Happy forecasting! 🚀**
