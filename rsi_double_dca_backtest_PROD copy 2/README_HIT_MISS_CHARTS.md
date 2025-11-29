# Hit/Miss Marker Charts - Documentation

## Overview
Three additional charts are now attached to PROD monitoring emails, providing visual tracking of rainy day buy decisions with clear hit/miss markers.

## Charts Generated

### 1. **cash_pool_hit_miss.png**
- **Purpose**: Track cash pool evolution over time
- **Markers**:
  - ✓ Green circles: Successful rainy buys (had sufficient cash)
  - ✗ Red X's: Missed rainy opportunities (insufficient cash)
- **Insights**: Shows cash discipline and ability to deploy when needed

### 2. **spy_price_hit_miss.png**
- **Purpose**: Visualize SPY price action with buy decisions
- **Markers**:
  - ✓ Green triangles (up): Successful rainy buys at key price levels
  - ✗ Red triangles (down): Missed rainy opportunities
  - Gray dots (sampled): Regular base buys (showing 1/10 to avoid clutter)
- **Insights**: Shows timing of rainy buys during market dips

### 3. **rsi_hit_miss.png**
- **Purpose**: Display RSI SMA(7) with rainy day triggers
- **Markers**:
  - ✓ Green circles: Rainy buys when RSI < 45
  - ✗ Red X's: Missed opportunities (rainy but no cash)
  - Gray dots (sampled): Base buys (showing 1/10)
- **Features**:
  - Dashed line: RSI threshold (45)
  - Green zone: Oversold (<30)
  - Red zone: Overbought (>70)
- **Insights**: Confirms strategy triggers at correct RSI levels

## Generation

Run the chart generator script to create/update all three charts:

```bash
cd rsi_double_dca_backtest_PROD
python generate_hit_miss_charts.py
```

This will:
1. Fetch historical SPY and FX data
2. Compute RSI indicators
3. Simulate strategy execution
4. Generate three PNG charts with hit/miss markers

## Email Integration

Charts are automatically attached to monitoring emails via `monitor_strategy.py`:

```python
chart_files = [
    # ... existing charts ...
    'cash_pool_hit_miss.png',
    'spy_price_hit_miss.png',
    'rsi_hit_miss.png'
]
```

## Performance Summary (Last Run)

- **Total rainy buy hits**: 105 (87.5% success rate)
- **Total rainy buy misses**: 15 (12.5% - insufficient cash)
- **Total base buys**: 411
- **Execution days**: 531 (3rd & 17th of each month, 2003-2025)

## Chart Specifications

- **Resolution**: 300 DPI (high quality for email viewing)
- **Size**: 14" x 7" (optimized for email clients)
- **Format**: PNG with transparent backgrounds
- **Color scheme**: 
  - Success: #06A77D (green)
  - Miss: #D00000 (red)
  - Neutral: #6C757D (gray)
  - Primary line: #2E86AB (blue)

## Regenerating Charts

Charts should be regenerated when:
- New backtest data is available
- Strategy parameters change
- Historical data is updated

Simply run:
```bash
python generate_hit_miss_charts.py
```

The charts will be overwritten with updated data.
