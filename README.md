# AlphaPulse — Investment Risk & Volatility Monitor

> **A production-grade quantitative risk analytics pipeline for portfolio management.**
> Built for a boutique investment firm to monitor real-time market risk exposure.

---

## Project Overview

| Item | Detail |
|---|---|
| **Brand** | AlphaPulse |
| **Stack** | Python · yfinance · NumPy · Tableau |
| **Portfolio** | 10 diversified equities + S&P 500 benchmark |
| **Key Metrics** | VaR (95%/99%), Monte Carlo (10,000 runs), Rolling Volatility, Correlation |
| **Investment Capital** | $1,000,000 simulated portfolio |

---

## Two-Week Delivery Plan

### Week 1 — Data Acquisition & Cleaning
| Task | Status | Script |
|---|---|---|
| Select 10-stock diversified portfolio | ✅ | `config.py` |
| Fetch 2-year OHLCV via yfinance | ✅ | `data_pipeline.py` |
| Exponential back-off retry (5 attempts) | ✅ | `data_pipeline.py` |
| Stock split & dividend adjustment (`auto_adjust=True`) | ✅ | `data_pipeline.py` |
| Missing value imputation & outlier detection | ✅ | `data_pipeline.py` |
| Data quality report generation | ✅ | `data_pipeline.py` |

**Critical Review Point — Data Quality Check:**
- `auto_adjust=True` retroactively corrects historical prices for splits & dividends
- Quality report: `data/data_quality_report.csv`

---

### Week 2 — Quantitative Analysis
| Task | Status | Script |
|---|---|---|
| Daily Log Returns via NumPy | ✅ | `analytics_engine.py` |
| Portfolio Variance (wᵀΣw matrix multiply) | ✅ | `analytics_engine.py` |
| 30-Day Rolling Volatility (annualised) | ✅ | `analytics_engine.py` |
| Correlation Matrix (np.corrcoef) | ✅ | `analytics_engine.py` |
| Value at Risk — 95% & 99% historical | ✅ | `analytics_engine.py` |
| Monte Carlo GBM — 10,000 paths × 252 days | ✅ | `analytics_engine.py` |
| Statistical Validation (skewness & kurtosis) | ✅ | `analytics_engine.py` |

**Critical Review Point — Statistical Validation:**
```
Validation Report: reports/mc_validation_report.csv
  Skewness  |Δ| < 0.50  → PASS/FAIL
  Kurtosis  |Δ| < 1.50  → PASS/FAIL
```

---

## Portfolio Composition

| Ticker | Company | Sector | Weight |
|---|---|---|---|
| AAPL | Apple Inc. | Technology | 12% |
| MSFT | Microsoft Corp. | Technology | 12% |
| NVDA | NVIDIA Corp. | Technology | 8% |
| JNJ | Johnson & Johnson | Healthcare | 10% |
| UNH | UnitedHealth Group | Healthcare | 8% |
| JPM | JPMorgan Chase | Financials | 10% |
| GS | Goldman Sachs | Financials | 8% |
| AMZN | Amazon.com Inc. | Consumer Discret. | 12% |
| PG | Procter & Gamble | Consumer Staples | 10% |
| XOM | Exxon Mobil Corp. | Energy | 10% |
| ^GSPC | S&P 500 | Benchmark | — |

---

## Project Structure

```
proj 2/
├── scripts/
│   ├── config.py              # Central configuration (tickers, params)
│   ├── data_pipeline.py       # Week 1 — yfinance data acquisition
│   ├── analytics_engine.py    # Week 2 — NumPy analytics (VaR, MC, etc.)
│   ├── export_for_tableau.py  # Tableau CSV builder
│   └── run_all.py             # Master orchestrator (runs all stages)
│
├── data/
│   ├── raw/                   # Per-ticker OHLCV CSVs
│   ├── prices.csv             # Combined closing price matrix
│   ├── log_returns.csv        # Daily log returns
│   ├── rolling_volatility.csv # 30-day rolling vol (annualised)
│   ├── correlation_matrix.csv # NxN correlation matrix
│   ├── correlation_long.csv   # Long-format for heatmap
│   ├── monte_carlo_paths.csv  # 500 sampled MC paths
│   ├── monte_carlo_terminal.csv  # 10,000 terminal values
│   ├── var_results.csv        # VaR table
│   └── data_quality_report.csv   # Week-1 quality checkpoint
│
├── tableau_exports/           # Tableau-ready CSVs (7 files)
│   ├── tab_prices.csv
│   ├── tab_volume.csv
│   ├── tab_daily_returns.csv
│   ├── tab_rolling_vol.csv
│   ├── tab_correlation.csv
│   ├── tab_monte_carlo.csv
│   ├── tab_mc_bands.csv
│   └── tab_var_summary.csv
│
├── reports/
│   └── mc_validation_report.csv   # Week-2 statistical validation
│
├── logs/                      # Timestamped execution logs
│   ├── data_pipeline.log
│   ├── analytics_engine.log
│   ├── tableau_export.log
│   └── master_run.log
│
├── tableau/
│   └── TABLEAU_BUILD_GUIDE.md  # Click-by-click Tableau build instructions
│
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Full Pipeline
```bash
python scripts/run_all.py
```

### 3. Individual Stages
```bash
# Week 1 only
python scripts/data_pipeline.py

# Week 2 only (requires Week 1 output)
python scripts/analytics_engine.py

# Tableau export (requires Week 2 output)
python scripts/export_for_tableau.py
```

### 4. Build Tableau Dashboard
See `tableau/TABLEAU_BUILD_GUIDE.md` for step-by-step instructions.

---

## Key Financial Formulas

| Metric | Formula | NumPy Implementation |
|---|---|---|
| Log Return | `ln(P_t / P_{t-1})` | `np.log(prices / prices.shift(1))` |
| Portfolio Variance | `wᵀ Σ w` | `w.T @ np.cov(returns.T)*252 @ w` |
| Rolling Volatility | `σ_t × √252` | `rolling(30).std() * np.sqrt(252)` |
| VaR (95%) | `−percentile(r, 5%) × V₀` | `np.percentile(returns, 5)` |
| Monte Carlo | `S_{t+1} = S_t · exp((μ−σ²/2)dt + σ√dt · Z)` | `np.exp(drift + diffusion * np.random.normal(...))` |
| Correlation | `ρ(X,Y) = Cov(X,Y)/(σ_X · σ_Y)` | `np.corrcoef(returns.T)` |

---

## Output Highlights

```
─────────────────────────────────────────────────────
AlphaPulse  |  Risk Monitor Output Summary
─────────────────────────────────────────────────────
Portfolio Value (start)  :  $1,000,000
Monte Carlo Horizon      :  252 trading days (1 year)
Simulations              :  10,000 paths

Value at Risk (95%)      :  See data/var_results.csv
Value at Risk (99%)      :  See data/var_results.csv

MC Median (1yr)          :  See data/monte_carlo_terminal.csv
MC 5th Percentile        :  Worst-case 95% scenario

Validation               :  See reports/mc_validation_report.csv
─────────────────────────────────────────────────────
```

---

## Dependencies

| Library | Version | Purpose |
|---|---|---|
| `yfinance` | ≥0.2.55 | Market data API |
| `numpy` | ≥1.26 | Core mathematical engine |
| `pandas` | ≥2.2 | Data manipulation |
| `scipy` | ≥1.13 | Statistical validation (skewness, kurtosis) |
| `matplotlib` | ≥3.9 | Optional: diagnostic plots |

---

*AlphaPulse v1.0.0 — Production Build*
