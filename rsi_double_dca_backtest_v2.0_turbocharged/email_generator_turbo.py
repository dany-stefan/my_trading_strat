"""
Turbo Email content generation with adaptive 3-factor system
=============================================================

This module generates the TURBO v2.0 email subject and body including:
- Market Regime adaptive RSI threshold (Bull/Neutral/Bear)
- Volatility (VIX) based rainy amount sizing
- Smoothed RSI SMA(7) oversold confirmation
- Restored CRITERIA EXPLANATION and 3-FACTOR SYSTEM SUMMARY blocks

It does NOT modify the PROD email generator. Monitored script should import
from this file for TURBO output.
"""
from datetime import datetime, timedelta
from market_metrics import calculate_market_metrics

# Base strategy constants (same rainy base; adaptive threshold derived later)
DCA_BASE_AMOUNT = 150.0
BASE_RAINY_AMOUNT = 150.0  # default rainy sizing before volatility scaling
RSI_THRESHOLD = 45.0       # neutral baseline threshold
CASH_ACCUMULATION = 30.0
PAYDAY_DAY_OF_MONTH_2 = 15


def generate_email_content(rsi_sma, price, cash_pool, total_contributions, rainy_buys,
                           is_simulation=False, spy_200ma=None, vix=None):
    """Generate TURBO email (subject, body) with adaptive logic."""
    today = datetime.now().date()

    # Subject marker
    turbo_marker = "[🚀 TURBO v2.0] " if not is_simulation else "[TEST - TURBO v2.0] "

    # Calculate all market metrics using centralized module
    metrics = calculate_market_metrics(price, spy_200ma, vix, rsi_sma)
    
    # Extract computed values from metrics module
    market_regime = metrics.market_regime
    adaptive_threshold = metrics.adaptive_threshold
    volatility_sizing = metrics.volatility_sizing
    vix_level = metrics.vix_level
    deviation_pct = metrics.deviation_pct
    
    # Display helpers (from metrics)
    all_metrics_dict = metrics.get_all_metrics()
    vix_display = all_metrics_dict["vix_display"]
    spy_200ma_display = all_metrics_dict["spy_200ma_display"]
    ma_plus_5_display = all_metrics_dict["ma_plus_5_display"]
    ma_minus_5_display = all_metrics_dict["ma_minus_5_display"]
    deviation_display = all_metrics_dict["deviation_display"]
    vix_level_display = all_metrics_dict["vix_level_display"]
    regime_emoji = metrics.regime_emoji
    
    # Get regime-based checkmarks (from module calculations)
    # REGIME factor: Always provides context, checkmark shows what threshold is active
    regime_provides_threshold = True  # Regime always sets the threshold
    regime_checkmark = "✅" if regime_provides_threshold else "❌"

    # Next payday
    if today.day < PAYDAY_DAY_OF_MONTH_2:
        next_payday_text = f"{PAYDAY_DAY_OF_MONTH_2}th of this month"
    else:
        next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
        next_payday_text = f"1st of {next_month.strftime('%B')}"

    # Core rainy (PROD baseline) evaluation
    is_rainy_prod = rsi_sma < RSI_THRESHOLD
    can_deploy_prod = cash_pool >= BASE_RAINY_AMOUNT

    # Adaptive rainy evaluation (TURBO)
    is_rainy_adaptive = rsi_sma < adaptive_threshold
    can_deploy_adaptive = cash_pool >= volatility_sizing

    # Action box (show rainy amount only when rainy & possible)
    if is_rainy_adaptive and can_deploy_adaptive:
        new_cash_pool = cash_pool - volatility_sizing + CASH_ACCUMULATION
        action_box = f"""
╔══════════════════════════════════════════════════════════════╗
║  🔥 TURBO RAINY DAY - DEPLOY ADAPTIVE CAPITAL               ║
╚══════════════════════════════════════════════════════════════╝

TODAY'S ACTION PLAN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ STEP 1: Base DCA → Invest $150 CAD
🔥 STEP 2: RAINY BUY → Deploy ${int(volatility_sizing)} CAD (adaptive)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⭐⭐⭐ ACTION REQUIRED: RAINY BUY ${int(volatility_sizing)} CAD ⭐⭐⭐

WHY? RSI SMA(7) = {rsi_sma:.2f} < {adaptive_threshold:.0f} (adaptive threshold met)
REGIME: {market_regime} | VIX: {vix_display} ({vix_level or 'Unknown'})
CASH: ${cash_pool:.2f} → ${new_cash_pool:.2f} (after buy & save)
"""
    elif is_rainy_adaptive and not can_deploy_adaptive:
        new_cash_pool = cash_pool + CASH_ACCUMULATION
        action_box = f"""
╔══════════════════════════════════════════════════════════════╗
║  ⚠️  ADAPTIVE RAINY DAY BUT INSUFFICIENT CASH              ║
╚══════════════════════════════════════════════════════════════╝

TODAY'S ACTION PLAN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ STEP 1: Base DCA → Invest $150 CAD
❌ STEP 2: NO RAINY BUY (need ${int(volatility_sizing)}, have ${cash_pool:.2f})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⭐⭐⭐ ACTION REQUIRED: BASE BUY ONLY $150 CAD ⭐⭐⭐

WHY? RSI SMA(7) = {rsi_sma:.2f} < {adaptive_threshold:.0f} but cash short
REGIME: {market_regime} | VIX: {vix_display} ({vix_level or 'Unknown'})
CASH AFTER SAVE: ${new_cash_pool:.2f}
"""
    else:
        new_cash_pool = cash_pool + CASH_ACCUMULATION
        action_box = f"""
╔══════════════════════════════════════════════════════════════╗
║  💾 STANDARD PAYDAY - BUILD CASH FOR FUTURE DIPS            ║
╚══════════════════════════════════════════════════════════════╝

TODAY'S ACTION PLAN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ STEP 1: Base DCA → Invest $150 CAD
💾 STEP 2: SAVE → Add $30 CAD to cash pool
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⭐⭐⭐ ACTION REQUIRED: BASE BUY ONLY $150 CAD ⭐⭐⭐

RSI SMA(7) = {rsi_sma:.2f} ≥ {adaptive_threshold:.0f} (no adaptive trigger)
REGIME: {market_regime} | VIX: {vix_display} ({vix_level or 'Unknown'})
CASH: ${cash_pool:.2f} → ${new_cash_pool:.2f} (after save)
"""

    # Decision table values (3 factors)
    deviation_str = deviation_display

    # Metrics markdown table (embed in email; also written to METRICS_SNAPSHOT.md by monitor)
    metrics_markdown = f"""
📌 METRICS SNAPSHOT (Markdown)
| Metric | Value |
|---|---|
| SPY Price | {all_metrics_dict['price_display']} |
| 200MA | {spy_200ma_display} |
| Deviation | {deviation_display} |
| 200MA +5% | {ma_plus_5_display} |
| 200MA -5% | {ma_minus_5_display} |
| RSI SMA(7) | {all_metrics_dict.get('rsi_sma_display', f"{rsi_sma:.2f}")} |
| VIX | {vix_display} ({vix_level_display}) |
| Market Regime | {regime_emoji} {market_regime} |
| Adaptive Threshold | {adaptive_threshold:.0f} |
| Rainy Sizing | ${int(volatility_sizing)} |
"""

    decision_table = f"""
📊 TURBO DECISION TABLE - 3-Factor System

| Factor | Today | Rule | Status |
|--------|-------|------|--------|
| **REGIME** | {regime_emoji} {market_regime} {deviation_str} | RSI < {adaptive_threshold:.0f} | {regime_checkmark} Active |
| **VOLATILITY** | VIX {vix_display} | Size ${int(volatility_sizing)} | ✅ ${int(volatility_sizing)} |
| **RSI SMA(7)** | {rsi_sma:.2f} | < {adaptive_threshold:.0f} | {'✅ Rainy' if is_rainy_adaptive else '❌ Not Rainy'} |
"""

    # Criteria explanation + 3-factor summary (restored block)
    regime_expl_line = metrics.get_regime_threshold_line()
    vix_expl_line = metrics.get_vix_sizing_line()
    rainy_trigger_line = (
        f"RSI SMA(7) {rsi_sma:.2f} < {adaptive_threshold:.0f} → Rainy ✅" if is_rainy_adaptive else f"RSI SMA(7) {rsi_sma:.2f} ≥ {adaptive_threshold:.0f} → Not Rainy ❌"
    )
    factor_rsi_result = "✅ Rainy" if is_rainy_adaptive else "❌ Not Rainy"
    factor_vix_result = f"Sizing ${int(volatility_sizing)}" if vix_level else "Sizing $150"

    criteria_block = f"""
🔬 CRITERIA EXPLANATION (Adaptive Rainy System)
• Regime shifts threshold (selective bull / aggressive bear)
• VIX scales deployment (fear = opportunity)
• RSI SMA(7) confirms sustained weakness (smoothed noise)
• Cash discipline: Only deploy if cash_pool ≥ rainy amount

CURRENT SNAPSHOT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SPY Price: ${price:.2f}
200MA: {spy_200ma_display}
Deviation: {deviation_display}
200MA +5%: {ma_plus_5_display}
200MA -5%: {ma_minus_5_display}
RSI SMA(7): {rsi_sma:.2f}
VIX: {vix_display} ({vix_level_display})

Market Regime: {regime_emoji} {market_regime}
   → {regime_expl_line}

VIX Fear Index: {vix_display} ({vix_level_display} volatility)
   → {vix_expl_line}

Adaptive RSI Threshold: {adaptive_threshold:.0f}
   → {rainy_trigger_line}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 3-FACTOR SYSTEM SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Factor | Value | Calculation | Result |
|--------|-------|-------------|--------|
| **1. REGIME** | {regime_emoji} {market_regime} {deviation_display} | SPY ${price:.2f} vs 200MA {spy_200ma_display} | ✅ Threshold {adaptive_threshold:.0f} |
| **2. VOLATILITY** | VIX {vix_display} ({vix_level_display}) | {vix_expl_line} | ✅ ${int(volatility_sizing)} |
| **3. RSI SMA(7)** | {rsi_sma:.2f} | Must be < {adaptive_threshold:.0f} | {factor_rsi_result} |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    # Initial cash pool explanatory note
    initial_note = ""
    if total_contributions == 0:
        initial_note = f"\n   📌 NOTE: Starting with ${cash_pool:.2f} initial cash pool (enough for 2 rainy buys)"

    # Subject
    if is_simulation:
        subject = f"{turbo_marker}🧪 TEST EMAIL (Local Run): TURBO Metrics - {today.strftime('%B %d, %Y')}"
    else:
        subject = f"{turbo_marker}📅 PAYDAY: TURBO Metrics - {today.strftime('%B %d, %Y')}"

    # Headers
    if is_simulation:
        header_suffix = " - TEST EMAIL (LOCAL RUN)"
        date_suffix = " 🧪"
        test_notice = "\n🧪 THIS IS A TEST EMAIL (TURBO)\nManual local run with FORCE_EMAIL=true.\n"
    else:
        header_suffix = " - PAYDAY"
        date_suffix = ""
        test_notice = ""

    body = f"""
🚀 TURBO v2.0 - ADAPTIVE RSI SYSTEM{header_suffix}
{test_notice}════════════════════════════════════════════════════════════════
📅 DATE: {today.strftime('%B %d, %Y')}{date_suffix}
════════════════════════════════════════════════════════════════

{criteria_block}
{metrics_markdown}
{decision_table}
{action_box}

📈 NEXT PAYDAY: {next_payday_text}
💡 STRATEGY: Adaptive threshold (Regime) + Vol sizing (VIX) + Smoothed RSI

RAINY DAY CRITERIA (SIMPLIFIED):
1. Evaluate RSI SMA(7) only on payday
2. Regime sets threshold (42 / 45 / 48)
3. VIX sets rainy amount (150 / 180 / 210)
4. Deploy only if cash_pool ≥ rainy amount
5. Else save $30 and wait

CURRENT STATUS:
Cash Pool: ${cash_pool:.2f}
Total Contributions: ${total_contributions:,.2f}
Rainy Buys To Date: {len(rainy_buys)}{initial_note}

📊 ATTACHED CHARTS - TURBO PERFORMANCE ANALYTICS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- strategy_comparison_prod_vs_turbo.png - PROD vs TURBO equity curves
- dashboard_interactive_turbo.png - Bloomberg-style multi-panel dashboard
- regime_performance_turbo.png - Performance by market regime (Bull/Bear/Neutral)
- monte_carlo_cash_pool_turbo.png - Cash pool risk simulation (10K scenarios)
- consecutive_rainy_heatmap_turbo.png - Rainy day clustering patterns
- yearly_prod_vs_turbo.png - Year-by-year performance comparison
- rainy_amount_over_time_prod_vs_turbo.png - Deployment sizing evolution
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    if is_simulation:
        body += "\n🧪 This is a simulated email - no production trade implied.\n"

    return subject, body
