"""
=============================================================================
AlphaPulse — Master Runner
=============================================================================
Run all three pipeline stages in sequence:
  1. data_pipeline.py   (Week 1 — data acquisition & cleaning)
  2. analytics_engine.py (Week 2 — NumPy quantitative analysis)
  3. export_for_tableau.py (Tableau export)

Usage:
    python scripts/run_all.py
=============================================================================
"""

import sys
import os
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as CFG

os.makedirs(CFG.LOGS_DIR, exist_ok=True)
log_path = os.path.join(CFG.LOGS_DIR, "master_run.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    handlers=[
        logging.FileHandler(log_path, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("AlphaPulse.Master")


def main():
    start = datetime.now()
    log.info("==============================================================")
    log.info("|          AlphaPulse  |  FULL PIPELINE RUN                    |")
    log.info(f"|          {start.strftime('%Y-%m-%d  %H:%M:%S')}                              |")
    log.info("==============================================================")

    # ── Stage 1: Data Acquisition ─────────────────────────────────────────────
    log.info("\n> Stage 1/3  --  Data Acquisition & Cleaning  (Week 1)")
    import data_pipeline
    data_pipeline.run()

    # ── Stage 2: Analytics Engine ─────────────────────────────────────────────
    log.info("\n> Stage 2/3  --  Quantitative Analytics Engine  (Week 2)")
    import analytics_engine
    analytics_engine.run()

    # ── Stage 3: Tableau Export ───────────────────────────────────────────────
    log.info("\n> Stage 3/3  --  Tableau Export Builder")
    import export_for_tableau
    export_for_tableau.run()

    elapsed = (datetime.now() - start).total_seconds()
    log.info(f"\n==============================================================")
    log.info(f"|  ALL STAGES COMPLETE  |  Elapsed: {elapsed:.1f}s{' '*(25-len(str(round(elapsed,1))))}|")
    log.info(f"|                                                              |")
    log.info(f"|  Outputs:                                                    |")
    log.info(f"|   * Raw data    ->  /data/raw/                               |")
    log.info(f"|   * Analytics   ->  /data/*.csv                              |")
    log.info(f"|   * Tableau     ->  /tableau_exports/tab_*.csv               |")
    log.info(f"|   * Reports     ->  /reports/mc_validation_report.csv        |")
    log.info(f"|   * Logs        ->  /logs/                                   |")
    log.info(f"==============================================================")


if __name__ == "__main__":
    main()
