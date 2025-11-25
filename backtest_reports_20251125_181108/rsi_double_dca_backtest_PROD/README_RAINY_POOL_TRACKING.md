# Rainy Pool ROI Tracking

## Overview

Starting December 3, 2025, production emails will include real-time tracking of accumulated rainy day contributions and their return on investment (ROI).

## What Gets Tracked

The rainy pool tracker monitors:

- **Total Rainy Contributions**: Sum of all rainy buy amounts ($150 each)
- **Average Rainy Buy Price**: Average SPY price across all rainy day purchases
- **Current SPY Price**: Current market price (for comparison)
- **Current Rainy Pool Value**: Current market value of shares purchased during rainy buys
- **Rainy Pool Profit**: Dollar gain/loss on rainy contributions
- **Rainy Pool ROI**: Percentage return on rainy investments only
- **Rainy Buys Deployed**: Count of successful rainy day deployments (on 3rd/17th)

## How It Works

### Data Source
- Reads from `strategy_tracking.json` → `rainy_buys[]` array
- Each rainy buy record contains: `{date, rsi_sma, price, amount, cash_before, cash_after}`

### Calculation Logic

```python
# 1. Sum all rainy contributions
total_invested = sum(buy['amount'] for buy in rainy_buys)

# 2. Calculate total shares from rainy buys
total_shares = sum(buy['amount'] / buy['price'] for buy in rainy_buys)

# 3. Get current market value
current_value = total_shares * current_spy_price

# 4. Calculate profit and ROI
profit = current_value - total_invested
roi_percent = (profit / total_invested) * 100
```

### Display Location

The rainy pool section appears in the **METRICS SNAPSHOT** section of production emails:

```
📌 METRICS SNAPSHOT (Markdown)
| Metric | Value |
|---|---|
| SPY Price | $668.73 |
| RSI(14) | 49.48 |
| RSI SMA(7) | 42.68 |
| Cash Pool | $330.00 |
| Threshold | 45 |
| Rainy Today? | Yes |

💧 RAINY POOL PERFORMANCE TRACKER
| Metric | Value |
|---|---|
| Total Rainy Contributions | $450.00 CAD |
| Average Rainy Buy Price | $558.33 USD |
| Current SPY Price | $668.73 USD |
| Current Rainy Pool Value | $542.19 CAD |
| Rainy Pool Profit | $92.19 CAD |
| Rainy Pool ROI | 20.49% |
| Rainy Buys Executed | 3 |

*This tracks ONLY your rainy day contributions and their performance*
```

## Production vs Test Mode

**Production Emails** (`is_simulation=False`):
- ✅ Shows rainy pool tracking section
- Sent on 3rd/17th deployment days via GitHub Actions

**Test Emails** (`is_simulation=True`):
- ❌ Hides rainy pool tracking section
- Run manually via `simulate_payday_email.py`

## Example Timeline

| Date | Event | Rainy Contributions | Avg Buy Price | Current Value | ROI |
|------|-------|---------------------|---------------|---------------|-----|
| Dec 3, 2025 | First deployment check | $0 | $0 | $0 | 0% |
| Mar 3, 2026 | First rainy buy @ $520 | $150 | $520.00 | $160 | 6.7% |
| Apr 17, 2026 | Second rainy buy @ $535 | $300 | $527.50 | $325 | 8.3% |
| Nov 3, 2026 | Third rainy buy @ $620 | $450 | $558.33 | $542 | 20.5% |

## Files Modified

### `email_generator.py`
- Added rainy pool calculation logic at function start
- Created `rainy_pool_section` variable with conditional display
- Appended section to `metrics_markdown` (only when `not is_simulation`)

### `monitor_strategy.py`
- No changes needed - already tracks rainy buys with price data
- Existing `strategy_tracking.json` structure supports ROI calculation

### `strategy_tracking.json`
- Existing structure already captures required data:
  ```json
  {
    "rainy_buys": [
      {
        "date": "2025-03-03",
        "rsi_sma": 42.5,
        "price": 520.0,
        "amount": 150.0,
        "cash_before": 330.0,
        "cash_after": 180.0
      }
    ]
  }
  ```

## Testing

Run test script to verify tracking:

```bash
cd rsi_double_dca_backtest_PROD
python3 test_rainy_pool_tracking.py
```

Expected output:
- ✅ Rainy pool section appears in production mode
- ✅ Rainy pool section hidden in test mode
- ✅ ROI calculations match expected values

## Notes

- **Isolated Tracking**: This tracks ONLY rainy day contributions ($150 each), not base DCA ($150 bi-weekly)
- **Real-Time Updates**: Recalculates on every email using current SPY price
- **Historical Accuracy**: Uses actual purchase prices from `strategy_tracking.json`
- **Cumulative Display**: Shows lifetime rainy pool performance, not period-specific

## Future Enhancements

Potential additions:
- Average rainy buy price
- Best/worst rainy buy performance
- Rainy pool CAGR calculation
- Comparison to base DCA performance
