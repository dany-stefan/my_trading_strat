#!/bin/bash

################################################################################
# REGENERATE ALL BACKTEST REPORTS - SINGLE SOURCE OF TRUTH
################################################################################
# This script runs all backtests and regenerates all report files from scratch
# using consistent data sources and calculations.
#
# Usage: bash regenerate_all_reports.sh
################################################################################

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROD_DIR="$SCRIPT_DIR/rsi_double_dca_backtest_PROD"

echo "════════════════════════════════════════════════════════════════════════"
echo "REGENERATING ALL BACKTEST REPORTS FROM SOURCE OF TRUTH"
echo "════════════════════════════════════════════════════════════════════════"
echo ""
echo "Source: yfinance SPY data (2003-present)"
echo "Method: compute_rsi_with_sma() - Wilder's RMA"
echo "Output: 19 files (CSVs, charts, reports, email preview)"
echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo ""

cd "$PROD_DIR"

# 1. Main calendar date backtest (generates core equity and rainy data)
echo "════════════════════════════════════════════════════════════════════════"
echo "1/7 - Running Calendar Date Backtest (Core Data)"
echo "════════════════════════════════════════════════════════════════════════"
python3 rsi_calendar_date_backtest.py
echo ""

# 2. Generate performance report and rainy day analysis chart
echo "════════════════════════════════════════════════════════════════════════"
echo "2/7 - Generating Performance Report"
echo "════════════════════════════════════════════════════════════════════════"
python3 generate_performance_report.py
echo ""

# 3. Generate hit/miss analysis charts
echo "════════════════════════════════════════════════════════════════════════"
echo "3/7 - Generating Hit/Miss Charts"
echo "════════════════════════════════════════════════════════════════════════"
python3 generate_hit_miss_charts.py
echo ""

# 4. Generate RSI timeline chart
echo "════════════════════════════════════════════════════════════════════════"
echo "4/7 - Generating RSI Timeline Chart"
echo "════════════════════════════════════════════════════════════════════════"
python3 generate_rsi_timeline_chart.py
echo ""

# 5. Generate RSI vs SMA payday analysis (needed for cash pool viz)
echo "════════════════════════════════════════════════════════════════════════"
echo "5/7 - Generating RSI vs SMA Payday Analysis"
echo "════════════════════════════════════════════════════════════════════════"
python3 compare_rsi_sma_paydays.py
echo ""

# 6. Generate cash pool visualization
echo "════════════════════════════════════════════════════════════════════════"
echo "6/7 - Generating Cash Pool Visualization"
echo "════════════════════════════════════════════════════════════════════════"
python3 generate_cash_pool_visualization.py
echo ""

# 7. Run variants backtest (generates SPY price rainy periods, variants data)
echo "════════════════════════════════════════════════════════════════════════"
echo "7/7 - Running RSI Variants Backtest (SPY Price Charts & Variants)"
echo "════════════════════════════════════════════════════════════════════════"
python3 rsi_variants_backtest.py
echo ""

# 8. Generate simulated email preview
echo "════════════════════════════════════════════════════════════════════════"
echo "8/8 - Generating Simulated Email Preview"
echo "════════════════════════════════════════════════════════════════════════"
python3 simulate_payday_email.py
echo ""

# Verify all files exist
echo "════════════════════════════════════════════════════════════════════════"
echo "VERIFYING ALL FILES IN TO_SHARE LIST"
echo "════════════════════════════════════════════════════════════════════════"
cd "$SCRIPT_DIR"
missing_count=0
total_count=0

while IFS= read -r file; do
  total_count=$((total_count + 1))
  if [ -f "$file" ]; then
    echo "✅ $file"
  else
    echo "❌ MISSING: $file"
    missing_count=$((missing_count + 1))
  fi
done < to_share_via_email_reports.txt

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "REGENERATION COMPLETE"
echo "════════════════════════════════════════════════════════════════════════"
echo "Files verified: $total_count"
echo "Missing files: $missing_count"
echo ""

if [ $missing_count -eq 0 ]; then
  echo "✅ ALL FILES GENERATED SUCCESSFULLY!"
  echo ""
  echo "Ready to create ZIP package:"
  echo "  bash to_share_send_reports_via_email.sh"
else
  echo "⚠️  WARNING: Some files are missing!"
  echo "Review the list above and check for errors."
fi
echo "════════════════════════════════════════════════════════════════════════"
