# RSI Calculation - Single Source of Truth

## 📌 Overview

All RSI calculations in this project use the **shared `rsi_indicators.py` module** to ensure consistency across all scripts.

## ✅ Canonical Implementation

**File:** `rsi_indicators.py`

**Method:** Wilder's Smoothing (industry standard, matches TradingView)

**Functions:**
- `compute_rsi(series, period=14)` - Calculate RSI using Wilder's smoothing
- `compute_rsi_sma(rsi_series, period=7)` - Calculate SMA of RSI values  
- `compute_rsi_with_sma(price_series, rsi_period=14, sma_period=7)` - Calculate both in one call

## 🔧 Scripts Using Shared Module

All scripts import from `rsi_indicators.py` to ensure identical calculations:

1. **`rsi_calendar_date_backtest.py`** - Main backtest (historical analysis)
2. **`monitor_strategy.py`** - Live monitoring (bi-weekly emails)
3. **`update_rsi_verification.py`** - RSI verification list updates
4. **`simulate_payday_email.py`** - Email simulation/testing

## ⚠️ DO NOT Duplicate RSI Logic

**Never** copy/paste RSI calculation code. Always import from `rsi_indicators.py`.

### ❌ Bad (duplicated logic):
```python
def my_rsi_function(data):
    delta = data.diff()
    # ... duplicated Wilder's smoothing logic
```

### ✅ Good (reuse shared module):
```python
from rsi_indicators import compute_rsi_with_sma

rsi, rsi_sma = compute_rsi_with_sma(price_data)
```

## 🎯 Why This Matters

**Consistency:** All scripts calculate identical RSI values
- Backtest uses same RSI as live monitoring
- Verification list uses same RSI as email reports
- No discrepancies between different scripts

**Maintainability:** Change RSI logic in one place
- Update `rsi_indicators.py` → all scripts updated
- No need to hunt down duplicated code
- Easier to fix bugs or improve algorithm

**Accuracy:** Single implementation = single point of validation
- Verified against TradingView once
- All scripts inherit verified calculation
- Reduces testing burden

## 📊 Verification

The RSI calculation has been verified to match TradingView exactly:
- File: `RSI_VERIFICATION_LIST.txt`
- Match rate: 100% (all dates match TradingView values)
- Period: 2025-03-31 to present

## 🔍 Implementation Details

**Wilder's Smoothing Formula:**

1. First average: Simple Moving Average over initial period
   ```
   avg_gain[period] = mean(gains[1:period+1])
   avg_loss[period] = mean(losses[1:period+1])
   ```

2. Subsequent averages: Wilder's smoothing
   ```
   avg_gain[i] = (avg_gain[i-1] * (period-1) + gain[i]) / period
   avg_loss[i] = (avg_loss[i-1] * (period-1) + loss[i]) / period
   ```

3. RSI calculation:
   ```
   RS = avg_gain / avg_loss
   RSI = 100 - (100 / (1 + RS))
   ```

This matches the industry standard used by:
- TradingView
- MetaTrader
- Bloomberg Terminal
- Most financial platforms

## 📚 Related Files

- `rsi_indicators.py` - **SINGLE SOURCE OF TRUTH** for RSI calculations
- `RSI_VERIFICATION_LIST.txt` - Verification against TradingView
- `WILDER_RSI_MIGRATION_COMPLETE.md` - Migration history to Wilder's method
