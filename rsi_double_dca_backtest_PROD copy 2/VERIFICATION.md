# Final Setup Verification

## ✅ Quick Checklist

### 1. Test Email Preview Locally First
```bash
cd /Users/danystefan/Documents/workspace/my_trading_strat/rsi_double_dca_backtest
/Users/danystefan/Documents/workspace/my_trading_strat/.venv/bin/python simulate_payday_email.py
```
**This shows you what the email will look like WITHOUT sending it!**

### 2. Code Pushed to GitHub
- [x] Repository created: https://github.com/dany-stefan/my_trading_strat
- [x] Code pushed successfully

### 3. Secrets Configuration Required

Go to: https://github.com/dany-stefan/my_trading_strat/settings/secrets/actions

Add these 5 secrets (click "New repository secret" for each):

| Secret Name | Value |
|-------------|-------|
| `SMTP_SERVER` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SENDER_EMAIL` | `d4388707373@gmail.com` |
| `SENDER_PASSWORD` | `kzuf dozw badx wwro` |
| `RECIPIENT_EMAIL` | `d4388707373@gmail.com` |

### 4. Enable GitHub Actions

1. Go to: https://github.com/dany-stefan/my_trading_strat/actions
2. If prompted, click **"I understand my workflows, go ahead and enable them"**
3. You should see "RSI Strategy Monitor" workflow listed

### 4. Test Email Preview Locally (Before Cloud Setup)

**Preview what your payday email will look like WITHOUT sending:**

```bash
cd /Users/danystefan/Documents/workspace/my_trading_strat/rsi_double_dca_backtest
/Users/danystefan/Documents/workspace/my_trading_strat/.venv/bin/python simulate_payday_email.py
```

This will:
- ✅ Fetch live SPY RSI and price data
- ✅ Show exactly what your payday email will contain
- ✅ Display current cash pool status
- ✅ Show buy/skip recommendation based on current RSI
- ✅ **No email sent** - just a preview in terminal

**Run this anytime** to see what action you'd take if today were payday!

### 5. Test the Workflow (After Cloud Setup)

1. Go to: https://github.com/dany-stefan/my_trading_strat/actions
2. Click **"RSI Strategy Monitor"**
3. Click **"Run workflow"** button (top right)
4. Click **"Run workflow"** in the dropdown
5. Wait ~60 seconds, then refresh the page
6. Click on the workflow run to see logs
7. **Check your email!** (even though it's not the 1st/15th, manual runs can test the email)

---

## How It Works

### Daily Checks (No Email)
- Workflow runs every day at 1:00 PM EST
- Script checks if it's an execution day (3rd or 17th, or next TSX trading day)
- If NOT execution day: Logs check, no email sent
- Free GitHub Actions minutes used: <1 minute/day
- Note: Execution days are 3rd and 17th (2 days after payday on 1st and 15th) to sync with Wealthsimple recurring buys

### Payday Emails (Execution on 3rd and 17th)

**Important:** While payday occurs on the 1st and 15th of each month, the strategy executes buy orders and sends email alerts on the 3rd and 17th (2 days later) to align with Wealthsimple's recurring purchase schedule. If the 3rd or 17th falls on a weekend or TSX holiday, execution automatically moves to the next TSX trading day.

- Workflow runs at 1:00 PM EST on execution days (3rd and 17th)
- Script fetches SPY price and calculates RSI(14)
- Calculates RSI SMA(7) from 7-day RSI history
- Calculates cash pool balance
- **Sends email with:**
  - Current RSI SMA(7) and recommendation
  - Whether to buy extra $150 or skip
  - Variant comparison table
  - Strategy framework

### Weekend and Holiday Handling
- If 3rd or 17th falls on a weekend or TSX holiday
- Email sent on the next TSX trading day instead
- Automatic - no configuration needed
- TSX holidays checked: New Year's Day, Canada Day, Christmas, Boxing Day
- Note: Payday is always 1st and 15th, but execution moves to 3rd and 17th (2 days later)

---

## Expected Email Schedule

**Note:** Payday is the 1st and 15th of each month, but email alerts and buy order execution occur on the 3rd and 17th (2 days later) to align with Wealthsimple's recurring purchase schedule.

| Payday Date | Execution Date | Email Sent? | Reason |
|-------------|----------------|-------------|--------|
| Nov 21, 2025 | N/A | ❌ No | Not a payday or execution day |
| Dec 1, 2025 | Dec 3, 2025 | ✅ Yes | Execution day (3rd) - 2 days after payday (1st) |
| Dec 15, 2025 | Dec 17, 2025 | ✅ Yes | Execution day (17th) - 2 days after payday (15th) |
| Jan 1, 2026 | Jan 3, 2026 | ✅ Yes | Execution day (3rd) - 2 days after payday (1st) |
| Jan 15, 2026 | Jan 17, 2026 | ✅ Yes | Execution day (17th) - 2 days after payday (15th) |

---

## Logs and Debugging

### View Workflow Logs
1. https://github.com/dany-stefan/my_trading_strat/actions
2. Click any workflow run
3. Click "monitor" job
4. Expand steps to see output

### Check Email Configuration
Look for these in logs:
```
✅ Email sent: 📅 EXECUTION DAY: Investment Metrics - 2025-12-03
```

Note: Email subject references execution date (3rd or 17th), which is 2 days after payday (1st or 15th).

Or:
```
❌ Failed to send email: [error message]
```

### Common Issues

**No email received?**
- Verify all 5 secrets are set correctly
- Check spam folder
- Review workflow logs for errors
- Ensure Gmail app password is valid

**Workflow not running?**
- Verify Actions tab is enabled
- Check `.github/workflows/rsi_monitor.yml` exists in repo
- GitHub requires at least 1 commit in last 60 days

**Wrong timezone?**
- Workflow uses UTC
- Current schedule: 18:00 UTC = 1:00 PM EST (on 3rd and 17th)
- Note: Execution is on 3rd and 17th (2 days after payday on 1st and 15th)
- Adjust cron in workflow file if needed

---

## Cost: $0

- ✅ GitHub Actions: 2,000 free minutes/month
- ✅ Your usage: ~30 minutes/month (1 min/day × 30 days)
- ✅ Usage: 1.5% of free quota
- ✅ No credit card needed
- ✅ Works forever on free tier

---

## Next Steps

1. **Add the 5 secrets** (most important!)
2. **Run workflow manually** to test
3. **Check your email**
4. **Relax** - you're now fully automated!

Your next real email: **December 1, 2025 at ~10:00 AM**

---

## Support

If you need help:
- Check logs: https://github.com/dany-stefan/my_trading_strat/actions
- Review this guide
- Test with manual workflow trigger
