# Complete Integration Flow - Trading Strategy System

## Overview
This document describes the complete data and code flow from backtesting to email generation for both PROD and TURBO variants.

---

## 🔄 TURBO v2.0 Integration Flow

### 1. Data Collection & Backtesting
**Files:** `rsi_calendar_date_backtest.py`, `rsi_variants_backtest.py`
- Historical SPY data (yfinance)
- RSI calculations with SMA(7) smoothing
- 200MA regime classification
- VIX volatility data
- Backtest simulations (2003-2025)

**Output:**
- CSV files: `equity_variant_*.csv`, `rainy_buys_*.csv`
- Performance metrics

### 2. Visualization Generation
**Files:** `enhanced_visualizations.py`, `generate_cash_pool_visualization.py`

**Charts Created:**
```
strategy_comparison_prod_vs_turbo.png
dashboard_interactive_turbo.png
regime_performance_turbo.png
monte_carlo_cash_pool_turbo.png
consecutive_rainy_heatmap_turbo.png
yearly_prod_vs_turbo.png
rainy_amount_over_time_prod_vs_turbo.png
```

### 3. Market Metrics Calculation Module
**File:** `market_metrics.py`

**Class:** `MarketMetrics`

**Inputs:**
- `price`: Current SPY price
- `spy_200ma`: 200-day moving average
- `vix`: VIX fear index
- `rsi_sma`: RSI SMA(7) value

**Calculations:**
1. **200MA Thresholds:**
   - `ma_plus_5_pct` = 200MA × 1.05
   - `ma_minus_5_pct` = 200MA × 0.95
   - `deviation_pct` = (price - 200MA) / 200MA × 100

2. **Regime Determination:**
   ```
   if deviation_pct > 5:  → BULL (threshold 42)
   elif deviation_pct < -5: → BEAR (threshold 48)
   else: → NEUTRAL (threshold 45)
   ```

3. **VIX-Based Sizing:**
   ```
   if vix < 15: → $150 (standard)
   elif vix < 25: → $180 (+20%)
   else: → $210 (+40%)
   ```

**Outputs:**
- All raw numeric values
- Formatted display strings (no N/A)
- Regime emoji 🐂/🐻/⚖️
- Text blocks for email

**Function:** `calculate_market_metrics(price, spy_200ma, vix, rsi_sma)`

### 4. Email Content Generation
**File:** `email_generator_turbo.py`

**Function:** `generate_email_content()`

**Flow:**
1. Import `calculate_market_metrics` from `market_metrics`
2. Call metrics calculation:
   ```python
   metrics = calculate_market_metrics(price, spy_200ma, vix, rsi_sma)
   all_metrics = metrics.get_all_metrics()
   ```
3. Extract computed values (NO inline calculations):
   - `market_regime` = metrics.market_regime
   - `adaptive_threshold` = metrics.adaptive_threshold
   - `volatility_sizing` = metrics.volatility_sizing
   - `deviation_display` = all_metrics["deviation_display"]
   - etc.

4. Build email sections:
   - **Current Snapshot** (with all numeric values)
   - **Metrics Markdown Table** (embedded)
   - **Decision Table** (3 factors)
   - **3-Factor Summary**
   - **Action Box** (rainy/save logic)

**Output:**
- `subject`: Email subject line
- `body`: Plain text email body

### 5. HTML Formatting
**File:** `email_formatter.py`

**Function:** `convert_to_html(body)`

**Flow:**
1. Parse plain text sections
2. Apply HTML styling:
   - Headers → `<h1>`, `<h2>`
   - Tables → `<table>` with CSS classes
   - Emphasis → `<strong>`, `<em>`
   - Code blocks → preserved
3. Special handling:
   - Decision tables → `decision-table` class
   - Test notices → `test-notice` class
   - Checkmarks → highlight-cell

**Output:**
- Styled HTML email body

### 6. Monitor & Send
**File:** `monitor_strategy.py`

**Function:** `check_conditions()`

**Flow:**
1. **Fetch Live Data:**
   ```python
   rsi, rsi_sma, price, ma_200, vix = get_rsi(lookback_days=400)
   ```

2. **Calculate Metrics & Write Snapshots:**
   ```python
   metrics_obj = calculate_market_metrics(price, ma_200, vix, rsi_sma)
   metrics = metrics_obj.get_all_metrics()
   
   # Write METRICS_SNAPSHOT.md
   # Update README_MARKET_METRICS.md (live section)
   ```

3. **Generate Email:**
   ```python
   subject, body = generate_email_content(
       rsi_sma=rsi_sma,
       price=price,
       cash_pool=cash_pool,
       total_contributions=total_contributions,
       rainy_buys=rainy_buys,
       is_simulation=FORCE_EMAIL,
       spy_200ma=ma_200,
       vix=vix
   )
   ```

4. **Convert to HTML:**
   ```python
   html_body = convert_to_html(body)
   ```

5. **Attach Charts:**
   - All 7 PNG visualization files

6. **Send via SMTP:**
   - Gmail SMTP with TLS
   - Multipart MIME (text + HTML + images)

**Outputs:**
- METRICS_SNAPSHOT.md (current run)
- README_MARKET_METRICS.md (updated)
- Email sent to recipient

---

## 🎯 PROD Integration Flow

### 1. Data Collection & Backtesting
**Files:** `rsi_calendar_date_backtest.py`, `compare_rsi_sma_paydays.py`
- Historical SPY data
- RSI SMA(7) calculations
- Payday-aligned execution schedule
- Backtest results (2003-2025)

**Output:**
- CSV files: `equity_baseline_*.csv`
- Performance comparison data

### 2. Visualization Generation
**Files:** `generate_hit_miss_charts.py`, `generate_cash_pool_visualization.py`

**Charts Created:**
```
strategy_comparison_with_baseline.png
rainy_day_analysis_detailed.png
spy_price_rainy_periods_drawdown.png
cash_pool_hit_miss.png (with markers)
spy_price_hit_miss.png (with markers)
rsi_hit_miss.png (with markers)
```

### 3. Market Metrics Calculation Module
**File:** `market_metrics.py`

**Class:** `MarketMetrics`

**Inputs:**
- `rsi_sma`: RSI SMA(7) value
- `price`: Current SPY price
- `cash_pool`: Current cash balance
- `total_contributions`: Total invested
- `rainy_buys`: Historical rainy buy list

**Calculations:**
1. **Rainy Day Logic:**
   ```python
   is_rainy = rsi_sma < 45.0
   can_deploy = cash_pool >= 150.0
   ```

2. **Action Determination:**
   ```
   if is_rainy and can_deploy: → rainy_deploy ($300 total)
   elif is_rainy and not can_deploy: → rainy_insufficient (base only)
   else: → save (base + $30)
   ```

3. **Cash Flow:**
   ```
   rainy_deploy: cash_pool - 150 + 30 = new_cash_pool
   save: cash_pool + 30 = new_cash_pool
   ```

4. **Next Payday:**
   - Determines 1st or 15th based on current date

**Outputs:**
- Action type (rainy_deploy/rainy_insufficient/save)
- Cash calculations
- Text blocks (recommendation, action_text, cash_after_text)
- Formatted display strings

**Function:** `calculate_market_metrics(rsi_sma, price, cash_pool, ...)`

### 4. Email Content Generation
**File:** `email_generator.py`

**Function:** `generate_email_content()`

**Flow:**
1. Import `calculate_market_metrics` from `market_metrics`
2. Call metrics calculation:
   ```python
   metrics = calculate_market_metrics(
       rsi_sma=rsi_sma,
       price=price,
       cash_pool=cash_pool,
       total_contributions=total_contributions,
       rainy_buys=rainy_buys
   )
   all_metrics = metrics.get_all_metrics()
   ```

3. Extract computed values (NO inline calculations):
   - `is_rainy` = all_metrics["is_rainy"]
   - `recommendation` = all_metrics["recommendation"]
   - `action_text` = all_metrics["action_text"]
   - `cash_pool_display` = all_metrics["cash_pool_display"]
   - etc.

4. Build email sections:
   - **Header** (date, SPY price, RSI)
   - **Decision Path** (from module)
   - **Today's Actions** (base + rainy/save)
   - **Metrics Markdown Table** (embedded)
   - **Performance Summary**

**Output:**
- `subject`: Email subject line
- `body`: Plain text email body

### 5. HTML Formatting
**File:** `email_formatter.py`

**Function:** `convert_to_html(body)`

**Flow:** (Same as TURBO)
1. Parse plain text
2. Apply HTML styling
3. Table conversion
4. Emphasis formatting

**Output:**
- Styled HTML email body

### 6. Monitor & Send
**File:** `monitor_strategy.py`

**Function:** `check_conditions()`

**Flow:**
1. **Fetch Live Data:**
   ```python
   rsi, rsi_sma, price = get_rsi(lookback_days=100)
   ```

2. **Calculate Metrics & Write Snapshots:**
   ```python
   metrics_obj = calculate_market_metrics(
       rsi_sma, price, cash_pool,
       total_contributions, rainy_buys
   )
   m = metrics_obj.get_all_metrics()
   
   # Write METRICS_SNAPSHOT.md
   # Update README_MARKET_METRICS.md (live section)
   ```

3. **Generate Email:**
   ```python
   subject, body = generate_email_content(
       rsi_sma=rsi_sma,
       price=price,
       cash_pool=cash_pool,
       total_contributions=tracking.get('total_contributions', 0),
       rainy_buys=tracking.get('rainy_buys', []),
       is_simulation=FORCE_EMAIL
   )
   ```

4. **Convert to HTML:**
   ```python
   html_body = convert_to_html(body)
   ```

5. **Attach Charts:**
   - All 8 PNG chart files

6. **Send via SMTP:**
   - Gmail SMTP with TLS
   - Multipart MIME (text + HTML + images)

**Outputs:**
- METRICS_SNAPSHOT.md (current run)
- README_MARKET_METRICS.md (updated)
- strategy_tracking.json (updated state)
- Email sent to recipient

---

## 📊 Key Integration Points

### Module Dependencies

**TURBO:**
```
monitor_strategy.py
    ├─> market_metrics.py (calculate_market_metrics)
    ├─> email_generator_turbo.py
    │   └─> market_metrics.py (calculate_market_metrics)
    ├─> email_formatter.py (convert_to_html)
    └─> payday_scheduler.py
```

**PROD:**
```
monitor_strategy.py
    ├─> market_metrics.py (calculate_market_metrics)
    ├─> email_generator.py
    │   └─> market_metrics.py (calculate_market_metrics)
    ├─> email_formatter.py (convert_to_html)
    └─> payday_scheduler.py
```

### Data Flow Guarantees

1. **No N/A Values:**
   - 200MA: 400-day lookback ensures availability
   - VIX: 10-day lookback with last valid value
   - All metrics: Module returns numeric or uses fallbacks

2. **Single Source of Truth:**
   - All calculations in `market_metrics.py`
   - Email templates display computed values only
   - No inline math in templates

3. **Live Snapshots:**
   - Every run updates METRICS_SNAPSHOT.md
   - README_MARKET_METRICS.md live section auto-refreshed
   - Timestamp tracked

4. **Email Consistency:**
   - Plain text → HTML conversion preserves structure
   - Charts attached in correct order
   - Module values embedded in markdown tables

---

## 🧪 Testing the Flow

### TURBO Test:
```bash
cd /Users/danystefan/Documents/workspace/my_trading_strat/rsi_double_dca_backtest_v2.0_turbocharged
FORCE_EMAIL=true ../.venv/bin/python monitor_strategy.py
```

**Verify:**
1. METRICS_SNAPSHOT.md updated
2. README_MARKET_METRICS.md updated (📊 Latest Snapshot)
3. Email sent with all 7 charts
4. HTML contains metrics table with numeric values

### PROD Test:
```bash
cd /Users/danystefan/Documents/workspace/my_trading_strat/rsi_double_dca_backtest_PROD
FORCE_EMAIL=true ../.venv/bin/python monitor_strategy.py
```

**Verify:**
1. METRICS_SNAPSHOT.md updated
2. README_MARKET_METRICS.md updated (📊 Latest Snapshot)
3. Email sent with all 8 charts
4. HTML contains metrics table with numeric values

---

## ✅ Integration Checklist

- [x] Backtest data flows to charts
- [x] Charts generated as PNG files
- [x] Market metrics calculated in module
- [x] No inline calculations in email templates
- [x] Metrics embedded in email as markdown tables
- [x] Plain text converted to styled HTML
- [x] Charts attached to emails
- [x] Live snapshots written to files
- [x] README auto-updated on each run
- [x] No N/A values in snapshots
- [x] Numeric values guaranteed (fallbacks in place)
- [x] SMTP email delivery working
- [x] Test mode (FORCE_EMAIL) functional

---

## 📁 File Structure Summary

### TURBO Files:
```
rsi_double_dca_backtest_v2.0_turbocharged/
├── market_metrics.py          (calculations)
├── email_generator_turbo.py   (content)
├── email_formatter.py         (HTML)
├── monitor_strategy.py        (orchestration)
├── METRICS_SNAPSHOT.md        (live values)
├── README_MARKET_METRICS.md   (docs + live)
└── *.png                      (7 charts)
```

### PROD Files:
```
rsi_double_dca_backtest_PROD/
├── market_metrics.py          (calculations)
├── email_generator.py         (content)
├── email_formatter.py         (HTML)
├── monitor_strategy.py        (orchestration)
├── METRICS_SNAPSHOT.md        (live values)
├── README_MARKET_METRICS.md   (docs + live)
└── *.png                      (8 charts)
```

---

## 🎯 Design Principles

1. **Separation of Concerns:** Calculations, content, formatting, delivery are separate modules
2. **Single Source of Truth:** Metrics module is authoritative for all values
3. **No Magic Values:** All numbers come from module calculations
4. **Fail-Safe Defaults:** Missing data falls back gracefully (no N/A)
5. **Audit Trail:** Snapshots written to disk for each run
6. **Self-Documenting:** README updates show current state
7. **Testable:** Each module can be tested independently

---

*Last Updated: 2025-11-22*
