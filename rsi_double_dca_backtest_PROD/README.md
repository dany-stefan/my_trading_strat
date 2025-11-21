# RSI Rainy Day Strategy - User Guide

## 📧 Email Preview & Testing

### Option 1: Local HTML Preview (No Email Sent)
**Command:**
```bash
python simulate_payday_email.py
```

**What it does:**
- Fetches current SPY price and RSI
- Generates email content
- Creates `simulated_email_preview.html` file
- **Does NOT send any email**

**Output:**
- View the HTML file in your browser to see exactly how the email will look
- Perfect for testing formatting changes safely

---

### Option 2: Send Real Test Email (Local)
**Command:**
```bash
bash local_email_send_test.sh
```

**What it does:**
- Sends a **real email** to your Gmail inbox
- Marks email as "🧪 TEST EMAIL (Local Run)"
- Does NOT update tracking.json (no cash pool changes)

**Email received:**
- Subject: `🧪 TEST EMAIL (Local Run): Investment Metrics - [Date]`
- Header: "🎯 RSI STRATEGY MONITOR - TEST EMAIL (LOCAL RUN)"
- Notice: "🧪 THIS IS A TEST EMAIL FROM LOCAL RUN"

---

### Option 3: Manual GitHub Actions Trigger (Test Email)
**Where:** GitHub repository → Actions tab → "RSI Strategy Monitor" workflow

**Steps:**
1. Go to: https://github.com/dany-stefan/my_trading_strat/actions
2. Click "RSI Strategy Monitor"
3. Click "Run workflow" button (top right)
4. Click green "Run workflow" button

**What it does:**
- Sends a **real email** to your Gmail inbox
- Marks email as "🧪 TEST EMAIL (Local Run)"
- Does NOT update tracking.json

**Email received:**
- Same as Option 2 (marked as TEST EMAIL)

---

### Option 4: Scheduled GitHub Actions (Official Payday Email)
**Schedule:** Automatically runs on 1st and 15th of each month at 1:00 PM EST

**What it does:**
- Sends **official payday email** to your Gmail inbox
- Updates tracking.json with cash pool and rainy buys
- Records rainy day purchases

**Email received:**
- Subject: `📅 PAYDAY: Investment Metrics - [Date]`
- Header: "🎯 RSI STRATEGY MONITOR - PAYDAY"
- **No test markers** - this is the real thing!

---

## 📊 Strategy Analysis & Reports

### Generate Backtest Analysis
**Command:**
```bash
python sp500_ath_vix_backtest.py
```

**What it does:**
- Runs 22-year backtest (2003-2025)
- Tests your strategy vs alternatives
- Generates performance metrics

**Output Files:**

#### 📁 CSV Data Files (in `backtest_results/`)
- `equity_baseline_dca.csv` - Simple DCA performance (no rainy day logic)
- `equity_smas_strategy.csv` - Your rainy day strategy performance
- `event_buybacks.csv` - All rainy day purchase events
- `events_detected.csv` - All detected rainy opportunities (hit/miss)
- `strategy_comparison_summary.csv` - Side-by-side comparison metrics

#### 📈 Generated Charts (PNG files)
- `strategy_comparison_with_baseline.png` - Growth curves comparison
- `rainy_day_analysis_detailed.png` - Hit/miss pattern & cash pool over time
- `spy_price_rainy_periods_drawdown.png` - When you bought during crashes
- `variant_comparison_*.png` - Different strategy variant comparisons
- `top_3_variants_comparison.png` - Top 3 performing variants

#### 📄 Analysis Reports (Markdown)
- `STRATEGY_ANALYSIS.md` - Comprehensive strategy analysis
  - Performance metrics (CAGR, total return, Sharpe ratio)
  - Cash pool dynamics
  - Rainy day hit rate analysis
  - Comparison vs simple DCA and buy & hold
  
- `STRATEGY_SUMMARY.md` - Executive summary
  - Key takeaways
  - Top variant comparison
  - Why you chose Variant #2
  - Expected results over 22 years

---

## 📧 Email Content Structure

### What's Included in Every Email

1. **Current Market Data**
   - SPY price (USD)
   - RSI SMA(7) value (7-day Simple Moving Average of RSI - this is your rainy day indicator)
   - Rainy day status (RSI SMA(7) < 45?)

2. **Today's Actions**
   - Base investment: $150 CAD (always)
   - Rainy day check results
   - Recommendation (buy extra $150 or save cash)
   - Cash pool before/after

3. **Performance Tables**
   - Variant Performance Summary (3 variants)
   - Strategy vs Alternatives (DCA, Buy & Hold)
   - Top 3 Variants Comparison

3. **Strategy Framework**
   - Payday schedule (1st & 15th)
   - Cash accumulation rules ($30 per payday)
   - Rainy day deployment rules (RSI SMA(7) < 45)

5. **Current Status**
   - Cash pool balance
   - Total contributions to date
   - Total rainy buys to date
   - Expected long-term results

6. **Attached Charts** (5 PNG files)
   - strategy_comparison_with_baseline.png
   - rainy_day_analysis_detailed.png
   - spy_price_rainy_periods_drawdown.png
   - variant_comparison_rsi_thresholds.png
   - variant_comparison_frequencies.png

---

## 🔧 Data Flow Diagram

```
sp500_ath_vix_backtest.py (run manually)
    ↓
Generates CSV files in backtest_results/
    ├── equity_baseline_dca.csv
    ├── equity_smas_strategy.csv
    ├── event_buybacks.csv
    ├── events_detected.csv
    └── strategy_comparison_summary.csv
    ↓
Generates PNG charts
    ├── strategy_comparison_with_baseline.png
    ├── rainy_day_analysis_detailed.png
    ├── spy_price_rainy_periods_drawdown.png
    ├── variant_comparison_*.png
    └── top_3_variants_comparison.png
    ↓
Generates Markdown reports
    ├── STRATEGY_ANALYSIS.md
    └── STRATEGY_SUMMARY.md
    ↓
Charts are attached to emails
    ↓
monitor_strategy.py (scheduled: 1st & 15th)
    ↓
Sends official payday email with:
    - Current market data (live from Yahoo Finance)
    - Recommendations based on current RSI
    - Historical performance metrics (from CSV files)
    - Charts (PNG attachments)
    ↓
Updates tracking.json
    - Cash pool balance
    - Rainy buy history
    - Total contributions
```

---

## 📂 File Structure

```
rsi_double_dca_backtest/
├── Python Scripts
│   ├── sp500_ath_vix_backtest.py         # Run backtest & generate reports
│   ├── monitor_strategy.py               # Production email sender (GitHub Actions)
│   ├── simulate_payday_email.py          # Local HTML preview generator
│   ├── email_formatter.py                # Shared HTML formatting
│   └── email_generator.py                # Shared email content generation
│
├── Shell Scripts
│   └── local_email_send_test.sh          # Send test email locally
│
├── Data Files
│   ├── tracking.json                     # Live tracking (cash pool, rainy buys)
│   └── backtest_results/
│       ├── equity_baseline_dca.csv
│       ├── equity_smas_strategy.csv
│       ├── event_buybacks.csv
│       ├── events_detected.csv
│       └── strategy_comparison_summary.csv
│
├── Generated Reports
│   ├── STRATEGY_ANALYSIS.md
│   ├── STRATEGY_SUMMARY.md
│   └── simulated_email_preview.html      # Local preview (from simulate script)
│
└── Generated Charts (PNG)
    ├── strategy_comparison_with_baseline.png
    ├── rainy_day_analysis_detailed.png
    ├── spy_price_rainy_periods_drawdown.png
    ├── variant_comparison_rsi_thresholds.png
    ├── variant_comparison_frequencies.png
    └── top_3_variants_comparison.png
```

---

## 🎯 Quick Reference

| What I Want | Command | Sends Email? | Updates Tracking? |
|-------------|---------|--------------|-------------------|
| Preview HTML only | `python simulate_payday_email.py` | ❌ No | ❌ No |
| Test email (local) | `bash local_email_send_test.sh` | ✅ Yes (marked TEST) | ❌ No |
| Test email (GitHub) | Manual workflow trigger | ✅ Yes (marked TEST) | ❌ No |
| Official payday email | GitHub Actions (scheduled) | ✅ Yes (official) | ✅ Yes |
| Run backtest | `python sp500_ath_vix_backtest.py` | ❌ No | ❌ No |

---

## 💡 Tips

- **Before making changes:** Run `python simulate_payday_email.py` to preview
- **Testing email format:** Use `bash local_email_send_test.sh` to send test email
- **Check current status:** View `tracking.json` for cash pool and rainy buy history
- **Review performance:** Open `STRATEGY_SUMMARY.md` for quick overview
- **Deep dive analysis:** Open `STRATEGY_ANALYSIS.md` for full metrics
- **Visual comparison:** Look at PNG charts in the main directory

---

## 🔐 Email Configuration

- **Sender:** d4388707373@gmail.com
- **Recipient:** d4388707373@gmail.com
- **SMTP:** smtp.gmail.com:587
- **App Password:** Stored in GitHub Secrets (for Actions)
- **Local Password:** Hardcoded in `monitor_strategy.py` (kzuf dozw badx wwro)

---

## ⚙️ Strategy Parameters

- **Base DCA:** $150 CAD every payday
- **Rainy Amount:** $150 CAD extra (when RSI SMA(7) < 45)
- **Cash Accumulation:** $30 CAD per payday
- **RSI SMA(7) Threshold:** < 45.0 (7-day Simple Moving Average of RSI(14))
- **Why RSI SMA(7)?** Reduces noise and false signals compared to raw RSI(14)
  - 85.6% agreement with raw RSI on payday schedule
  - Hit rate difference: only +0.4% (minimal impact)
  - Prevents buying on temporary RSI dips that quickly reverse
  - Smooths out daily volatility for more reliable signals
- **Schedule:** 1st and 15th of each month
- **Asset:** SPY (S&P 500 ETF)

---

## 🚀 Next Steps

1. **First time setup:** Run `python sp500_ath_vix_backtest.py` to generate baseline data
2. **Test email locally:** Run `bash local_email_send_test.sh` to verify email looks good
3. **Preview HTML:** Run `python simulate_payday_email.py` and open the HTML file
4. **Wait for payday:** GitHub Actions will automatically send official emails on 1st & 15th
5. **Monitor performance:** Check `STRATEGY_ANALYSIS.md` after each backtest run
