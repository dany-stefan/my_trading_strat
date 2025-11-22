# Market Metrics Module - Documentation

## 📊 Latest Snapshot
*Auto-updated on each monitor run*

| Metric | Value |
|---|---|
| SPY Price | $659.03 |
| 200MA | $612.30 |
| Deviation | +7.6% |
| 200MA +5% | $642.91 |
| 200MA -5% | $581.68 |
| RSI SMA(7) | 34.64 |
| VIX | 23.4 (Medium) |
| Market Regime | 🐂 BULL |
| Adaptive Threshold | 42 |
| Rainy Sizing | $180 |

*Last Updated: 2025-11-22 01:54:48*

---

## Overview
The `market_metrics.py` module centralizes all market-related calculations for the TURBO email template. It computes 200MA thresholds, determines market regime, calculates adaptive RSI thresholds, and VIX-based sizing.

## Purpose
- **Separation of Concerns**: Keep calculations separate from email formatting
- **Single Source of Truth**: All metric logic in one place
- **Testability**: Easy to test calculations independently
- **Maintainability**: Update calculation logic without touching templates

## Key Features

### 1. Market Regime Classification
Determines market regime based on SPY price vs 200-day moving average:

- **BULL**: SPY > 200MA +5% → Adaptive threshold: RSI < 42 (selective)
- **NEUTRAL**: SPY ±5% of 200MA → Adaptive threshold: RSI < 45 (standard)
- **BEAR**: SPY < 200MA -5% → Adaptive threshold: RSI < 48 (aggressive)

### 2. Fallback Logic (No 200MA Available)
When 200MA data is unavailable, uses VIX as secondary indicator:

- **Low VIX (<15)**: NEUTRAL regime
- **Medium VIX (15-30)**: NEUTRAL regime
- **High VIX (>30)**: BEAR regime
- **No VIX**: Defaults to NEUTRAL (instead of UNKNOWN)

### 3. 200MA Threshold Calculations
Automatically computes boundary values:

- **200MA +5%**: Upper regime boundary (bull threshold)
- **200MA -5%**: Lower regime boundary (bear threshold)
- **Deviation %**: Current distance from 200MA

### 4. VIX-Based Volatility Sizing
Scales rainy day deployment based on fear index:

- **VIX < 15 (Low)**: $150 standard deployment
- **VIX 15-25 (Medium)**: $180 deployment (+20%)
- **VIX > 25 (High)**: $210 deployment (+40%)

## Usage

### Basic Usage
```python
from market_metrics import calculate_market_metrics

# Calculate all metrics
metrics = calculate_market_metrics(
    price=659.03,
    spy_200ma=549.75,
    vix=23.4
)

# Access individual metrics
print(metrics.market_regime)        # "BULL"
print(metrics.adaptive_threshold)   # 42.0
print(metrics.volatility_sizing)    # 180.0
```

### Get All Metrics as Dictionary
```python
all_metrics = metrics.get_all_metrics()

# Raw values
print(all_metrics['price'])              # 659.03
print(all_metrics['deviation_pct'])      # 19.9

# Formatted display strings
print(all_metrics['price_display'])      # "$659.03"
print(all_metrics['deviation_display'])  # "+19.9%"
print(all_metrics['regime_emoji'])       # "🐂"
```

### Get Explanation Lines
```python
# For email template
regime_line = metrics.get_regime_threshold_line()
# "BULL (SPY > 200MA +5%) → Selective RSI < 42"

vix_line = metrics.get_vix_sizing_line()
# "Medium VIX (15-25) → Enhanced rainy $180 (+20%)"

description = metrics.get_regime_description()
# "Bull Market (SPY > 200MA +5%)"
```

## Integration with Email Generator

The email_generator_turbo.py now imports and uses this module:

```python
from market_metrics import calculate_market_metrics

def generate_email_content(rsi_sma, price, cash_pool, ...):
    # Calculate all metrics
    metrics = calculate_market_metrics(price, spy_200ma, vix)
    
    # Extract values for template
    market_regime = metrics.market_regime
    adaptive_threshold = metrics.adaptive_threshold
    volatility_sizing = metrics.volatility_sizing
    
    # Get formatted display strings
    all_metrics = metrics.get_all_metrics()
    spy_200ma_display = all_metrics["spy_200ma_display"]
    ma_plus_5_display = all_metrics["ma_plus_5_display"]
    # ... etc
```

## Return Values

### MarketMetrics.get_all_metrics() Returns:

**Raw Values:**
- `price`: Current SPY price (float)
- `spy_200ma`: 200-day MA (float or None)
- `ma_plus_5_pct`: 200MA * 1.05 (float or None)
- `ma_minus_5_pct`: 200MA * 0.95 (float or None)
- `deviation_pct`: % deviation from 200MA (float or None)
- `market_regime`: "BULL", "BEAR", or "NEUTRAL"
- `adaptive_threshold`: RSI threshold (42.0, 45.0, or 48.0)
- `vix`: VIX value (float or None)
- `vix_level`: "Low", "Medium", "High", or None
- `volatility_sizing`: Rainy amount (150.0, 180.0, or 210.0)

**Display Strings:**
- `price_display`: "$659.03"
- `spy_200ma_display`: "$549.75" or "N/A"
- `ma_plus_5_display`: "$577.24" or "N/A"
- `ma_minus_5_display`: "$522.26" or "N/A"
- `deviation_display`: "+19.9%" or "N/A"
- `vix_display`: "23.4" or "N/A"
- `vix_level_display`: "Medium" or "N/A"
- `regime_emoji`: "🐂", "🐻", or "⚖️"
- `regime_description`: "Bull Market (SPY > 200MA +5%)"
- `regime_threshold_line`: "BULL (SPY > 200MA +5%) → Selective RSI < 42"
- `vix_sizing_line`: "Medium VIX (15-25) → Enhanced rainy $180 (+20%)"

## Testing

Run unit tests:
```bash
python -c "
from market_metrics import calculate_market_metrics

# Test BULL regime
metrics = calculate_market_metrics(659.03, 549.75, 23.4)
assert metrics.market_regime == 'BULL'
assert metrics.adaptive_threshold == 42.0
assert metrics.volatility_sizing == 180.0
print('✓ BULL regime test passed')

# Test NEUTRAL fallback
metrics = calculate_market_metrics(659.03, None, None)
assert metrics.market_regime == 'NEUTRAL'
assert metrics.adaptive_threshold == 45.0
print('✓ NEUTRAL fallback test passed')
"
```

## Benefits

1. **No More Inline Calculations**: Email template is clean, only displays values
2. **Consistent Logic**: Regime determination in one place, can't get out of sync
3. **Easy Testing**: Test calculations independently from email generation
4. **Maintainability**: Change threshold values or logic in one place
5. **Fallback Handling**: Graceful degradation when data unavailable
6. **Type Safety**: Returns properly typed values with clear semantics

## Default Behavior

- **Missing 200MA**: Defaults to NEUTRAL regime (uses VIX as hint if available)
- **Missing VIX**: Defaults to $150 standard rainy sizing
- **Missing Both**: NEUTRAL regime, $150 sizing, 45.0 threshold
- **Display Strings**: Always return "N/A" for missing data (never None or empty)
