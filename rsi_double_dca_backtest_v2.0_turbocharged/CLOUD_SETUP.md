# RSI Strategy Monitor - GitHub Actions Setup

## ✅ Complete Setup (5 minutes)

Your RSI strategy will run automatically in the cloud, **no Mac needed**!

---

## Step 1: Push Code to GitHub

```bash
cd /Users/danystefan/Documents/workspace/my_trading_strat

# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Add RSI Cash Strategy monitoring"

# Create a new repository on GitHub (https://github.com/new)
# Name it: my_trading_strat
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/my_trading_strat.git
git branch -M main
git push -u origin main
```

---

## Step 2: Add Secrets to GitHub

Your email credentials need to be stored securely:

1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/my_trading_strat`

2. Click **Settings** → **Secrets and variables** → **Actions**

3. Click **New repository secret** and add these **5 secrets**:

   | Secret Name | Value |
   |-------------|-------|
   | `SMTP_SERVER` | `smtp.gmail.com` |
   | `SMTP_PORT` | `587` |
   | `SENDER_EMAIL` | `d4388707373@gmail.com` |
   | `SENDER_PASSWORD` | `kzuf dozw badx wwro` |
   | `RECIPIENT_EMAIL` | `d4388707373@gmail.com` |

---

## Step 3: Enable GitHub Actions

1. Go to **Actions** tab in your repository

2. Click **I understand my workflows, go ahead and enable them**

3. You should see **RSI Strategy Monitor** workflow

---

## Step 4: Preview Email Locally First (Optional but Recommended)

**Before triggering the cloud workflow, test locally:**

```bash
cd /Users/danystefan/Documents/workspace/my_trading_strat/rsi_double_dca_backtest
/Users/danystefan/Documents/workspace/my_trading_strat/.venv/bin/python simulate_payday_email.py
```

This shows exactly what the email will contain - no email sent, just a preview!

## Step 5: Test Cloud Workflow

1. Click on **RSI Strategy Monitor** workflow

2. Click **Run workflow** → **Run workflow**

3. Wait 30-60 seconds, refresh page

4. Click on the running workflow to see logs

5. **Check your email!** You should receive the payday metrics email

---

## ✅ That's It!

The workflow will now run automatically:
- **Daily at 1:00 PM EST** (18:00 UTC)
- **Execution days: 3rd and 17th of each month** (or next TSX trading day)

**Important:** Payday occurs on the 1st and 15th of each month, but buy order execution and email alerts are sent on the 3rd and 17th (2 days later) to align with Wealthsimple's recurring purchase schedule.

### What happens:
- ✅ GitHub servers run your script in the cloud
- ✅ No Mac needed - works even when your computer is off
- ✅ Completely free (GitHub Actions gives 2,000 minutes/month free)
- ✅ Email sent on execution days (3rd and 17th) only
- ✅ Logs saved for 30 days

---

## Useful Commands

### View Workflow Status
- Go to: `https://github.com/YOUR_USERNAME/my_trading_strat/actions`
- See all runs, check logs, debug issues

### Manually Trigger Workflow
- Actions tab → RSI Strategy Monitor → Run workflow

### View Logs
- Click any workflow run → Click "monitor" job → Expand steps

### Update Schedule
Edit `.github/workflows/rsi_monitor.yml`:
```yaml
schedule:
  - cron: '0 15 * * *'  # Change time (UTC)
```

### Disable Monitoring
- Actions tab → RSI Strategy Monitor → ⋯ menu → Disable workflow

---

## Timezone Note

GitHub Actions uses **UTC time**. Current schedule:
- `0 18 3,17 * *` = 1:00 PM EST on 3rd and 17th (18:00 UTC)

**Execution Logic:**
- Payday: 1st and 15th of each month
- Execution: 3rd and 17th (2 days later) to sync with Wealthsimple recurring buys
- If 3rd or 17th is a weekend or TSX holiday, execution moves to next TSX trading day

Adjust if needed for your timezone.

---

## 🧪 Testing Your Setup (Manual Trigger)

You can **manually test** the GitHub Actions workflow to receive an email **even when it's not an execution day (3rd or 17th)**:

### Steps:

1. Go to your GitHub repository
2. Click the **Actions** tab at the top
3. On the left sidebar, select **RSI Strategy Monitor** workflow
4. Click the **Run workflow** button (top right, next to the branch dropdown)
5. You'll see a dropdown with an option:
   - **"Send email even if not execution day (for testing)"**
   - Select **true**
6. Click the green **Run workflow** button

### What Happens:

Within 1-2 minutes, you'll receive an email with:
- **Subject:** "🧪 TEST EMAIL (Local Run): Investment Metrics - [Date]"
- **Content:** Current SPY price, RSI SMA(7), and your recommendation
- **Note:** This will NOT update your cash pool or tracking (test mode only)
- **Reminder:** Actual execution occurs on 3rd and 17th (2 days after payday on 1st and 15th)

### Perfect For:

- ✅ Verifying email configuration works
- ✅ Seeing what execution day emails look like
- ✅ Checking current market conditions remotely
- ✅ Testing after changing email settings
- ✅ Understanding the 2-day delay (payday → execution)

### Local Testing Alternative:

If you want to test locally without GitHub:

```bash
cd /Users/danystefan/Documents/workspace/my_trading_strat
FORCE_EMAIL=true ./venv/bin/python rsi_double_dca_backtest/monitor_strategy.py
```

This sends a test email from your machine.

---

## Troubleshooting

### Email not sending?
- Check secrets are entered correctly (no extra spaces)
- Verify Gmail app password is valid
- Check workflow logs for errors

### Workflow not running?
- Verify `.github/workflows/rsi_monitor.yml` is in your repo
- Check Actions tab is enabled
- GitHub Actions requires at least 1 commit in the last 60 days

### Want to change email?
- Update secrets in GitHub repository settings
- No code changes needed!

---

## Cost: $0

GitHub provides:
- ✅ 2,000 minutes/month free (your script uses ~1 minute/day = 30 min/month)
- ✅ Unlimited private repositories
- ✅ No credit card required

You'll use less than 2% of your free quota.

---

## Alternative: Replit (Even Easier)

If you want a web-based option with no git/GitHub knowledge:

1. Go to https://replit.com (free account)
2. Create new Repl → Python
3. Upload your `monitor_strategy.py` file
4. Click **Deployments** → **Autoscale** → Schedule cron job
5. Add cron: `0 10 * * *` (daily at 10 AM)
6. Done! No git, no command line.

Cost: Free tier available, or $7/month for always-on.

---

**Recommendation: Use GitHub Actions** - it's free, reliable, and you already have the code set up!
