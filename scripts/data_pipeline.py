"""
=============================================================================
AlphaPulse — Week 1: Data Acquisition & Cleaning Pipeline
=============================================================================
Purpose : Fetch 2-year daily OHLCV data for 10 portfolio stocks + S&P 500
          benchmark using a single yf.download() batch call.

Critical Review Point (Manager Checkpoint):
  ✓ auto_adjust=True  → prices retroactively corrected for splits & dividends
  ✓ Single batch yf.download() for all tickers — avoids per-ticker rate limits
  ✓ Exponential-backoff retry (up to 5 attempts) on batch failure
  ✓ Missing-value imputation & outlier detection logged to /logs/
  ✓ Data quality report written to data/data_quality_report.csv

Run:
    python scripts/data_pipeline.py
============================================================================="""

import os
import sys
import time
import logging
import warnings
from datetime import datetime

import random
import numpy as np
import pandas as pd
import yfinance as yf

# ── resolve repo root so script works from any cwd ───────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as CFG

warnings.filterwarnings("ignore")

# ── Logging ──────────────────────────────────────────────────────────────────
os.makedirs(CFG.LOGS_DIR, exist_ok=True)
os.makedirs(CFG.DATA_DIR, exist_ok=True)

log_path = os.path.join(CFG.LOGS_DIR, "data_pipeline.log")
# Clear existing handlers to avoid duplicates on re-run
for h in logging.root.handlers[:]:
    logging.root.removeHandler(h)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    handlers=[
        logging.FileHandler(log_path, encoding="utf-8", mode="w"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("AlphaPulse.Pipeline")


# ─────────────────────────────────────────────────────────────────────────────
# Step 1: Batch download with exponential-backoff retry
# ─────────────────────────────────────────────────────────────────────────────
def batch_download(symbols: list) -> pd.DataFrame:
    """
    Single yf.download() call for all symbols.
    Returns MultiIndex DataFrame (Price x Ticker).
    Retries up to MAX_RETRIES with exponential back-off.
    """
    backoff = CFG.RETRY_BACKOFF
    for attempt in range(1, CFG.MAX_RETRIES + 1):
        try:
            log.info(f"  Batch download attempt {attempt}/{CFG.MAX_RETRIES} "
                     f"({len(symbols)} symbols, period=2y)")
            raw = yf.download(
                tickers   = symbols,
                period    = "2y",
                interval  = CFG.INTERVAL,
                auto_adjust = CFG.AUTO_ADJUST,
                progress  = False,
                threads   = True,
            )
            if raw is None or raw.empty:
                raise ValueError("yf.download() returned empty DataFrame")
            log.info(f"  ✓ Batch download OK — "
                     f"{raw.shape[0]} rows × {raw.shape[1]} cols")
            return raw
        except Exception as exc:
            if attempt < CFG.MAX_RETRIES:
                wait = backoff + random.uniform(1.0, 3.0)
                log.warning(f"  ✗ Attempt {attempt} failed: {exc}. "
                            f"Retrying in {wait:.1f}s …")
                time.sleep(wait)
                backoff = min(backoff * 2, 60)
            else:
                log.error(f"  ✗✗ All {CFG.MAX_RETRIES} attempts failed.")
                raise


# ─────────────────────────────────────────────────────────────────────────────
# Step 2: Extract Close price matrix
# ─────────────────────────────────────────────────────────────────────────────
def extract_close(raw: pd.DataFrame) -> pd.DataFrame:
    """
    Extract the Close sub-frame from the MultiIndex batch result.
    yfinance 1.x returns (Price, Ticker) MultiIndex — raw['Close']
    gives a clean (Date x Ticker) DataFrame directly.
    """
    # Strip timezone if present
    if hasattr(raw.index, "tz") and raw.index.tz is not None:
        raw.index = raw.index.tz_localize(None)
    raw.index.name = "Date"

    prices = raw["Close"].copy()
    # Drop fully-empty ticker columns
    prices.dropna(axis=1, how="all", inplace=True)
    log.info(f"  Close frame: {prices.shape[0]} dates × "
             f"{prices.shape[1]} tickers")
    log.info(f"  Tickers available: {prices.columns.tolist()}")
    return prices


# ─────────────────────────────────────────────────────────────────────────────
# Step 3: Extract OHLCV per ticker (for raw CSVs & volume)
# ─────────────────────────────────────────────────────────────────────────────
def extract_ohlcv(raw: pd.DataFrame, symbols: list) -> dict:
    """Return {ticker: OHLCV DataFrame} from the batch MultiIndex result."""
    ohlcv = {}
    price_cols = ["Open", "High", "Low", "Close", "Volume"]
    for sym in symbols:
        try:
            df = raw.xs(sym, axis=1, level=1)
            keep = [c for c in price_cols if c in df.columns]
            df   = df[keep].dropna(subset=["Close"])
            if not df.empty:
                ohlcv[sym] = df
        except (KeyError, Exception):
            pass
    return ohlcv


# ─────────────────────────────────────────────────────────────────────────────
# Step 4: Quality checks
# ─────────────────────────────────────────────────────────────────────────────
def quality_check(ticker: str, series: pd.Series) -> dict:
    rpt = {
        "ticker":      ticker,
        "total_rows":  len(series),
        "date_start":  str(series.index.min().date()),
        "date_end":    str(series.index.max().date()),
    }
    daily_ret  = series.pct_change()
    extreme    = int((daily_ret.abs() > 0.30).sum())
    non_pos    = int((series <= 0).sum())
    rpt["extreme_daily_moves_gt30pct"] = extreme
    rpt["non_positive_price_rows"]     = non_pos
    rpt["final_rows"]                  = len(series)
    rpt["quality_pass"]                = (non_pos == 0)
    if extreme:
        log.warning(f"  ⚠ {ticker}: {extreme} extreme daily move(s) >±30%")
    return rpt


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def run():
    log.info("=" * 70)
    log.info("AlphaPulse  |  Week-1 Data Acquisition Pipeline  |  START")
    log.info(f"Run timestamp : {datetime.now().isoformat()}")
    log.info("=" * 70)

    all_symbols = CFG.TICKERS + [CFG.BENCHMARK]
    log.info(f"Symbols ({len(all_symbols)}): {all_symbols}")

    # ── 1: Batch download ─────────────────────────────────────────────────────
    log.info("\n── Step 1: Batch download ──")
    raw = batch_download(all_symbols)

    # ── 2: Extract Close matrix ───────────────────────────────────────────────
    log.info("\n── Step 2: Extract Close prices ──")
    prices_df = extract_close(raw)

    if prices_df.empty or len(prices_df.columns) == 0:
        raise RuntimeError("No Close data found in batch result. "
                           "Check internet connection and try again.")

    # ── 3: Clean price matrix ─────────────────────────────────────────────────
    log.info("\n── Step 3: Clean & align price matrix ──")
    prices_df.sort_index(inplace=True)
    prices_df.dropna(how="all", inplace=True)
    prices_df.ffill(limit=2, inplace=True)
    prices_df.dropna(inplace=True)
    log.info(f"  Clean matrix: {prices_df.shape[0]} trading days × "
             f"{prices_df.shape[1]} tickers")

    # ── 4: Quality checks ─────────────────────────────────────────────────────
    log.info("\n── Step 4: Quality checks ──")
    qc_reports = []
    for col in prices_df.columns:
        qr = quality_check(col, prices_df[col])
        qc_reports.append(qr)
        log.info(f"  {col}: {'PASS' if qr['quality_pass'] else 'WARN'} | "
                 f"{qr['final_rows']} rows | "
                 f"{qr['date_start']} → {qr['date_end']}")

    # ── 5: Save outputs ───────────────────────────────────────────────────────
    log.info("\n── Step 5: Saving outputs ──")

    # prices.csv
    prices_path = os.path.join(CFG.DATA_DIR, "prices.csv")
    prices_df.to_csv(prices_path)
    log.info(f"  ✓ Saved → {prices_path}")

    # Per-ticker OHLCV raw CSVs
    raw_dir = os.path.join(CFG.DATA_DIR, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    ohlcv_dict = extract_ohlcv(raw, prices_df.columns.tolist())
    for ticker, df_t in ohlcv_dict.items():
        df_t.to_csv(os.path.join(raw_dir, f"{ticker}_ohlcv.csv"))
    log.info(f"  ✓ Saved {len(ohlcv_dict)} OHLCV files → {raw_dir}")

    # Volume CSV for Tableau
    vol_frames = []
    for sym, df_t in ohlcv_dict.items():
        if "Volume" in df_t.columns:
            tmp            = df_t[["Volume"]].copy()
            tmp["Ticker"]  = sym
            tmp["Sector"]  = CFG.PORTFOLIO.get(sym, {}).get("sector", "Index")
            vol_frames.append(tmp.reset_index())
    if vol_frames:
        vol_df   = pd.concat(vol_frames, ignore_index=True)
        vol_path = os.path.join(CFG.DATA_DIR, "volume.csv")
        vol_df.to_csv(vol_path, index=False)
        log.info(f"  ✓ Saved → {vol_path}")

    # Data quality report
    qc_df   = pd.DataFrame(qc_reports)
    qc_path = os.path.join(CFG.DATA_DIR, "data_quality_report.csv")
    qc_df.to_csv(qc_path, index=False)
    log.info(f"  ✓ Saved → {qc_path}")

    # ── Summary ───────────────────────────────────────────────────────────────
    passed = sum(1 for r in qc_reports if r["quality_pass"])
    log.info("\n" + "=" * 70)
    log.info("PIPELINE COMPLETE")
    log.info(f"  Tickers        : {prices_df.columns.tolist()}")
    log.info(f"  Date range     : {prices_df.index.min().date()} "
             f"→ {prices_df.index.max().date()}")
    log.info(f"  Trading days   : {len(prices_df)}")
    log.info(f"  Quality PASS   : {passed}/{len(qc_reports)}")
    log.info("=" * 70)

    return prices_df


if __name__ == "__main__":
    run()
