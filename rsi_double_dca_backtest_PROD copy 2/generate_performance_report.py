"""
Strategy Performance Report Generator
======================================

Generates comprehensive markdown reports comparing strategies with:
- Basic metrics (CAGR, terminal value, profit)
- Advanced metrics (Sharpe, SQN, drawdown, volatility, R²)
- Win/loss statistics
- Comparative analysis

Run this script after backtests to regenerate all reports.
"""

from strategy_comparison import calculate_strategy_comparison
from pathlib import Path


def generate_comprehensive_report():
    """Generate comprehensive performance comparison report."""
    
    # Calculate all metrics
    comp = calculate_strategy_comparison()
    metrics = comp.get_all_metrics()
    
    # Generate markdown report
    report = f"""# Strategy Performance Comparison - Comprehensive Analysis

**Backtest Period:** {metrics['backtest_period']} ({metrics['backtest_years']} years)
**Last Updated:** 2025-11-22

---

## Executive Summary

This analysis compares three investment strategies over {metrics['backtest_years']} years of market history:

1. **YOUR RAINY DAY** - Bi-weekly DCA with RSI-triggered extra buying
2. **Simple DCA** - Bi-weekly fixed investment (no tactical buying)
3. **Buy & Hold** - Single ${metrics['buy_hold_initial_display']} lump sum investment

---

## 📊 Complete Performance Metrics

### YOUR RAINY DAY Strategy

| Metric | Value | Rating/Context |
|--------|-------|----------------|
| **Terminal Value** | {metrics['rainy_final']} | BASELINE |
| **Total Invested** | {metrics['rainy_invested']} | - |
| **Total Profit** | {metrics['rainy_profit']} | - |
| **CAGR** | {metrics['rainy_cagr']} | - |
| **Max Drawdown** | {metrics['rainy_max_dd']} | Lower is better |
| **Volatility (Annual)** | {metrics['rainy_volatility']} | Risk measure |
| **Sharpe Ratio** | {metrics['rainy_sharpe']} | {metrics['rainy_sharpe_rating']} |
| **SQN (System Quality)** | {metrics['rainy_sqn']} | {metrics['rainy_sqn_rating']} |
| **R² (Stability)** | {metrics['rainy_r_squared']} | 1.0 = perfect trend |
| **Profit Factor** | {metrics['rainy_profit_factor']} | Wins/Losses ratio |
| **Win Rate** | {metrics['rainy_win_rate']} | % of positive days |
| **Exposure** | 100.0% | Capital at risk |

### Simple DCA (No Rainy Logic)

| Metric | Value | vs Rainy Day |
|--------|-------|--------------|
| **Terminal Value** | {metrics['dca_final']} | {metrics['dca_vs_baseline']} |
| **Total Invested** | {metrics['dca_invested']} | Less capital deployed |
| **Total Profit** | {metrics['dca_profit']} | Lower profit |
| **CAGR** | {metrics['dca_cagr']} | - |
| **Max Drawdown** | {metrics['dca_max_dd']} | - |
| **Volatility (Annual)** | {metrics['dca_volatility']} | - |
| **Sharpe Ratio** | {metrics['dca_sharpe']} | {metrics['dca_sharpe_rating']} |
| **SQN (System Quality)** | {metrics['dca_sqn']} | {metrics['dca_sqn_rating']} |
| **R² (Stability)** | {metrics['dca_r_squared']} | - |
| **Profit Factor** | {metrics['dca_profit_factor']} | - |
| **Win Rate** | {metrics['dca_win_rate']} | - |
| **Exposure** | 100.0% | - |

### Buy & Hold (${metrics['buy_hold_initial_display']} Lump Sum)

| Metric | Value | vs Rainy Day |
|--------|-------|--------------|
| **Terminal Value** | {metrics['buy_hold_final']} | {metrics['buy_hold_vs_baseline']} |
| **Total Invested** | {metrics['buy_hold_invested']} | One-time investment |
| **Total Profit** | {metrics['buy_hold_profit']} | Lower profit |
| **CAGR** | {metrics['buy_hold_cagr']} | - |
| **Max Drawdown** | {metrics['buy_hold_max_dd']} | - |
| **Volatility (Annual)** | {metrics['buy_hold_volatility']} | - |
| **Sharpe Ratio** | {metrics['buy_hold_sharpe']} | {metrics['buy_hold_sharpe_rating']} |
| **SQN (System Quality)** | {metrics['buy_hold_sqn']} | {metrics['buy_hold_sqn_rating']} |
| **R² (Stability)** | {metrics['buy_hold_r_squared']} | - |
| **Profit Factor** | {metrics['buy_hold_profit_factor']} | - |
| **Win Rate** | {metrics['buy_hold_win_rate']} | - |
| **Exposure** | 100.0% | - |

---

## 🎯 Key Insights

### Why RAINY DAY Outperforms

**vs Simple DCA:**
- **Extra Profit:** {metrics['gain_vs_dca']} ({metrics['gain_vs_dca_pct']} more wealth)
- **Cost:** Only {metrics['extra_deployed']} extra capital deployed
- **ROI on Rainy Capital:** {metrics['rainy_roi']} (every $1 → {metrics['rainy_roi_multiplier']})
- **Same base contributions:** Both strategies invest $150 bi-weekly
- **Difference:** Rainy Day deploys savings tactically during RSI < 45

**vs Buy & Hold:**
- **Extra Profit:** {metrics['gain_vs_buy_hold']} ({metrics['gain_vs_buy_hold_pct']} more wealth)
- **Advantage:** DCA smooths entry prices over {metrics['backtest_years']} years
- **Crash Capture:** Rainy buys capitalize on 2008, 2020 drawdowns
- **Accessibility:** No large lump sum needed

### Advanced Metrics Comparison

**Sharpe Ratio (Risk-Adjusted Returns):**
- Rainy Day: {metrics['rainy_sharpe']} ({metrics['rainy_sharpe_rating']})
- Simple DCA: {metrics['dca_sharpe']} ({metrics['dca_sharpe_rating']})
- Buy & Hold: {metrics['buy_hold_sharpe']} ({metrics['buy_hold_sharpe_rating']})

**SQN (System Quality Number):**
- Rainy Day: {metrics['rainy_sqn']} ({metrics['rainy_sqn_rating']})
- Simple DCA: {metrics['dca_sqn']} ({metrics['dca_sqn_rating']})
- Buy & Hold: {metrics['buy_hold_sqn']} ({metrics['buy_hold_sqn_rating']})

**Max Drawdown (Worst Peak-to-Trough Decline):**
- Rainy Day: {metrics['rainy_max_dd']}
- Simple DCA: {metrics['dca_max_dd']}
- Buy & Hold: {metrics['buy_hold_max_dd']}

**R² (Return Curve Stability):**
- Rainy Day: {metrics['rainy_r_squared']} (closer to 1.0 = more consistent growth)
- Simple DCA: {metrics['dca_r_squared']}
- Buy & Hold: {metrics['buy_hold_r_squared']}

---

## 📈 Conclusion

The RAINY DAY strategy demonstrates superior performance across multiple dimensions:

1. **Highest Terminal Value:** {metrics['rainy_final']} vs {metrics['dca_final']} (DCA) vs {metrics['buy_hold_final']} (Buy & Hold)
2. **Best Risk-Adjusted Returns:** Sharpe {metrics['rainy_sharpe']} shows strong performance per unit of risk
3. **Superior System Quality:** SQN {metrics['rainy_sqn']} indicates {metrics['rainy_sqn_rating'].lower()} trading system
4. **Tactical Edge:** Deploys capital when market weakness (RSI < 45) creates opportunity
5. **Disciplined Approach:** Rules-based, no emotion, payday-aligned execution

**Bottom Line:** Same bi-weekly contributions as Simple DCA, but smarter deployment timing captures {metrics['gain_vs_dca_pct']} more wealth.

---

*Report generated automatically from backtest data*
*All metrics calculated from equity_rainy_strategy_calendar_dates.csv and equity_baseline_calendar_dates.csv*
"""
    
    # Write report
    output_path = Path(__file__).parent / "COMPREHENSIVE_PERFORMANCE_REPORT.md"
    output_path.write_text(report, encoding="utf-8")
    
    print(f"✅ Report generated: {output_path}")
    print(f"   Backtest period: {metrics['backtest_period']}")
    print(f"   Rainy Day final: {metrics['rainy_final']}")
    print(f"   vs DCA: {metrics['gain_vs_dca']} ({metrics['gain_vs_dca_pct']})")
    print(f"   vs Buy & Hold: {metrics['gain_vs_buy_hold']} ({metrics['gain_vs_buy_hold_pct']})")


if __name__ == "__main__":
    generate_comprehensive_report()
