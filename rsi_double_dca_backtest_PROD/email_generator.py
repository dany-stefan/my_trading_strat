"""
Email content generation for RSI strategy monitoring
Shared by both simulation and production email scripts
"""

from datetime import datetime, timedelta

# Strategy parameters
DCA_BASE_AMOUNT = 150.0
RAINY_AMOUNT = 150.0
RSI_THRESHOLD = 45.0
CASH_ACCUMULATION = 30.0
PAYDAY_DAY_OF_MONTH_2 = 15


def generate_email_content(rsi, price, cash_pool, total_contributions, rainy_buys, is_simulation=False):
    """
    Generate email subject and body for payday notifications.
    
    Args:
        rsi: Current RSI value
        price: Current SPY price
        cash_pool: Current cash pool balance
        total_contributions: Total contributions to date
        rainy_buys: List of rainy buy records
        is_simulation: If True, adds simulation notices
    
    Returns:
        tuple: (subject, body) - email subject and plain text body
    """
    today = datetime.now().date()
    
    # Determine next payday
    if today.day < PAYDAY_DAY_OF_MONTH_2:
        next_payday_text = f"{PAYDAY_DAY_OF_MONTH_2}th of this month"
    else:
        next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
        next_payday_text = f"1st of {next_month.strftime('%B')}"
    
    # Check if rainy day
    is_rainy = rsi < RSI_THRESHOLD
    can_deploy = cash_pool >= RAINY_AMOUNT
    
    # Determine recommendation
    if is_rainy and can_deploy:
        recommendation = f"🔥 RECOMMENDATION: Buy extra ${RAINY_AMOUNT:.0f} from cash pool"
        total_investment_today = DCA_BASE_AMOUNT + RAINY_AMOUNT
        cash_after_deploy = cash_pool - RAINY_AMOUNT
        new_cash_pool = cash_pool - RAINY_AMOUNT + CASH_ACCUMULATION
        action_text = f"Total investment today: ${total_investment_today:.0f} (${DCA_BASE_AMOUNT:.0f} base + ${RAINY_AMOUNT:.0f} rainy)"
        cash_after_text = f"Cash pool after rainy buy: ${cash_after_deploy:.2f}\n   Add today's savings: +${CASH_ACCUMULATION:.0f}\n   Final cash pool: ${new_cash_pool:.2f}"
    elif is_rainy and not can_deploy:
        recommendation = f"⚠️  Rainy day but insufficient cash (need ${RAINY_AMOUNT:.0f}, have ${cash_pool:.2f})"
        total_investment_today = DCA_BASE_AMOUNT
        new_cash_pool = cash_pool + CASH_ACCUMULATION
        action_text = f"Total investment today: ${total_investment_today:.0f} (base only)"
        cash_after_text = f"Cash pool after saving: ${new_cash_pool:.2f}"
    else:
        recommendation = f"💰 RECOMMENDATION: Save your cash for next rainy day"
        total_investment_today = DCA_BASE_AMOUNT
        new_cash_pool = cash_pool + CASH_ACCUMULATION
        action_text = f"Total investment today: ${total_investment_today:.0f} (base only)"
        cash_after_text = f"Cash pool after saving: ${new_cash_pool:.2f}"
    
    rainy_status = "✅ RAINY DAY - RSI < 45!" if is_rainy else "⛅ NOT RAINY - RSI ≥ 45"
    
    # Note about initial balance
    initial_note = ""
    if total_contributions == 0:
        initial_note = f"\n   📌 NOTE: Starting with ${cash_pool:.2f} initial cash pool (enough for 2 rainy buys)"
    
    # Email subject
    if is_simulation:
        subject = f"🧪 TEST EMAIL (Local Run): Investment Metrics - {today.strftime('%B %d, %Y')}"
    else:
        subject = f"📅 PAYDAY: Investment Metrics - {today.strftime('%B %d, %Y')}"
    
    # Email body
    if is_simulation:
        header_suffix = " - TEST EMAIL (LOCAL RUN)"
        date_suffix = " 🧪 LOCAL TEST"
        test_notice = "\n🧪 THIS IS A TEST EMAIL FROM LOCAL RUN\nThis email was manually triggered for testing purposes.\n"
    else:
        header_suffix = " - PAYDAY"
        date_suffix = ""
        test_notice = ""
    
    body = f"""
🎯 RSI STRATEGY MONITOR{header_suffix}
{test_notice}
Date: {today.strftime('%B %d, %Y')}{date_suffix}
Current SPY Price: ${price:.2f} USD
Current RSI(14): {rsi:.2f}

📊 TODAY'S PAYDAY ACTIONS

1️⃣ BASE INVESTMENT (always):
   Invest: ${DCA_BASE_AMOUNT:.0f} CAD into SPY
   
2️⃣ RAINY DAY CHECK:
   Current RSI: {rsi:.2f}
   Rainy threshold: < {RSI_THRESHOLD}
   
   {rainy_status}
   
   {recommendation}
   
   {action_text}
   {cash_after_text}

Next payday: {next_payday_text}

VARIANT PERFORMANCE SUMMARY (22-year backtest)

| Variant | CAGR | Hit Rate | End Value | Total Cost |
|---------|------|----------|-----------|------------|
| #1 Weekly $150 RSI<40 | 33.54% | 68.5% | $600,967 | $104,500 |
| #2 Bi-weekly $150 RSI<45 (YOUR PICK) | 33.54% | 80.0% ⭐ | $600,907 | $104,350 |
| #3 Weekly $100 RSI<45 | 33.54% | 65.3% | $600,679 | $104,450 |

Key Metrics:
• All 3 variants: Identical 33.54% CAGR (same long-term returns)
• Your variant (#2): HIGHEST hit rate at 80% (most sustainable)
• 22-year period: 2003-2025 (includes 2008 crash, COVID, all cycles)
• Return per $1 invested: $5.76 (every dollar becomes $5.76)

STRATEGY ASSUMPTIONS & FRAMEWORK

Your Regular Strategy (Variant #2):
• Payday schedule: 1st and 15th of each month (next business day if weekend)
• Base investment: $150 CAD every payday (always do this)
• Cash savings: $30 CAD every payday → builds cash pool
• Asset: SPY (S&P 500 ETF) converted to CAD

Rainy Day Rule:
• Check RSI(14) only on payday (bi-weekly)
• If RSI < 45: Deploy extra $150 from cash pool
• If RSI ≥ 45: Only invest base $150, save the $30
• Expected hit rate: 80% of rainy opportunities

💰 PERFORMANCE VS OTHER STRATEGIES

Your Strategy vs Alternatives (22 years: 2003-2025):

| Strategy | CAGR | Final Value | Total Invested | Profit | vs Your Strategy |
|----------|------|-------------|----------------|--------|------------------|
| YOUR RAINY DAY (Variant #2) | 33.54% | $600,907 | $104,350 | $496,557 | BASELINE |
| Simple DCA (No Rainy) | 32.48% | $503,343 | $87,550 | $415,793 | -$97,564 ⚠️ |
| Buy & Hold (Lump Sum) | 31.12% | $450,234 | $87,550 | $362,684 | -$133,873 ⚠️ |

📈 WHAT YOU GAINED BY CHOOSING THIS STRATEGY:

• vs Simple DCA: You gained an extra $97,564 (+19.4% more wealth!)
  - Cost: Only $16,800 extra deployed during crashes
  - Return on rainy capital: 581% (every rainy $1 became $6.81)
  
• vs Buy & Hold: You gained an extra $133,873 (+26.5% more wealth!)
  - DCA smoothed your entry prices over 22 years
  - Rainy buys captured crash discounts (2008, 2020, etc.)
  
• Key Advantage: Same contributions as simple DCA ($150 bi-weekly)
  - You just deployed the $30 savings SMARTER (during RSI < 45)
  - Hit rate: 80% success rate on rainy deployments
  - No timing skill needed - just follow RSI on payday

📊 See attached charts:
- strategy_comparison_with_baseline.png - Growth curves comparison
- rainy_day_analysis_detailed.png - Hit/miss pattern & cash pool
- spy_price_rainy_periods_drawdown.png - When you bought during crashes

WHY YOU CHOSE VARIANT #2 (Reminder)

Top 3 Variants Comparison:

| Rank | Cadence | Amount | RSI | CAGR | Hit Rate | Why NOT |
|------|---------|--------|-----|------|----------|---------|
| #1 | Weekly Every Mon | $150 | < 40 | 33.54% | 68.5% | Must check weekly |
| #2 ✅ (YOU) | Bi-weekly Payday 1st & 15th | $150 | < 45 | 33.54% | 80.0% | PAYDAY ALIGNED SIMPLE! |
| #3 | Weekly Every Mon | $100 | < 45 | 33.54% | 65.3% | Smaller position |

Your Choice = #2 Because:
✅ Only check RSI when you get paid (easier schedule)
✅ Highest hit rate (80% vs 68.5% and 65.3%)
✅ Same returns as #1 and #3 (33.54% CAGR)
✅ Best for busy people with paychecks

CURRENT STATUS

Cash Pool: ${cash_pool:.2f}
Total Contributions to Date: ${total_contributions:,.2f}
Total Rainy Buys to Date: {len(rainy_buys)}{initial_note}

Expected Long-Term Results (22 years):
• CAGR: 33.54%
• Final Equity: $600,907
• Total Invested: $104,350
• Successful Rainy Buys: 112 / 140 opportunities (80%)
"""
    
    if is_simulation:
        body += "\nThis is a SIMULATED email for testing purposes.\n"
        body += "Actual payday emails will be sent on the 1st and 15th of each month.\n"
    
    return subject, body
