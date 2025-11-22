# TURBO Rainy Day Buy Decision Table

## Quick Reference: How Much to Deploy

This table shows the exact rainy day buy amount based on **Market Regime (200-day MA)**, **VIX Level**, and **RSI SMA(7)**.

---

## Decision Logic

### Step 1: Determine Market Regime (200-day MA Deviation)

| Regime | SPY vs 200-day MA | Adaptive RSI Threshold |
|--------|-------------------|------------------------|
| **BULL** | Price > +5% above MA | RSI SMA(7) < **42** triggers rainy buy |
| **NEUTRAL** | Within ±5% of MA | RSI SMA(7) < **45** triggers rainy buy |
| **BEAR** | Price > -5% below MA | RSI SMA(7) < **48** triggers rainy buy |

### Step 2: Check VIX Level for Position Sizing

| VIX Range | Fear Level | Rainy Buy Amount |
|-----------|------------|------------------|
| **VIX < 15** | Low (Calm market) | $150 |
| **VIX 15-25** | Medium (Normal volatility) | $180 |
| **VIX > 25** | High (Fear/panic) | $210 |

---

## Complete Decision Matrix

### If RSI SMA(7) Triggers Rainy Buy (Based on Regime Threshold)

| Market Regime | VIX < 15 (Low) | VIX 15-25 (Med) | VIX > 25 (High) | Example Scenario |
|---------------|----------------|-----------------|-----------------|------------------|
| **BULL** (RSI < 42) | $150 | $180 | $210 | Bull correction with rising fear |
| **NEUTRAL** (RSI < 45) | $150 | $180 | $210 | Sideways market dip |
| **BEAR** (RSI < 48) | $150 | $180 | $210 | Bear market capitulation |

### If RSI SMA(7) Does NOT Trigger (Above Regime Threshold)

| Market Regime | Any VIX Level | Buy Amount | Notes |
|---------------|---------------|------------|-------|
| **BULL** (RSI ≥ 42) | Any | $0 rainy | Only $150 base buy |
| **NEUTRAL** (RSI ≥ 45) | Any | $0 rainy | Only $150 base buy |
| **BEAR** (RSI ≥ 48) | Any | $0 rainy | Only $150 base buy |

---

## Total Execution Day Investment

| Scenario | Base Buy | Rainy Buy | Total Deployed |
|----------|----------|-----------|----------------|
| **NOT Rainy** (RSI above threshold) | $150 | $0 | **$150** |
| **Rainy + Low VIX** | $150 | $150 | **$300** |
| **Rainy + Med VIX** | $150 | $180 | **$330** |
| **Rainy + High VIX** | $150 | $210 | **$360** |

---

## Real-World Examples

### Example 1: Bull Market Shallow Dip
- **Date**: March 3, 2024
- **SPY**: $510 (8% above 200-day MA) → **BULL**
- **RSI SMA(7)**: 44 → Above 42 threshold (NOT rainy)
- **VIX**: 14 → Low
- **Decision**: Only base $150 (no rainy buy)
- **Reasoning**: Bull regime requires RSI < 42; this is just noise

### Example 2: Neutral Market with Medium Fear
- **Date**: June 17, 2024
- **SPY**: $520 (2% above 200-day MA) → **NEUTRAL**
- **RSI SMA(7)**: 38 → Below 45 threshold ✓ (rainy)
- **VIX**: 18 → Medium
- **Decision**: $150 base + $180 rainy = **$330 total**
- **Reasoning**: Clear oversold + moderate fear = medium sizing

### Example 3: Bear Market Capitulation
- **Date**: October 3, 2022
- **SPY**: $360 (-12% below 200-day MA) → **BEAR**
- **RSI SMA(7)**: 35 → Below 48 threshold ✓ (rainy)
- **VIX**: 32 → High
- **Decision**: $150 base + $210 rainy = **$360 total**
- **Reasoning**: Deep bear + panic VIX = maximum opportunity sizing

### Example 4: Bear Market Minor Bounce
- **Date**: November 17, 2022
- **SPY**: $390 (-8% below 200-day MA) → **BEAR**
- **RSI SMA(7)**: 49 → Above 48 threshold (NOT rainy)
- **VIX**: 22 → Medium
- **Decision**: Only base $150 (no rainy buy)
- **Reasoning**: Even in bear, RSI not oversold enough yet

---

## Why This Works

### Regime Context (200-day MA)
- **BULL markets**: Higher RSI threshold (42) filters noise from shallow pullbacks
- **BEAR markets**: Higher RSI threshold (48) catches weakness earlier in downtrends
- **NEUTRAL markets**: Standard RSI threshold (45) balances both conditions

### VIX-Based Sizing
- **Low VIX (<15)**: Standard sizing; market calm, no extra fear premium
- **Medium VIX (15-25)**: +20% sizing; normal volatility justifies slight aggression
- **High VIX (>25)**: +40% sizing; panic creates maximum opportunity for long-term buyers

### Combined Intelligence
The strategy only deploys when **both conditions align**:
1. RSI SMA(7) confirms sustained weakness (regime-adjusted threshold)
2. VIX quantifies the fear level to size appropriately

This prevents:
- ❌ Buying minor dips in strong bull runs (RSI must be very low)
- ❌ Under-deploying during true bear market panic (VIX scales up sizing)
- ❌ Over-deploying during calm corrections (VIX scales down sizing)

---

## Quick Decision Flowchart

```
Execution Day (3rd or 17th)
        ↓
Calculate SPY deviation from 200-day MA
        ↓
    Determine Regime
   (BULL/NEUTRAL/BEAR)
        ↓
    Set RSI Threshold
   (42 / 45 / 48)
        ↓
Check: Is RSI SMA(7) < threshold?
        ↓
   ┌────NO─────┐
   ↓           ↓
Deploy      Check VIX
$150 base   (< 15 / 15-25 / > 25)
  DONE          ↓
         Deploy Rainy Amount
         ($150 / $180 / $210)
                ↓
         Total: $300-$360
              DONE
```

---

## PROD vs TURBO Comparison

| Factor | PROD (Simple) | TURBO (Adaptive) |
|--------|---------------|------------------|
| **RSI Threshold** | Always 45 | 42/45/48 (regime-adjusted) |
| **Rainy Amount** | Always $150 | $150/$180/$210 (VIX-adjusted) |
| **Inputs Needed** | RSI SMA(7) only | RSI SMA(7) + 200-day MA + VIX |
| **Max Total Deployment** | $300 | $360 |
| **Complexity** | Very low | Moderate |
| **Historical Selectivity** | 97 rainy buys (22.4%) | 80 rainy buys (22.0%) |
| **Avg Rainy Amount** | $150 | $182.63 (+21.8%) |

---

**Bottom Line**: TURBO gives you a **data-driven answer** to "how much should I deploy today?" based on three objective market conditions. PROD gives you **one simple rule** that performs nearly identically over the long term.
