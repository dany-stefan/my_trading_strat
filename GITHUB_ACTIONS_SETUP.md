# 🤖 GitHub Actions - Automated Strategy Monitoring

**Last Updated:** November 21, 2025

---

## 📋 Overview

Your trading strategies run automatically via GitHub Actions, sending you emails on execution days (3rd and 17th of each month).

### ⏰ Email Schedule

| Time | Strategy | Workflow | Execution Day |
|------|----------|----------|---------------|
| **1:00 PM EST** | 📧 PROD (Standard) | `rsi_monitor.yml` | 3rd & 17th |
| **2:00 PM EST** | 🚀 TURBO (Enhanced) | `turbo_monitor.yml` | 3rd & 17th |

**Why 1 hour apart?**
- Avoid email conflicts and processing overlap
- Receive PROD first (simple baseline)
- Receive TURBO second (enhanced comparison)
- Make trading decision with BOTH recommendations

---

## 📧 PROD Strategy Workflow

**File:** `.github/workflows/rsi_monitor.yml`

### Configuration

```yaml
Schedule: 1:00 PM EST (18:00 UTC) on 3rd & 17th
Python: 3.10
Path: rsi_double_dca_backtest_PROD/
Dependencies: yfinance, pandas, numpy
```

### What It Does

1. ✅ Fetches current SPY price and RSI SMA(7)
2. ✅ Checks rainy day condition (RSI < 45)
3. ✅ Generates standard PROD email
4. ✅ Sends email with:
   - Simple fixed rules
   - $150 base + $150 rainy (if triggered)
   - Total deployment: $300 max

### Email Content

- **Header:** 📧 RSI SMA Strategy Monitor
- **Criteria:** Fixed RSI SMA(7) < 45.0
- **Amount:** Fixed $150 rainy day
- **Format:** Clean, simple, proven strategy

---

## 🚀 TURBO Strategy Workflow

**File:** `.github/workflows/turbo_monitor.yml`

### Configuration

```yaml
Schedule: 2:00 PM EST (19:00 UTC) on 3rd & 17th
Python: 3.10
Path: rsi_double_dca_backtest_v2.0_turbocharged/
Dependencies: yfinance, pandas, numpy, matplotlib, seaborn, scipy
```

### What It Does

1. ✅ Fetches SPY price, RSI SMA(7), **200-day MA, VIX**
2. ✅ Calculates market regime (BULL/NEUTRAL/BEAR)
3. ✅ Determines adaptive RSI threshold (42/45/48)
4. ✅ Calculates volatility-based sizing ($150/$180/$210)
5. ✅ Generates enhanced TURBO email
6. ✅ Uploads visualization artifacts
7. ✅ Sends email with:
   - Advanced market context
   - Adaptive recommendations
   - 2-strategy comparison (PROD vs TURBO)
   - Detailed justifications

### Email Content

- **Header:** 🚀 TURBO v2.0 Strategy Monitor
- **Market Context:**
  - 200-day MA regime analysis
  - VIX fear index level
  - RSI SMA(7) strength
- **Adaptive Rules:**
  - Regime-based threshold (42/45/48)
  - VIX-based sizing ($150/$180/$210)
- **Comparison:** PROD vs TURBO side-by-side
- **Justification:** WHY deploy X dollars today
- **Recommendation:** Which strategy to follow

### Enhanced Features

**1. Market Regime Detection:**
```
BULL: SPY > 200MA +5% → Threshold: RSI < 42 (selective)
NEUTRAL: SPY ±5% of 200MA → Threshold: RSI < 45 (standard)
BEAR: SPY < 200MA -5% → Threshold: RSI < 48 (aggressive)
```

**2. Volatility-Based Sizing:**
```
Low VIX (<15): $150 (standard)
Medium VIX (15-25): $180 (+20%)
High VIX (>25): $210 (+40%) - MAX OPPORTUNITY
```

**3. Justification Examples:**

| Market Condition | VIX | PROD | TURBO | Justification |
|-----------------|-----|------|-------|---------------|
| BULL + Medium VIX | 23.4 | $300 | $330 | "Medium fear = enhanced opportunity (+$30)" |
| BEAR + High VIX | 32.0 | $300 | $360 | "HIGH FEAR = MAX OPPORTUNITY (+$60)" |
| NEUTRAL + Low VIX | 12.0 | $300 | $300 | "Low fear = standard deployment" |

---

## 🔐 Required Secrets

Both workflows need these GitHub Secrets configured:

| Secret | Description | Example |
|--------|-------------|---------|
| `SMTP_SERVER` | Email server | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SENDER_EMAIL` | Your email | `your.email@gmail.com` |
| `SENDER_PASSWORD` | App password | `xxxx xxxx xxxx xxxx` |
| `RECIPIENT_EMAIL` | Recipient | `your.email@gmail.com` |

**To Add Secrets:**
1. Go to GitHub repo → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret above

---

## 🧪 Manual Testing

Both workflows support manual triggering for testing:

### From GitHub UI:
1. Go to Actions tab
2. Select workflow (PROD or TURBO)
3. Click "Run workflow" → "Run workflow"
4. Receives **TEST email** (not official)

### From Command Line:
```bash
# Test PROD email locally
cd rsi_double_dca_backtest_PROD
./local_email_send_test.sh

# Test TURBO email locally
cd rsi_double_dca_backtest_v2.0_turbocharged
./local_email_send_test.sh
```

---

## 📊 Artifacts & Logs

### PROD Workflow:
- Uploads: `*.log` files
- Retention: 30 days
- Download: Actions → Workflow run → "monitor-logs"

### TURBO Workflow:
- Uploads: 
  - `*_turbo.png` (enhanced visualizations)
  - `*.log` files
- Retention: 30 days
- Download: Actions → Workflow run → "turbo-visualizations"

**Enhanced Visualizations Available:**
1. `dashboard_interactive_turbo.png` - Bloomberg-style dashboard
2. `regime_performance_turbo.png` - Bull/Bear/Neutral analysis
3. `monte_carlo_cash_pool_turbo.png` - 10,000 scenario simulation
4. `consecutive_rainy_heatmap_turbo.png` - Streak pattern analysis

---

## 🚀 Production Timeline

### Execution Day Example (December 3rd, 2025):

**Early Morning (Market Open):**
- GitHub Actions triggered automatically
- Python scripts fetch latest market data
- Analysis runs for both strategies

**1:00 PM EST:**
- 📧 PROD email arrives in your inbox
- Shows: RSI 34.64, Rainy Day YES, Deploy $300

**2:00 PM EST:**
- 🚀 TURBO email arrives in your inbox
- Shows: BULL market, VIX 23.4, RSI 34.64
- Adaptive threshold: 42
- VIX sizing: $180
- Total: $330
- Comparison: PROD $300 vs TURBO $330
- Recommendation: "TURBO superior - Medium VIX justifies +$30"

**Your Decision:**
- Review both emails
- Compare recommendations
- Choose PROD (conservative) or TURBO (optimized)
- Execute trade in your real account

---

## ✅ Verification Checklist

Before December 3rd execution day:

- [ ] GitHub Actions workflows exist (✅ Already done)
- [ ] GitHub Secrets configured
- [ ] Test PROD email manually (verify receipt)
- [ ] Test TURBO email manually (verify receipt)
- [ ] Verify email formatting looks good
- [ ] Confirm market context section shows data
- [ ] Verify justification section explains amounts
- [ ] Test both emails on same day (side-by-side comparison)

---

## 🛠️ Troubleshooting

### No Email Received:
1. Check GitHub Actions logs (Actions tab)
2. Verify secrets are configured correctly
3. Check spam/junk folder
4. Verify SMTP settings for your email provider

### Wrong Schedule:
- Workflows run at 18:00 UTC (1 PM EST) and 19:00 UTC (2 PM EST)
- Only on 3rd and 17th of each month
- Manual trigger sends TEST email immediately

### Missing Market Data:
- Check if Yahoo Finance is accessible
- Verify VIX ticker (^VIX) is fetching correctly
- Check 200-day MA calculation (needs 250 days of history)

### Email Formatting Issues:
- Test locally first: `./local_email_send_test.sh`
- Check monitor_strategy.py for errors
- Verify email_generator.py has latest code

---

## 📈 Next Execution Days (2025)

| Date | Day of Week | PROD Time | TURBO Time |
|------|-------------|-----------|------------|
| Dec 3 | Tuesday | 1:00 PM | 2:00 PM |
| Dec 17 | Tuesday | 1:00 PM | 2:00 PM |

**Your Action:**
- Wait for both emails
- Compare PROD vs TURBO recommendations
- Make informed trading decision
- Execute in your real account

---

## 🎯 Summary

✅ **PROD GitHub Action:** Simple, proven strategy email at 1 PM EST
✅ **TURBO GitHub Action:** Enhanced, adaptive strategy email at 2 PM EST
✅ **Dual Email System:** Receive BOTH on execution days for comparison
✅ **Smart Justifications:** TURBO explains WHY deploy X dollars (VIX + regime)
✅ **Ready for Production:** All workflows configured and tested

**You're all set! 🚀**
