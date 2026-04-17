# =============================================================================
# AlphaPulse — Central Configuration
# Project   : Investment Risk & Volatility Monitor
# Author    : AlphaPulse Analytics Team
# Version   : 1.0.0  (Production)
# =============================================================================

# ── Portfolio Definition ─────────────────────────────────────────────────────
# 10 diversified equities + S&P 500 benchmark (11 symbols total)
PORTFOLIO = {
    # Technology
    "AAPL":  {"name": "Apple Inc.",            "sector": "Technology",        "weight": 0.12},
    "MSFT":  {"name": "Microsoft Corp.",       "sector": "Technology",        "weight": 0.12},
    "NVDA":  {"name": "NVIDIA Corp.",          "sector": "Technology",        "weight": 0.08},
    # Healthcare
    "JNJ":   {"name": "Johnson & Johnson",     "sector": "Healthcare",        "weight": 0.10},
    "UNH":   {"name": "UnitedHealth Group",    "sector": "Healthcare",        "weight": 0.08},
    # Financials
    "JPM":   {"name": "JPMorgan Chase",        "sector": "Financials",        "weight": 0.10},
    "GS":    {"name": "Goldman Sachs",         "sector": "Financials",        "weight": 0.08},
    # Consumer
    "AMZN":  {"name": "Amazon.com Inc.",       "sector": "Consumer Discret.", "weight": 0.12},
    "PG":    {"name": "Procter & Gamble",      "sector": "Consumer Staples",  "weight": 0.10},
    # Energy
    "XOM":   {"name": "Exxon Mobil Corp.",     "sector": "Energy",            "weight": 0.10},
}

# Benchmark index
BENCHMARK = "^GSPC"   # S&P 500

TICKERS = list(PORTFOLIO.keys())
WEIGHTS  = [v["weight"] for v in PORTFOLIO.values()]   # must sum to 1.0

# ── Data Parameters ───────────────────────────────────────────────────────────
HISTORY_PERIOD   = "2y"         # 2 years of daily OHLCV
INTERVAL         = "1d"
AUTO_ADJUST      = True         # Corrects for stock splits & dividend payouts

# ── Monte Carlo Parameters ────────────────────────────────────────────────────
MC_SIMULATIONS   = 10_000       # Number of simulation paths
MC_HORIZON_DAYS  = 252          # 1 trading year
INITIAL_PORTFOLIO_VALUE = 1_000_000   # $1 000 000 starting capital

# ── Risk Parameters ───────────────────────────────────────────────────────────
VAR_CONFIDENCE_LEVELS = [0.95, 0.99]   # 95 % and 99 % VaR
ROLLING_WINDOW = 30                     # 30-day rolling volatility

# ── Paths ─────────────────────────────────────────────────────────────────────
import os
BASE_DIR         = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR         = os.path.join(BASE_DIR, "data")
TABLEAU_DIR      = os.path.join(BASE_DIR, "tableau_exports")
REPORTS_DIR      = os.path.join(BASE_DIR, "reports")
LOGS_DIR         = os.path.join(BASE_DIR, "logs")

# ── API Resilience ────────────────────────────────────────────────────────────
MAX_RETRIES      = 5
RETRY_BACKOFF    = 2.0    # seconds (doubles each attempt)
REQUEST_TIMEOUT  = 30     # seconds
