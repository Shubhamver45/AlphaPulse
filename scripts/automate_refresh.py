"""
=============================================================================
AlphaPulse — Automated Refresh Pipeline (Week 4)
=============================================================================
Purpose : Automate the end-to-end data refresh process.
          1. Data Acquisition (yfinance)
          2. Analytics (NumPy)
          3. Tableau Export Reshaping

Usage:
    python scripts/automate_refresh.py
=============================================================================
"""

import os
import sys
import time
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_all

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
log_path = os.path.join(LOG_DIR, "automation.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    handlers=[
        logging.FileHandler(log_path, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("AlphaPulse.Automation")

def main():
    log.info("==============================================================")
    log.info("|          AlphaPulse  |  AUTOMATED REFRESH START             |")
    log.info(f"|          {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}                              |")
    log.info("==============================================================")
    
    try:
        run_all.main()
        log.info("SUCCESS: Full pipeline refresh completed successfully.")
    except Exception as e:
        log.error(f"FAILURE: Automation failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
