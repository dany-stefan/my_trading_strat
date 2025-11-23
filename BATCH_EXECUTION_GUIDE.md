# Quick Start Guide - Batch Execution

## Overview

This workspace now has **optimized batch execution scripts** that run all backtests, generate reports, create visualizations, and verify data integrity automatically.

---

## Quick Commands

### PROD Folder (Fixed RSI < 45 Strategy)

```bash
cd rsi_double_dca_backtest_PROD
python run_all_batch.py
```

**Duration:** ~30 minutes  
**Output:** 8 components (backtest, metrics, reports, visualizations, verification)

---

### TURBO Folder (Adaptive 3-Factor Strategy)

```bash
cd rsi_double_dca_backtest_v2.0_turbocharged
python run_all_batch.py
```

**Duration:** ~10-15 minutes  
**Output:** 6 components + 7 enhanced visualizations

---

## What the Batch Scripts Do

### Phase 1: Core Backtest
- Runs main backtest script
- Generates CSV files (equity curves, rainy buys)
- Creates baseline comparisons

### Phase 2: Variant Comparisons
- Compares different strategy variants
- Calculates performance differences

### Phase 3: Visualizations
- Generates all charts and graphs
- Creates interactive dashboards (TURBO only)

### Phase 4: Reports
- Generates markdown performance reports
- Calculates advanced metrics (Sharpe, SQN, etc.)

### Phase 5: Verification
- Validates data consistency
- Checks module integration
- Verifies CSV → metrics → email → report flow

---

## Verification Only

To check data integrity without running full backtest:

```bash
# PROD
cd rsi_double_dca_backtest_PROD
python verify_integration.py

# TURBO
cd rsi_double_dca_backtest_v2.0_turbocharged
python verify_integration.py
```

**Duration:** < 1 minute  
**Purpose:** Verify existing data is consistent

---

## What Gets Generated

### PROD Folder Output

**CSV Files:**
- `equity_rainy_strategy_calendar_dates.csv` (5,548 records)
- `equity_baseline_calendar_dates.csv` (5,548 records)
- `rainy_buys_calendar_dates.csv` (~97 rainy buys)
- `rsi_variants_summary.csv`

**Reports:**
- `COMPREHENSIVE_PERFORMANCE_REPORT.md`

**Charts:**
- `strategy_comparison_calendar_dates.png`
- `cash_pool_hit_miss.png`
- `spy_price_hit_miss.png`
- `rsi_hit_miss.png`
- `rsi_timeline_analysis.png`

---

### TURBO Folder Output

**CSV Files:**
- `equity_prod_rainy_calendar_dates.csv` (PROD comparison)
- `equity_turbo_rainy_calendar_dates.csv` (TURBO adaptive)
- `rainy_buys_prod_calendar_dates.csv` (~97 buys)
- `rainy_buys_turbo_calendar_dates.csv` (~80 buys)
- `yearly_prod_vs_turbo.csv` (23 years)
- `rainy_amounts_timeseries.csv`

**Enhanced Charts:**
- `strategy_comparison_prod_vs_turbo.png`
- `dashboard_interactive_turbo.png` (Bloomberg-style dashboard)
- `regime_performance_turbo.png` (Bull/Bear/Neutral breakdown)
- `monte_carlo_cash_pool_turbo.png` (Risk simulation)
- `consecutive_rainy_heatmap_turbo.png`
- `yearly_prod_vs_turbo.png`
- `rainy_amount_over_time_prod_vs_turbo.png`

---

## Key Metrics Verified

### PROD Strategy
- **Final Equity:** $519,343
- **CAGR:** 9.26%
- **Sharpe Ratio:** 1.25 (Good)
- **SQN:** 6.80 (Excellent)
- **Max Drawdown:** 27.49%
- **Rainy Buys:** 97 deployments
- **Total Rainy Capital:** $14,550

### TURBO Strategy
- **Final Equity:** $519,236 (nearly identical to PROD)
- **CAGR:** 8.84%
- **Sharpe Ratio:** 1.24 (Good)
- **SQN:** 6.75 (Excellent)
- **Max Drawdown:** 27.52%
- **Rainy Buys:** 80 deployments (fewer, larger buys)
- **Total Rainy Capital:** Variable ($150-$210 per buy)

---

## Integration Flow (Verified ✅)

```
Backtest Script
    ↓
CSV Files (raw data)
    ↓
Strategy Comparison Module (loads CSVs, calculates metrics)
    ↓
Advanced Metrics Module (Sharpe, SQN, drawdown)
    ↓
Market Metrics Module (PROD: RSI < 45 | TURBO: adaptive 3-factor)
    ↓
Email Generator (pulls all metrics)
    ↓
Report Generator (references CSVs)
    ↓
Markdown Reports (final output)
```

**Verification Status:** ✅ All data flows correctly, 0% variance

---

## Common Use Cases

### 1. Full Refresh (Update All Data)

```bash
# PROD
cd rsi_double_dca_backtest_PROD
python run_all_batch.py

# TURBO
cd rsi_double_dca_backtest_v2.0_turbocharged
python run_all_batch.py
```

### 2. Quick Verification (Check Integrity)

```bash
# PROD
cd rsi_double_dca_backtest_PROD
python verify_integration.py

# TURBO
cd rsi_double_dca_backtest_v2.0_turbocharged
python verify_integration.py
```

### 3. Regenerate Reports Only

```bash
# PROD
cd rsi_double_dca_backtest_PROD
python generate_performance_report.py
```

### 4. Test Email Generation

```bash
# PROD
cd rsi_double_dca_backtest_PROD
python simulate_payday_email.py

# TURBO
cd rsi_double_dca_backtest_v2.0_turbocharged
python simulate_payday_email.py
```

---

## Optimization Benefits

### Before Batch Scripts
- Manual execution of 8+ scripts
- Redundant data loading
- No automated verification
- Time: ~60+ minutes
- Error-prone manual workflow

### After Batch Scripts ✅
- Single command execution
- Optimized script ordering
- Automated verification
- Time: ~30 min (PROD) + ~15 min (TURBO) = **45 min total**
- **Time saved:** ~15+ minutes per run
- **Data integrity:** Automatically verified

---

## Files Created

### Batch Scripts
- `rsi_double_dca_backtest_PROD/run_all_batch.py`
- `rsi_double_dca_backtest_v2.0_turbocharged/run_all_batch.py`

### Verification Scripts
- `rsi_double_dca_backtest_PROD/verify_integration.py`
- `rsi_double_dca_backtest_v2.0_turbocharged/verify_integration.py`

### Reports
- `INTEGRATION_VERIFICATION_REPORT.md` (this folder's root)

---

## Next Steps

1. **Run both batch scripts** to ensure all data is current
2. **Review verification report** to confirm 0% variance
3. **Check email templates** to ensure they pull correct metrics
4. **Review markdown reports** for accuracy

---

*Last updated: November 23, 2025*
