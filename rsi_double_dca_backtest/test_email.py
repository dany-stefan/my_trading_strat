"""Quick test to send a sample email"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email settings
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "d4388707373@gmail.com",
    "sender_password": "kzuf dozw badx wwro",
    "recipient_email": "d4388707373@gmail.com",
}

def get_rsi(ticker="SPY", period=14, lookback_days=100):
    """Fetch SPY data and calculate current RSI."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days)
    
    try:
        df = yf.download(ticker, start=start_date, end=end_date, interval="1d", progress=False)
        if df.empty:
            return None, None
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        close = df["Close"] if "Close" in df.columns else df["Adj Close"]
        
        # Calculate RSI
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(period).mean()
        avg_loss = loss.rolling(period).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        current_price = close.iloc[-1]
        
        return current_rsi, current_price
    
    except Exception as e:
        print(f"Error fetching RSI: {e}")
        return None, None

def send_email(subject, body):
    """Send email notification."""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = EMAIL_CONFIG['recipient_email']
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['recipient_email'], text)
        server.quit()
        
        print(f"✅ Email sent: {subject}")
        return True
    
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

# Get current market data
print("Fetching current SPY data...")
rsi, price = get_rsi()

if rsi:
    print(f"Current SPY RSI(14): {rsi:.2f}")
    print(f"Current SPY Price: ${price:.2f}")
    print("\nSending test email...")
    
    subject = f"🧪 TEST - RSI Strategy Monitor - RSI {rsi:.2f}"
    body = f"""
RSI Cash Strategy Variant #2 - TEST EMAIL

Current Market Conditions:
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
SPY RSI(14): {rsi:.2f}
SPY Price: ${price:.2f}

Starting Cash Pool: $330.00

═══════════════════════════════════════════════════════════════════

This is a test email to verify your email configuration is working.

Your strategy will send emails on:
• 1st of each month (or next business day if weekend)
• 15th of each month (or next business day if weekend)

The email will include:
✅ Current RSI and price
✅ Your cash pool balance
✅ Clear recommendation: Buy extra $150 or skip
✅ Variant comparison table
✅ Strategy framework

Next actual payday email: December 1st, 2025

═══════════════════════════════════════════════════════════════════

Market Status: {'🔥 RAINY DAY (RSI < 45)' if rsi < 45 else '☀️ NORMAL CONDITIONS (RSI ≥ 45)'}

If today were a payday with $330 cash pool:
{'→ BUY $150 base + $150 rainy = $300 total' if rsi < 45 else '→ BUY $150 base only, save $30 to pool'}

═══════════════════════════════════════════════════════════════════

Email test successful! You're all set up.
    """
    
    if send_email(subject, body):
        print("\n✅ SUCCESS! Check your inbox.")
    else:
        print("\n❌ Email failed. Check your configuration.")
else:
    print("❌ Could not fetch market data.")
