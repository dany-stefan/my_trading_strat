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


def generate_email_content(rsi_sma, price, cash_pool, total_contributions, rainy_buys, is_simulation=False):
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
    
    Returns:
        tuple: (subject, body) - email subject and plain text body
    """
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
    metrics_markdown = f"""
📌 METRICS SNAPSHOT (Markdown)
| Metric | Value |
|---|---|
| SPY Price | {price_display} |
| RSI SMA(7) | {rsi_sma_display} |
| Cash Pool | {cash_pool_display} |
| Threshold | {RSI_THRESHOLD:.0f} |
| Rainy Today? | {('Yes' if is_rainy else 'No')} |
"""

    body = f"""
🎯 RSI STRATEGY MONITOR - PROD{header_suffix}
{test_notice}
════════════════════════════════════════════════════════════════
📅 DATE: {today.strftime('%B %d, %Y')}{date_suffix}
📈 SPY PRICE: {price_display} USD
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
• Check RSI SMA(7) only on payday (bi-weekly)
• If RSI SMA(7) < 45: Deploy extra $150 from cash pool
• If RSI SMA(7) ≥ 45: Only invest base $150, save the $30

💰 PERFORMANCE VS OTHER STRATEGIES

Your Strategy vs Alternatives ({comp_metrics['backtest_years']} years: {comp_metrics['backtest_period']}):

| Strategy | CAGR | Final Value | Total Invested | Profit | vs Your Strategy |
|----------|------|-------------|----------------|--------|------------------|
| YOUR RAINY DAY (Variant #2) | {comp_metrics['rainy_cagr']} | {comp_metrics['rainy_final']} | {comp_metrics['rainy_invested']} | {comp_metrics['rainy_profit']} | {comp_metrics['rainy_vs_baseline']} |
| Simple DCA (No Rainy) | {comp_metrics['dca_cagr']} | {comp_metrics['dca_final']} | {comp_metrics['dca_invested']} | {comp_metrics['dca_profit']} | {comp_metrics['dca_vs_baseline']} ⚠️ |
| Buy & Hold (${comp_metrics['buy_hold_initial_display']} Lump Sum) | {comp_metrics['buy_hold_cagr']} | {comp_metrics['buy_hold_final']} | {comp_metrics['buy_hold_invested']} | {comp_metrics['buy_hold_profit']} | {comp_metrics['buy_hold_vs_baseline']} ⚠️ |

📊 ADVANCED METRICS (Risk & Quality):

| Strategy | Sharpe Ratio | SQN | Max Drawdown | Volatility | R² (Stability) |
|----------|--------------|-----|--------------|------------|----------------|
| YOUR RAINY DAY | {comp_metrics['rainy_sharpe']} | {comp_metrics['rainy_sqn']} | {comp_metrics['rainy_max_dd']} | {comp_metrics['rainy_volatility']} | {comp_metrics['rainy_r_squared']} |
| Simple DCA | {comp_metrics['dca_sharpe']} | {comp_metrics['dca_sqn']} | {comp_metrics['dca_max_dd']} | {comp_metrics['dca_volatility']} | {comp_metrics['dca_r_squared']} |
| Buy & Hold | {comp_metrics['buy_hold_sharpe']} | {comp_metrics['buy_hold_sqn']} | {comp_metrics['buy_hold_max_dd']} | {comp_metrics['buy_hold_volatility']} | {comp_metrics['buy_hold_r_squared']} |

*Sharpe: {comp_metrics['rainy_sharpe_rating']} | SQN: {comp_metrics['rainy_sqn_rating']}*
*Lower drawdown = less risk | Higher R² = more stable growth*

📈 WHAT YOU GAINED BY CHOOSING THIS STRATEGY:

• vs Simple DCA: You gained an extra {comp_metrics['gain_vs_dca']} (+{comp_metrics['gain_vs_dca_pct']} more wealth!)
  - Base contributions (bi-weekly DCA): {comp_metrics['base_contributions']}
  - Extra rainy deployments ({comp_metrics['num_rainy_buys']} crash buys): {comp_metrics['extra_deployed']}
  - Total invested: {comp_metrics['rainy_invested']}
  - Return on rainy capital: {comp_metrics['rainy_roi']} (every rainy $1 became {comp_metrics['rainy_roi_multiplier']})
  - *Your rainy buys during crashes generated the extra {comp_metrics['gain_vs_dca']} profit vs simple DCA!*
  
• vs Buy & Hold: You gained an extra {comp_metrics['gain_vs_buy_hold']} (+{comp_metrics['gain_vs_buy_hold_pct']} more wealth!)
  - DCA smoothed your entry prices over {comp_metrics['backtest_years']} years
  - Rainy buys captured crash discounts (2008, 2020, etc.)
  
• Key Advantage: Same contributions as simple DCA ($150 bi-weekly)
  - You just deployed the $30 savings SMARTER (during RSI < 45)
  - No timing skill needed - just follow RSI on payday

📊 See attached charts:
- strategy_comparison_with_baseline.png - Growth curves comparison
- rainy_day_analysis_detailed.png - Hit/miss pattern & cash pool
- spy_price_rainy_periods_drawdown.png - When you bought during crashes
- cash_pool_hit_miss.png - Cash pool evolution with rainy buy markers
- spy_price_hit_miss.png - SPY price with successful/missed buy markers
- rsi_hit_miss.png - RSI indicator with rainy day trigger points

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

Cash Pool: {cash_pool_display}
Total Contributions to Date: {total_contributions_display}
Total Rainy Buys to Date: {rainy_buys_count}{initial_note}

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
