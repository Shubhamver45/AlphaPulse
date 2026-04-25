"""
=============================================================================
AlphaPulse — Week 2: Quantitative Analytics Engine
=============================================================================
Purpose  : Core NumPy-powered financial calculations on the clean prices
           produced by data_pipeline.py.

Calculations:
  1. Daily Log Returns           — np.log(P_t / P_{t-1})
  2. Portfolio-weighted Returns  — matrix algebra with asset weights
  3. Rolling 30-day Volatility   — annualised standard deviation
  4. Correlation Matrix          — np.corrcoef() on returns
  5. Value at Risk (VaR)         — 95 % and 99 % historical simulation
  6. Monte Carlo Simulation      — 10,000 paths × 252 trading days
                                   using Geometric Brownian Motion

Statistical Validation (Critical Review Point — Week 2):
  • Compare MC distribution skewness & kurtosis to historical returns
  • Print Pass/Fail verdict for manager review

Run:
    python scripts/analytics_engine.py     (runs data_pipeline first if needed)
=============================================================================
"""

import os
import sys
import logging
from datetime import datetime

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as CFG

# ── Logging ──────────────────────────────────────────────────────────────────
os.makedirs(CFG.LOGS_DIR, exist_ok=True)
log_path = os.path.join(CFG.LOGS_DIR, "analytics_engine.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    handlers=[
        logging.FileHandler(log_path, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("AlphaPulse.Analytics")

np.random.seed(42)   # reproducible results for manager review


# ─────────────────────────────────────────────────────────────────────────────
# 1. Daily Log Returns
# ─────────────────────────────────────────────────────────────────────────────
def compute_log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Log return: r_t = ln(P_t / P_{t-1})

    Why log returns?
      • Additive over time  (multi-period sums are valid)
      • Symmetrical around 0  (no downward bias vs simple returns)
      • More normally distributed — required assumption for VaR & Monte Carlo
    """
    log.info("Computing daily log returns …")
    log_ret = np.log(prices / prices.shift(1))
    log_ret.dropna(inplace=True)
    path = os.path.join(CFG.DATA_DIR, "log_returns.csv")
    log_ret.to_csv(path)
    log.info(f"  Shape: {log_ret.shape}   Saved → {path}")
    return log_ret


# ─────────────────────────────────────────────────────────────────────────────
# 2. Portfolio-weighted Returns
# ─────────────────────────────────────────────────────────────────────────────
def compute_portfolio_returns(log_ret: pd.DataFrame,
                               weights: np.ndarray) -> pd.Series:
    """
    Portfolio daily return = w · r  (dot product of weights × asset returns)
    Portfolio variance     = wᵀ Σ w  (matrix multiplication via np.dot)
    """
    log.info("Computing portfolio-weighted returns …")
    # Only use equity tickers (exclude benchmark from return calculation)
    equity_cols = [c for c in log_ret.columns if c != CFG.BENCHMARK]
    ret_matrix  = log_ret[equity_cols].values          # shape (T, N)
    w           = np.array(weights)                    # shape (N,)

    portfolio_ret = ret_matrix @ w                     # shape (T,)
    portfolio_ret = pd.Series(portfolio_ret,
                               index=log_ret.index,
                               name="Portfolio")

    # Covariance matrix (annualised)
    cov_matrix = np.cov(ret_matrix.T) * 252            # shape (N, N)
    port_variance = w.T @ cov_matrix @ w               # scalar — wᵀΣw
    port_annualised_vol = np.sqrt(port_variance)

    log.info(f"  Annualised portfolio volatility : {port_annualised_vol:.4f} "
             f"({port_annualised_vol*100:.2f} %)")

    path = os.path.join(CFG.DATA_DIR, "portfolio_returns.csv")
    portfolio_ret.to_csv(path)
    log.info(f"  Saved → {path}")
    return portfolio_ret, cov_matrix


# ─────────────────────────────────────────────────────────────────────────────
# 3. Rolling 30-Day Volatility
# ─────────────────────────────────────────────────────────────────────────────
def compute_rolling_volatility(log_ret: pd.DataFrame,
                                window: int = CFG.ROLLING_WINDOW) -> pd.DataFrame:
    """
    Annualised rolling std-dev of log returns.
    σ_t = rolling_std(r_t, window=30) × √252
    """
    log.info(f"Computing {window}-day rolling volatility (annualised) …")
    rolling_vol = log_ret.rolling(window=window).std() * np.sqrt(252)
    rolling_vol.dropna(inplace=True)

    path = os.path.join(CFG.DATA_DIR, "rolling_volatility.csv")
    rolling_vol.to_csv(path)
    log.info(f"  Shape: {rolling_vol.shape}   Saved → {path}")
    return rolling_vol


# ─────────────────────────────────────────────────────────────────────────────
# 4. Correlation Matrix
# ─────────────────────────────────────────────────────────────────────────────
def compute_correlation(log_ret: pd.DataFrame) -> pd.DataFrame:
    """
    Pearson correlation matrix of log returns using np.corrcoef.
    Values range [−1, +1]:
      +1 → perfect positive correlation (move together)
       0 → no linear correlation
      −1 → perfect negative correlation (hedge)
    """
    log.info("Computing asset correlation matrix …")
    equity_cols = [c for c in log_ret.columns if c != CFG.BENCHMARK]
    ret_matrix  = log_ret[equity_cols].values.T     # shape (N, T) for corrcoef
    corr_matrix = np.corrcoef(ret_matrix)           # np.corrcoef — shape (N, N)

    corr_df = pd.DataFrame(corr_matrix,
                            index=equity_cols,
                            columns=equity_cols)

    path = os.path.join(CFG.DATA_DIR, "correlation_matrix.csv")
    corr_df.to_csv(path)
    log.info(f"  Saved → {path}")

    # Also produce a long-format version for Tableau heatmap
    corr_long = (corr_df
                 .reset_index()
                 .melt(id_vars="index", var_name="Asset_Y", value_name="Correlation")
                 .rename(columns={"index": "Asset_X"}))
    long_path = os.path.join(CFG.DATA_DIR, "correlation_long.csv")
    corr_long.to_csv(long_path, index=False)
    log.info(f"  Long-format → {long_path}")

    return corr_df


# ─────────────────────────────────────────────────────────────────────────────
# 5. Value at Risk (VaR)
# ─────────────────────────────────────────────────────────────────────────────
def compute_var(portfolio_ret: pd.Series,
                initial_value: float = CFG.INITIAL_PORTFOLIO_VALUE) -> dict:
    """
    Historical-simulation VaR.
      VaR_α = − percentile(r, (1−α) × 100 ) × Portfolio Value

    Interpretation: With α=0.95 confidence, the portfolio will NOT lose more
    than VaR_95 on any given day.
    """
    log.info("Computing Value at Risk (VaR) …")
    results = {}
    for conf in CFG.VAR_CONFIDENCE_LEVELS:
        cutoff  = np.percentile(portfolio_ret.values, (1 - conf) * 100)
        var_val = -cutoff * initial_value
        results[f"VaR_{int(conf*100)}"] = {
            "confidence":      conf,
            "daily_return_cutoff": round(cutoff, 6),
            "VaR_dollar":      round(var_val, 2),
            "VaR_pct":         round(-cutoff * 100, 4),
        }
        log.info(f"  VaR {int(conf*100)}%  →  ${var_val:,.0f}  "
                 f"({-cutoff*100:.2f}%  of portfolio)")

    var_df = pd.DataFrame(results).T
    path   = os.path.join(CFG.DATA_DIR, "var_results.csv")
    var_df.to_csv(path)
    log.info(f"  Saved → {path}")
    return results


# ─────────────────────────────────────────────────────────────────────────────
# 6. Monte Carlo Simulation — Geometric Brownian Motion
# ─────────────────────────────────────────────────────────────────────────────
def run_monte_carlo(portfolio_ret: pd.Series,
                    n_simulations: int = CFG.MC_SIMULATIONS,
                    horizon: int      = CFG.MC_HORIZON_DAYS,
                    initial_value: float = CFG.INITIAL_PORTFOLIO_VALUE) -> dict:
    """
    Simulate N portfolio-value paths over `horizon` trading days.

    Model: Geometric Brownian Motion
        S_{t+1} = S_t × exp( (μ − σ²/2)Δt + σ√Δt × Z )
    where Z ~ N(0,1) drawn via np.random.normal (vectorised, no Python loop).

    Why GBM?
      • Prices are always positive (exponential form)
      • Percentage returns are log-normally distributed (empirically validated)
      • Industry-standard assumption in risk management (Black-Scholes)
    """
    log.info(f"\n{'='*60}")
    log.info(f"Monte Carlo Simulation  |  {n_simulations:,} paths × {horizon} days")
    log.info(f"{'='*60}")

    daily_ret_arr = portfolio_ret.values
    mu    = np.mean(daily_ret_arr)       # mean daily log return
    sigma = np.std(daily_ret_arr)        # daily std dev

    log.info(f"  μ (daily mean return)  : {mu:.6f}")
    log.info(f"  σ (daily std dev)      : {sigma:.6f}")
    log.info(f"  Annualised μ           : {mu*252*100:.2f}%")
    log.info(f"  Annualised σ           : {sigma*np.sqrt(252)*100:.2f}%")

    # ── Vectorised GBM — shape: (n_simulations, horizon) ─────────────────────
    dt         = 1.0                                       # one trading day
    drift      = (mu - 0.5 * sigma ** 2) * dt             # drift term
    diffusion  = sigma * np.sqrt(dt)                       # diffusion coefficient

    # Draw all random shocks at once — shape (n_simulations, horizon)
    Z          = np.random.normal(0, 1, (n_simulations, horizon))
    daily_step = np.exp(drift + diffusion * Z)             # log-normal daily factor

    # Cumulative product along the time axis → price paths
    cum_returns  = np.cumprod(daily_step, axis=1)          # shape (n_sims, horizon)
    price_paths  = initial_value * cum_returns             # absolute portfolio values

    # ── Terminal value statistics ─────────────────────────────────────────────
    terminal = price_paths[:, -1]                          # final day values
    stats_dict = {
        "mean":     float(np.mean(terminal)),
        "median":   float(np.median(terminal)),
        "std":      float(np.std(terminal)),
        "p5":       float(np.percentile(terminal, 5)),
        "p25":      float(np.percentile(terminal, 25)),
        "p75":      float(np.percentile(terminal, 75)),
        "p95":      float(np.percentile(terminal, 95)),
        "min":      float(np.min(terminal)),
        "max":      float(np.max(terminal)),
        "skewness": float(stats.skew(terminal)),
        "kurtosis": float(stats.kurtosis(terminal, fisher=True)),
    }

    log.info(f"\n  Terminal portfolio value statistics (after {horizon} days):")
    log.info(f"  {'Mean':<22}: ${stats_dict['mean']:>14,.0f}")
    log.info(f"  {'Median':<22}: ${stats_dict['median']:>14,.0f}")
    log.info(f"  {'5th Percentile (VaR)':<22}: ${stats_dict['p5']:>14,.0f}")
    log.info(f"  {'95th Percentile':<22}: ${stats_dict['p95']:>14,.0f}")
    log.info(f"  {'Min':<22}: ${stats_dict['min']:>14,.0f}")
    log.info(f"  {'Max':<22}: ${stats_dict['max']:>14,.0f}")
    log.info(f"  {'Skewness':<22}: {stats_dict['skewness']:>14.4f}")
    log.info(f"  {'Excess Kurtosis':<22}: {stats_dict['kurtosis']:>14.4f}")

    # ── Save summary paths for Tableau (sampled to 500 paths to keep file small) ──
    n_sample = min(500, n_simulations)
    idx      = np.random.choice(n_simulations, n_sample, replace=False)
    sampled  = price_paths[idx, :]          # shape (500, 252)

    days_arr = np.arange(1, horizon + 1)
    mc_long  = []
    for i, path in enumerate(sampled):
        for d, val in zip(days_arr, path):
            mc_long.append({"Simulation": i, "Day": d, "Portfolio_Value": round(val, 2)})

    mc_df    = pd.DataFrame(mc_long)
    mc_path  = os.path.join(CFG.DATA_DIR, "monte_carlo_paths.csv")
    mc_df.to_csv(mc_path, index=False)
    log.info(f"\n  Saved {n_sample} sampled paths → {mc_path}")

    # ── Save terminal distribution for histogram ──────────────────────────────
    term_df = pd.DataFrame({"Terminal_Value": terminal})
    term_path = os.path.join(CFG.DATA_DIR, "monte_carlo_terminal.csv")
    term_df.to_csv(term_path, index=False)
    log.info(f"  Saved terminal distribution → {term_path}")

    return {
        "price_paths":   price_paths,
        "terminal":      terminal,
        "stats":         stats_dict,
        "mu":            mu,
        "sigma":         sigma,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 7. Statistical Validation  (Critical Review Point — Week 2)
# ─────────────────────────────────────────────────────────────────────────────
def validate_monte_carlo(mc_result: dict, portfolio_ret: pd.Series) -> None:
    """
    Compare the Monte Carlo simulated output distribution against
    historical return distribution using skewness and kurtosis.

    Validation criteria (industry standard):
      | Skewness  difference | < 0.5   → PASS
      | Kurtosis  difference | < 1.5   → PASS

    A PASS on both metrics means the MC model faithfully replicates the
    statistical shape of observed market returns.
    """
    log.info("\n" + "=" * 60)
    log.info("Statistical Validation  (Week-2 Critical Review Point)")
    log.info("=" * 60)

    hist_ret  = portfolio_ret.values
    mc_term   = mc_result["terminal"]
    mc_daily  = np.log(mc_result["price_paths"][:, 1:] /
                        mc_result["price_paths"][:, :-1]).flatten()

    hist_skew = stats.skew(hist_ret)
    hist_kurt = stats.kurtosis(hist_ret, fisher=True)
    mc_skew   = stats.skew(mc_daily)
    mc_kurt   = stats.kurtosis(mc_daily, fisher=True)

    log.info(f"\n  {'Metric':<28} {'Historical':>12}  {'MC Simulated':>14}  {'Δ':>8}")
    log.info(f"  {'-'*68}")
    log.info(f"  {'Skewness':<28} {hist_skew:>12.4f}  {mc_skew:>14.4f}  "
             f"{abs(hist_skew-mc_skew):>8.4f}")
    log.info(f"  {'Excess Kurtosis':<28} {hist_kurt:>12.4f}  {mc_kurt:>14.4f}  "
             f"{abs(hist_kurt-mc_kurt):>8.4f}")

    skew_pass = abs(hist_skew - mc_skew) < 0.5
    kurt_pass = abs(hist_kurt - mc_kurt) < 1.5

    log.info(f"\n  Skewness  validation : {'✓ PASS' if skew_pass else '✗ FAIL'}")
    log.info(f"  Kurtosis  validation : {'✓ PASS' if kurt_pass else '✗ FAIL'}")
    overall   = "✓ PASS — MC model is statistically valid" if (skew_pass and kurt_pass) \
                else "✗ FAIL — Review model parameters"
    log.info(f"\n  Overall result       : {overall}")

    # Save validation report
    vr = pd.DataFrame([{
        "metric":         "Skewness",
        "historical":     round(hist_skew, 6),
        "mc_simulated":   round(mc_skew, 6),
        "delta":          round(abs(hist_skew - mc_skew), 6),
        "threshold":      0.50,
        "pass":           skew_pass,
    }, {
        "metric":         "Excess Kurtosis",
        "historical":     round(hist_kurt, 6),
        "mc_simulated":   round(mc_kurt, 6),
        "delta":          round(abs(hist_kurt - mc_kurt), 6),
        "threshold":      1.50,
        "pass":           kurt_pass,
    }])
    vr["overall_pass"] = skew_pass and kurt_pass
    vr_path = os.path.join(CFG.REPORTS_DIR, "mc_validation_report.csv")
    os.makedirs(CFG.REPORTS_DIR, exist_ok=True)
    vr.to_csv(vr_path, index=False)
    log.info(f"\n  Validation report saved → {vr_path}")
    log.info("=" * 60)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def run():
    log.info("=" * 70)
    log.info("AlphaPulse  |  Week-2 Analytics Engine  |  START")
    log.info(f"Run timestamp : {datetime.now().isoformat()}")
    log.info("=" * 70)

    # ── Load prices (run pipeline first if CSVs are missing) ─────────────────
    prices_path = os.path.join(CFG.DATA_DIR, "prices.csv")
    if not os.path.exists(prices_path):
        log.info("prices.csv not found — running data pipeline first …")
        import data_pipeline
        data_pipeline.run()

    prices = pd.read_csv(prices_path, index_col="Date", parse_dates=True)
    log.info(f"Loaded prices: {prices.shape}  "
             f"({prices.index.min().date()} → {prices.index.max().date()})")

    weights = np.array(CFG.WEIGHTS)
    weights = weights / weights.sum()          # ensure exact sum=1

    # ── Execute all analytics ─────────────────────────────────────────────────
    log_ret        = compute_log_returns(prices)
    port_ret, cov  = compute_portfolio_returns(log_ret, weights)
    rolling_vol    = compute_rolling_volatility(log_ret)
    corr_df        = compute_correlation(log_ret)
    var_results    = compute_var(port_ret)
    mc_result      = run_monte_carlo(port_ret)
    validate_monte_carlo(mc_result, port_ret)

    log.info("\n" + "=" * 70)
    log.info("ANALYTICS ENGINE COMPLETE — All outputs in /data/")
    log.info("=" * 70)

    return {
        "log_ret":     log_ret,
        "port_ret":    port_ret,
        "rolling_vol": rolling_vol,
        "corr_df":     corr_df,
        "var_results": var_results,
        "mc_result":   mc_result,
    }


if __name__ == "__main__":
    run()
