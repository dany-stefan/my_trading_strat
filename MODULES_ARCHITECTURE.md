# Modules Architecture - Separation of Calculations and Display

## ✅ Current Architecture Confirmed

Both PROD and TURBO systems already follow best practices with **complete separation** between:
- **Calculation modules** (`market_metrics.py`) - All computations happen here
- **Display modules** (`email_generator.py`) - Only read values, no calculations

---

## 📊 PROD Architecture

### Module: `market_metrics.py`
**Purpose:** All calculations for PROD strategy

**Calculations Performed:**
- ✅ Rainy day evaluation: `is_rainy = rsi_sma < rsi_threshold`
- ✅ Cash deployment check: `can_deploy = cash_pool >= rainy_amount`
- ✅ Action determination: `rainy_deploy`, `rainy_insufficient`, or `save`
- ✅ Cash flow calculations: `new_cash_pool`, `cash_after_deploy`
- ✅ Total investment: `total_investment_today`
- ✅ Next payday calculation
- ✅ Display formatting: `price_display`, `cash_pool_display`, etc.
- ✅ Text blocks: `recommendation`, `action_text`, `cash_after_text`

**Class:** `MarketMetrics`
```python
metrics = calculate_market_metrics(
    rsi_sma=34.64,
    price=659.03,
    cash_pool=330.0,
    total_contributions=0,
    rainy_buys=[]
)
```

**Returns:** Dictionary with all computed values
```python
{
    "is_rainy": True,
    "can_deploy": True,
    "total_investment_today": 300.0,
    "new_cash_pool": 210.0,
    "price_display": "$659.03",
    "recommendation": "🔥 RECOMMENDATION: Buy extra $150 from cash pool",
    "action_text": "⭐⭐⭐ ACTION REQUIRED: RAINY BUY $150 CAD ⭐⭐⭐",
    ...
}
```

### Module: `email_generator.py`
**Purpose:** Read computed values and generate email content

**Operations:**
- ✅ Import `calculate_market_metrics` from `market_metrics`
- ✅ Call metrics calculation: `metrics = calculate_market_metrics(...)`
- ✅ Extract values: `all_metrics = metrics.get_all_metrics()`
- ✅ Read display strings: `price_display`, `rsi_sma_display`
- ✅ Read text blocks: `recommendation`, `action_text`
- ✅ Build email template with extracted values
- ❌ **NO inline calculations** - all math delegated to module

**Code Pattern:**
```python
from market_metrics import calculate_market_metrics

# Call calculation module
metrics = calculate_market_metrics(rsi_sma, price, cash_pool, ...)
all_metrics = metrics.get_all_metrics()

# Read values only (NO calculations)
is_rainy = all_metrics["is_rainy"]
recommendation = all_metrics["recommendation"]
action_text = all_metrics["action_text"]

# Use in template
body = f"""
{recommendation}
{action_text}
"""
```

---

## 🚀 TURBO Architecture

### Module: `market_metrics.py`
**Purpose:** All calculations for TURBO adaptive strategy

**Calculations Performed:**
- ✅ 200MA thresholds: `ma_plus_5_pct`, `ma_minus_5_pct`
- ✅ Deviation: `deviation_pct = (price - 200MA) / 200MA * 100`
- ✅ Regime classification: `BULL`, `BEAR`, or `NEUTRAL` (based on ±5%)
- ✅ Adaptive threshold: 42 (bull), 45 (neutral), 48 (bear)
- ✅ VIX level: `Low` (<15), `Medium` (15-25), `High` (>25)
- ✅ Volatility sizing: $150 (low), $180 (medium), $210 (high)
- ✅ All display formatting: regime emoji, formatted strings
- ✅ Explanation lines: regime logic, VIX sizing logic

**Class:** `MarketMetrics`
```python
metrics = calculate_market_metrics(
    price=659.03,
    spy_200ma=612.30,
    vix=23.4,
    rsi_sma=34.64
)
```

**Returns:** Dictionary with all computed values
```python
{
    "market_regime": "BULL",
    "regime_emoji": "🐂",
    "adaptive_threshold": 42,
    "vix_level": "Medium",
    "volatility_sizing": 180,
    "deviation_pct": 7.6,
    "deviation_display": "+7.6%",
    "ma_plus_5_display": "$642.91",
    "regime_threshold_line": "BULL (SPY > 200MA + 5%) → Selective RSI < 42",
    "vix_sizing_line": "Medium VIX (15-25) → Enhanced rainy $180 (+20%)",
    ...
}
```

### Module: `email_generator_turbo.py`
**Purpose:** Read computed values and generate TURBO email

**Operations:**
- ✅ Import `calculate_market_metrics` from `market_metrics`
- ✅ Call metrics calculation: `metrics = calculate_market_metrics(...)`
- ✅ Extract regime data: `market_regime`, `adaptive_threshold`
- ✅ Extract VIX data: `vix_level`, `volatility_sizing`
- ✅ Read display values: `deviation_display`, `regime_emoji`
- ✅ Read explanation lines: `regime_threshold_line`, `vix_sizing_line`
- ✅ Build decision tables and 3-factor summary
- ❌ **NO inline calculations** - all math delegated to module

**Code Pattern:**
```python
from market_metrics import calculate_market_metrics

# Call calculation module
metrics = calculate_market_metrics(price, spy_200ma, vix, rsi_sma)
all_metrics_dict = metrics.get_all_metrics()

# Read values only (NO calculations)
market_regime = metrics.market_regime
adaptive_threshold = metrics.adaptive_threshold
volatility_sizing = metrics.volatility_sizing
deviation_display = all_metrics_dict["deviation_display"]

# Use in template
decision_table = f"""
| REGIME | {market_regime} {deviation_display} | RSI < {adaptive_threshold} | ✅ Active |
| VOLATILITY | VIX {vix_display} | Size ${int(volatility_sizing)} | ✅ ${int(volatility_sizing)} |
"""
```

---

## 🔄 Integration Flow

### PROD Flow:
```
monitor_strategy.py
    ↓ fetch data (yfinance)
    ↓ calls calculate_market_metrics()
    ↓
market_metrics.py
    ↓ performs ALL calculations
    ↓ returns MarketMetrics object
    ↓
email_generator.py
    ↓ reads metrics.get_all_metrics()
    ↓ NO calculations, only template formatting
    ↓
email_formatter.py
    ↓ converts plain text to HTML
    ↓
SMTP delivery
```

### TURBO Flow:
```
monitor_strategy.py
    ↓ fetch data (yfinance + VIX)
    ↓ calls calculate_market_metrics()
    ↓
market_metrics.py
    ↓ performs ALL calculations
    ↓ regime detection, thresholds, VIX sizing
    ↓ returns MarketMetrics object
    ↓
email_generator_turbo.py
    ↓ reads metrics.get_all_metrics()
    ↓ NO calculations, only template formatting
    ↓
email_formatter.py
    ↓ converts plain text to HTML (with markdown tables)
    ↓
SMTP delivery
```

---

## ✅ Best Practices Confirmed

### ✓ Single Source of Truth
- All calculations in `market_metrics.py`
- Email generators are **read-only** consumers
- No duplicate logic across modules

### ✓ Testability
- `market_metrics.py` can be unit tested independently
- Email generators test templates, not calculations
- Mock metrics objects for email testing

### ✓ Maintainability
- Change threshold? Update `market_metrics.py` only
- Change regime logic? Update `market_metrics.py` only
- Change email format? Update `email_generator.py` only
- **No cross-contamination**

### ✓ Type Safety
- Metrics class provides structured data
- `get_all_metrics()` returns typed dictionary
- Clear contract between modules

### ✓ Reusability
- `market_metrics.py` used by:
  - `monitor_strategy.py` (live monitoring)
  - `email_generator.py` (email content)
  - Backtest scripts (can use same logic)
  - README snapshot writers

---

## 📋 Verification Checklist

- [x] PROD `market_metrics.py` exists and centralizes calculations
- [x] TURBO `market_metrics.py` exists and centralizes calculations
- [x] PROD `email_generator.py` imports from `market_metrics`
- [x] TURBO `email_generator_turbo.py` imports from `market_metrics`
- [x] No inline math in email generators (verified via grep)
- [x] All display formatting in metrics modules
- [x] All text blocks computed in metrics modules
- [x] Email generators only read and template
- [x] Monitor scripts use metrics for snapshots
- [x] Complete separation of concerns

---

## 🎯 Architecture Benefits

1. **Accuracy:** Calculations only exist in one place
2. **Consistency:** Email, snapshots, backtests use same logic
3. **Debugging:** Easy to trace where values come from
4. **Testing:** Can test calculations separately from templates
5. **Performance:** Calculations happen once, values reused
6. **Documentation:** Metrics module is self-documenting
7. **Auditing:** All decision logic in one reviewable module

---

*Last Verified: 2025-11-22*
*Architecture Status: ✅ FULLY COMPLIANT*
