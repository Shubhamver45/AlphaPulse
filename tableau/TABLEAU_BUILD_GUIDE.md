# AlphaPulse — Investment Risk & Volatility Monitor

## Professional Tableau Build Guide
### Connecting CSVs and Building Each Sheet

---

## Step 0 — Connect Data Sources in Tableau

1. Open **Tableau Desktop** → **Connect → Text File**
2. Navigate to `tableau_exports/` and connect **all 7 CSVs** listed below
3. For each sheet in this guide, the exact **Data Source** name is stated

| File | Purpose |
|---|---|
| `tab_prices.csv` | Closing price line chart |
| `tab_volume.csv` | Volume bar chart |
| `tab_daily_returns.csv` | Daily returns area/bar chart |
| `tab_rolling_vol.csv` | 30-day rolling volatility |
| `tab_correlation.csv` | Correlation heatmap |
| `tab_monte_carlo.csv` | Monte Carlo simulation paths |
| `tab_mc_bands.csv` | MC percentile fan chart |
| `tab_var_summary.csv` | VaR KPI card |

---

## Sheet 1 — Stock Price Line Chart

**Data Source:** `tab_prices.csv`

| Field | Role | Shelf |
|---|---|---|
| `Date` | Time dimension | Columns |
| `Close` | Measure (AVG) | Rows |
| `Ticker` | Dimension | Color |
| `Type` | Filter | Filter (show "Portfolio Stock" only, or include Benchmark) |

**Steps:**
1. Drag `Date` → Columns → right-click → **Exact Date**
2. Drag `Close` → Rows → change to **AVG**
3. Drag `Ticker` → **Color** mark card
4. Drag `Type` → Filters shelf → keep **both** values
5. Mark type: **Line**
6. In Color → Edit Colors → assign distinct colors per sector:
   - Technology: `#4F8EF7` (blue family)
   - Healthcare: `#2ECC71` (green)
   - Financials: `#F39C12` (amber)
   - Consumer: `#9B59B6` (purple)
   - Energy: `#E74C3C` (red)
   - Benchmark: `#95A5A6` (grey, dashed)
7. Benchmark line: right-click `^GSPC` → **Format** → Line style: **Dashed**
8. Title: **"Portfolio Stock Prices — Adjusted Close (2 Years)"**

---

## Sheet 2 — Trading Volume Bar Chart

**Data Source:** `tab_volume.csv`

| Field | Role | Shelf |
|---|---|---|
| `Date` | Time | Columns |
| `Volume` | Measure (SUM) | Rows |
| `Ticker` | Dimension | Color |
| `Sector` | Dimension | Filter |

**Steps:**
1. Drag `Date` → Columns → set to **Month**
2. Drag `Volume` → Rows → SUM
3. Drag `Ticker` → **Color**
4. Mark type: **Bar**
5. Add `Sector` to Filters → show **Filter** control on dashboard
6. Right-click Y axis → **Format** → Numbers → **Custom** → `#,##0,,"M"` (millions)
7. Title: **"Monthly Trading Volume by Stock"**

---

## Sheet 3 — Daily Returns Bar Chart

**Data Source:** `tab_daily_returns.csv`

| Field | Role | Shelf |
|---|---|---|
| `Date` | Time | Columns |
| `Pct_Return` | Measure (AVG) | Rows |
| `Positive` | Calculated field | Color |
| `Ticker` | Dimension | Filter / Pages |

**Steps:**
1. Drag `Date` → Columns → **Exact Date**
2. Drag `Pct_Return` → Rows → AVG
3. Create **Calculated Field** → "Return Color":
   ```
   IF AVG([Pct_Return]) >= 0 THEN "Gain" ELSE "Loss" END
   ```
4. Drag "Return Color" → **Color** → set **Gain** = `#27AE60`, **Loss** = `#E74C3C`
5. Mark type: **Bar**
6. Drag `Ticker` → **Pages** shelf (allows per-stock animation)
7. Add **Reference Line**: Right-click Y axis → Add Reference Line → Value = 0
8. Title: **"Daily % Returns — Portfolio Stocks"**

---

## Sheet 4 — 30-Day Rolling Volatility

**Data Source:** `tab_rolling_vol.csv`

| Field | Role | Shelf |
|---|---|---|
| `Date` | Time | Columns |
| `Rolling_Vol_Pct` | Measure (AVG) | Rows |
| `Ticker` | Dimension | Color |
| `Sector` | Dimension | Filter |

**Steps:**
1. Drag `Date` → Columns → **Exact Date**
2. Drag `Rolling_Vol_Pct` → Rows → AVG
3. Drag `Ticker` → Color
4. Mark type: **Line**
5. Add `Sector` to Filters with **Show Filter** control
6. Format Y axis: suffix `%`
7. Add **Annotation** at crisis spikes (right-click peak → Annotate → Mark)
8. Title: **"30-Day Rolling Volatility — Annualised (%)"**

---

## Sheet 5 — Correlation Heatmap

**Data Source:** `tab_correlation.csv`

| Field | Role | Shelf |
|---|---|---|
| `Asset_X` | Dimension | Columns |
| `Asset_Y` | Dimension | Rows |
| `Correlation` | Measure (AVG) | Color + Label |
| `Strength` | Dimension | Tooltip |

**Steps:**
1. Drag `Asset_X` → Columns
2. Drag `Asset_Y` → Rows
3. Drag `Correlation` → **Color** → change to **Diverging** palette:
   - Min (−1): `#C0392B` (deep red)
   - Centre (0): `#FFFFFF` (white)
   - Max (+1): `#27AE60` (deep green)
   - Stepped Color: **OFF** (continuous gradient)
4. Mark type: **Square**
5. Drag `Correlation` → **Label** → Format to 2 decimal places
6. Drag `Strength` → **Tooltip**
7. Right-click Column header → **Sort** → **By Field** → alphabetical
8. Title: **"Asset Correlation Matrix — Log Returns (2Y)"**

> **Manager Note:** Dark green diagonal top-left to bottom-right = perfect self-correlation (expected, value=1.0). Off-diagonal reds indicate effective diversification.

---

## Sheet 6 — Monte Carlo Simulation Fan Chart

**Data Source (primary):** `tab_mc_bands.csv`
**Data Source (secondary):** `tab_monte_carlo.csv`

### Part A — Simulated Paths (background)
1. Connect `tab_monte_carlo.csv`
2. Drag `Day` → Columns
3. Drag `Portfolio_Value` → Rows → AVG
4. Drag `Simulation` → **Detail** mark (creates individual path lines)
5. Mark type: **Line**
6. Color: `#AED6F1` (light blue), Opacity: **8%** (creates density effect)

### Part B — Percentile Bands (overlay)
1. Add `tab_mc_bands.csv` → **Dual Axis**
2. On the second axis:
   - Drag `Median` → Rows → **Line**, Color: `#E74C3C` (red), Size: **3**
   - Drag `P5` → Rows → **Line**, Color: `#F39C12` (amber), dashed
   - Drag `P95` → Rows → **Line**, Color: `#27AE60` (green), dashed
   - Drag `P25`, `P75` → **Area** between → Color `#5DADE2` at 30% opacity
3. Synchronise axes → right-click secondary axis → **Synchronise Axis**
4. Add **Annotation** at Day 252 showing Median and P5 values
5. Title: **"Monte Carlo Simulation — 10,000 Portfolio Paths (1-Year Horizon)"**
6. Y-axis: custom format `$#,##0,,"M"` or `$#,##0`

---

## Dashboard Assembly — "AlphaPulse Risk Monitor"

### Layout (1440 × 900 px Fixed)

```
┌─────────────────────────────────────────────────────────┐
│  AlphaPulse  |  Investment Risk & Volatility Monitor     │  ← Header (60px)
├──────────────┬──────────────┬──────────────┬────────────┤
│  VaR 95%     │  VaR 99%     │  Portfolio   │  Best      │
│  KPI Card    │  KPI Card    │  Volatility  │  Ticker    │  ← KPI Row (100px)
├──────────────────────────┬──────────────────────────────┤
│                           │                              │
│  Sheet 1: Price Chart     │  Sheet 5: Correlation        │
│  (left, 60% width)        │  Heatmap  (right, 40%)       │  ← Row 1 (280px)
│                           │                              │
├──────────────────────────┴──────────────────────────────┤
│                                                          │
│  Sheet 6: Monte Carlo Fan Chart  (full width)           │  ← Row 2 (260px)
│                                                          │
├─────────────────────────┬────────────────────────────────┤
│  Sheet 4: Rolling Vol   │  Sheet 3: Daily Returns        │  ← Row 3 (200px)
│  (left 50%)             │  (right 50%)                   │
└─────────────────────────┴────────────────────────────────┘
```

### Dashboard Setup Steps:
1. **New Dashboard** → Size: Fixed → **1440 × 900**
2. Drag sheets from the left panel into position per layout above
3. **Background**: Dashboard → Format → Shading → `#1A1A2E` (dark navy)
4. Sheet borders: `#2C3E7A` (subtle blue border)
5. **Filter Actions**: Dashboard → Actions → Add Action → Filter:
   - Source: Sheet 1 (Price Chart)
   - Run on: Select
   - Target sheets: Sheet 3, Sheet 4 (syncs on ticker click)
6. Add **Text Object** header: Font = `Montserrat Bold 24pt`, Color = `#FFFFFF`
7. Add company logo placeholder with **Image Object**
8. Save as: `AlphaPulse.twbx` (Packaged Workbook — includes all data)

---

## KPI Card Setup (VaR Summary)

**Data Source:** `tab_var_summary.csv`

1. Drag `Var_Level` → Rows
2. Drag `Var_Dollar` → **Text** mark
3. Create **BANs** (Big-Ass Numbers):
   - Format: `$#,##0`
   - Font: `36pt Bold`
   - Color: `#E74C3C` (red — indicates risk)
4. Sub-label: `VaR_Description` as second text row, `12pt`, grey `#95A5A6`

---

## Color Palette Reference (AlphaPulse Brand)

| Element | Hex | Use |
|---|---|---|
| Background | `#1A1A2E` | Dashboard, sheet backgrounds |
| Card Background | `#16213E` | KPI cards, tooltips |
| Accent Blue | `#4F8EF7` | Primary lines, highlights |
| Positive/Gain | `#27AE60` | Green — gains, low risk |
| Negative/Loss | `#E74C3C` | Red — losses, high risk |
| Warning | `#F39C12` | Amber — moderate risk |
| Text Primary | `#FFFFFF` | Titles, labels |
| Text Secondary | `#95A5A6` | Sub-labels, tooltips |
| Grid Lines | `#2C3E7A` | Subtle grid on dark bg |
