# Market Metrics Module - PROD Documentation

## 📊 Latest Snapshot
*Auto-updated on each monitor run*

| Metric | Value |
|---|---|
| SPY Price | $680.62 |
| RSI SMA(7) | 45.56 |
| Cash Pool | $330.00 |
| Threshold | 45 |
| Rainy Today? | No |

*Last Updated: 2025-11-26 16:32:18*

---

## Overview
The `market_metrics.py` module centralizes all market-related calculations for the PROD email template. It computes rainy day logic, cash pool calculations, and provides formatted display values.

## Purpose
- **Separation of Concerns**: Keep calculations separate from email formatting
- **Single Source of Truth**: All decision logic in one place
- **Testability**: Easy to test calculations independently
- **Maintainability**: Update logic without touching templates

## Key Features

### 1. Rainy Day Logic
Determines if conditions are met for rainy day deployment:

- **RSI Check**: RSI SMA(7) < 45.0 (threshold)
- **Cash Check**: Cash pool >= $150 (rainy amount)
- **Action Types**: 
  - `rainy_deploy`: Deploy extra $150 (rainy + sufficient cash)
  - `rainy_insufficient`: Rainy but can't deploy (insufficient cash)
  - `save`: Not rainy, save $30 for future

### 2. Cash Pool Calculations
Automatically computes cash flow:

- **Rainy Deploy**: cash_pool - $150 + $30 = new_cash_pool
- **Save Mode**: cash_pool + $30 = new_cash_pool
- **Total Investment Today**: $150 base (always) + $150 rainy (if applicable)

### 3. Next Payday Calculation
Determines next payday text:

- **Before 15th**: "15th of this month"
- **After 15th**: "1st of [next month]"

## Usage

### Basic Usage
```python
from market_metrics import calculate_market_metrics

# Calculate all metrics
metrics = calculate_market_metrics(
    rsi_sma=34.64,
    price=659.03,
    cash_pool=330.0,
    total_contributions=0,
    rainy_buys=[]
)

# Access individual metrics
print(metrics.is_rainy)        # True
print(metrics.can_deploy)      # True
print(metrics.action_type)     # "rainy_deploy"
```

### Get All Metrics as Dictionary
```python
all_metrics = metrics.get_all_metrics()

# Raw values
print(all_metrics['rsi_sma'])              # 34.64
print(all_metrics['is_rainy'])             # True
print(all_metrics['new_cash_pool'])        # 210.0

# Formatted display strings
print(all_metrics['rsi_sma_display'])      # "34.64"
print(all_metrics['cash_pool_display'])    # "$330.00"
print(all_metrics['price_display'])        # "$659.03"
```

### Get Text Blocks
```python
# For email template
recommendation = metrics.get_recommendation()
# "🔥 RECOMMENDATION: Buy extra $150 from cash pool"

action_text = metrics.get_action_text()
# "⭐⭐⭐ ACTION REQUIRED: RAINY BUY $150 CAD ⭐⭐⭐..."

rainy_status = metrics.get_rainy_status()
# "✅ RAINY DAY - RSI SMA(7) < 45!"

cash_after_text = metrics.get_cash_after_text()
# "Cash pool after rainy buy: $180.00..."
```

## Integration with Email Generator

The email_generator.py now imports and uses this module:

```python
from market_metrics import calculate_market_metrics

def generate_email_content(rsi_sma, price, cash_pool, ...):
    # Calculate all metrics
    metrics = calculate_market_metrics(
        rsi_sma=rsi_sma,
        price=price,
        cash_pool=cash_pool,
        total_contributions=total_contributions,
        rainy_buys=rainy_buys
    )
    
    # Extract all computed values
    all_metrics = metrics.get_all_metrics()
    is_rainy = all_metrics["is_rainy"]
    recommendation = all_metrics["recommendation"]
    action_text = all_metrics["action_text"]
    # ... etc
```

## Return Values

### MarketMetrics.get_all_metrics() Returns:

**Raw Values:**
- `rsi_sma`: RSI SMA(7) value (float)
- `price`: Current SPY price (float)
- `cash_pool`: Current cash balance (float)
- `total_contributions`: Total contributions to date (float)
- `rainy_buys_count`: Number of rainy buys (int)
- `rsi_threshold`: RSI threshold (45.0)
- `is_rainy`: Rainy day condition met (bool)
- `can_deploy`: Sufficient cash to deploy (bool)
- `total_investment_today`: Base + rainy if applicable (float)
- `new_cash_pool`: Cash pool after action (float)
- `cash_after_deploy`: Cash after rainy buy, before save (float or None)
- `next_payday_text`: Next payday description (str)
- `action_type`: "rainy_deploy", "rainy_insufficient", or "save" (str)

**Display Strings:**
- `price_display`: "$659.03"
- `rsi_sma_display`: "34.64"
- `cash_pool_display`: "$330.00"
- `total_contributions_display`: "$0.00"
- `new_cash_pool_display`: "$210.00"

**Text Blocks:**
- `recommendation`: Full recommendation text
- `action_text`: Action required text with stars
- `cash_after_text`: Cash flow explanation
- `rainy_status`: Status with emoji
- `decision_result`: Decision path result
- `initial_note`: Initial cash pool note (if applicable)
- `cash_available_line`: Cash available line (if rainy)

## Testing

Run unit tests:
```bash
python -c "
from market_metrics import calculate_market_metrics

# Test rainy deploy
metrics = calculate_market_metrics(34.64, 659.03, 330.0, 0, [])
assert metrics.is_rainy == True
assert metrics.can_deploy == True
assert metrics.action_type == 'rainy_deploy'
print('✓ Rainy deploy test passed')

# Test rainy insufficient
metrics = calculate_market_metrics(38.5, 659.03, 100.0, 500.0, [])
assert metrics.is_rainy == True
assert metrics.can_deploy == False
assert metrics.action_type == 'rainy_insufficient'
print('✓ Rainy insufficient test passed')

# Test save mode
metrics = calculate_market_metrics(52.3, 659.03, 200.0, 1000.0, [])
assert metrics.is_rainy == False
assert metrics.action_type == 'save'
print('✓ Save mode test passed')
"
```

## Benefits

1. **No More Inline Calculations**: Email template is clean, only displays values
2. **Consistent Logic**: All decision logic in one place
3. **Easy Testing**: Test calculations independently from email generation
4. **Maintainability**: Change threshold values or logic in one place
5. **Type Safety**: Returns properly typed values with clear semantics
6. **Formatted Display**: Automatic formatting for currency and decimals

## Action Types

- **rainy_deploy**: RSI < 45 AND cash >= $150 → Deploy $150 rainy buy
- **rainy_insufficient**: RSI < 45 BUT cash < $150 → Base buy only, save $30
- **save**: RSI >= 45 → Base buy only, save $30

## Default Parameters

- `rsi_threshold`: 45.0 (RSI SMA(7) threshold)
- `dca_base_amount`: 150.0 (Base investment per payday)
- `rainy_amount`: 150.0 (Extra deployment on rainy days)
- `cash_accumulation`: 30.0 (Cash saved per payday)
- `payday_day_of_month_2`: 15 (Second payday of month)
