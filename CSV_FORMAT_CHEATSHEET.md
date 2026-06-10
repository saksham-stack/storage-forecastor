# CSV Format Cheat Sheet

## Quick Reference - 16 Required Columns

```
user_id,profile,date,day_index,total_capacity_gb,used_gb,free_gb,used_pct,photos_gb,videos_gb,apps_gb,documents_gb,system_gb,other_gb,daily_delta_gb,cleanup_event
```

---

## Column Quick Guide

| Column | Type | Example | Notes |
|--------|------|---------|-------|
| user_id | Text | "U001", "my_phone" | Device identifier - unique per device |
| profile | Text | "media_heavy" | Profile type or custom label |
| date | Date | "2024-01-01" | **Must be YYYY-MM-DD** |
| day_index | Integer | 0, 1, 2... | Counter from 0 for each user |
| total_capacity_gb | Number | 256.0, 512.0 | Device storage capacity |
| used_gb | Number | 147.14 | Currently used storage |
| free_gb | Number | 364.86 | = total_capacity_gb - used_gb |
| used_pct | Number | 28.74 | = (used_gb/total_capacity_gb)*100 |
| photos_gb | Number | 41.43 | Storage by photos |
| videos_gb | Number | 33.68 | Storage by videos |
| apps_gb | Number | 24.88 | Storage by apps |
| documents_gb | Number | 8.50 | Storage by documents |
| system_gb | Number | 25.10 | Storage by system files |
| other_gb | Number | 13.54 | Other storage |
| daily_delta_gb | Number | 0.44 | Daily change (0 for first day) |
| cleanup_event | Integer | 0 or 1 | 1 = cleanup, 0 = normal |

---

## One-Minute Setup

1. **Download** `storage_data_template.csv` from the app
2. **Open** in Excel or Google Sheets
3. **Replace** the example data with your actual values
4. **Save** as CSV
5. **Upload** to the app

---

## Validation Checklist

```
☑ 16 columns with correct headers
☑ No missing columns
☑ Column names match exactly (case-sensitive)
☑ Dates in YYYY-MM-DD format
☑ No gaps in dates (consecutive days)
☑ used_gb ≤ total_capacity_gb
☑ free_gb = total_capacity_gb - used_gb (approximately)
☑ used_pct = (used_gb/total_capacity_gb)*100 (approximately)
☑ Sum of components ≈ used_gb
☑ cleanup_event is 0 or 1
☑ At least 7 rows per device
☑ day_index starts at 0 for each user
☑ No empty cells
☑ No extra columns or rows
```

---

## Example: Minimal Valid CSV

```csv
user_id,profile,date,day_index,total_capacity_gb,used_gb,free_gb,used_pct,photos_gb,videos_gb,apps_gb,documents_gb,system_gb,other_gb,daily_delta_gb,cleanup_event
device_001,media_heavy,2024-01-01,0,256.0,100.0,156.0,39.06,30.0,40.0,20.0,5.0,3.0,2.0,0.0,0
device_001,media_heavy,2024-01-02,1,256.0,101.0,155.0,39.45,30.5,40.5,20.0,5.0,3.0,2.0,1.0,0
device_001,media_heavy,2024-01-03,2,256.0,102.0,154.0,39.84,31.0,41.0,20.0,5.0,3.0,2.0,1.0,0
device_001,media_heavy,2024-01-04,3,256.0,103.0,153.0,40.23,31.5,41.5,20.0,5.0,3.0,2.0,1.0,0
device_001,media_heavy,2024-01-05,4,256.0,104.0,152.0,40.63,32.0,42.0,20.0,5.0,3.0,2.0,1.0,0
device_001,media_heavy,2024-01-06,5,256.0,105.0,151.0,41.02,32.5,42.5,20.0,5.0,3.0,2.0,1.0,0
device_001,media_heavy,2024-01-07,6,256.0,106.0,150.0,41.41,33.0,43.0,20.0,5.0,3.0,2.0,1.0,0
```

---

## Common Mistakes

### ❌ Wrong Date Format
```
date
01/01/2024          ← WRONG
2024-01-01          ← CORRECT
January 1, 2024     ← WRONG
```

### ❌ Missing Column
```
user_id,date,used_gb         ← Missing 13 columns!
user_id,profile,date,...     ← Need all 16 columns
```

### ❌ Inconsistent Calculations
```
total_capacity_gb: 256, used_gb: 256, used_pct: 75.0
                                      ↑ Wrong! Should be 100.0
```

### ❌ Components Don't Sum
```
used_gb: 100.0
photos: 30 + videos: 30 + apps: 20 + docs: 5 + system: 5 + other: 5 = 95.0
        ↑ Doesn't match! Should sum to 100.0
```

### ✅ Correct Examples

```csv
256.0,128.0,128.0,50.0,32.0,32.0,20.0,8.0,8.0,6.0,4.0,16.0,0.0,0
total_capacity_gb=256, used_gb=128, free_gb=128, used_pct=50.0 ✓
Components: 32+32+20+8+8+6+4+16 = 126 ≈ 128 ✓ (rounding OK)
```

---

## How to Calculate Computed Columns

If you need to fill these columns, use these formulas:

### In Excel:

**free_gb** (Column G, assuming data starts at row 2)
```excel
=E2-F2
```
(where E2 is total_capacity_gb, F2 is used_gb)

**used_pct** (Column H)
```excel
=ROUND(F2/E2*100,2)
```
(dividing used by total, multiply by 100, round to 2 decimals)

**day_index** (Column D)
For each user, manually enter: 0, 1, 2, 3, 4...
Or use: `=ROW()-2` (if data starts at row 2)

### In Google Sheets:

Same formulas work in Google Sheets:
```
=E2-F2              (free_gb)
=ROUND(F2/E2*100,2) (used_pct)
```

---

## Multiple Devices Example

```csv
user_id,profile,date,day_index,total_capacity_gb,used_gb,free_gb,used_pct,photos_gb,videos_gb,apps_gb,documents_gb,system_gb,other_gb,daily_delta_gb,cleanup_event
phone,media_heavy,2024-01-01,0,256.0,100.0,156.0,39.06,30.0,40.0,20.0,5.0,3.0,2.0,0.0,0
phone,media_heavy,2024-01-02,1,256.0,101.0,155.0,39.45,30.5,40.5,20.0,5.0,3.0,2.0,1.0,0
laptop,office_user,2024-01-01,0,512.0,200.0,312.0,39.06,10.0,5.0,50.0,100.0,20.0,15.0,0.0,0
laptop,office_user,2024-01-02,1,512.0,210.0,302.0,41.02,10.0,5.0,52.0,105.0,20.0,18.0,10.0,0
```

**Note:**
- Device 1 (phone): dates 2024-01-01 to 01-02, day_index 0-1
- Device 2 (laptop): dates 2024-01-01 to 01-02, day_index **restarts at 0**

---

## File Size & Limits

| Metric | Limit |
|--------|-------|
| File size | 50 MB |
| Max rows | 100,000 |
| Min rows | 7 (1 week) |
| Recommended | 60-180 (2-6 months) |

---

## Profile Types (Suggested)

```
media_heavy   - Photo/video intensive
gamer         - Game-heavy usage
office_user   - Document-heavy usage
cleaner       - Periodic cleanups
custom_name   - Any custom label
```

---

## Date Range Examples

### Past Data (3 months ago)
```
date
2023-10-01
2023-10-02
...
2023-12-31
```

### Recent Data (last month)
```
date
2024-01-01
2024-01-02
...
2024-01-31
```

### Future Projections (experimental)
```
date
2024-06-01
2024-06-02
...
2024-08-31
```

---

## Quick Copy-Paste Templates

### For 1 Device, 7 Days
```
user_id,profile,date,day_index,total_capacity_gb,used_gb,free_gb,used_pct,photos_gb,videos_gb,apps_gb,documents_gb,system_gb,other_gb,daily_delta_gb,cleanup_event
device_001,media_heavy,2024-01-01,0,256.0,100.0,156.0,39.06,30.0,40.0,20.0,5.0,3.0,2.0,0.0,0
device_001,media_heavy,2024-01-02,1,256.0,101.0,155.0,39.45,30.5,40.5,20.0,5.0,3.0,2.0,1.0,0
device_001,media_heavy,2024-01-03,2,256.0,102.0,154.0,39.84,31.0,41.0,20.0,5.0,3.0,2.0,1.0,0
device_001,media_heavy,2024-01-04,3,256.0,103.0,153.0,40.23,31.5,41.5,20.0,5.0,3.0,2.0,1.0,0
device_001,media_heavy,2024-01-05,4,256.0,104.0,152.0,40.63,32.0,42.0,20.0,5.0,3.0,2.0,1.0,0
device_001,media_heavy,2024-01-06,5,256.0,105.0,151.0,41.02,32.5,42.5,20.0,5.0,3.0,2.0,1.0,0
device_001,media_heavy,2024-01-07,6,256.0,106.0,150.0,41.41,33.0,43.0,20.0,5.0,3.0,2.0,1.0,0
```

### For 2 Devices, 7 Days Each
```
user_id,profile,date,day_index,total_capacity_gb,used_gb,free_gb,used_pct,photos_gb,videos_gb,apps_gb,documents_gb,system_gb,other_gb,daily_delta_gb,cleanup_event
device_001,media_heavy,2024-01-01,0,256.0,100.0,156.0,39.06,30.0,40.0,20.0,5.0,3.0,2.0,0.0,0
device_001,media_heavy,2024-01-02,1,256.0,101.0,155.0,39.45,30.5,40.5,20.0,5.0,3.0,2.0,1.0,0
device_001,media_heavy,2024-01-03,2,256.0,102.0,154.0,39.84,31.0,41.0,20.0,5.0,3.0,2.0,1.0,0
device_001,media_heavy,2024-01-04,3,256.0,103.0,153.0,40.23,31.5,41.5,20.0,5.0,3.0,2.0,1.0,0
device_001,media_heavy,2024-01-05,4,256.0,104.0,152.0,40.63,32.0,42.0,20.0,5.0,3.0,2.0,1.0,0
device_001,media_heavy,2024-01-06,5,256.0,105.0,151.0,41.02,32.5,42.5,20.0,5.0,3.0,2.0,1.0,0
device_001,media_heavy,2024-01-07,6,256.0,106.0,150.0,41.41,33.0,43.0,20.0,5.0,3.0,2.0,1.0,0
device_002,gamer,2024-01-01,0,512.0,300.0,212.0,58.59,20.0,150.0,100.0,10.0,15.0,5.0,0.0,0
device_002,gamer,2024-01-02,1,512.0,310.0,202.0,60.55,20.0,160.0,100.0,10.0,15.0,5.0,10.0,0
device_002,gamer,2024-01-03,2,512.0,320.0,192.0,62.50,20.0,170.0,100.0,10.0,15.0,5.0,10.0,0
device_002,gamer,2024-01-04,3,512.0,330.0,182.0,64.45,20.0,180.0,100.0,10.0,15.0,5.0,10.0,0
device_002,gamer,2024-01-05,4,512.0,340.0,172.0,66.41,20.0,190.0,100.0,10.0,15.0,5.0,10.0,0
device_002,gamer,2024-01-06,5,512.0,350.0,162.0,68.36,20.0,200.0,100.0,10.0,15.0,5.0,10.0,0
device_002,gamer,2024-01-07,6,512.0,360.0,152.0,70.31,20.0,210.0,100.0,10.0,15.0,5.0,10.0,1
```

---

## More Help

- **Full Guide**: See `CSV_DATA_GUIDE.md`
- **Step-by-Step**: See `CSV_TEMPLATE_INSTRUCTIONS.md`
- **Template**: Download from app or use `storage_data_template.csv`

**Ready to upload? Go to Forecast Lab tab and select "Upload CSV"!** 📤
