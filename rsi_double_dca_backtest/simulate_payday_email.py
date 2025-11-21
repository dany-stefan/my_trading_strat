"""
Simulate Payday Email - Preview Email Content With HTML Formatting

This script shows exactly what your payday email will look like,
including HTML table formatting, without actually sending it.
"""

import os
import json
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from email.mime.image import MIMEImage
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================
TRACKING_FILE = "strategy_tracking.json"
INITIAL_CASH_POOL = 330.0

# Strategy parameters (Variant #2)
DCA_BASE_AMOUNT = 150.0
CASH_ACCUMULATION = 30.0
RAINY_AMOUNT = 150.0
RSI_THRESHOLD = 45
RSI_PERIOD = 14

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def get_rsi(ticker="SPY", period=14, lookback_days=100):
    """Fetch current RSI for a ticker."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days)
    
    df = yf.download(ticker, start=start_date, end=end_date, interval="1d", progress=False)
    if df.empty:
        return None, None
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    col = "Adj Close" if "Adj Close" in df.columns else "Close"
    prices = df[col].copy()
    
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    current_rsi = rsi.iloc[-1]
    current_price = prices.iloc[-1]
    
    return current_rsi, current_price

def load_tracking():
    """Load tracking data or initialize if not exists."""
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = {
            "cash_pool": INITIAL_CASH_POOL,
            "total_contributions": 0.0,
            "rainy_buys": [],
            "last_payday": None,
            "last_check": None
        }
    
    # Ensure initial cash pool is set
    if data.get("cash_pool", 0) == 0 and data.get("total_contributions", 0) == 0:
        data["cash_pool"] = INITIAL_CASH_POOL
    
    return data

def convert_to_html(text):
    """Convert plain text email to HTML with styled tables matching markdown format."""
    html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background-color: #f5f5f5;
            padding: 10px;
            line-height: 1.7;
            color: #333;
            font-size: 17px;
            -webkit-text-size-adjust: 100%;
            margin: 0;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            max-width: 100%;
            margin: 0 auto;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 4px solid #3498db;
            padding-bottom: 15px;
            font-size: 26px;
            font-weight: 700;
            margin: 20px 0 25px 0;
            line-height: 1.3;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
            border-bottom: 3px solid #34495e;
            padding-bottom: 12px;
            font-size: 21px;
            font-weight: 700;
            line-height: 1.4;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            font-size: 14px;
            table-layout: auto;
        }
        th {
            background-color: #3498db;
            color: white;
            padding: 14px 10px;
            text-align: left;
            font-weight: 600;
            border: 1px solid #2980b9;
            font-size: 14px;
            word-wrap: break-word;
        }
        td {
            padding: 12px 10px;
            border: 1px solid #ddd;
            background-color: white;
            font-size: 14px;
            word-wrap: break-word;
        }
        tr:nth-child(even) td {
            background-color: #f8f9fa;
        }
        .highlight-row td {
            background-color: #fff9e6 !important;
            font-weight: 600;
        }
        .status-box {
            background-color: #d4edda;
            border-left: 5px solid #28a745;
            padding: 18px;
            margin: 20px 0;
            border-radius: 6px;
            font-size: 17px;
        }
        .warning-box {
            background-color: #fff3cd;
            border-left: 5px solid #ffc107;
            padding: 18px;
            margin: 20px 0;
            border-radius: 6px;
            font-size: 17px;
        }
        .test-notice {
            background-color: #cce5ff;
            border: 3px solid #2196f3;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
            font-weight: bold;
            font-size: 18px;
        }
        .info-section {
            background-color: #f8f9fa;
            padding: 16px;
            border-radius: 6px;
            margin: 12px 0;
            border-left: 4px solid #6c757d;
            font-size: 16px;
            line-height: 1.6;
        }
        .divider {
            border: none;
            border-top: 4px double #34495e;
            margin: 30px 0;
            height: 4px;
        }
        p {
            margin: 14px 0;
            font-size: 17px;
            line-height: 1.6;
        }
        strong {
            color: #2c3e50;
            font-weight: 700;
        }
        em {
            font-style: italic;
            color: #555;
        }
        .section-title {
            font-size: 19px;
            font-weight: 700;
            color: #2c3e50;
            margin: 25px 0 15px 0;
            line-height: 1.4;
        }
        .number-step {
            font-size: 18px;
            font-weight: 700;
            color: #3498db;
            margin: 15px 0;
            line-height: 1.5;
        }
        @media only screen and (max-width: 600px) {
            .container {
                padding: 15px;
            }
            table {
                font-size: 13px;
            }
            th, td {
                padding: 10px 6px;
                font-size: 13px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
"""
    
    # Process the text line by line
    lines = text.split('\n')
    in_table = False
    table_headers = []
    
    for line in lines:
        # Detect test mode notice
        if '🧪 THIS IS A TEST EMAIL' in line or 'PREVIEW ONLY' in line:
            html += f'<div class="test-notice">{line}</div>\n'
        # Detect main header
        elif line.startswith('🎯 RSI STRATEGY MONITOR'):
            html += f'<h1>{line}</h1>\n'
        # Detect section dividers
        elif line.startswith('════'):
            if not in_table:
                html += '<div class="divider"></div>\n'
        # Detect ASCII table borders (ignore them)
        elif line.startswith('┌─') or line.startswith('├─') or line.startswith('└─'):
            continue
        # Detect markdown-style table header row
        elif '|' in line and ('Rank' in line or 'Variant' in line or 'Cadence' in line):
            in_table = True
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            table_headers = cells
            html += '<table>\n<thead>\n<tr>'
            for cell in cells:
                html += f'<th>{cell}</th>'
            html += '</tr>\n</thead>\n<tbody>\n'
        # Detect markdown table separator row (|-----|-----|)
        elif in_table and '|' in line and '---' in line:
            continue
        # Detect markdown table data rows
        elif in_table and '|' in line and line.strip().startswith('|'):
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            # Check if this is a highlighted row (contains stars or "YOU")
            is_highlight = '⭐' in line or 'YOU' in line or '**' in line
            row_class = ' class="highlight-row"' if is_highlight else ''
            html += f'<tr{row_class}>'
            for cell in cells:
                # Remove markdown bold markers
                cell = cell.replace('**', '')
                html += f'<td>{cell}</td>'
            html += '</tr>\n'
        # Detect end of table (empty line after table rows)
        elif in_table and not line.strip():
            html += '</tbody>\n</table>\n'
            in_table = False
            html += '<br>\n'
        # ASCII table rows with │
        elif line.startswith('│') and not in_table:
            # Skip ASCII table rows - we handle markdown tables instead
            continue
        # Regular content
        else:
            if line.strip():
                # Status boxes
                if line.startswith('🔥 RECOMMENDATION') or line.startswith('✅ RAINY'):
                    html += f'<div class="status-box"><strong>{line}</strong></div>\n'
                elif line.startswith('⚠️') or line.startswith('💰 RECOMMENDATION'):
                    html += f'<div class="warning-box"><strong>{line}</strong></div>\n'
                # Section headers with emojis
                elif line.startswith('📊') or line.startswith('📈') or line.startswith('💵'):
                    html += f'<h2>{line}</h2>\n'
                # Numbered steps (1️⃣, 2️⃣, etc.)
                elif '1️⃣' in line or '2️⃣' in line or '3️⃣' in line:
                    html += f'<p class="number-step">{line}</p>\n'
                # Info sections (bullet points)
                elif line.startswith('•'):
                    # Make text after colon bold
                    if ':' in line:
                        parts = line.split(':', 1)
                        html += f'<div class="info-section"><strong>{parts[0]}:</strong> {parts[1]}</div>\n'
                    else:
                        html += f'<div class="info-section">{line}</div>\n'
                # Numbered lists
                elif len(line) > 2 and line[0].isdigit() and line[1] == '.':
                    html += f'<div class="info-section">{line}</div>\n'
                # Key Metrics or special labels
                elif line.startswith('Key Metrics:') or line.startswith('Your Choice') or line.startswith('Expected Long-Term'):
                    html += f'<p class="section-title">{line}</p>\n'
                # Lines with checkmarks
                elif line.startswith('✅') or line.startswith('✔️'):
                    html += f'<p><strong>{line}</strong></p>\n'
                # Regular paragraphs - check for inline formatting
                else:
                    # Convert markdown-style bold (**text**) to HTML
                    formatted_line = line
                    import re
                    # Bold: **text** -> <strong>text</strong>
                    formatted_line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', formatted_line)
                    # Italic: *text* -> <em>text</em> (single asterisk not part of bold)
                    formatted_line = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', formatted_line)
                    html += f'<p>{formatted_line}</p>\n'
            else:
                html += '<br>\n'
    
    # Close any open table
    if in_table:
        html += '</tbody>\n</table>\n'
    
    html += """
    </div>
</body>
</html>
"""
    
    return html

# =============================================================================
# MAIN SIMULATION
# =============================================================================
def main():
    print("=" * 80)
    print("SIMULATED PAYDAY EMAIL PREVIEW - November 21, 2025")
    print("=" * 80)
    print("\nFetching current market data...")
    
    # Fetch current market data
    rsi, price = get_rsi("SPY", RSI_PERIOD)
    
    if rsi is None:
        print("❌ Error: Could not fetch RSI data")
        return
    
    print(f"✅ Current SPY RSI(14): {rsi:.2f}")
    print(f"✅ Current SPY Price: ${price:.2f}")
    
    # Load tracking
    tracking = load_tracking()
    cash_pool = tracking.get("cash_pool", INITIAL_CASH_POOL)
    total_contributions = tracking.get("total_contributions", 0.0)
    rainy_buys = tracking.get("rainy_buys", [])
    
    print(f"✅ Current cash pool: ${cash_pool:.2f}")
    print(f"✅ Total contributions to date: ${total_contributions:,.2f}")
    print(f"✅ Total rainy buys to date: {len(rainy_buys)}\n")
    
    # Simulate payday
    today = datetime.now()
    simulated_payday_date = today.strftime("%B %d, %Y")
    
    # Determine next payday (for email)
    if today.day < 15:
        next_payday_text = "15th of this month"
    else:
        next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
        next_payday_text = f"1st of {next_month.strftime('%B')}"
    
    # Check if rainy day
    is_rainy = rsi < RSI_THRESHOLD
    can_deploy = cash_pool >= RAINY_AMOUNT
    
    # Build email subject
    subject = f"📅 PAYDAY SIMULATION: Investment Metrics - {simulated_payday_date}"
    
    # Determine recommendation
    if is_rainy and can_deploy:
        recommendation = f"🔥 RECOMMENDATION: Buy extra ${RAINY_AMOUNT:.0f} from cash pool"
        total_investment_today = DCA_BASE_AMOUNT + RAINY_AMOUNT
        # IMPORTANT: Even on rainy days, you still save $30 to cash pool
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
        initial_note = f"\n   📌 NOTE: Starting with ${INITIAL_CASH_POOL:.2f} initial cash pool (enough for 2 rainy buys)"
    
    # Print email preview
    print("=" * 80)
    print("EMAIL SUBJECT:")
    print("=" * 80)
    print(subject)
    print("\n" + "=" * 80)
    print("EMAIL BODY:")
    print("=" * 80)
    
    email_body = f"""
════════════════════════════════════════════════════════════════════
🎯 RSI STRATEGY MONITOR - PAYDAY SIMULATION
════════════════════════════════════════════════════════════════════

Date: {simulated_payday_date} (SIMULATED)
Current SPY Price: ${price:.2f} USD
Current RSI(14): {rsi:.2f}

════════════════════════════════════════════════════════════════════

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

═══════════════════════════════════════════════════════════════════

VARIANT PERFORMANCE SUMMARY (22-year backtest)

| Variant | CAGR | Hit Rate | End Value | Total Cost |
|---------|------|----------|-----------|------------|
| #1 Weekly $150 RSI<40 | 33.54% | 68.5% | $600,967 | $104,500 |
| **#2 Bi-weekly $150 RSI<45 (YOUR PICK)** | **33.54%** | **80.0% ⭐** | **$600,907** | **$104,350** |
| #3 Weekly $100 RSI<45 | 33.54% | 65.3% | $600,679 | $104,450 |

Key Metrics:
• All 3 variants: Identical 33.54% CAGR (same long-term returns)
• Your variant (#2): HIGHEST hit rate at 80% (most sustainable)
• 22-year period: 2003-2025 (includes 2008 crash, COVID, all cycles)
• Return per $1 invested: $5.76 (every dollar becomes $5.76)

═══════════════════════════════════════════════════════════════════

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

═══════════════════════════════════════════════════════════════════

💰 PERFORMANCE VS OTHER STRATEGIES

Your Strategy vs Alternatives (22 years: 2003-2025):

| Strategy | CAGR | Final Value | Total Invested | Profit | vs Your Strategy |
|----------|------|-------------|----------------|--------|------------------|
| **YOUR RAINY DAY (Variant #2)** | **33.54%** | **$600,907** | **$104,350** | **$496,557** | **BASELINE** |
| Simple DCA (No Rainy) | 32.48% | $503,343 | $87,550 | $415,793 | **-$97,564** ⚠️ |
| Buy & Hold (Lump Sum) | 31.12% | $450,234 | $87,550 | $362,684 | **-$133,873** ⚠️ |

📈 WHAT YOU GAINED BY CHOOSING THIS STRATEGY:

• **vs Simple DCA**: You gained an extra **$97,564** (+19.4% more wealth!)
  - Cost: Only $16,800 extra deployed during crashes
  - Return on rainy capital: 581% (every rainy $1 became $6.81)
  
• **vs Buy & Hold**: You gained an extra **$133,873** (+26.5% more wealth!)
  - DCA smoothed your entry prices over 22 years
  - Rainy buys captured crash discounts (2008, 2020, etc.)
  
• **Key Advantage**: Same contributions as simple DCA ($150 bi-weekly)
  - You just deployed the $30 savings SMARTER (during RSI < 45)
  - Hit rate: 80% success rate on rainy deployments
  - No timing skill needed - just follow RSI on payday

📊 **See attached charts:**
- strategy_comparison_with_baseline.png - Growth curves comparison
- rainy_day_analysis_detailed.png - Hit/miss pattern & cash pool
- spy_price_rainy_periods_drawdown.png - When you bought during crashes

═══════════════════════════════════════════════════════════════════

WHY YOU CHOSE VARIANT #2 (Reminder)

Top 3 Variants Comparison:

| Rank | Cadence | Amount | RSI | CAGR | Hit Rate | Why NOT |
|------|---------|--------|-----|------|----------|---------|
| #1 | Weekly Every Mon | $150 | < 40 | 33.54% | 68.5% | Must check weekly |
| **#2 ✅ (YOU)** | **Bi-weekly Payday 1st & 15th** | **$150** | **< 45** | **33.54%** | **80.0%** | **PAYDAY ALIGNED SIMPLE!** |
| #3 | Weekly Every Mon | $100 | < 45 | 33.54% | 65.3% | Smaller position |

Your Choice = #2 Because:
✅ Only check RSI when you get paid (easier schedule)
✅ Highest hit rate (80% vs 68.5% and 65.3%)
✅ Same returns as #1 and #3 (33.54% CAGR)
✅ Best for busy people with paychecks

═══════════════════════════════════════════════════════════════════

CURRENT STATUS

Cash Pool: ${cash_pool:.2f}
Total Contributions to Date: ${total_contributions:,.2f}
Total Rainy Buys to Date: {len(rainy_buys)}{initial_note}

Expected Long-Term Results (22 years):
• CAGR: 33.54%
• Final Equity: $600,907
• Total Invested: $104,350
• Successful Rainy Buys: 112 / 140 opportunities (80%)

═══════════════════════════════════════════════════════════════════

This is a SIMULATED email for testing purposes.
Actual payday emails will be sent on the 1st and 15th of each month.

════════════════════════════════════════════════════════════════════
"""
    
    # Print plain text version
    print(email_body)
    print("\n" + "=" * 80)
    print("✅ EMAIL PREVIEW COMPLETE (Plain Text Version)")
    print("=" * 80)
    
    # Generate and save HTML version
    html_body = convert_to_html(email_body)
    html_file = "simulated_email_preview.html"
    with open(html_file, 'w') as f:
        f.write(html_body)
    
    print(f"\n📧 HTML email preview saved to: {html_file}")
    print("   Open this file in your browser to see the formatted email!\n")
    print("=" * 80)
    print("This is what you'll receive on the 1st and 15th of each month!")
    print("The actual email will be sent via GitHub Actions workflow.\n")

if __name__ == "__main__":
    main()
