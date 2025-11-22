# 🚀 RSI Double DCA Backtest - TURBO v2.0

## Overview

This is the enhanced analytics version of the production RSI DCA strategy. It uses the exact same trading parameters as PROD but adds professional-grade visualizations and advanced statistics for deeper insights.

### Key Distinction: TURBO vs PROD

- Same Strategy: Identical trading logic, parameters, and execution rules
- Enhanced Analytics: Additional professional visualizations + advanced statistics
- Dual Email System: Separate emails sent 1 hour after PROD on 3rd & 17th
- Same Performance: Strategy outcomes are identical to PROD

## Trading Parameters (Unchanged from PROD)

- Payday Schedule: 1st & 15th of each month (triggers the process)
- Execution Days: 3rd & 17th (2 days after payday)
- Base DCA Amount: $150 CAD on execution day (always)
- Rainy Day Accumulation: $30 CAD saved on execution day when RSI SMA(7) ≥ 45
- Initial Cash Pool: $330 CAD (starting buffer)
- Buy Trigger: RSI SMA(7) < 45 checked on execution day (3rd/17th)
- Asset: SPY (S&P 500 ETF) via Yahoo Finance (CADUSD=X)
- Email Timing: Sent on execution day (3rd/17th) with RSI analysis and buy recommendation

## Enhanced Visualizations (New in TURBO)

### 1. Interactive Dashboard (`dashboard_interactive_turbo.png`)

- Equity curve with drawdown shading
- Cash pool dynamics with accumulation/depletion zones
- RSI indicator with buy/hold zones
- Monthly returns heatmap
- Risk-adjusted performance metrics

### 2. Market Regime Performance (`regime_performance_turbo.png`)

- Breakdown of performance across Bull / Neutral / Bear regimes
- Returns, Sharpe ratio, max drawdown per regime

### 3. Monte Carlo Cash Pool Simulation (`monte_carlo_cash_pool_turbo.png`)

- Cash pool sufficiency probability
- Confidence intervals (5th, 50th, 95th percentiles)
- Depletion risk assessment

### 4. Consecutive Rainy Day Heatmap (`consecutive_rainy_heatmap_turbo.png`)

- Distribution of consecutive accumulation periods
- Year-over-year trends
- Identifies cash pool stress periods

## PROD vs TURBO Comparison (Mirrored)

This section mirrors the key PROD vs TURBO artifacts so you can view them directly from TURBO docs.

### Equity Curves + Cumulative Outperformance

![PROD vs TURBO Comparison](./strategy_comparison_prod_vs_turbo.png)

### Yearly ROI/Profit (Per-Year)

- Data: `yearly_prod_vs_turbo.csv` (yearly equity start/end, contributions, profit, ROI%)
- Visual: `yearly_prod_vs_turbo.png`

![Yearly Profit and Difference](./yearly_prod_vs_turbo.png)

### Rainy Amounts Over Time (Per Execution Day)

- Data: `rainy_amounts_timeseries.csv` (columns: `rainy_prod`, `rainy_turbo`)
- Visual: `rainy_amount_over_time_prod_vs_turbo.png`
- Note: Chart includes a 3-execution rolling-average overlay for both series.

![Rainy Amounts Over Time](./rainy_amount_over_time_prod_vs_turbo.png)

## Email System

TURBO emails are clearly marked to distinguish from PROD:

- Subject Line: `[🚀 TURBO v2.0] 📅 PAYDAY: Investment Metrics - {date}`
- Test Emails: `[TEST - TURBO v2.0] 🧪 TEST EMAIL (Local Run): Investment Metrics - {date}`
- Timing: Sent on execution day (3rd/17th) at 2:00 PM EST (1 hour after PROD at 1:00 PM EST)
- Content: RSI SMA(7) analysis, VIX level, market regime, and buy recommendation for that day

## Automation

### GitHub Actions

- Workflow: `.github/workflows/turbo_monitor.yml`
- Schedule: 2:00 PM EST on execution days (3rd & 17th) at 19:00 UTC
- Process: Checks RSI SMA(7), VIX, market regime → generates email with buy decision
- Manual Trigger: Available via GitHub UI (sends TEST email)

### Local Testing

```bash
cd /Users/danystefan/Documents/workspace/my_trading_strat/rsi_double_dca_backtest_v2.0_turbocharged
./local_email_send_test.sh
```

## Enhanced Statistics (Coming Soon)

Additional metrics to be added to `Summary_Analysis.md`:

- Calmar ratio (return/max drawdown)
- Sortino ratio (downside deviation)
- Win/loss streaks
- Monthly return distribution
- Value at Risk (VaR) analysis
- Conditional VaR (CVaR)

## File Structure

```text
rsi_double_dca_backtest_v2.0_turbocharged/
├── monitor_strategy.py              # Main execution script
├── rsi_calendar_date_backtest.py    # Enhanced backtest with visualizations
├── email_generator.py               # TURBO-branded email formatter
├── enhanced_visualizations.py       # Professional chart generation
├── strategy_config.py               # Strategy parameters (same as PROD)
├── payday_scheduler.py              # Calendar logic
├── trading_calendar.py              # TSX trading day validation
├── local_email_send_test.sh         # Local test script
├── Summary_Analysis.md              # Enhanced performance report
└── README.md                        # This file
```

## Performance: PROD vs TURBO Comparison

### Backtest Results (22.10 years: Oct 2003 - Nov 2025)

| Metric | PROD | TURBO | Difference |
|--------|------|-------|------------|
| **Final Equity** | $512,450 | $512,346 | -$104 (-0.02%) |
| **Total Contributions** | $89,200 | $89,260 | +$60 (+0.07%) |
| **Total Returns** | $423,250 | $423,086 | -$164 (-0.04%) |
| **ROI** | 474.5% | 474.1% | -0.4% |
| **CAGR** | 30.92% | 30.41% | -0.51% |
| **Max Drawdown** | -27.49% | -27.52% | -0.03% |
| **Rainy Buys Executed** | 97 | 80 | -17 |
| **Rainy Hit Rate** | 88.2% | 74.1% | -14.1% |
| **Rainy Frequency** | 22.4% | 22.0% | -0.4% |
| **Final Cash Pool** | $510 | $570 | +$60 |

### Capital Deployment Analysis

**PROD (Fixed Sizing):**
- Rainy amount: Always $150
- Total rainy capital: 97 buys × $150 = **$14,550**
- Average per rainy day: $150

**TURBO (VIX-Scaled Sizing):**
- Rainy amounts: $150 (Low VIX) / $180 (Med VIX) / $210 (High VIX)
- Total rainy capital deployed: **$14,610** (from backtest)
- Extra deployed vs PROD: **+$60** (+0.4%)
- Average per rainy day: $182.63 (21.8% higher than PROD)

### Recommendation: Cash Pool Sizing for TURBO

If following TURBO instead of PROD, you should increase your initial cash pool:

| Strategy | Recommended Initial Pool | Reasoning |
|----------|-------------------------|----------|
| **PROD** | $330 (2.2× rainy amount) | Covers ~2 consecutive $150 rainy buys |
| **TURBO** | **$450** (2.5× median rainy) | Covers ~2-3 consecutive buys at $180-$210 |

**Why $450 for TURBO?**
- VIX-scaled amounts range $150-$210 (avg ~$183 historically)
- Bear markets + high VIX clusters can trigger multiple $210 buys in sequence
- $450 = 2.14× buys at $210 (high VIX scenario)
- Provides buffer for worst-case rainy streaks (3× consecutive bear+high VIX days)

**Additional Monthly Commitment:**
- Payday (1st/15th): Initiates the 2-day countdown to execution
- Execution (3rd/17th): RSI checked, buy executed, $30 saved if not rainy
- PROD: Save $30/execution → typical pool range $180-$480
- TURBO: Same $30/execution, but higher depletion during fear spikes
- Expected extra capital deployed annually: ~$60-$120 more than PROD in high-volatility years

### Performance Verdict

Historically (2003-2025), TURBO and PROD delivered **nearly identical** long-term results:
- TURBO deployed slightly more capital (+$60 total)
- TURBO was more selective (80 vs 97 rainy buys)
- Final equity difference: -$104 (-0.02%)

**TURBO's value is NOT higher returns—it's smarter context:**
- Same base strategy, better decision transparency
- VIX sizing captures deeper discounts in true fear
- Adaptive thresholds filter noise in bull markets
- Richer email justifications reduce emotional second-guessing

**Use TURBO if:** You want clarity on WHY to deploy rainy capital and are comfortable with slightly higher cash pool needs ($450 vs $330).

**Use PROD if:** You prefer maximum simplicity and minimal cash pool ($330 sufficient).

## Development Notes

- Created: January 2025
- Purpose: Enhanced analytics without changing trading strategy
- Rationale: PROD folder remains stable for production use, TURBO experiments with advanced reporting
- Future: May add sensitivity analysis, walk-forward validation, regime-adaptive parameters

## Usage

This folder is meant for users who want:

1. Deeper insights into strategy performance
2. Professional-grade visualizations for presentations
3. Risk analysis and stress testing
4. Understanding of market regime impacts

Do NOT use for: Parameter optimization testing (keep PROD stable for live trading decisions)

---

Version: 2.0 Turbocharged  
Last Updated: January 2025  
Status: Active (Dual email system operational)

