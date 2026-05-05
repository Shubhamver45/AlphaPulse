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

### 3. Pipeline Execution & Exports
* Ran `run_all.py` successfully. All outputs were correctly generated in:
  * `data/` (Raw and processed analysis CSVs)
  * `reports/` (Validation reports)
  * `tableau_exports/` (8 CSVs formatted specifically for Tableau)
* Added a `.gitignore` to prevent pushing large generated CSV datasets to GitHub.
* Pushed all code to the `main` branch of the GitHub repository.

## Jupyter Notebook Presentation Layer
Since the Tableau dashboard is a separate manual step, we created a comprehensive Jupyter Notebook script to visualize the backend logic live. The notebook code provided includes:
1. **Normalized Performance Comparison:** Tracking asset growth indexed to 100.
2. **Correlation Heatmap:** Visualizing cross-asset correlations.
3. **Rolling Volatility:** 30-day annualized risk trend.
4. **Monte Carlo Distribution:** Plotting simulated paths and a terminal value histogram with a 95% VaR cutoff line.
5. **Fat Tails Analysis:** Overlaying a Normal Distribution curve on the actual return density to show kurtosis.
6. **Cumulative Wealth vs Benchmark:** Plotting the AlphaPulse portfolio vs. S&P 500 tracking $1M investment growth.
7. **Maximum Drawdown Chart:** Peak-to-trough underwater chart showing max losses.
8. **Final Validation & Sharpe Ratio:** Calculating the annualized risk-adjusted return (Sharpe Ratio) and validating statistical skew/kurtosis.

## Next Steps / Pending Work
* Open Tableau Desktop, connect the 8 CSVs in `tableau_exports/` as text files, and follow `tableau/TABLEAU_BUILD_GUIDE.md` to build the frontend dashboard.
* Potential Future Enhancements: Migrating the UI to a React/Next.js dashboard, implementing dynamic data fetching via an API, or integrating more advanced models (e.g., Jump Diffusion).
