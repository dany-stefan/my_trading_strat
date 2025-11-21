# RSI Cash Strategy Variant #2 - Implementation Guide

## Strategy Summary

**Variant:** #2 - Bi-weekly $150 RSI < 45  
**Expected CAGR:** 33.54%  
**Hit Rate:** 80.0% (highest of all variants!)  
**Final Equity (22 years):** $600,907 CAD  
**vs Baseline DCA:** +19.4% more wealth (+$97,624)

**Why this variant beats simple DCA:**
- Same bi-weekly schedule, but adds rainy day buying
- +1.07% higher CAGR with minimal effort
- 80% success rate on rainy opportunities
- See full analysis: `RSI_VARIANTS_ANALYSIS.md`

---

## Your Schedule

### Bi-weekly Paydays
- **1st of each month** (or next business day if weekend)
- **15th of each month** (or next business day if weekend)

### Actions on Payday

1. **ALWAYS invest $150 CAD base amount** (no matter what)
2. **ALWAYS save $30 CAD to your cash pool** (mental accounting or separate account)
3. **Check SPY RSI(14):**
   - If RSI < 45 AND cash pool ≥ $150:
     - **BUY EXTRA $150 from cash pool** (rainy day buy)
     - Total investment: $300 ($150 base + $150 rainy)
   - If RSI ≥ 45:
     - Only invest the $150 base
     - Cash pool grows by $30

---

## Email Alert Setup

I've created `monitor_strategy.py` which will:
- ✅ Check SPY RSI(14) on your payday (1st and 15th)
- ✅ Track your cash pool automatically
- ✅ Send email with current metrics and recommendation
- ✅ Tell you whether to buy extra $150 or skip (based on RSI < 45)
- ✅ Track all investments in `strategy_tracking.json`

### Configure Email Notifications

1. **Open `monitor_strategy.py`** and find the `EMAIL_CONFIG` section (line ~26)

2. **For Gmail users:**
   ```python
   EMAIL_CONFIG = {
       "smtp_server": "smtp.gmail.com",
       "smtp_port": 587,
       "sender_email": "yourname@gmail.com",
       "sender_password": "your_app_password_here",  # NOT your regular password!
       "recipient_email": "yourname@gmail.com",
   }
   ```

3. **Get Gmail App Password:**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable **2-Step Verification** (required)
   - Click **App Passwords**
   - Generate password for "Mail"
   - Copy the 16-character password
   - Use that in `sender_password` (no spaces)

4. **For other email providers:**
   - **Outlook/Hotmail:**
     ```python
     "smtp_server": "smtp-mail.outlook.com",
     "smtp_port": 587,
     ```
   - **Yahoo:**
     ```python
     "smtp_server": "smtp.mail.yahoo.com",
     "smtp_port": 587,
     ```

---

## Running the Monitor

### Preview Email Without Sending (Do this first!)

**Before setting up email credentials, preview what you'll receive:**

```bash
cd /Users/danystefan/Documents/workspace/my_trading_strat/rsi_double_dca_backtest
/Users/danystefan/Documents/workspace/my_trading_strat/.venv/bin/python simulate_payday_email.py
```

This will:
- ✅ Fetch live SPY data and calculate current RSI(14)
- ✅ Show your current cash pool status
- ✅ Display exactly what your payday email will contain
- ✅ Show buy/skip recommendation based on current market
- ✅ **NO email sent** - just a preview!

**Run this anytime to see what action you'd take if today were payday!**

### Manual Test with Email (After email setup)
```bash
cd /Users/danystefan/Documents/workspace/my_trading_strat
.venv/bin/python rsi_double_dca_backtest/monitor_strategy.py
```

You should see:
- Current RSI
- Cash pool status
- Email sent (if configured)
- Summary saved to `strategy_tracking.json`

### Automate with Cron (Daily checks at 10 AM)

1. **Open cron editor:**
   ```bash
   crontab -e
   ```

2. **Add this line:**
   ```
   0 10 * * * cd /Users/danystefan/Documents/workspace/my_trading_strat && /Users/danystefan/Documents/workspace/my_trading_strat/.venv/bin/python rsi_double_dca_backtest/monitor_strategy.py >> /Users/danystefan/Documents/workspace/my_trading_strat/rsi_double_dca_backtest/monitor.log 2>&1
   ```

3. **Save and exit** (`:wq` in vim)

Now the script runs every day at 10 AM and logs to `monitor.log`.

---

## Email Alert Examples

### Payday Metrics Email
**Subject:** 📅 PAYDAY: Investment Metrics - 2025-12-01

**Body:**
```
RSI Cash Variant #2 - Payday Investment Metrics

Date: 2025-12-01
SPY RSI(14): 42.30
SPY Price: $587.45
Cash Pool: $120.00

YOUR DECISION TODAY:

1️⃣ BASE INVESTMENT (Always do this):
   ✅ Invest $150 CAD in SPY
   ✅ Add $30 to your cash pool
   → New cash pool will be: $120.00

2️⃣ RAINY DAY CHECK:
   Current RSI: 42.30
   Rainy threshold: < 45
   
   ✅ RAINY DAY - RSI < 45!
   
   🔥 RECOMMENDATION: Buy extra $150 from cash pool
   
   Total investment today: $300 ($150 base + $150 rainy)
   Cash pool after: $0.00

Next payday: 15th of this month
```

---

## Tracking Your Performance

The script maintains `strategy_tracking.json` with:
- Current cash pool
- All rainy day buys (date, RSI, price, amount)
- Total contributions
- Last check timestamp

**Example:**
```json
{
  "cash_pool": 60.0,
  "total_contributions": 0.0,
  "rainy_buys": [
    {
      "date": "2025-12-01",
      "rsi": 42.15,
      "price": 562.30,
      "amount": 150.0,
      "cash_before": 120.0,
      "cash_after": 0.0
    }
  ],
  "last_payday": "2025-12-01",
  "last_check": "2025-12-01 10:00:15"
}
```

---

## Quick Reference Card

| Event | Date | Base Investment | Cash Savings | Rainy Check | Rainy Buy? |
|-------|------|-----------------|--------------|-------------|------------|
| Payday 1 | 1st of month* | $150 | +$30 | If RSI < 45 | If cash ≥ $150 |
| Payday 2 | 15th of month* | $150 | +$30 | If RSI < 45 | If cash ≥ $150 |

*Or next business day if weekend

**Cash Pool Math:**
- Starts at $0
- Grows by $30 every payday
- After 5 paydays (2.5 months): $150 available for first rainy buy
- 80% of rainy opportunities = you'll deploy cash successfully
- 20% misses = expected and healthy (prevents depletion)

---

## Expected Results (22-year backtest)

- **Total contributions:** $104,350 CAD
- **Final equity:** $600,907 CAD
- **CAGR:** 33.54%
- **Max drawdown:** -27.47%
- **Rainy buys:** 112 out of 140 opportunities (80% hit rate)
- **Missed opportunities:** 28 (20%) — this is normal and expected

---

## Troubleshooting

### Email not sending?
1. Check Gmail app password (16 characters, no spaces)
2. Verify 2-Step Verification is enabled
3. Test with a simple Python script first
4. Check spam folder

### Wrong payday dates?
- Edit `PAYDAY_DAY_OF_MONTH_1 = 1` and `PAYDAY_DAY_OF_MONTH_2 = 15` in `monitor_strategy.py`
- Weekend handling is automatic (next business day)

### Want to change RSI threshold?
- Edit `RSI_THRESHOLD = 45.0` (not recommended, 45 is optimal for this variant)

### Want to track manually without email?
- Just run the script manually on paydays
- Check the console output for buy signals
- Review `strategy_tracking.json` anytime

---

## Next Steps

1. ✅ Configure email in `monitor_strategy.py`
2. ✅ Run manual test: `python rsi_double_dca_backtest/monitor_strategy.py`
3. ✅ Verify email received
4. ✅ Set up cron job for daily automation
5. ✅ Wait for first payday (1st or 15th, or next business day)
6. ✅ Follow email instructions when alerts arrive

**Good luck! You're now running the #2 ranked RSI Cash Strategy variant with 80% historical hit rate and 33.54% expected CAGR.**
