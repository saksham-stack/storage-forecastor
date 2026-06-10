# CSV Preparation Complete Guide

## What Users Need to Know

When users want to upload their own device data to test the XGBoost model, they need to provide a **CSV file** with a specific format. This guide explains everything they need to do.

---

## 📋 What is Required?

### File Format: CSV
- **Name**: Any name (e.g., `my_device.csv`, `device_data.csv`)
- **Type**: CSV (Comma-Separated Values)
- **Size**: Max 50 MB
- **Rows**: Minimum 7 (1 week), recommended 30-90 (1-3 months)

### Data Required: 16 Columns
Exactly these columns in this order:
```
user_id, profile, date, day_index, total_capacity_gb, used_gb, free_gb, used_pct,
photos_gb, videos_gb, apps_gb, documents_gb, system_gb, other_gb, daily_delta_gb, cleanup_event
```

### Minimum Timeline
- **7 days**: Absolute minimum
- **30 days**: Good for testing
- **60+ days**: Best for accurate forecasts

---

## 🚀 How to Get Started (Quick Path)

### Step 1: Download the Template
- **From the app**: Go to "Forecast Lab" tab → Click "Download CSV Template"
- **From project**: Open `data/storage_data_template.csv`
- **File includes**: 31 days of example data with proper format

### Step 2: Edit the Template
Replace the example data with your actual device storage data:
- Change device ID (column A)
- Change dates (column C)
- Update storage values (columns E-N)

### Step 3: Save as CSV
- **In Excel**: File → Save As → CSV (Comma delimited)
- **In Google Sheets**: File → Download → CSV
- **In Numbers**: File → Export To → CSV

### Step 4: Upload to App
- Open Streamlit app
- Go to "Forecast Lab" tab
- Select "Upload CSV"
- Choose your file
- App validates and forecasts!

---

## 📊 Where to Get Your Data

### For Smartphones (iPhone/Android)
1. Go to device settings → Storage
2. Write down or screenshot:
   - Total device capacity
   - Used storage
   - Available space
   - Breakdown by category (Photos, Videos, Apps, Documents, System, Other)
3. Collect this daily for 30+ days
4. Enter into spreadsheet

### For Computers (Mac/Windows)
1. Use built-in storage tools:
   - **Mac**: System Settings → General → Storage
   - **Windows**: Settings → System → Storage
2. Get total, used, free space
3. Get breakdown by category using:
   - Disk analysis tools (TreeSize, DiskSight)
   - File explorer (sort by size)
4. Record daily for 30+ days

### For Servers/Cloud
1. Export from monitoring tool (AWS CloudWatch, Azure Monitor, etc.)
2. Map fields to the 16 required columns
3. Use at least 30 days of data

---

## 📝 16 Columns Explained

### Column A: user_id
- **What**: Device identifier
- **Example**: "my_iphone", "device_001", "work_laptop"
- **Must be**: Same for all rows of same device
- **Format**: Any text

### Column B: profile
- **What**: Device type or category
- **Suggested**: "media_heavy", "gamer", "office_user", "cleaner"
- **Example**: A phone with lots of photos = "media_heavy"
- **Format**: Any text

### Column C: date
- **What**: Date of measurement
- **Format**: **YYYY-MM-DD** (e.g., 2024-01-15)
- **Required**: Consecutive dates (one per day)
- **Important**: This format only - not MM/DD/YYYY!

### Column D: day_index
- **What**: Sequential counter
- **Values**: 0, 1, 2, 3, 4... (starts at 0 for each device)
- **Purpose**: Used by model for time-based features
- **Auto**: Can be calculated as 0, 1, 2, etc.

### Column E: total_capacity_gb
- **What**: Total device storage capacity
- **Examples**: 64, 128, 256, 512, 1024 GB
- **Must be**: Same for all rows (or update if device changed)
- **Format**: Decimal number (256.0, not "256 GB")

### Column F: used_gb
- **What**: Currently used storage
- **Formula**: Sum of all component columns (I-N)
- **Range**: Must be ≤ total_capacity_gb
- **Example**: If device has 256 GB total and 150 GB used → 150.0

### Column G: free_gb
- **What**: Free available storage
- **Formula**: total_capacity_gb - used_gb
- **Example**: 256 - 150 = 106 GB free
- **Calculate in Excel**: =E2-F2

### Column H: used_pct
- **What**: Percentage of storage used
- **Formula**: (used_gb / total_capacity_gb) × 100
- **Range**: 0-100
- **Example**: 150/256×100 = 58.59%
- **Calculate in Excel**: =F2/E2*100

### Columns I-N: Storage Breakdown
Six components that sum to used_gb:

- **I. photos_gb**: Storage used by photos
- **J. videos_gb**: Storage used by videos
- **K. apps_gb**: Storage used by applications
- **L. documents_gb**: Storage used by documents
- **M. system_gb**: Storage used by system files
- **N. other_gb**: Other storage usage

**Important**: These 6 must sum to used_gb (approximately)

### Column O: daily_delta_gb
- **What**: Daily change in used storage
- **Formula**: used_gb (today) - used_gb (yesterday)
- **First row**: 0.0
- **Example**: 
  - Day 1: 150.0 GB → daily_delta = 0.0 (first day)
  - Day 2: 150.5 GB → daily_delta = 0.5 (grew by 0.5 GB)
  - Day 3: 145.0 GB → daily_delta = -5.5 (cleanup freed 5.5 GB)

### Column P: cleanup_event
- **What**: Whether a cleanup event occurred
- **Values**: 0 (no) or 1 (yes)
- **Purpose**: Model learns cleanup patterns
- **Example**: Mark 1 when you manually cleared storage

---

## ✅ Validation Rules

Your CSV must pass ALL these checks:

```
✓ Exactly 16 columns (no more, no less)
✓ Column headers match exactly (case-sensitive)
✓ Columns in correct order
✓ No missing columns
✓ At least 7 rows (recommended 30+)
✓ Dates in YYYY-MM-DD format
✓ Consecutive dates (no gaps)
✓ All numeric values are numbers (not text)
✓ used_gb ≤ total_capacity_gb
✓ free_gb = total_capacity_gb - used_gb (approximately)
✓ used_pct = (used_gb/total_capacity_gb)*100 (approximately)
✓ Sum of components ≈ used_gb
✓ cleanup_event is 0 or 1 only
✓ day_index starts at 0 for each user
✓ No empty cells
✓ No extra spaces in headers
```

---

## 🎯 Common Scenarios

### Scenario 1: Single Phone, 30 Days
```
Total rows: 31 (header + 30 days)
user_id: my_iphone
profile: media_heavy
dates: 2024-01-01 to 2024-01-31
capacity: 256 GB
used: 150-160 GB (typical phone)
```

### Scenario 2: Phone + Laptop, 7 Days Each
```
Total rows: 15 (header + 7 phone + 7 laptop)
Device 1: my_iphone (user_id: phone_01)
Device 2: my_macbook (user_id: laptop_01)
Each has their own dates and day_index
```

### Scenario 3: Historical Data, 90 Days
```
Total rows: 91 (header + 90 days)
One device tracked for 3 months
More data = more accurate forecasts!
```

---

## 🛠️ How to Create Your CSV

### Option 1: Use Excel/Google Sheets (Easiest)
1. Create new spreadsheet
2. Add headers (or copy from template)
3. Fill in data rows
4. Export as CSV

### Option 2: Use the Template
1. Download `storage_data_template.csv`
2. Open in Excel
3. Replace values
4. Save as CSV

### Option 3: Python Script
```python
import pandas as pd

data = {
    'user_id': ['my_phone', 'my_phone'],
    'profile': ['media_heavy', 'media_heavy'],
    'date': ['2024-01-01', '2024-01-02'],
    'day_index': [0, 1],
    'total_capacity_gb': [256.0, 256.0],
    'used_gb': [150.0, 151.0],
    'free_gb': [106.0, 105.0],
    'used_pct': [58.59, 58.98],
    'photos_gb': [50.0, 51.0],
    'videos_gb': [60.0, 60.0],
    'apps_gb': [30.0, 30.0],
    'documents_gb': [5.0, 5.0],
    'system_gb': [5.0, 5.0],
    'other_gb': [0.0, 0.0],
    'daily_delta_gb': [0.0, 1.0],
    'cleanup_event': [0, 0]
}

df = pd.DataFrame(data)
df.to_csv('my_device.csv', index=False)
```

### Option 4: Copy-Paste Template
- Copy the minimal template below into a text editor
- Save as `.csv`
- Fill in your values

**Minimal 7-day template:**
```csv
user_id,profile,date,day_index,total_capacity_gb,used_gb,free_gb,used_pct,photos_gb,videos_gb,apps_gb,documents_gb,system_gb,other_gb,daily_delta_gb,cleanup_event
device_001,media_heavy,2024-01-01,0,256.0,150.0,106.0,58.59,50.0,60.0,30.0,5.0,5.0,0.0,0.0,0
device_001,media_heavy,2024-01-02,1,256.0,151.0,105.0,58.98,51.0,60.0,30.0,5.0,5.0,0.0,1.0,0
device_001,media_heavy,2024-01-03,2,256.0,150.5,105.5,58.79,50.5,60.0,30.0,5.0,5.0,0.0,-0.5,1
device_001,media_heavy,2024-01-04,3,256.0,151.2,104.8,59.06,51.0,60.0,30.0,5.0,5.0,0.2,0.7,0
device_001,media_heavy,2024-01-05,4,256.0,152.0,104.0,59.38,51.5,60.0,30.0,5.0,5.0,0.5,0.8,0
device_001,media_heavy,2024-01-06,5,256.0,153.0,103.0,59.77,52.0,60.0,30.0,5.0,5.0,1.0,1.0,0
device_001,media_heavy,2024-01-07,6,256.0,154.0,102.0,60.16,52.5,60.0,30.0,5.0,5.0,1.5,1.0,0
```

---

## 📦 Resources Provided

Your project includes:

1. **CSV_DATA_GUIDE.md** - Comprehensive column reference
2. **CSV_TEMPLATE_INSTRUCTIONS.md** - Step-by-step tutorial
3. **CSV_FORMAT_CHEATSHEET.md** - Quick reference
4. **storage_data_template.csv** - Downloadable template with 31 days of example data
5. **In-app help** - Download button in Forecast Lab tab

---

## 🎓 User Experience Flow

### User's Journey:
```
1. User opens app → Goes to "Forecast Lab" tab
2. Sees "📋 CSV Format Help" expander
3. Clicks to expand → Sees:
   - Quick format summary
   - Link to download template
   - Links to full guides
4. Clicks "Download CSV Template" button
5. Gets `storage_data_template.csv`
6. Opens in Excel/Sheets
7. Replaces values with their data
8. Saves as CSV
9. Returns to app
10. Clicks "Upload a CSV..."
11. Selects their file
12. Gets forecast!
```

---

## 💡 Tips for Success

### ✅ Data Quality
- **Real data** is better than estimates
- **More data** (60+ days) gives better forecasts
- **Accurate values** improve accuracy
- **Daily snapshots** are ideal

### ✅ Format Correctness
- **Dates**: Always YYYY-MM-DD
- **Decimals**: Use periods (3.14, not 3,14)
- **No text**: All numeric columns should be numbers
- **No quotes**: Unless your CSV tool adds them

### ✅ Completeness
- **Fill all 16 columns**: Don't skip any
- **No empty cells**: Fill everything with values
- **Match calculations**: Check your math before uploading
- **Use the template**: It's already correct!

### ✅ Realistic Data
- **Use your actual values**: Don't make up numbers
- **Be consistent**: Same measurement time each day
- **Track honestly**: Include cleanups, unusual usage
- **Include variety**: Different daily patterns help model learn

---

## ❓ Common Questions

**Q: Do I need all 16 columns?**
A: Yes, exactly 16. The model uses all of them.

**Q: Can I use MM/DD/YYYY dates?**
A: No, must be YYYY-MM-DD format.

**Q: What if my device capacity changed?**
A: You can either:
- Create two separate entries with different capacity values
- Use the new capacity and recalculate percentages

**Q: Do components need to sum exactly to used_gb?**
A: They should be approximately equal. Small rounding differences (±0.1 GB) are OK.

**Q: How many days of data do I need?**
A: Minimum 7, recommended 30-90 for good forecasts.

**Q: Can I test with made-up data?**
A: Yes! The template has realistic example data. Use it to test the app first.

**Q: What if I only have 3 days of data?**
A: Won't work - need minimum 7. Try the sample user data in the dashboard instead.

---

## 🚀 Ready to Go!

### For Users:
1. Download template from app
2. Fill with your data
3. Upload and test!

### For Help:
- **Quick ref**: CSV_FORMAT_CHEATSHEET.md (1 min read)
- **Full guide**: CSV_DATA_GUIDE.md (5 min read)
- **Step-by-step**: CSV_TEMPLATE_INSTRUCTIONS.md (10 min read)

**Let's get your data forecasting!** 📊
