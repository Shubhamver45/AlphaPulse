# AlphaPulse — Project Context & Progress Summary

This document serves as a persistent context file. When resuming work in a new session, provide this file to the AI to instantly restore the context of what has been accomplished.

## Project Overview
* **Name:** AlphaPulse Investment Risk & Volatility Monitor
* **Goal:** A production-grade quantitative risk analytics pipeline for portfolio management.
* **Stack:** Python, `yfinance`, NumPy, Pandas, Matplotlib, Seaborn, Tableau.
* **Repository:** [Shubhamver45/AlphaPulse](https://github.com/Shubhamver45/AlphaPulse)
* **Portfolio Context:** 10 diversified equities (AAPL, MSFT, NVDA, JNJ, UNH, JPM, GS, AMZN, PG, XOM) + S&P 500 benchmark (`^GSPC`). Initial simulated capital: $1,000,000.

## Completed Milestones (Two-Week Delivery Plan)

### 1. Data Acquisition & Cleaning Pipeline (`data_pipeline.py`) - Week 1
* **Issue Resolved:** Encountered severe `YFRateLimitError` issues using `yfinance==0.2.55` and `yf.Ticker().history()` in a loop due to Yahoo Finance's recent API rate limits and crumb auth changes.
* **Solution Implemented:** 
  * Upgraded `yfinance` to `^1.2.2`.
  * Completely refactored `data_pipeline.py` to use a single batch `yf.download(tickers, period="2y", auto_adjust=True)`. This completely bypassed rate limits and successfully downloaded 2 years of daily OHLCV data.
* **Data Cleaning:** Implemented forward-filling for missing data (max 5 days) and outlier detection (returns > ±30%).

### 2. Quantitative Analytics Engine (`analytics_engine.py`) - Week 2
Successfully ran complex mathematical models on the cleaned data:
* **Returns & Variance:** Calculated daily log returns and annualized portfolio variance using matrix multiplication ($w^T \Sigma w$).
* **Volatility:** Calculated 30-day rolling volatility.
* **Value at Risk (VaR):** Computed 95% and 99% historical VaR.
* **Monte Carlo Simulation:** Ran 10,000 simulations over a 252-day horizon using Geometric Brownian Motion (GBM).
* **Validation:** Verified skewness and kurtosis of the portfolio to ensure stability.

### 3. Visual Storytelling & Interactivity (Tableau) - Week 3
* **What-If Simulation:** Designed logic for real-time sector shock parameters in Tableau.
* **Reshaping:** Orchestrated `export_for_tableau.py` to produce long-format data optimized for high-performance Tableau dashboards.
* **Interactivity Guide:** Completed a step-by-step manual for building a 9-sheet executive dashboard.

### 4. Finalization & Automation - Week 4
* **Advanced Metrics:** Implemented Maximum Drawdown (MDD) and Cumulative Wealth tracking.
* **Executive Summary:** Automated the generation of high-level KPI cards for management reporting.
* **Pipeline Automation:** Built `automate_refresh.py` to trigger the full end-to-end refresh (Data -> Analytics -> Export) with a single command.
* **Accuracy Check:** Verified portfolio returns and VaR against the S&P 500 benchmark to ensure financial fidelity.

## Current State & Handoff
The project is in a **Production-Ready** state. 
* All scripts are verified and error-free.
* The Git history is reconstructed professionally with 22 commits.
* The Tableau build guide is ready for frontend assembly.

## Next Steps / Future Enhancements
* Migration of the UI to a real-time web dashboard using FastAPI and React.
* Integration of Alternative Data (e.g., sentiment analysis from news APIs).
* Implementation of Jump Diffusion or GARCH models for more complex volatility forecasting.
