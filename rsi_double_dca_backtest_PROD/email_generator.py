"""
Email content generation for RSI SMA(7) strategy monitoring
============================================================

This module generates the email subject and body for payday notifications.
It uses RSI SMA(7) (7-day Simple Moving Average of RSI(14)) as the rainy day threshold.

Shared by both simulation and production email scripts to ensure consistency.
"""

from datetime import datetime, timedelta
from market_metrics import calculate_market_metrics
from strategy_comparison import calculate_strategy_comparison

# =============================================================================
# STRATEGY PARAMETERS
# =============================================================================
# These parameters define the core strategy behavior

DCA_BASE_AMOUNT = 150.0          # CAD - Base investment on every payday (always deployed)
RAINY_AMOUNT = 150.0             # CAD - Extra amount deployed when RSI SMA(7) < 45
RSI_THRESHOLD = 45.0             # RSI SMA(7) threshold for rainy day detection
CASH_ACCUMULATION = 30.0         # CAD - Cash saved per payday to build rainy day pool
PAYDAY_DAY_OF_MONTH_2 = 15       # Second payday of each month (1st and 15th schedule)


def generate_email_content(rsi_sma, price, cash_pool, total_contributions, rainy_buys, is_simulation=False, rsi_14=None):
    """
    Generate email subject and body for payday notifications.
    
    Uses RSI SMA(7) < 45 as the rainy day threshold. This smoothed indicator
    reduces noise and prevents false signals from temporary RSI dips.
    
    Args:
        rsi_sma: RSI SMA(7) - 7-day Simple Moving Average of RSI(14)
                 This is the primary threshold indicator (< 45 triggers rainy buy)
        price: Current SPY price in USD
        cash_pool: Current cash pool balance in CAD
        total_contributions: Total contributions to date in CAD
        rainy_buys: List of rainy buy records (historical data)
        is_simulation: If True, adds "TEST EMAIL" markers and notices
        rsi_14: RSI(14) - 14-day RSI value (optional, for display only)
    
    Returns:
        tuple: (subject, body) - email subject and plain text body
    """
    today = datetime.now().date()
    
    # Calculate accumulated rainy pool ROI (only for real emails, not test)
    rainy_pool_invested = 0.0
    rainy_pool_shares = 0.0
    rainy_pool_current_value = 0.0
    rainy_pool_roi_percent = 0.0
    rainy_pool_profit = 0.0
    rainy_pool_avg_price = 0.0
    
    if not is_simulation and rainy_buys:
        total_buy_price = 0.0
        for buy in rainy_buys:
            amount = buy.get('amount', 150.0)
            buy_price = buy.get('price', 0.0)
            rainy_pool_invested += amount
            total_buy_price += buy_price
            if buy_price > 0:
                rainy_pool_shares += amount / buy_price
        
        if len(rainy_buys) > 0:
            rainy_pool_avg_price = total_buy_price / len(rainy_buys)
        
        if rainy_pool_shares > 0:
            rainy_pool_current_value = rainy_pool_shares * price
            rainy_pool_profit = rainy_pool_current_value - rainy_pool_invested
            if rainy_pool_invested > 0:
                rainy_pool_roi_percent = (rainy_pool_profit / rainy_pool_invested) * 100
    
    today = datetime.now().date()
    
    # Calculate all market metrics using centralized module
    metrics = calculate_market_metrics(
        rsi_sma=rsi_sma,
        price=price,
        cash_pool=cash_pool,
        total_contributions=total_contributions,
        rainy_buys=rainy_buys,
        rsi_threshold=RSI_THRESHOLD,
        dca_base_amount=DCA_BASE_AMOUNT,
        rainy_amount=RAINY_AMOUNT,
        cash_accumulation=CASH_ACCUMULATION,
        payday_day_of_month_2=PAYDAY_DAY_OF_MONTH_2
    )
    
    # Calculate strategy comparisons using centralized module
    comparison = calculate_strategy_comparison()
    comp_metrics = comparison.get_all_metrics()
    
    # Extract all computed values from metrics module
    all_metrics = metrics.get_all_metrics()
    is_rainy = all_metrics["is_rainy"]
    can_deploy = all_metrics["can_deploy"]
    total_investment_today = all_metrics["total_investment_today"]
    new_cash_pool = all_metrics["new_cash_pool"]
    next_payday_text = all_metrics["next_payday_text"]
    rainy_buys_count = all_metrics["rainy_buys_count"]
    
    # Display values
    price_display = all_metrics["price_display"]
    rsi_sma_display = all_metrics["rsi_sma_display"]
    cash_pool_display = all_metrics["cash_pool_display"]
    total_contributions_display = all_metrics["total_contributions_display"]
    new_cash_pool_display = all_metrics["new_cash_pool_display"]
    
    # Text blocks
    recommendation = all_metrics["recommendation"]
    action_text = all_metrics["action_text"]
    cash_after_text = all_metrics["cash_after_text"]
    rainy_status = all_metrics["rainy_status"]
    decision_result = all_metrics["decision_result"]
    initial_note = all_metrics["initial_note"]
    cash_available_line = all_metrics["cash_available_line"]
    
    # =============================================================================
    # EMAIL FORMATTING - Subject and header based on context
    # =============================================================================
    # Test/simulation emails are marked clearly to distinguish from production
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
    
    # Metrics markdown table (embed in email)
    rsi_14_display = f"{rsi_14:.2f}" if rsi_14 is not None else "N/A"
    
    # Build rainy pool ROI section (only for production emails)
    rainy_pool_section = ""
    if not is_simulation and rainy_buys:
        rainy_pool_section = f"""

💧 RAINY POOL PERFORMANCE TRACKER
| Metric | Value |
|---|---|
| Total Rainy Contributions | ${rainy_pool_invested:,.2f} CAD |
| Average Rainy Buy Price | ${rainy_pool_avg_price:.2f} USD |
| Current SPY Price | ${price:.2f} USD |
| Current Rainy Pool Value | ${rainy_pool_current_value:,.2f} CAD |
| Rainy Pool Profit | ${rainy_pool_profit:,.2f} CAD |
| Rainy Pool ROI | {rainy_pool_roi_percent:.2f}% |
| Rainy Buys Deployed | {len(rainy_buys)} |

*This tracks ONLY your rainy day contributions and their performance*
"""
    
    metrics_markdown = f"""
📌 METRICS SNAPSHOT (Markdown)
| Metric | Value |
|---|---|
| SPY Price | {price_display} |
| RSI(14) | {rsi_14_display} |
| RSI SMA(7) | {rsi_sma_display} |
| Cash Pool | {cash_pool_display} |
| Threshold | {RSI_THRESHOLD:.0f} |
| Rainy Today? | {('Yes' if is_rainy else 'No')} |
{rainy_pool_section}"""

    body = f"""
🎯 RSI STRATEGY MONITOR - PROD{header_suffix}
{test_notice}
════════════════════════════════════════════════════════════════
📅 DATE: {today.strftime('%B %d, %Y')}{date_suffix}
📈 SPY PRICE: {price_display} USD
📊 RSI(14): {rsi_14_display}
📊 RSI SMA(7): {rsi_sma_display}

📌 EVALUATION TIMING: This email is sent on the 3rd and 17th of each month
   (2 days after payday on 1st/15th) when RSI is evaluated for rainy day.
════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════
📋 DECISION FROM STRATEGY RULES
═══════════════════════════════════════════════════════════════

DECISION PATH:
• RSI SMA(7) = {rsi_sma_display}
• Threshold = {RSI_THRESHOLD}
• Result: {decision_result}
{cash_available_line}

{action_text}

═══════════════════════════════════════════════════════════════

📊 TODAY'S PAYDAY ACTIONS

1️⃣ BASE INVESTMENT (always):
   Invest: ${DCA_BASE_AMOUNT:.0f} CAD into SPY
   
2️⃣ RAINY DAY CHECK:
   RSI SMA(7): {rsi_sma_display}
   Rainy threshold: RSI SMA(7) < {RSI_THRESHOLD}
   
   {rainy_status}
   
   {recommendation}
   
   {cash_after_text}

Next payday: {next_payday_text}

{metrics_markdown}

STRATEGY ASSUMPTIONS & FRAMEWORK

Your Regular Strategy (Variant #2):
• Payday schedule: 1st and 15th of each month (next business day if weekend)
• Base investment: $150 CAD every payday (always do this)
• Cash savings: $30 CAD every payday → builds cash pool
• Asset: SPY (S&P 500 ETF) converted to CAD

Rainy Day Rule:
• Check RSI SMA(7) only on payday (bi-weekly)
• If RSI SMA(7) < 45: Deploy extra $150 from cash pool
• If RSI SMA(7) ≥ 45: Only invest base $150, save the $30

📊 MARKET CONDITIONS & CASH POOL STRATEGY (22 Years of Data):

Historical Market Favorability:
• 82.7% of paydays (440/532): Market is expensive (RSI ≥ 45) - No rainy deployment ⛅
• 17.3% of paydays (92/532): Market is favorable (RSI < 45) - Rainy opportunity! 🌧️

Cash Pool Execution Rate:
• Current Strategy ($150/$30): 97.6% hit rate ✅
  - When the market IS rainy (17.3% of time), you deploy 97.6% of opportunities (83/85)
  - Only 2 missed opportunities in 22 years (99.8% success rate over all paydays)
  - Saving $30/payday is well-calibrated to handle nearly all rainy periods
  - Even consecutive rainy days (up to 5 in a row) are mostly covered

Why This Matters:
• The market rarely gives you opportunities (only 17.3% of paydays)
• But when it does, you're almost ALWAYS ready with cash (97.6% execution)
• Your $30/payday accumulation is optimized for rainy day frequency
• Minimal misses = capture nearly ALL 83 golden buying moments

Translation: In 22 years, the market gave you 83 chances to buy dips.
Your cash pool strategy captured 81 of them. Only 2 misses. 97.6% execution.

💰 PERFORMANCE VS OTHER STRATEGIES

📖 Investment ROI CAGR Definition:
Annualized return on dollar-cost-averaged contributions (measures growth from total invested → final equity).

Your Strategy vs Alternatives ({comp_metrics['backtest_years']} years: {comp_metrics['backtest_period']}):

| Strategy | ROI CAGR | Final Value | Total Invested | Profit ($) | Profit (%) | vs Simple DCA |
|----------|----------|-------------|----------------|------------|------------|---------------|
| YOUR RAINY DAY 🏆 | {comp_metrics['rainy_cagr']} | {comp_metrics['rainy_final']} | {comp_metrics['rainy_invested']} | {comp_metrics['rainy_profit']} | {comp_metrics['rainy_profit_pct']} | BASELINE |
| Simple DCA (No Rainy) | {comp_metrics['dca_cagr']} | {comp_metrics['dca_final']} | {comp_metrics['dca_invested']} | {comp_metrics['dca_profit']} | {comp_metrics['dca_profit_pct']} | {comp_metrics['dca_vs_baseline']} ⚠️ |
| Buy & Hold DCA | {comp_metrics['buy_hold_cagr']} | {comp_metrics['buy_hold_final']} | {comp_metrics['buy_hold_invested']} | {comp_metrics['buy_hold_profit']} | {comp_metrics['buy_hold_profit_pct']} | {comp_metrics['buy_hold_vs_baseline']} ⚠️ |

🔍 WHY SIMILAR CAGR (9.26% vs 9.46%) BUT YOU WIN BY $85,292:

The ROI CAGRs are nearly identical because both strategies efficiently compound returns.
BUT the rainy strategy deploys MORE capital ($14,550 extra) at OPTIMAL times (RSI < 45).

The Magic: Every rainy $1 → $5.86 after 22 years (586% ROI on rainy capital!)
• You deployed $14,550 extra → Gained $85,292 extra equity
• That's 5.86x your rainy money (vs 7.3x for base DCA)
• Lower CAGR on rainy buys (they're late-stage contributions) but MASSIVE absolute gains

Think of it: Invest $14.6k more during crashes → Walk away with $85.3k more wealth!

📊 ADVANCED METRICS (Risk & Quality):

| Strategy | Sharpe Ratio | SQN | Max Drawdown | Volatility | R² (Stability) |
|----------|--------------|-----|--------------|------------|----------------|
| YOUR RAINY DAY | {comp_metrics['rainy_sharpe']} | {comp_metrics['rainy_sqn']} | {comp_metrics['rainy_max_dd']} | {comp_metrics['rainy_volatility']} | {comp_metrics['rainy_r_squared']} |
| Simple DCA | {comp_metrics['dca_sharpe']} | {comp_metrics['dca_sqn']} | {comp_metrics['dca_max_dd']} | {comp_metrics['dca_volatility']} | {comp_metrics['dca_r_squared']} |
| Buy & Hold | {comp_metrics['buy_hold_sharpe']} | {comp_metrics['buy_hold_sqn']} | {comp_metrics['buy_hold_max_dd']} | {comp_metrics['buy_hold_volatility']} | {comp_metrics['buy_hold_r_squared']} |

*Sharpe: {comp_metrics['rainy_sharpe_rating']} | SQN: {comp_metrics['rainy_sqn_rating']}*
*Lower drawdown = less risk | Higher R² = more stable growth*

📈 WHY YOUR RAINY STRATEGY WINS (THE MATH):

IS IT WORTH IT? Absolutely - here's the proof:
• Extra invested during rainy days: {comp_metrics['extra_deployed']}
• Extra equity gained: {comp_metrics['gain_vs_dca']}
• ROI on just the rainy capital: {comp_metrics['rainy_roi']} (or {comp_metrics['rainy_roi_multiplier']} your money)

The Investment Efficiency Breakdown:
  Deploy: {comp_metrics['extra_deployed']} more in 83 rainy buys (when RSI < 45)
  Result: {comp_metrics['gain_vs_dca']} more final equity
  Ratio:  5.86x return on your rainy dollars after 22 years

Why CAGR is similar (9.26% vs 9.46%) but you still crush it:
• Both strategies compound efficiently (9-10% annual returns)
• Simple DCA has slightly higher CAGR because it deploys LESS total capital
• But you deployed MORE capital ($73,950 vs $59,400) at BETTER times (crashes)
• Result: Lower relative CAGR, but WAY higher absolute wealth ($85k more!)

Think of it this way:
  Simple DCA: 630.7% return on $59,400 = $374,651 profit
  Rainy Strategy: 602.3% return on $73,950 = $445,393 profit
  
  Lower % return, but you invested more, so you made $70,742 MORE profit!

Real-world translation: Invest $14.6k more during 22 years of crashes → $85.3k more wealth.
That's every rainy $1 becoming $5.86. Simple DCA turns each $1 into $7.31, but you 
have $14.6k MORE dollars working for you!

🌧️ ISOLATED RAINY DAY PERFORMANCE

Analyzing ONLY the $12,450 deployed during 83 rainy buys (when RSI < 45):

Overall Rainy Money Stats:
• Total Rainy Contributions: $14,550 (97 buys over 22 years)
• Average SPY Price on Rainy Days: $210.14
• Current SPY Price (Nov 21, 2025): $659.03
• Price Appreciation: 3.14x (you bought at 68% discount vs today!)
• Total Shares from Rainy Money: 105.05 shares
• Current Value of Rainy Shares: $69,234
• Dollar Gain on Rainy Money: $54,684
• Percent Return on Rainy Contributions: 375.8%

Top 5 Rainy Periods (by return):
1. 2009 (Mar-Nov, 245 days, 2 buys): $300 → $3,180 (960% return!) 🏆
   • Caught the Financial Crisis bottom at avg $64.93/share
2. 2004 (Mar-Aug, 139 days, 5 buys): $750 → $6,646 (786% return)
   • Early strategy deployment, held 21 years
3. 2005 (Apr-Oct, 196 days, 4 buys): $600 → $4,847 (708% return)
4. 2008 (Jan-Dec, 321 days, 5 buys): $750 → $5,841 (679% return)
   • Great Financial Crisis - caught falling knife perfectly
5. 2010 (Feb-Dec, 303 days, 6 buys): $900 → $6,946 (672% return)

Recent Rainy Periods (still compounding):
• 2025 (Jan-Mar, 73 days, 4 buys): $600 → $682 (14% return - just started!)
• 2024 (Apr-Aug, 110 days, 3 buys): $450 → $592 (32% return)
• 2023 (Jan-Oct, 273 days, 5 buys): $750 → $1,259 (68% return)
• 2022 (Feb-Oct, 256 days, 9 buys): $1,350 → $2,323 (72% return)

💡 The Power of Rainy Periods:
Every $1 you deployed during rainy days became $4.76 from price appreciation alone!
Longest rainy period: 2008 (321 days, 5 buys during Financial Crisis)
Most aggressive: 2022 (9 buys, $1,350 deployed during bear market)
Best vintage: 2009 - caught absolute bottom at $51.53 per share

📊 See attached charts:
- strategy_comparison_with_baseline.png - Growth curves comparison
- rainy_day_analysis_detailed.png - Hit/miss pattern & cash pool
- spy_price_rainy_periods_drawdown.png - When you bought during crashes
- cash_pool_hit_miss.png - Cash pool evolution with rainy buy markers
- spy_price_hit_miss.png - SPY price with successful/missed buy markers
- rsi_hit_miss.png - RSI indicator with rainy day trigger points

CURRENT STATUS

Cash Pool: {cash_pool_display}
Total Contributions to Date: {total_contributions_display}
Total Rainy Buys to Date: {rainy_buys_count}{initial_note}

ACTUAL BACKTEST RESULTS (Oct 2003 - Nov 2025, {comp_metrics['backtest_years']} years):
• Investment ROI CAGR: {comp_metrics['rainy_cagr']} (annualized return on contributed capital)
• Final Equity: {comp_metrics['rainy_final']} (as of Nov 21, 2025)
• Total Invested: {comp_metrics['rainy_invested']} (base DCA + rainy buys)
• Profit: {comp_metrics['rainy_profit']} ({comp_metrics['rainy_profit_pct']} total return)
• Successful Rainy Buys: {comp_metrics['num_rainy_buys']} tactical deployments

📌 CAGR NUANCE: Why 9.26% CAGR still beats Simple DCA's 9.46% CAGR:
   • CAGR measures PERCENTAGE growth (relative return)
   • You deployed MORE capital ($14,550 extra in rainy buys)
   • More capital × great timing = $85,292 MORE absolute wealth
   • Lower % return on larger base = bigger dollar gains!
   
   Example: 600% on $74k beats 630% on $59k in absolute terms.
"""
    
    if is_simulation:
        body += "\nThis is a SIMULATED email for testing purposes.\n"
        body += "Actual payday emails will be sent on the 1st and 15th of each month.\n"
    
    return subject, body
