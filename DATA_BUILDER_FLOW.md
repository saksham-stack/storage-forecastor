# 📊 Data Builder - User Flow Diagram

## The Complete User Journey

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Opens Dashboard                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
         ┌──────▼──────┐         ┌───────▼────────┐
         │              │         │                │
    ┌────┴──────────┐   │   ┌─────┴──────────┐    │
    │ Data Builder  │   │   │  Other Tabs    │    │
    │    Tab        │   │   │                │    │
    └────┬──────────┘   │   └────────────────┘    │
         │              │                         │
    ┌────▼─────────────────────────────────┐      │
    │  Choose Method:                      │      │
    │  • See Example Data                  │      │
    │  • Generate Template                 │      │
    │  • Download Real Example             │      │
    └──┬──────────────┬──────────────┬─────┘      │
       │              │              │            │
   ┌───▼───┐    ┌─────▼────┐   ┌────▼─────┐      │
   │ Method │    │ Method 2 │   │  Method  │      │
   │   1    │    │          │   │    3     │      │
   └───┬───┘    └─────┬────┘   └────┬─────┘      │
       │              │              │            │
       │         ┌────▼────────────┐ │            │
       │         │ Fill Simple Form│ │            │
       │         │ • Device ID     │ │            │
       │         │ • Days          │ │            │
       │         │ • Profile       │ │            │
       │         │ • Capacity      │ │            │
       │         │ • Start Date    │ │            │
       │         └────┬────────────┘ │            │
       │              │              │            │
       │         ┌────▼────────────┐ │            │
       │         │ Generate Blank  │ │            │
       │         │ CSV Template    │ │            │
       │         └────┬────────────┘ │            │
       │              │              │            │
   ┌───▼──────┐  ┌────▼──────┐  ┌───▼──────┐     │
   │   View   │  │ Download  │  │ Download │     │
   │ Example  │  │  CSV      │  │ Example  │     │
   │   Data   │  │           │  │   CSV    │     │
   └──────────┘  └────┬──────┘  └─────┬────┘     │
                      │               │          │
                 ┌────▼───────────────▼────┐     │
                 │  User Has CSV File       │     │
                 │  (blank or pre-filled)   │     │
                 └────┬──────────────────────┘     │
                      │                           │
                      │  (Fill in Excel/Sheets)   │
                      │                           │
                 ┌────▼──────────────────────┐    │
                 │ Go to Forecast Lab Tab    │    │
                 └────┬──────────────────────┘    │
                      │                           │
                 ┌────▼──────────────────────┐    │
                 │ Upload CSV                │    │
                 └────┬──────────────────────┘    │
                      │                           │
                 ┌────▼──────────────────────┐    │
                 │ Get 30/60/90 Day          │    │
                 │ Forecasts! 🎉             │    │
                 └──────────────────────────┘    │
```

---

## Method 1: See Example Data

```
Start
  │
  ├─→ View real example (15 rows)
  │
  ├─→ See column meanings
  │
  ├─→ Understand format
  │
  └─→ Ready to try Method 2 or 3
```

---

## Method 2: Generate Template (Most Used)

```
┌─────────────────────────┐
│  User fills simple form │
├─────────────────────────┤
│ Device ID: my_phone     │
│ Days: 30                │
│ Profile: heavy_user     │
│ Capacity: 256           │
│ Start: 2024-01-01       │
└────────┬────────────────┘
         │
         ├─→ Click "Generate"
         │
         ├─→ System creates:
         │   • 30 dated rows
         │   • All 16 columns
         │   • Proper structure
         │
         ├─→ Download CSV
         │
         ├─→ User opens in Excel/Sheets
         │
         ├─→ User fills numbers:
         │   • used_gb
         │   • free_gb
         │   • storage breakdown
         │
         ├─→ User saves file
         │
         └─→ Go to Forecast Lab and upload!
```

---

## Method 3: Download Real Example

```
Click Download
  │
  ├─→ Get pre-filled CSV
  │   (31 days of real data)
  │
  ├─→ Download to computer
  │
  └─→ Go to Forecast Lab
      and upload immediately!
```

---

## Data Flow

```
┌──────────────────────────────────┐
│  Data Builder Tab                │
├──────────────────────────────────┤
│                                  │
│  Method 1        Method 2        │
│  View Example    Generate CSV    
│  (Learn)         (Create)        
│                  │               
│                  ├─ Input form   
│                  ├─ Generate     
│                  └─ Download     
│                                  
│  Method 3                        
│  Real Example                    
│  (Test)                          
│  └─ Download                     
│                                  
└──────────────┬───────────────────┘
               │
               │ CSV File
               │
         ┌─────▼──────────┐
         │ User Machine   │
         ├────────────────┤
         │ Excel/Sheets   │
         │ Fill in Data   │
         └─────┬──────────┘
               │
               │ Filled CSV
               │
         ┌─────▼──────────────┐
         │ Forecast Lab Tab   │
         ├────────────────────┤
         │ Upload CSV         │
         │ Validate           │
         │ Process            │
         │ Generate Forecast  │
         └────────────────────┘
               │
               ▼
         🎉 30/60/90 Day
         Forecasts!
```

---

## User Decision Tree

```
START: I want to test the forecaster
  │
  ├─ Do I have my own storage data?
  │
  ├─→ YES, I have data
  │   │
  │   ├─ Do I know the CSV format?
  │   │
  │   ├─→ NO
  │   │   └─ Go to "See Example Data"
  │   │       Then "Generate Template"
  │   │
  │   └─→ YES
  │       └─ Go to "Generate Template"
  │           (Fill form, download, fill CSV)
  │
  ├─→ NO, I don't have data
  │   │
  │   ├─ Do I want to learn first?
  │   │
  │   ├─→ YES
  │   │   └─ Go to "See Example Data"
  │   │
  │   └─→ NO, just test the app
  │       └─ Go to "Download Real Example"
  │           (One-click, ready to upload)
  │
  └─ (Any method) → Forecast Lab → Upload CSV → Get forecast! 🎉
```

---

## What Each Tab Does

```
┌─────────────────────────────────────────────────────┐
│              STREAMLIT DASHBOARD                    │
├────────────┬──────────────┬──────────┬────────┬────┤
│ Overview   │ Data Builder │ Forecast │ Bench- │    │
│            │              │   Lab    │  mark  │    │
├────────────┼──────────────┼──────────┼────────┼────┤
│            │              │          │        │    │
│ • View     │ • See        │ • Pick   │ • View │    │
│   user     │   examples   │   data   │   model│    │
│   behavior │              │   source │   comp │    │
│            │ • Generate   │          │        │    │
│ • Storage  │   template   │ • Run    │        │    │
│   patterns │              │   model  │        │    │
│            │ • Download   │          │        │    │
│            │   sample     │ • Log    │        │    │
│            │              │   results│        │    │
│            │              │          │        │    │
└────────────┴──────────────┴──────────┴────────┴────┘
```

---

## Success Path

```
📋 Data Builder Tab
       ↓
   Choose Method
       ↓
  [Method 1] [Method 2] [Method 3]
   (Learn)  (Create)   (Test)
       ↓      ↓          ↓
     View  Generate   Download
    Example Template  Example
       ↓      ↓          ↓
    Ready   Download    Ready
    to Go    CSV →      to Use
       │     Fill        │
       │     Data        │
       │      ↓          │
       └──────┴──────────┘
              ↓
        Upload to
      Forecast Lab
              ↓
        Get Forecast! 🎉
```

---

## Time to Forecast

### Before Data Builder
```
Manual template download ........... 5 min
Figure out columns ................ 10 min
Format data correctly .............. 15 min
Fix validation errors .............. 10 min
Upload and forecast ................ 5 min
────────────────────────────────────────
TOTAL ........................ 45+ minutes ⏱️
```

### With Data Builder
```
Click "Generate Template" .......... 30 sec
Fill simple form ................... 1 min
Download CSV ....................... 30 sec
Fill numbers in Excel .............. 3 min
Upload to Forecast Lab ............. 1 min
Get forecast! ....................... 30 sec
────────────────────────────────────────
TOTAL ...................... ~6-7 minutes ⚡
```

**Improvement:** 7x faster! ⚡

---

## Summary

✅ **Easy to use:** Visual, step-by-step flow
✅ **Multiple options:** Choose what fits your needs
✅ **Fast:** From start to forecast in minutes
✅ **Guided:** Help at every step
✅ **No confusion:** All options in one place
