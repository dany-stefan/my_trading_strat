# RSI Cash Strategy - Automated Investment Monitor

**Your Strategy:** Variant #2 - Bi-weekly $150 with RSI < 45 Rainy Day Buying

## 📊 Quick Stats

- **33.54% CAGR** over 22-year backtest (2003-2025)
- **80% hit rate** (highest of all tested variants!)
- **+19.4% more wealth** vs simple DCA (+$97,624)
- **$600,907 final equity** vs $104,350 invested
- **Payday-aligned** (1st & 15th of each month)

---

## 🚀 Quick Start

### 1. Preview Your Email (No Email Sent!)

```bash
cd /Users/danystefan/Documents/workspace/my_trading_strat/rsi_double_dca_backtest
/Users/danystefan/Documents/workspace/my_trading_strat/.venv/bin/python simulate_payday_email.py
```

**This shows you:**
- Current SPY RSI(14) and price
- Your cash pool balance
- Today's recommendation (buy extra $150 or skip)
- Exactly what your payday email will contain
- **NO email sent** - just a preview in terminal!

Run this **anytime** to see what action you'd take if today were payday.

---

## 📁 Project Structure

```
my_trading_strat/
├── rsi_double_dca_backtest/
│   ├── rsi_variants_backtest.py      # Backtest & optimization (run once)
│   ├── monitor_strategy.py           # Live monitoring with email alerts
│   ├── simulate_payday_email.py      # Preview email WITHOUT sending ✨
│   ├── strategy_tracking.json        # Your investment history (private)
│   │
│   ├── RSI_VARIANTS_ANALYSIS.md      # Full analysis & results
│   ├── IMPLEMENTATION_GUIDE.md       # How to use the monitor
│   ├── VERIFICATION.md               # Cloud setup checklist
│   ├── CLOUD_SETUP.md                # GitHub Actions guide
│   │
│   └── backtest_results/             # CSVs and visualizations
│       ├── equity_baseline_dca.csv
│       ├── equity_variant_2_biweekly_150_45.csv
│       ├── strategy_comparison_with_baseline.png
│       ├── variant_2_equity_curve.png
│       ├── rainy_day_analysis_detailed.png
│       ├── spy_price_rainy_periods_drawdown.png
│       ├── rsi_history_thresholds.png
│       └── rsi_variants_heatmap_biweekly.png
│
└── .github/workflows/
    └── rsi_monitor.yml               # Automated cloud monitoring
```

---

## 📖 Documentation

| File | Purpose |
|------|---------|
| **RSI_VARIANTS_ANALYSIS.md** | Complete backtest results, why Variant #2 wins, performance charts |
| **IMPLEMENTATION_GUIDE.md** | How to run locally, email setup, cron automation |
| **CLOUD_SETUP.md** | Deploy to GitHub Actions (free, runs in cloud) |
| **VERIFICATION.md** | Setup checklist and troubleshooting |

---

## 🎯 Your Strategy (Variant #2)

### On Every Payday (1st & 15th of month):

1. **Always invest $150 CAD** in SPY (no matter what)
2. **Always save $30 CAD** to cash pool
3. **Check RSI(14):**
   - If RSI < 45 AND cash pool ≥ $150:
     - 🔥 **Buy extra $150** from cash pool (total $300)
   - If RSI ≥ 45:
     - 💰 Only invest $150, cash pool grows by $30

### Why This Works:

- **Same schedule as your payday** - no weekly checks needed
- **80% success rate** - you'll catch most opportunities
- **+1.07% higher CAGR** than simple DCA
- **19.4% more wealth** over 22 years
- **Sustainable** - cash pool prevents overdeployment

---

## 🛠️ Commands Reference

### Preview Email (Most Useful!)
```bash
cd rsi_double_dca_backtest
../venv/bin/python simulate_payday_email.py
```
Shows current market conditions and what you'd do if today were payday. **No email sent!**

### Run Backtest (Already Done)
```bash
cd rsi_double_dca_backtest
../venv/bin/python rsi_variants_backtest.py
```
Regenerates all CSVs and visualizations. Takes ~2 minutes.

### Manual Monitor Check (Sends Email)
```bash
cd rsi_double_dca_backtest
../venv/bin/python monitor_strategy.py
```
Checks if it's payday and sends email alert if configured.

---

## 🌩️ Cloud Automation (Recommended)

**Cost:** $0 (GitHub Actions free tier)

1. Push code to GitHub
2. Add email secrets to repository settings
3. Enable GitHub Actions
4. Monitor runs automatically:
   - Daily check at 10 AM EST
   - Emails sent on 1st & 15th
   - No Mac needed - runs in cloud!

**Full guide:** See `CLOUD_SETUP.md`

### 🧪 Testing the Email (Manual Trigger)

You can **manually trigger** the GitHub Actions workflow to receive a test email **even when it's not payday**:

1. Go to your GitHub repository
2. Click **Actions** tab
3. Select **RSI Strategy Monitor** workflow
4. Click **Run workflow** (top right)
5. Set **"Send email even if not payday"** to **true**
6. Click **Run workflow**

The test email will:
- Be marked as "🧪 TEST EMAIL (Not Payday)"
- Show current market conditions
- **NOT update** your cash pool or tracking
- Arrive in your inbox within 1-2 minutes

**Perfect for:**
- Testing your email configuration
- Previewing what payday emails look like
- Checking current market conditions remotely

---

## 📈 Visualizations Generated

All charts focus on **your chosen Variant #2**:

1. **strategy_comparison_with_baseline.png** - Your strategy vs simple DCA
2. **variant_2_equity_curve.png** - Portfolio growth over 22 years
3. **rainy_day_analysis_detailed.png** - Hit/miss markers by RSI band
4. **spy_price_rainy_periods_drawdown.png** - Market context & crashes
5. **rsi_history_thresholds.png** - RSI patterns since 2003
6. **rsi_variants_heatmap_biweekly.png** - Parameter optimization results

---

## 📊 Expected Results (22-year backtest)

| Metric | Value |
|--------|-------|
| Total Invested | $104,350 CAD |
| Final Equity | $600,907 CAD |
| CAGR | 33.54% |
| Hit Rate | 80.0% |
| Rainy Buys | 112 / 140 opportunities |
| Baseline DCA | $503,343 (32.48% CAGR) |
| **Improvement** | **+$97,624 (+19.4%)** |

---

## 🔥 Current Market Check

**Run this now to see live market conditions:**

```bash
cd rsi_double_dca_backtest
../venv/bin/python simulate_payday_email.py
```

Example output:
```
✅ Current SPY RSI(14): 28.29
✅ Current SPY Price: $652.53
🔥 RECOMMENDATION: Buy extra $150 from cash pool
   (RSI < 45 = Rainy Day!)
```

---

## 🔒 Privacy

- `strategy_tracking.json` is gitignored (contains your investment history)
- Email credentials stored as GitHub secrets (encrypted)
- No data leaves your control

---

## 📧 Questions?

1. Read `IMPLEMENTATION_GUIDE.md` for local setup
2. Read `CLOUD_SETUP.md` for cloud automation
3. Read `RSI_VARIANTS_ANALYSIS.md` for strategy details
4. Check `VERIFICATION.md` for troubleshooting

---

## 🎉 Next Steps

1. ✅ **Run email preview:** `simulate_payday_email.py`
2. ✅ **Review analysis:** Open `RSI_VARIANTS_ANALYSIS.md`
3. ✅ **Set up cloud:** Follow `CLOUD_SETUP.md`
4. ✅ **Wait for payday:** 1st or 15th of month
5. ✅ **Check email:** Follow the recommendations!

**Your first payday email arrives:** December 1, 2025 🎯
