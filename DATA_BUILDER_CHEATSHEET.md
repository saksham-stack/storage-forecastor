# 📱 Data Builder - Quick Cheat Sheet

## 🎯 One-Minute Overview

| What | Where | How |
|------|-------|-----|
| **See Examples** | Data Builder Tab | Click "📊 See Example Data" |
| **Create Template** | Data Builder Tab | Click "🔨 Generate Template" |
| **Get Sample Data** | Data Builder Tab | Click "📥 Download Real Example" |
| **Upload & Forecast** | Forecast Lab Tab | Upload your CSV → Get forecast! |

---

## 🔨 Generate Template (Most Used)

### Step 1: Fill This Form
```
Device ID:        my_phone_001
Days of data:     30
Device profile:   heavy_user
Storage capacity: 256 GB
Start date:       2024-01-01
```

### Step 2: Click Button
```
📥 Download template (30 rows)
```

### Step 3: You Get
```
✅ CSV with 30 rows
✅ All dates filled in
✅ All 16 columns
✅ Ready to fill your numbers
```

### Step 4: Fill in Excel/Sheets
```
Column              Example
─────────────────────────────
user_id             ← my_phone_001
profile             ← heavy_user
date                ← auto-filled
...
used_gb             ← 120.5 (YOUR DATA)
free_gb             ← 135.5 (YOUR DATA)
photos_gb           ← 45.2 (YOUR DATA)
videos_gb           ← 32.1 (YOUR DATA)
... (rest of the data)
```

### Step 5: Upload & Done!
```
Go to Forecast Lab tab
└── Upload your filled CSV
    └── Get 30/60/90 day forecasts! 🎉
```

---

## 📊 The 16 Columns (Easy Version)

```
1.  user_id              Your device name
2.  profile              Device type
3.  date                 YYYY-MM-DD
4.  day_index            0, 1, 2, 3...
5.  total_capacity_gb    Total storage
6.  used_gb              ← YOU FILL THIS
7.  free_gb              ← YOU FILL THIS
8.  used_pct             ← YOU FILL THIS
9.  photos_gb            ← YOU FILL THIS
10. videos_gb            ← YOU FILL THIS
11. apps_gb              ← YOU FILL THIS
12. documents_gb         ← YOU FILL THIS
13. system_gb            ← YOU FILL THIS
14. other_gb             ← YOU FILL THIS
15. daily_delta_gb       ← YOU FILL THIS
16. cleanup_event        0 or 1
```

---

## ⚡ Quickest Path to Forecast

```
1. Open app
   streamlit run dashboard\app.py

2. Go to Data Builder tab

3. Click "Download Real Example"

4. Go to Forecast Lab tab

5. Upload that CSV

6. See forecast! 🎉
```
**Time: 2 minutes**

---

## ✅ Before You Upload

Check these:
- [ ] At least 7 days of data
- [ ] All 16 columns present
- [ ] No negative numbers
- [ ] Dates in YYYY-MM-DD
- [ ] used_gb ≤ total_capacity_gb

---

## 📥 Where to Get Help

| Need | Find Here |
|------|-----------|
| **In-app help** | Data Builder tab (click expand) |
| **Visual guide** | Open `DATA_BUILDER_GUIDE.html` in browser |
| **Quick ref** | Read `CSV_QUICK_START.md` |
| **Detailed guide** | Read `DATA_BUILDER_GUIDE.md` |
| **How it works** | Read `DATA_BUILDER_FLOW.md` |

---

## 🚀 Real Example

### My Device:
- iPhone 12 Pro
- 256GB total
- Last 30 days of data

### What I Do:
1. Go to Data Builder
2. Fill form:
   - Device ID: `iphone_12_pro_john`
   - Days: `30`
   - Profile: `heavy_media`
   - Capacity: `256`
   - Start date: Today
3. Download CSV
4. Open Excel
5. Fill 30 rows with my storage numbers:
   - used_gb each day
   - Photos/Videos/Apps breakdown
   - Any cleanup events
6. Upload to Forecast Lab
7. **See my storage forecast for next 90 days!** 🎉

---

## 🎯 Quick Decision Tree

```
START HERE
    │
    ├─ Never done this before?
    │  └─ Go to "See Example Data" first
    │
    ├─ Have my own data?
    │  └─ Go to "Generate Template"
    │
    └─ Want to test now?
       └─ Go to "Download Real Example"
```

---

## 📋 Column-by-Column Cheat Sheet

### IDs & Dates
- **user_id**: Just give your device a name (any text)
- **profile**: Type of user (heavy_user, light_user, etc.)
- **date**: YYYY-MM-DD format (2024-01-15, not 01/15/2024)
- **day_index**: 0, 1, 2, 3... (auto-numbered in template)

### Storage Numbers (Capacity)
- **total_capacity_gb**: Your device's total (256, 512, 1024)
- **used_gb**: How much you're using TODAY
- **free_gb**: Usually = total - used
- **used_pct**: (used_gb / total_capacity_gb) × 100

### Storage Breakdown
- **photos_gb**: Storage from photos
- **videos_gb**: Storage from videos
- **apps_gb**: Storage from apps
- **documents_gb**: Storage from docs
- **system_gb**: Used by system/OS
- **other_gb**: Everything else

### Activity
- **daily_delta_gb**: How much changed today
- **cleanup_event**: Did you delete stuff? (0 = no, 1 = yes)

---

## ✨ What Happens After Upload

```
You upload CSV
    │
    ├─ App validates:
    │  • All 16 columns?
    │  • At least 7 days?
    │  • No negative numbers?
    │  • Dates correct?
    │
    ├─ If OK ✅:
    │  └─ Runs XGBoost model
    │     └─ Shows 30/60/90 day forecast
    │
    └─ If error ❌:
       └─ Clear error message
          └─ Fix and try again
```

---

## 💡 Pro Tips

1. **More data = Better forecast**
   - 7 days = minimum
   - 30 days = good
   - 60+ days = best

2. **Be accurate**
   - Real numbers work best
   - Approximate OK for testing
   - Don't make up numbers

3. **Recent data**
   - Last 30 days ideal
   - Not old data from 6 months ago

4. **One device at a time**
   - One user_id per CSV
   - Want multiple? Upload multiple times

5. **Missing columns?**
   - Use template generator
   - Handles all 16 automatically

---

## 🆘 Common Issues

| Problem | Fix |
|---------|-----|
| "Missing columns" | Use Generate Template |
| "Not enough rows" | Need 7+ days minimum |
| "Date format error" | Use YYYY-MM-DD |
| "Negative numbers" | GB values must be ≥ 0 |
| "used_gb > capacity" | Check your numbers |

---

## 📊 Example CSV Content

```
user_id,profile,date,day_index,total_capacity_gb,used_gb,free_gb,used_pct,photos_gb,videos_gb,apps_gb,documents_gb,system_gb,other_gb,daily_delta_gb,cleanup_event
my_phone,heavy_user,2024-01-01,0,256,120.5,135.5,47.05,45.2,32.1,18.3,12.0,10.1,2.8,0.0,0
my_phone,heavy_user,2024-01-02,1,256,121.0,135.0,47.27,45.3,32.3,18.4,12.0,10.2,2.8,0.5,0
my_phone,heavy_user,2024-01-03,2,256,118.8,137.2,46.41,44.2,31.5,18.2,11.8,10.0,3.1,0.0,1
... (continue for 30 days)
```

---

## 🎉 Ready?

1. Open dashboard: `streamlit run dashboard\app.py`
2. Click **Data Builder** tab
3. Choose your method
4. Done! Simple as that.

**Fastest way:** Download Real Example → Upload → Forecast (2 min) ⚡

**Your way:** Generate Template → Fill data → Upload → Forecast (5-10 min) 📋

Good luck! 🚀
