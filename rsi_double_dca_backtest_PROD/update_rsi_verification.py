"""
RSI Verification List Updater
==============================

Updates RSI_VERIFICATION_LIST.txt with missing dates from the last entry to today.
Called by monitor_strategy.py to keep verification list current.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path


def calculate_rsi(data, period=14):
    """Calculate RSI using Wilder's smoothing (matches TradingView)"""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def update_verification_list(verification_file_path=None):
    """
    Update RSI_VERIFICATION_LIST.txt with missing dates.
    
    Args:
        verification_file_path: Path to RSI_VERIFICATION_LIST.txt
                               (defaults to ../RSI_VERIFICATION_LIST.txt)
    
    Returns:
        int: Number of new entries added
    """
    # Determine file path
    if verification_file_path is None:
        script_dir = Path(__file__).parent
        verification_file_path = script_dir.parent / "RSI_VERIFICATION_LIST.txt"
    else:
        verification_file_path = Path(verification_file_path)
    
    # Read existing file
    try:
        with open(verification_file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Verification file not found: {verification_file_path}")
        return 0
    
    # Find the last date entry
    lines = content.split('\n')
    last_date = None
    last_date_line_idx = None
    
    for idx, line in enumerate(lines):
        # Look for date pattern: YYYY-MM-DD at start of line
        if line.strip() and line[0:4].isdigit() and '-' in line[0:10]:
            try:
                date_str = line.split()[0]
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                last_date = date_obj
                last_date_line_idx = idx
            except:
                continue
    
    if last_date is None:
        print("❌ Could not find any date entries in verification file")
        return 0
    
    print(f"📅 Last verification entry: {last_date.strftime('%Y-%m-%d')}")
    
    # Calculate dates to add (from day after last_date to today)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    if last_date.date() >= today.date():
        print("✅ Verification list is already up to date")
        return 0
    
    # Fetch market data
    start_date = last_date + timedelta(days=1)
    end_date = today + timedelta(days=1)  # Include today
    
    print(f"📊 Fetching market data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
    
    try:
        df = yf.download('SPY', start=start_date, end=end_date, interval='1d', progress=False)
        
        if df.empty:
            print("⚠️  No new market data available")
            return 0
        
        # Handle multi-index columns from yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Calculate indicators
        df['RSI'] = calculate_rsi(df)
        df['RSI_SMA_7'] = df['RSI'].rolling(window=7).mean()
        
        # Filter to only valid dates (where we have RSI SMA calculated)
        df = df.dropna(subset=['RSI_SMA_7'])
        
        if df.empty:
            print("⚠️  Not enough data to calculate RSI SMA(7)")
            return 0
        
        # Find the insertion point (after last date entry, before next section)
        insert_idx = last_date_line_idx + 1
        
        # Look for the next section header (line starting with letters after the last date)
        while insert_idx < len(lines) and lines[insert_idx].strip():
            if lines[insert_idx][0:3].isalpha() and lines[insert_idx][0:3].isupper():
                break
            insert_idx += 1
        
        # Generate new entries
        new_entries = []
        for date, row in df.iterrows():
            date_str = date.strftime('%Y-%m-%d')
            rsi = float(row['RSI'])
            rsi_sma = float(row['RSI_SMA_7'])
            
            # Determine if it's a rainy day
            is_rainy = rsi_sma < 45.0
            rainy_status = "YES RAINY" if is_rainy else "NO RAINY"
            
            # Check day markers
            day_of_month = date.day
            markers = []
            
            # Payday markers (1st and 15th)
            if day_of_month == 1:
                markers.append("Payday 1st")
            elif day_of_month == 15:
                markers.append("Payday 15th")
            
            # Deployment day markers (3rd and 17th)
            if day_of_month == 3:
                markers.append("Deploy 3rd")
            elif day_of_month == 17:
                markers.append("Deploy 17th")
            
            # Combine markers
            marker_text = f" ({', '.join(markers)})" if markers else ""
            
            # Format entry
            entry = f"{date_str}        {rsi:5.2f}        {rsi_sma:5.2f}   RSI={rsi:.2f} SMA={rsi_sma:.2f} ✅    100%     {rainy_status}{marker_text}"
            new_entries.append(entry)
        
        if not new_entries:
            print("✅ No new entries to add")
            return 0
        
        # Insert new entries
        lines[insert_idx:insert_idx] = new_entries
        
        # Write updated content
        updated_content = '\n'.join(lines)
        with open(verification_file_path, 'w') as f:
            f.write(updated_content)
        
        print(f"✅ Added {len(new_entries)} new verification entries")
        for entry in new_entries:
            print(f"   {entry}")
        
        return len(new_entries)
        
    except Exception as e:
        print(f"❌ Error updating verification list: {e}")
        return 0


if __name__ == "__main__":
    # Standalone execution
    print("═" * 75)
    print("RSI VERIFICATION LIST UPDATER")
    print("═" * 75)
    print()
    
    count = update_verification_list()
    
    print()
    print("═" * 75)
    if count > 0:
        print(f"✅ Successfully added {count} entries")
    else:
        print("✅ No updates needed")
    print("═" * 75)
