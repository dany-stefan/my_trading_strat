# 🚀 RSI Double DCA Backtest - TURBO v2.0

## Overview
This is the **enhanced analytics version** of the production RSI DCA strategy. It uses the **exact same trading parameters** as PROD but adds **professional-grade visualizations and advanced statistics** for deeper insights.

### Key Distinction: TURBO vs PROD
- **Same Strategy**: Identical trading logic, parameters, and execution rules
- **Enhanced Analytics**: 4 additional professional visualizations + advanced statistics
- **Dual Email System**: Separate emails sent 1 hour after PROD on 3rd & 17th
- **Same Performance**: Strategy outcomes are identical to PROD

## Trading Parameters (Unchanged from PROD)
- **Base DCA Amount**: $150 CAD every payday (1st & 15th)
- **Rainy Day Accumulation**: $30 CAD per payday when RSI SMA(7) ≥ 45
- **Initial Cash Pool**: $330 CAD (starting buffer)
- **Buy Trigger**: RSI SMA(7) < 45 (bearish market condition)
- **Asset**: SPY (S&P 500 ETF) via Yahoo Finance (CADUSD=X)
- **Execution Days**: 3rd & 17th (2 days after payday to sync with Wealthsimple)

## Enhanced Visualizations (New in TURBO)

### 1. Interactive Dashboard (`dashboard_interactive_turbo.png`)
Professional multi-panel layout inspired by Bloomberg Terminal:
- Equity curve with drawdown shading
- Cash pool dynamics with accumulation/depletion zones
- RSI indicator with buy/hold zones
- Monthly returns heatmap
- Risk-adjusted performance metrics

### 2. Market Regime Performance (`regime_performance_turbo.png`)
Breakdown of strategy performance across different market conditions:
- Bull markets (RSI > 60)
- Neutral markets (40 ≤ RSI ≤ 60)
- Bear markets (RSI < 40)
- Shows returns, Sharpe ratio, max drawdown per regime

### 3. Monte Carlo Cash Pool Simulation (`monte_carlo_cash_pool_turbo.png`)
Risk analysis using 10,000 simulations:
- Cash pool sufficiency probability
- Confidence intervals (5th, 50th, 95th percentiles)
- Depletion risk assessment
- Historical vs simulated comparison

### 4. Consecutive Rainy Day Heatmap (`consecutive_rainy_heatmap_turbo.png`)
Analysis of accumulation streak patterns:
- Distribution of consecutive accumulation periods
- Year-over-year trends
- Identifies cash pool stress periods
- Helps validate initial pool sizing

## Email System
TURBO emails are clearly marked to distinguish from PROD:
- **Subject Line**: `[🚀 TURBO v2.0] 📅 PAYDAY: Investment Metrics - {date}`
- **Test Emails**: `[TEST - TURBO v2.0] 🧪 TEST EMAIL (Local Run): Investment Metrics - {date}`
- **Timing**: Sent at 2:00 PM EST (1 hour after PROD at 1:00 PM EST)

## Automation

### GitHub Actions
- **Workflow**: `.github/workflows/turbo_monitor.yml`
- **Schedule**: 2:00 PM EST on 3rd & 17th (19:00 UTC)
- **Manual Trigger**: Available via GitHub UI (sends TEST email)

### Local Testing
```bash
cd /Users/danystefan/Documents/workspace/my_trading_strat/rsi_double_dca_backtest_v2.0_turbocharged
./local_email_send_test.sh
```

## Enhanced Statistics (Coming Soon)
Additional metrics to be added to Summary_Analysis.md:
- Calmar ratio (return/max drawdown)
- Sortino ratio (downside deviation)
- Win/loss streaks
- Monthly return distribution
- Value at Risk (VaR) analysis
- Conditional VaR (CVaR)

## File Structure
```
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

## Performance (Same as PROD)
Since TURBO uses identical trading parameters:
- **CAGR**: 30.92%
- **Sharpe Ratio**: 0.888
- **Max Drawdown**: -21.5%
- **Hit Rate**: 88.2%
- **Total Rainy Buys**: 214 (67.7% of opportunities)

## Development Notes
- **Created**: January 2025
- **Purpose**: Enhanced analytics without changing trading strategy
- **Rationale**: PROD folder remains stable for production use, TURBO experiments with advanced reporting
- **Future**: May add sensitivity analysis, walk-forward validation, regime-adaptive parameters

## Usage
This folder is meant for users who want:
1. Deeper insights into strategy performance
2. Professional-grade visualizations for presentations
3. Risk analysis and stress testing
4. Understanding of market regime impacts

**Do NOT use for**: Parameter optimization testing (keep PROD stable for live trading decisions)

---
**Version**: 2.0 Turbocharged  
**Last Updated**: January 2025  
**Status**: Active (Dual email system operational)
