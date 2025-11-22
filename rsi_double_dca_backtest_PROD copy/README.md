# YTD 2025 Backtest: Variant Strategy vs Simple DCA

This folder contains a streamlined backtest comparing two investment strategies for YTD 2025 (Feb 3 - Nov 20, 2025).

**Methodology:** This backtest ensures **100% execution rate** on rainy day signals by automatically adding lump sum deposits to the cash pool whenever insufficient funds are available. This demonstrates the maximum ROI potential from buying dips.

## Quick Summary

**Variant Strategy outperformed Simple DCA by 31.7%** ($974) with only 15.8% more capital deployed.

- **Simple DCA:** $3,075.28 (7.9% ROI)
- **Variant Strategy:** $4,049.36 (22.7% ROI)
- **ROI on Rainy Capital:** 216.5% (exceptional capital efficiency!)

## Files

### Main Report
- **`BACKTEST_SUMMARY_YTD2025.md`** - Complete 3-page analysis with all findings

### Charts
- `chart_1_equity_curves_ytd2025.png` - Performance comparison
- `chart_2_outperformance_ytd2025.png` - Cumulative outperformance
- `chart_3_contributions_ytd2025.png` - Capital deployment breakdown
- `chart_4_rsi_timeline_ytd2025.png` - RSI timeline with rainy day buy points

### Data Files
- `equity_simple_dca_ytd2025.csv` - Simple DCA daily equity curve
- `equity_variant_ytd2025.csv` - Variant strategy daily equity curve
- `rainy_buys_ytd2025.csv` - Log of all rainy day buys (with lump sum deposit info)
- `strategy_comparison_summary_ytd2025.csv` - Summary statistics

### Scripts
- `variant_vs_simple_dca_backtest.py` - Main backtest script
- `strategy_config.py` - Strategy configuration (shared utility)
- `trading_calendar.py` - TSX trading calendar (shared utility)

## How to Run

```bash
python variant_vs_simple_dca_backtest.py
```

This will regenerate all data files and charts.

## Strategy Details

**Simple DCA:**
- Invest $150 CAD on 3rd and 17th of each month
- No market timing

**Variant Strategy (100% Execution Rate):**
- Base: $150 CAD on 3rd and 17th (same as Simple DCA)
- Cash pool: Starts at $0, grows $30 per execution day
- Rainy day: Deploy extra $150 when RSI SMA(7) < 45
- **Automatic funding:** Lump sum deposits added when cash insufficient to ensure 100% execution

## Key Results

**Capital Efficiency:**
- Extra capital deployed: $450 (3 rainy days × $150)
- Outperformance generated: $974
- **ROI on rainy capital: 216.5%** (every dollar became $3.16)

**Execution Details:**
- 3 rainy days detected (15.8% of executions)
- 3 successful buys (100% via automatic lump sum deposits)
- Lump sum deposits: $330 total (2 of 3 rainy days needed funding)
- Buying discount: 7.5% below average execution day price
