# 📋 Data Builder - Easy CSV Guide

## What is the Data Builder?

The **Data Builder** tab in your Streamlit app makes it **super easy** to prepare your storage data for forecasting - **no complicated steps needed!**

## Three Simple Methods

### Method 1: 📊 See Example Data
**For users who want to understand the format first**

- View a real example of what storage data looks like
- See 15 rows of actual data from a device
- Learn what each column means in simple language
- No downloads, just viewing

**Use this when:**
- You want to understand the data format before creating your own
- You want to see real numbers and patterns

---

### Method 2: 🔨 Generate Template
**For users who want to create their own data CSV**

This is the **easiest way** to get started!

#### Step 1: Fill in simple info
- **Device ID**: Give your phone/tablet a name (e.g., `my_phone_001`)
- **Days of data**: How many days do you want to forecast for? (7-365 days)
- **Device profile**: Type of user (e.g., `heavy_user`, `light_user`, `media_heavy`)
- **Storage capacity**: Your device's total storage in GB (e.g., 256GB, 512GB)
- **Start date**: When your data collection begins

#### Step 2: Download blank template
Click "Generate blank template" and you'll get a CSV with:
- All 16 required columns
- All the dates you specified
- Empty cells ready for your numbers
- Correct formatting already done ✓

#### Step 3: Fill in Excel or Google Sheets
Open the downloaded CSV in:
- ✓ Microsoft Excel
- ✓ Google Sheets
- ✓ Apple Numbers
- ✓ Any spreadsheet app

Then fill in your actual storage numbers!

#### Step 4: Upload & Forecast
Go to **Forecast Lab** tab and upload your filled-in CSV to get predictions!

---

### Method 3: 📥 Download Real Example
**For users who want a quick test**

- Get a ready-made CSV with real example data
- 31 days of data from one device
- Perfect for testing the forecaster
- Can immediately upload to Forecast Lab

**Use this when:**
- You want to test the app quickly
- You want to see if it works before preparing your real data

---

## Column Meanings (Simple Version)

| Column | What it means | Example |
|--------|--------------|---------|
| **user_id** | Your device ID | `my_phone_001` |
| **profile** | Device type | `heavy_user` |
| **date** | The date | `2024-01-15` |
| **day_index** | Days since start | `0, 1, 2, 3...` |
| **total_capacity_gb** | Total storage | `256` |
| **used_gb** | How much used | `120.5` |
| **free_gb** | How much free | `135.5` |
| **used_pct** | Used as percent | `47.1` |
| **photos_gb** | Photos storage | `45.2` |
| **videos_gb** | Videos storage | `32.1` |
| **apps_gb** | Apps storage | `18.3` |
| **documents_gb** | Documents storage | `12.0` |
| **system_gb** | System storage | `10.1` |
| **other_gb** | Other files storage | `2.8` |
| **daily_delta_gb** | Change from yesterday | `0.5` |
| **cleanup_event** | Did you delete stuff? | `0` or `1` |

---

## Quick Tips

✅ **DO:**
- Use at least **7 days** of data (30+ is better)
- Keep dates in **YYYY-MM-DD** format
- Make sure all GB values are **≥ 0**
- Make sure **used_gb ≤ capacity_gb**
- Use realistic numbers from your device

❌ **DON'T:**
- Use negative numbers
- Mix date formats
- Leave important columns empty
- Put used_gb higher than total_capacity_gb
- Use special characters in device ID

---

## Example: Step-by-Step

### You have:
- Samsung phone with 512GB storage
- 30 days of storage data collected
- Want to forecast next 90 days

### What to do:

1. Go to **Data Builder** tab
2. Click **"🔨 Generate Template"**
3. Fill in:
   - Device ID: `samsung_s23`
   - Days of data: `30`
   - Device profile: `heavy_user`
   - Storage capacity: `512`
   - Start date: `2024-01-01`
4. Click **"Generate blank template"**
5. Download the CSV
6. Open in Excel/Sheets and fill in your data
7. Go to **Forecast Lab** tab
8. Choose **"Upload CSV"**
9. Upload your file
10. See your forecast! 🎉

---

## Still Need Help?

- **Data Builder** tab has all three methods built in - try them!
- See real examples without any downloads
- Generate templates with one click
- Validation catches common errors

That's it! 🎉 No complicated documents, no confusion - just fill in your data and forecast!
