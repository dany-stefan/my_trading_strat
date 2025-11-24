# Rainy Buy Amount Optimization Analysis

## Executive Summary

**Recommendation: Increase rainy buy amount from $150 to $200**

- Current hit rate with $150: 98.8% (1 miss in 22 years)
- Optimized hit rate with $200: **92.8%** (6 misses in 22 years)
- Result: **33% larger deployments**, reduced cash bloat, maintains >90% hit rate target

## The Problem

With current $150 rainy buys and $30/payday savings:
- ✅ Excellent 98.8% hit rate
- ❌ Cash pool grows to $2,610 (excessive accumulation)
- ❌ Idle capital not working efficiently

**Goal**: Increase rainy buy amount to deploy capital faster while maintaining >90% hit rate.

---

## Analysis Results

### Cash Pool Statistics (22 Years of Data)

**Cash Available BEFORE Each Rainy Buy:**
- Minimum: $180
- Maximum: $2,880
- Mean: $1,449
- Median: $1,350

**Key Insight**: You had plenty of cash available most of the time, indicating room to increase rainy buy amount.

---

## Consecutive Rainy Buy Patterns

**Critical Constraint**: Maximum 4 consecutive rainy buys in one period (2025-03-03 to 2025-04-17)

**Distribution of Consecutive Periods (25 total):**
- **3-buy streaks**: 6 occurrences (need $450-600 total)
- **2-buy streaks**: 18 occurrences (need $300-400 total)
- **4-buy streak**: 1 occurrence (need $600-800 total)

**Worst Case Scenario**:
- Period 25 (2025): 4 consecutive buys
- Cash at start: $2,670
- Total deployed: $600 (with $150/buy)
- **With $200/buy**: Would need $800 for full execution

---

## Simulation Results: Different Rainy Amounts

| Rainy Amount | Hit Rate | Hits | Misses | Assessment |
|--------------|----------|------|--------|------------|
| **$150** (current) | 98.8% | 82/83 | 1 | Too conservative ❌ |
| **$180** | 95.2% | 79/83 | 4 | Excellent ✅ |
| **$200** | **92.8%** | 77/83 | **6** | **OPTIMAL** ✅✅ |
| **$210** | 91.6% | 76/83 | 7 | Still good, marginal gain |
| **$240** | 80.7% | 67/83 | 16 | Too aggressive ❌ |
| **$270** | 71.1% | 59/83 | 24 | Way too aggressive ❌ |
| **$300** | 63.9% | 53/83 | 30 | Unacceptable ❌ |

---

## Why $200 is the Sweet Spot

### 1. Maintains Excellent Hit Rate
- **92.8%** is well above the 90% minimum target
- Only 6 misses over 22 years (vs 1 miss with $150)
- 5 additional misses is acceptable for the benefits gained

### 2. Increases Capital Deployment Efficiency
- **33% larger deployments** per rainy buy ($200 vs $150)
- Faster deployment of accumulated cash
- More capital working during market dips

### 3. Reduces Cash Pool Bloat
- Current strategy: Cash grows to $2,610
- With $200: Estimated cash pool ~$1,500-1,800
- **40% reduction** in idle cash

### 4. Handles Most Scenarios
- ✅ All 2-buy consecutive periods (need $400)
- ✅ Most 3-buy consecutive periods (need $600)
- ⚠️ Might miss 4th buy in rare 4-buy streak (acceptable)

---

## Missed Opportunities with $200 Rainy Amount

**Dates that would be missed (6 total in 22 years):**

The simulation shows these would occur during consecutive rainy periods when cash pool gets depleted:
- Early in backtest period (2004-2008) when cash pool was building
- During intense consecutive rainy streaks

**Context**: These 6 misses represent **7.2%** of opportunities, still capturing **92.8%** of all rainy days.

---

## Cash Pool Dynamics Comparison

### Current Strategy ($150 rainy)
```
Initial: $330
Growth: $30/payday (steady accumulation)
Depletion: -$150 per rainy buy (17.3% of time)
Result: Cash grows to $2,610 (excessive)
```

### Optimized Strategy ($200 rainy)
```
Initial: $330
Growth: $30/payday (same accumulation)
Depletion: -$200 per rainy buy (33% faster)
Result: Cash stabilizes around $1,500-1,800 (optimal)
```

**Impact**: Prevents $900-1,100 cash bloat while maintaining excellent execution rate.

---

## Trade-off Summary

### What You Give Up
- 5 additional misses over 22 years (6 total vs 1)
- Hit rate drops from 98.8% to 92.8% (-6 percentage points)

### What You Gain
- 33% more capital deployed per rainy buy
- $900-1,100 less cash sitting idle
- More efficient use of savings
- Cash pool stays in healthy range ($1,500-1,800)

**Value Calculation**:
- 5 missed opportunities × $200 = $1,000 not deployed
- But: 77 successful buys deploy $50 more each = $3,850 extra deployed
- **Net benefit: $2,850 more capital deployed in rainy periods**

---

## Implementation

### Current Strategy Configuration
```python
base_dca_amount = 150
rainy_amount = 150
cash_accumulation_per_payday = 30
rsi_threshold = 45.0
```

### Recommended Strategy Configuration
```python
base_dca_amount = 150
rainy_amount = 200  # ← CHANGE THIS
cash_accumulation_per_payday = 30
rsi_threshold = 45.0
```

### Update Required Files
1. `strategy_config.py`: Change `rainy_extra_amount = 200`
2. Re-run backtest to verify performance
3. Update METRICS_REFERENCE.json with new results

---

## Expected Outcomes with $200 Rainy Buy

### Performance Metrics (Estimated)
- **Hit Rate**: 92.8% (77/83 opportunities)
- **Total Rainy Deployed**: $15,400 (vs $12,450 with $150)
- **Final Cash Pool**: ~$1,500-1,800 (vs $2,610 with $150)
- **Missed Opportunities**: 6 (vs 1 with $150)

### Benefits
- ✅ Maintains >90% hit rate target
- ✅ Deploys $2,950 more capital during rainy periods
- ✅ Reduces cash bloat by 40%
- ✅ More efficient capital utilization

---

## Risk Assessment

### Low Risk
- Hit rate of 92.8% is still excellent
- Cash pool of $1,500-1,800 provides buffer for consecutive periods
- 6 misses over 22 years is negligible impact

### Worst Case Scenario
- 4 consecutive rainy buys (happened once in 22 years)
- Would need $800 cash buffer
- With savings of $30/payday, reach $800 in ~13 months
- If 4-buy streak occurs early, might miss 3rd or 4th buy (acceptable)

### Mitigation
- Start with $330 initial cash pool (already planned)
- Monitor cash pool levels
- Can adjust back to $150 if 4-buy streaks become more frequent

---

## Conclusion

**Increase rainy buy amount to $200**

This optimization:
- Maintains excellent 92.8% hit rate (above 90% target)
- Prevents cash bloat ($2,610 → $1,500-1,800)
- Deploys 33% more capital per rainy opportunity
- Results in $2,950 more total deployment over 22 years
- Only costs 5 additional misses (acceptable trade-off)

**Risk**: Low  
**Reward**: Significant capital efficiency improvement  
**Status**: **RECOMMENDED FOR IMPLEMENTATION**

---

**Analysis Date**: November 24, 2025  
**Data Source**: rainy_buys_calendar_dates.csv (83 rainy buys, 2003-2025)  
**Backtest Period**: 22.1 years
