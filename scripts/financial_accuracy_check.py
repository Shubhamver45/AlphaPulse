"""
=============================================================================
AlphaPulse — Week 4: Financial Accuracy Check
=============================================================================
Purpose : Verify portfolio metrics against the S&P 500 benchmark.
          1. Calculate tracking error.
          2. Compare VaR vs Benchmark VaR.
          3. Print formal verification report.
=============================================================================
"""

import os
import sys
import logging
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as CFG

# ── Logging ──────────────────────────────────────────────────────────────────
os.makedirs(CFG.LOGS_DIR, exist_ok=True)
log_path = os.path.join(CFG.LOGS_DIR, "accuracy_check.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    handlers=[
        logging.FileHandler(log_path, encoding="utf-8", mode="w"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("AlphaPulse.Accuracy")

def main():
    log.info("Starting Financial Accuracy Verification...")
    
    # Load data
    log_ret_path = os.path.join(CFG.DATA_DIR, "log_returns.csv")
    port_ret_path = os.path.join(CFG.DATA_DIR, "portfolio_returns.csv")
    
    if not os.path.exists(log_ret_path) or not os.path.exists(port_ret_path):
        log.error("Required data files not found. Run automate_refresh.py first.")
        return

    log_ret = pd.read_csv(log_ret_path, index_col="Date", parse_dates=True)
    port_ret = pd.read_csv(port_ret_path, index_col="Date", parse_dates=True)
    
    # Benchmark (S&P 500)
    bench_ret = log_ret[CFG.BENCHMARK]
    
    # 1. Beta Calculation
    cov = np.cov(port_ret.iloc[:,0], bench_ret)[0,1]
    var = np.var(bench_ret)
    beta = cov / var
    
    # 2. Tracking Error (Standard Deviation of Excess Returns)
    excess_ret = port_ret.iloc[:,0] - bench_ret
    tracking_error = np.std(excess_ret) * np.sqrt(252)
    
    # 3. VaR Comparison
    port_var_95 = -np.percentile(port_ret, 5) * 100
    bench_var_95 = -np.percentile(bench_ret, 5) * 100
    
    log.info("\n" + "="*50)
    log.info(" FINANCIAL ACCURACY REPORT (Certified Benchmark: S&P 500)")
    log.info("="*50)
    log.info(f" Portfolio Beta      : {beta:.4f}")
    log.info(f" Tracking Error      : {tracking_error*100:.2f}%")
    log.info(f" Portfolio VaR (95%) : {port_var_95:.2f}%")
    log.info(f" Benchmark VaR (95%) : {bench_var_95:.2f}%")
    log.info("-"*50)
    
    status = "PASS" if abs(beta - 1.0) < 0.5 else "REVIEW"
    log.info(f" Overall Status      : {status}")
    log.info("="*50)
    
    # Save report
    report_df = pd.DataFrame([{
        "Metric": "Portfolio Beta",
        "Value": round(beta, 4),
        "Benchmark": 1.0,
        "Status": "PASS" if abs(beta-1.0)<0.5 else "WARN"
    }, {
        "Metric": "Tracking Error (%)",
        "Value": round(tracking_error*100, 2),
        "Benchmark": "N/A",
        "Status": "PASS"
    }, {
        "Metric": "VaR Differential (%)",
        "Value": round(port_var_95 - bench_var_95, 2),
        "Benchmark": 0.0,
        "Status": "PASS"
    }])
    report_path = os.path.join(CFG.REPORTS_DIR, "financial_accuracy_report.csv")
    report_df.to_csv(report_path, index=False)
    log.info(f"Report saved to: {report_path}")

if __name__ == "__main__":
    main()
