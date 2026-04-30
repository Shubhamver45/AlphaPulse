"""
=============================================================================
AlphaPulse — Tableau Export Builder
=============================================================================
Purpose : Take all /data/*.csv files produced by analytics_engine.py and
          reshape / enrich them into the exact format Tableau expects for
          each of the 6 dashboard sheets.

Outputs (all in /tableau_exports/):
  1. tab_prices.csv          → Multi-ticker line chart
  2. tab_volume.csv          → Volume bar chart
  3. tab_daily_returns.csv   → Daily returns bar/area chart
  4. tab_rolling_vol.csv     → 30-day rolling volatility lines
  5. tab_correlation.csv     → Heatmap (long format: Asset_X, Asset_Y, Corr)
  6. tab_monte_carlo.csv     → Fan chart (Simulation, Day, Portfolio_Value)
  7. tab_var_summary.csv     → VaR summary KPI card

Run:
    python scripts/export_for_tableau.py
=============================================================================
"""

import os
import sys
import logging
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as CFG

os.makedirs(CFG.TABLEAU_DIR, exist_ok=True)
os.makedirs(CFG.LOGS_DIR,    exist_ok=True)

log_path = os.path.join(CFG.LOGS_DIR, "tableau_export.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    handlers=[
        logging.FileHandler(log_path, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("AlphaPulse.TableauExport")

SECTOR_MAP = {k: v["sector"] for k, v in CFG.PORTFOLIO.items()}
SECTOR_MAP[CFG.BENCHMARK] = "Index"

NAME_MAP = {k: v["name"] for k, v in CFG.PORTFOLIO.items()}
NAME_MAP[CFG.BENCHMARK] = "S&P 500"


def load_csv(filename: str) -> pd.DataFrame:
    path = os.path.join(CFG.DATA_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Required file not found: {path}\n"
            f"Run scripts/analytics_engine.py first."
        )
    return pd.read_csv(path, parse_dates=["Date"]) if "date" in filename.lower() or filename == "prices.csv" or filename == "log_returns.csv" or filename == "rolling_volatility.csv" else pd.read_csv(path)


def load_date_csv(filename: str) -> pd.DataFrame:
    path = os.path.join(CFG.DATA_DIR, filename)
    return pd.read_csv(path, index_col="Date", parse_dates=True)


# ─────────────────────────────────────────────────────────────────────────────
def export_prices():
    """Long-format closing prices for multi-line Tableau chart."""
    df = load_date_csv("prices.csv")
    long = (df.reset_index()
              .melt(id_vars="Date", var_name="Ticker", value_name="Close"))
    long["Company"]  = long["Ticker"].map(NAME_MAP)
    long["Sector"]   = long["Ticker"].map(SECTOR_MAP)
    long["Type"]     = long["Ticker"].apply(
        lambda x: "Benchmark" if x == CFG.BENCHMARK else "Portfolio Stock")
    out = os.path.join(CFG.TABLEAU_DIR, "tab_prices.csv")
    long.to_csv(out, index=False)
    log.info(f"  ✓ tab_prices.csv        → {len(long):,} rows")
    return long


def export_volume():
    """Volume bars enriched with sector and company name."""
    df = pd.read_csv(os.path.join(CFG.DATA_DIR, "volume.csv"), parse_dates=["Date"])
    df["Company"] = df["Ticker"].map(NAME_MAP)
    df["Sector"]  = df["Ticker"].map(SECTOR_MAP)
    out = os.path.join(CFG.TABLEAU_DIR, "tab_volume.csv")
    df.to_csv(out, index=False)
    log.info(f"  ✓ tab_volume.csv        → {len(df):,} rows")
    return df


def export_daily_returns():
    """Daily log returns + simple pct-return for Tableau area/bar chart."""
    df = load_date_csv("log_returns.csv")
    long = (df.reset_index()
              .melt(id_vars="Date", var_name="Ticker", value_name="Log_Return"))
    long["Company"] = long["Ticker"].map(NAME_MAP)
    long["Sector"]  = long["Ticker"].map(SECTOR_MAP)
    long["Pct_Return"] = (np.exp(long["Log_Return"]) - 1) * 100
    long["Positive"]   = (long["Pct_Return"] >= 0).astype(int)
    out = os.path.join(CFG.TABLEAU_DIR, "tab_daily_returns.csv")
    long.to_csv(out, index=False)
    log.info(f"  ✓ tab_daily_returns.csv → {len(long):,} rows")
    return long


def export_rolling_volatility():
    """30-day rolling annualised volatility for each ticker."""
    df = load_date_csv("rolling_volatility.csv")
    long = (df.reset_index()
              .melt(id_vars="Date", var_name="Ticker", value_name="Rolling_Vol_Annual"))
    long["Rolling_Vol_Pct"] = long["Rolling_Vol_Annual"] * 100
    long["Company"] = long["Ticker"].map(NAME_MAP)
    long["Sector"]  = long["Ticker"].map(SECTOR_MAP)
    out = os.path.join(CFG.TABLEAU_DIR, "tab_rolling_vol.csv")
    long.to_csv(out, index=False)
    log.info(f"  ✓ tab_rolling_vol.csv   → {len(long):,} rows")
    return long


def export_correlation():
    """Long-format correlation matrix for Tableau heatmap."""
    df = pd.read_csv(os.path.join(CFG.DATA_DIR, "correlation_long.csv"))
    df["Company_X"] = df["Asset_X"].map(NAME_MAP)
    df["Company_Y"] = df["Asset_Y"].map(NAME_MAP)
    df["Corr_Pct"]  = (df["Correlation"] * 100).round(1)
    df["Strength"]  = pd.cut(df["Correlation"].abs(),
                              bins=[0, 0.2, 0.5, 0.8, 1.0],
                              labels=["Weak", "Moderate", "Strong", "Very Strong"],
                              include_lowest=True)
    out = os.path.join(CFG.TABLEAU_DIR, "tab_correlation.csv")
    df.to_csv(out, index=False)
    log.info(f"  ✓ tab_correlation.csv   → {len(df):,} rows")
    return df


def export_monte_carlo():
    """Monte Carlo sampled paths — already built in analytics_engine."""
    src = os.path.join(CFG.DATA_DIR, "monte_carlo_paths.csv")
    df  = pd.read_csv(src)

    # Add percentile bands (computed across all simulations at each day)
    pivot = df.pivot(index="Day", columns="Simulation", values="Portfolio_Value")
    bands = pd.DataFrame({
        "Day":    pivot.index,
        "P5":     np.percentile(pivot.values, 5,  axis=1),
        "P25":    np.percentile(pivot.values, 25, axis=1),
        "Median": np.percentile(pivot.values, 50, axis=1),
        "P75":    np.percentile(pivot.values, 75, axis=1),
        "P95":    np.percentile(pivot.values, 95, axis=1),
    })

    out_paths = os.path.join(CFG.TABLEAU_DIR, "tab_monte_carlo.csv")
    df.to_csv(out_paths, index=False)

    out_bands = os.path.join(CFG.TABLEAU_DIR, "tab_mc_bands.csv")
    bands.to_csv(out_bands, index=False)
    log.info(f"  ✓ tab_monte_carlo.csv   → {len(df):,} rows")
    log.info(f"  ✓ tab_mc_bands.csv      → {len(bands):,} rows (percentile bands)")
    return df


def export_var_summary():
    """VaR KPI summary card."""
    df   = pd.read_csv(os.path.join(CFG.DATA_DIR, "var_results.csv"))
    df.rename(columns={"Unnamed: 0": "VaR_Level"}, inplace=True)
    df["VaR_Description"] = df["VaR_Level"].map({
        "VaR_95": "95% Confidence — 1-day maximum expected loss",
        "VaR_99": "99% Confidence — 1-day maximum expected loss (tail risk)",
    })
    df["Initial_Portfolio"] = CFG.INITIAL_PORTFOLIO_VALUE
    out = os.path.join(CFG.TABLEAU_DIR, "tab_var_summary.csv")
    df.to_csv(out, index=False)
    log.info(f"  ✓ tab_var_summary.csv   → {len(df):,} rows")
    return df


# ─────────────────────────────────────────────────────────────────────────────
def run():
    log.info("=" * 60)
    log.info("AlphaPulse  |  Tableau Export Builder  |  START")
    log.info("=" * 60)

    export_prices()
    export_volume()
    export_daily_returns()
    export_rolling_volatility()
    export_correlation()
    export_monte_carlo()
    export_var_summary()

    log.info("\n" + "=" * 60)
    log.info("ALL TABLEAU EXPORTS COMPLETE")
    log.info(f"Files ready in : {CFG.TABLEAU_DIR}")
    log.info("=" * 60)


if __name__ == "__main__":
    run()
