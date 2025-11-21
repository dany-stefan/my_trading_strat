# 3-Strategy Performance Comparison: Baseline DCA vs RSI Cash vs Rainy Day Only

**Backtest Period:** October 7, 2003 → November 20, 2025 (22.12 years)  
**Asset:** SPY (S&P 500 ETF) converted to CAD using CADUSD=X FX rate  
**Initial Investment:** $1,000 CAD lump sum on first trading day

---

![3-Way Equity Comparison](./equity_3way_comparison.png)

---

## Strategy Definitions

### Strategy 1: Baseline DCA (Dollar Cost Averaging)
**Simple, consistent buying strategy**

**Criteria:**
- Invest **$150 CAD** every bi-weekly Monday (577 total purchases)
- No timing, no market conditions considered
- Pure mechanical buying

**Assumptions:**
- Bi-weekly schedule: Every other Monday starting from first Monday after data availability
- No trading fees, taxes, or slippage
- SPY price converted to CAD using daily FX rate
- Full fractional share purchases allowed
- No dividends modeled

---

### Strategy 2: RSI Cash Accumulation Strategy
**Opportunistic buying during market weakness**

**Criteria:**
- **Regular investment:** $150 CAD every bi-weekly Monday (same as baseline)
- **Cash accumulation:** Save $30 CAD every bi-weekly period when RSI ≥ 50
- **Extra deployment:** When RSI(14) < 50 on a Monday AND cash pool ≥ $100:
  - Deploy additional $100 from accumulated cash pool
  - Total investment that Monday: $250 ($150 base + $100 extra)
- **RSI Threshold:** 50 (below = "rainy day" buying opportunity)
- **RSI Period:** 14 days
- **RSI Calculation:** Based on SPY USD closing prices

**Assumptions:**
- Same as Baseline DCA, plus:
- Cash pool starts at $0, grows by $30 every bi-weekly period
- Cash pool only depleted when RSI < 50 AND sufficient funds available
- Unspent cash included in final equity calculation
- Missed opportunities tracked when RSI < 50 but cash pool < $100

**Key Mechanics:**
- 577 bi-weekly Mondays total
- 184 Mondays had RSI < 50 ("rainy days")
- 165 successful extra buys (89.7% hit rate)
- 19 missed opportunities (10.3% miss rate due to insufficient cash)

---

### Strategy 3: Rainy Day Only
**Pure market-timing strategy - buy ONLY during weakness**

**Criteria:**
- **NO regular bi-weekly investment**
- **NO cash accumulation**
- **Only buy $250 CAD on rainy bi-weekly Mondays** when RSI(14) < 50
- Initial $1,000 lump sum only

**Key Mechanics:**
- 577 bi-weekly Mondays total
- 184 rainy Mondays (RSI < 50)
- 184 purchases of $250 = $46,000 total contributions (vs $87,550 baseline)
- 47.5% fewer contributions than baseline

---

## Performance Results

### 3-Way Comparison Table

| Metric | Baseline DCA | RSI Cash Strategy | Rainy Day Only |
|--------|--------------|-------------------|----------------|
| **Total Contributions** | $87,550 | $104,050 | $47,000 |
| **Final Equity** | $503,343 | $599,875 | $298,423 |
| **Total Return** | 50,234% | 59,888% | 29,742% |
| **CAGR** | 32.48% | 33.53% | 29.38% |
| **Max Drawdown** | -27.50% | -27.43% | -27.17% |
| **Rainy Buys** | 0 | 165 extra | 184 only |

---

### Baseline DCA Strategy

| Metric | Value |
|--------|-------|
| **Total Contributions** | $87,550 CAD |
| **Final Equity** | $503,343.42 CAD |
| **Total Return** | 50,234.34% |
| **CAGR** | 32.48% |
| **Max Drawdown** | -27.50% |

---

### RSI Cash Accumulation Strategy

| Metric | Value |
|--------|-------|
| **Total Contributions** | $104,050 CAD |
| **Final Equity** | $599,875.00 CAD |
| **Unspent Cash** | $810 CAD |
| **Total Return** | 59,888% |
| **CAGR** | 33.53% |
| **Max Drawdown** | -27.43% |

**Cash Deployment Breakdown:**
- Base contributions: $87,550 ($150 × 577 Mondays)
- Extra rainy-day buys: $16,500 ($100 × 165 successful deployments)
- Total: $104,050

---

### Rainy Day Only Strategy

| Metric | Value |
|--------|-------|
| **Total Contributions** | $47,000 CAD |
| **Final Equity** | $298,423.14 CAD |
| **Total Return** | 29,742% |
| **CAGR** | 29.38% |
| **Max Drawdown** | -27.17% |

**Contribution Breakdown:**
- Initial lump sum: $1,000
- Rainy Monday buys: $46,000 ($250 × 184 rainy Mondays)
- Total: $47,000 (46% less capital than baseline)

---

## Strategy Comparison & Analysis

### Key Findings

**1. Rainy Day Only Strategy:**
- **Middle performer** ($298,423 final equity) with 46% less capital
- **Lower CAGR** (29.38% vs 32.48% baseline) — missing regular DCA hurt compounding
- **Best capital efficiency?** Generated $6.35 per dollar invested vs $5.75 baseline
- **Conclusion:** Market timing alone underperforms regular DCA by -3.10% CAGR

**2. RSI Cash Strategy (Hybrid Approach):**
- **Highest returns** both absolute (+$96,532 vs baseline) and CAGR (33.53%)
- **Best of both worlds:** Regular DCA base + opportunistic extra buying
- **89.7% hit rate** on rainy-day deployments
- **Conclusion:** Combining regular DCA with tactical dip-buying delivers superior results

### 3-Way Performance Summary

| Metric | Baseline DCA | RSI Cash | Rainy Only | Winner |
|--------|--------------|----------|------------|--------|
| **Final Equity** | $503,343 | $599,875 | $298,423 | RSI Cash |
| **CAGR** | 32.48% | 33.53% | 29.38% | RSI Cash |
| **Capital Deployed** | $87,550 | $104,050 | $47,000 | Rainy Only (least) |
| **$ per $1 Invested** | $5.75 | $5.76 | $6.35 | Rainy Only |
| **Max Drawdown** | -27.50% | -27.43% | -27.17% | Rainy Only |

**Winner by Category:**
- **Absolute wealth creation:** RSI Cash Strategy
- **Risk-adjusted returns (CAGR):** RSI Cash Strategy
- **Capital efficiency ($/$ invested):** Rainy Day Only
- **Lowest drawdown:** Rainy Day Only (but only by 0.32%)

---

## Why Each Strategy Performed As It Did

### Baseline DCA: Solid but Unoptimized
- Consistent buying captures market growth over time
- No attempt to time entries = average entry prices
- Reliable, predictable, easy to execute

### RSI Cash: Best Overall Performance
- **Regular DCA foundation** ensures continuous market participation
- **Opportunistic add-ons** during weakness lower average cost basis
- **High hit rate (89.7%)** shows cash pool strategy works
- Caught major crises: 2008 (-35%), COVID (-30%), 2022 bear market

### Rainy Day Only: High Efficiency, Still Underperforms
- **Only buying dips** = better average entry prices (hence higher $/$ ratio at $6.35)
- **BUT:** Missed 393 bi-weekly Mondays of compounding (68% of opportunities)
- **Result:** Lower CAGR (29.38%) despite better capital efficiency
- **Lesson:** Even $250 rainy buys can't beat consistent DCA compounding over 22 years

---

## Outperformance Analysis (RSI Cash vs Baseline)

| Metric | Difference |
|--------|------------|
| **Absolute Gain** | **+$96,532 CAD** (19.18% more equity) |
| **CAGR Improvement** | +1.05 percentage points |
| **Extra Capital Deployed** | +$16,500 CAD |
| **Drawdown Improvement** | -0.07 percentage points (marginally better) |

### Return on Extra Capital Deployed (RSI Cash)
- Extra deployed: $16,500
- Extra gain: $96,532
- **Multiplier: 5.85x** (every extra $1 deployed generated $5.85 in additional wealth)

---

## Why Buying the Dips Works (But Not Alone)

### 1. **Lower Average Entry Prices**
- Rainy Day Only proves buying dips = better cost basis ($6.40 per $1 vs $5.75 baseline)
- BUT: Missing 68% of bi-weekly opportunities killed long-term compounding

### 2. **RSI Cash Gets Both Benefits**
- Regular DCA ensures continuous compounding
- Extra rainy-day buys lower average cost
- Result: Best CAGR (33.53%) AND best final equity ($599,875)

### 3. **Catching Major Crises**
### 3. **Catching Major Crises**
- Deployed capital during 184 rainy Mondays over 22 years
- Major opportunities captured:
  - **2008 Financial Crisis** (8-Monday period, -35% drawdown)
  - **COVID-19 Crash** (3-Monday period, -30% drawdown in 6 weeks)
  - **2022 Bear Market** (multiple 3-4 Monday periods)
  - **2011 Volatility** (5-Monday period, -11% drawdown)

### 4. **High Hit Rate (89.7% for RSI Cash)**
- Successfully deployed cash on 165 out of 184 rainy Mondays
- Only 19 missed opportunities (insufficient cash during prolonged downturns)
- $30 bi-weekly savings was sufficient for most dip-buying scenarios

### 5. **Same Downside Risk Across All Strategies**
- All three strategies had similar max drawdowns (-27.18% to -27.50%)
- Buying dips doesn't increase crash exposure
- Actually slightly reduces drawdown through better average entry prices

---

## Trade-offs & Limitations

### Baseline DCA
✅ Simplest to execute  
✅ Zero timing decisions  
✅ Proven long-term strategy  
❌ Doesn't capitalize on market weakness  
❌ Average entry prices  

### RSI Cash Strategy
✅ Highest returns (CAGR & absolute)  
✅ Opportunistic buying + regular base  
✅ High success rate (89.7%)  
❌ More complex (requires RSI monitoring)  
❌ Higher capital requirement (+$16,500)  
❌ Can miss opportunities in prolonged crashes (10.3% miss rate)  

### Rainy Day Only
✅ Best capital efficiency ($6.40 per $1)  
✅ Lowest capital requirement ($28,600)  
✅ Pure dip-buying discipline  
❌ **Lowest CAGR** (26.55% — underperforms baseline by 5.93%)  
❌ **Lowest final equity** ($183,028 — only 36% of baseline)  
❌ Missed 68% of compounding opportunities  
❌ Requires perfect execution (no emotional buying during rallies)  

---

## When To Use Each Strategy

### Use Baseline DCA If:
✅ You want zero complexity  
✅ You're uncomfortable with any market timing  
✅ You value set-it-and-forget-it simplicity  
✅ You don't want to track RSI or monitor markets  

### Use RSI Cash Strategy If:
✅ You want maximum long-term returns  
✅ You can save an extra $30 bi-weekly  
✅ You're comfortable monitoring RSI (simple indicator)  
✅ You want to capitalize on market dips systematically  
✅ You have 22+ year time horizon  

### Use Rainy Day Only If:
✅ You have limited capital and want to deploy it efficiently  
✅ You believe markets will have significant dips in your timeframe  
✅ You have discipline to NOT buy during rallies  
❌ **NOT recommended for wealth building** — underperformed baseline by -3.10% CAGR  
❌ Better suited for tactical deployment, not 20+ year strategy  
❌ Even with $250 buys, couldn't match regular DCA returns

---

## Rainy Period Analysis (RSI Cash Strategy)

### By Period Length

| Period Length | Count | Avg SPY Drawdown | Hit Rate | Avg Buys | Avg Missed |
|---------------|-------|------------------|----------|----------|------------|
| 1-Monday | 55 | 0.00% | 90.9% | 0.91 | 0.09 |
| 2-Monday | 25 | -1.66% | 98.0% | 1.96 | 0.04 |
| 3-Monday | 15 | -5.43% | 91.1% | 2.73 | 0.27 |
| 4-Monday | 4 | -3.35% | 75.0% | 3.00 | 1.00 |
| 5-Monday | 2 | -6.06% | 70.0% | 3.50 | 1.50 |
| 8-Monday | 1 | -34.98% | 37.5% | 3.00 | 5.00 |

**Key Insights:**
- Short periods (1-3 Mondays): Excellent hit rates (91-98%)
- Long periods (4+ Mondays): Cash pool depletes, miss rate increases
- Worst period: 2008 crisis (8 Mondays, only caught 3 out of 8 opportunities)

---

## Conclusion

### Bottom Line
**RSI Cash Strategy wins for wealth creation:**
- **+$96,532 more than baseline** (19.18% gain)
- **+1.05% higher CAGR** vs Baseline DCA
- **Same risk** (nearly identical max drawdown)
- **Modest extra capital** (+$16,500 over 22 years = $62/month)

**Rainy Day Only proves a critical insight:**
- Market timing improves cost basis (best $/$ efficiency at $6.35)
- BUT: Missing regular DCA destroyed long-term compounding
- Result: **Underperformed baseline** by -3.10% CAGR despite 46% less capital
- **Lesson:** Timing works ONLY when layered on top of regular DCA

### Final Verdict
**For maximum wealth creation over 22+ years:** RSI Cash Strategy delivers best results (+19.18% vs baseline, +1.05% higher CAGR).  
**For simplicity:** Baseline DCA is reliable and beats "Rainy Day Only" pure timing.  
**Key Insight:** Market timing works ONLY when combined with regular DCA — timing alone underperforms.

The 89.7% hit rate demonstrates the RSI Cash approach is **practical and sustainable** over decades. Rainy Day Only proves dip-buying improves cost basis but can't replace consistent compounding.

---

## Files & Charts Generated

1. **equity_baseline_rsi_dca.csv** - Daily baseline equity values
2. **equity_rsi_cash_strategy.csv** - Daily RSI strategy equity values
3. **equity_rainy_day_only.csv** - Daily Rainy Day Only equity values
4. **strategy_3way_comparison_summary.csv** - Performance metrics for all 3 strategies
5. **equity_rsi_comparison.png** - 2-way equity curves chart (Baseline vs RSI Cash)
6. **equity_3way_comparison.png** - 3-way equity curves chart (all strategies)
7. **rainy_period_cash_analysis.png** - Cash pool hit/miss visualization
8. **spy_price_with_rainy_periods.png** - SPY price with rainy periods highlighted
9. **consecutive_rsi_periods.csv** - Detailed rainy period tracking
10. **cash_spent_events.csv** - Log of 165 successful RSI Cash deployments
11. **missed_opportunities.csv** - 19 missed rainy Mondays (RSI Cash)
12. **rsi_below_30_mondays.csv** - All 184 rainy Monday events

---

*Backtest completed: November 21, 2025*  
*Script: `rsi_double_dca_backtest.py`*

---

## Parameter Sensitivity Analysis (RSI Cash Strategy)

### Current Settings
- **RSI Threshold:** 50
- **Cash Accumulation:** $30/period
- **Rainy-Day Buy:** $100

### Alternative Scenarios Tested

| Rainy-Day Amount | Hit Rate | Total Buys | Missed | Extra Deployed |
|------------------|----------|------------|--------|----------------|
| $30 | 100.0% | 184 | 0 | $5,520 |
| $50 | 97.3% | 179 | 5 | $8,950 |
| $75 | 92.4% | 170 | 14 | $12,750 |
| $90 | 90.2% | 166 | 18 | $14,940 |
| **$100** | **88.0%** | **162** | **22** | **$16,200** |
| $120 | 83.2% | 153 | 31 | $18,360 |
| $150 | 77.2% | 142 | 42 | $21,300 |

**Optimal Choice:** $100 provides ~88% hit rate, balancing aggression with consistency

---

## Assumptions & Caveats

### What's Modeled
✓ SPY price movements (2003-2025)  
✓ USD/CAD FX conversion  
✓ RSI(14) technical indicator  
✓ Fractional share purchases  
✓ Bi-weekly Monday investment schedule  

### What's NOT Modeled
✗ Trading commissions or fees  
✗ Taxes on capital gains  
✗ Dividends from SPY holdings  
✗ Slippage or market impact  
✗ Currency hedging costs  
✗ Actual VUN.TO tracking differences vs SPY  
✗ Psychological difficulty of executing strategy  
✗ Rebalancing or portfolio diversification  

### Data Limitations
- **Start Date:** 2003-10-07 (limited by FX data availability, not 2000-01-01 as requested)
- **Proxy Asset:** SPY + FX conversion (not actual VUN.TO Canadian ETF)
- **RSI Calculation:** Uses SPY USD prices (not CAD-adjusted)
- **Schedule Mapping:** Calendar Mondays mapped to nearest trading day

---

## Conclusion

### Bottom Line
**The RSI Cash Accumulation Strategy significantly outperformed Baseline DCA:**
- **+$97,616 more wealth** (19.18% gain)
- **+1.05% higher CAGR** 
- **Same risk** (nearly identical max drawdown)
- **Modest extra capital** (+$16,500 over 22 years = $62/month)

### Who Should Use This Strategy?
✅ Disciplined investors who can save $30 bi-weekly  
✅ Those comfortable with technical indicators (RSI)  
✅ Investors seeking to capitalize on market dips  
✅ Long-term holders (22+ year horizon)  

### Who Should Stick to Simple DCA?
✅ Investors wanting zero complexity  
✅ Those who can't commit extra capital during crashes  
✅ People uncomfortable with "timing" strategies  
✅ Set-it-and-forget-it mentality  

### Final Verdict
For investors willing to add modest complexity ($30 savings + RSI monitoring), the strategy delivers **material outperformance** with **no additional risk**. The 89.7% hit rate demonstrates it's practical and sustainable over decades.

---

## Files & Charts Generated

1. **equity_baseline_rsi_dca.csv** - Daily baseline equity values
2. **equity_rsi_cash_strategy.csv** - Daily RSI strategy equity values
3. **equity_rainy_day_only.csv** - Daily Rainy Day Only equity values
4. **strategy_3way_comparison_summary.csv** - Performance metrics for all 3 strategies
5. **equity_rsi_comparison.png** - 2-way equity curves chart (Baseline vs RSI Cash)
6. **equity_3way_comparison.png** - 3-way equity curves chart (all strategies)
7. **rainy_period_cash_analysis.png** - Cash pool hit/miss visualization
8. **spy_price_with_rainy_periods.png** - SPY price with rainy periods highlighted
9. **consecutive_rsi_periods.csv** - Detailed rainy period tracking
10. **cash_spent_events.csv** - Log of 165 successful RSI Cash deployments
11. **missed_opportunities.csv** - 19 missed rainy Mondays (RSI Cash)
12. **rsi_below_30_mondays.csv** - All 184 rainy Monday events

---

*Backtest completed: November 21, 2025*  
*Script: `rsi_double_dca_backtest.py`*
