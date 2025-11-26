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
from rsi_indicators import compute_rsi_with_sma


def update_verification_list(verification_file_path=None, trigger_source=None):
    """
    Update RSI_VERIFICATION_LIST.txt with missing dates AND update pending matches.
    
    This function:
    1. Adds new entries for any missing dates (with TBD for TradingView values)
    2. Updates pending entries (⏳) by checking if Local matches TradingView values
    
    Args:
        verification_file_path: Path to RSI_VERIFICATION_LIST.txt
                               (defaults to ../RSI_VERIFICATION_LIST.txt)
        trigger_source: String describing what triggered the update
                       (e.g., "Daily RSI Workflow (Auto)", "Bi-weekly Email (Manual)", "Local ZIP Script")
    
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
    
    # Find the "Last Updated" line to replace
    lines = content.split('\n')
    last_updated_idx = None
    for idx, line in enumerate(lines):
        if line.strip().startswith('Last Updated:'):
            last_updated_idx = idx
            break
    
    # Update the "Last Updated" line
    if trigger_source is None:
        trigger_source = "Manual Execution"
    
    update_time = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p EST')
    new_last_updated_line = f"Last Updated: {update_time} | Trigger: {trigger_source}"
    
    if last_updated_idx is not None:
        lines[last_updated_idx] = new_last_updated_line
    else:
        # If no "Last Updated" line exists, add it after the header
        for idx, line in enumerate(lines):
            if 'MATCH VERIFICATION:' in line:
                lines.insert(idx + 1, new_last_updated_line)
                lines.insert(idx + 2, '')  # Add blank line
                break
    
    # STEP 1: Update pending matches (⏳) - check if Local values match TradingView
    pending_updates = 0
    for idx, line in enumerate(lines):
        # Look for lines with pending match status (⏳)
        if '⏳' in line and line.strip() and line[0:4].isdigit():
            try:
                parts = line.split()
                if len(parts) >= 7:
                    date_str = parts[0]
                    local_rsi = float(parts[1])
                    local_sma = float(parts[2])
                    tv_rsi = parts[3]
                    tv_sma = parts[4]
                    
                    # Check if TradingView values are no longer TBD
                    if tv_rsi != 'TBD' and tv_sma != 'TBD':
                        tv_rsi_val = float(tv_rsi)
                        tv_sma_val = float(tv_sma)
                        
                        # Check if values match (within 1.0 tolerance)
                        rsi_match = abs(local_rsi - tv_rsi_val) <= 1.0
                        sma_match = abs(local_sma - tv_sma_val) <= 1.0
                        
                        if rsi_match and sma_match:
                            # Update to ✅ (match)
                            updated_line = line.replace('⏳', '✅')
                            lines[idx] = updated_line
                            pending_updates += 1
                            print(f"✅ Updated {date_str}: Local={local_rsi:.2f}/{local_sma:.2f} matches TV={tv_rsi_val:.2f}/{tv_sma_val:.2f}")
                        else:
                            # Update to ❌ (mismatch)
                            updated_line = line.replace('⏳', '❌')
                            lines[idx] = updated_line
                            pending_updates += 1
                            print(f"❌ Mismatch {date_str}: Local={local_rsi:.2f}/{local_sma:.2f} vs TV={tv_rsi_val:.2f}/{tv_sma_val:.2f}")
            except (ValueError, IndexError):
                continue
    
    # Write file if we updated any pending matches (before checking for new entries)
    if pending_updates > 0:
        print(f"📝 Updated {pending_updates} pending match status(es)")
        updated_content = '\n'.join(lines)
        with open(verification_file_path, 'w') as f:
            f.write(updated_content)
    
    # STEP 2: Add new entries (existing logic)
    # Find the last (most recent) date entry - NOW AT TOP after header
    # Use 'lines' which has the pending updates applied
    first_date = None
    first_date_line_idx = None
    header_end_idx = None
    
    # Find where data entries start (after "VERIFICATION ENTRIES:" header)
    for idx, line in enumerate(lines):
        if 'VERIFICATION ENTRIES:' in line:
            header_end_idx = idx + 2  # Skip header and separator line
            break
    
    if header_end_idx is None:
        print("❌ Could not find VERIFICATION ENTRIES header")
        return 0
    
    # Find first date entry (most recent, since file is reversed)
    for idx in range(header_end_idx, len(lines)):
        line = lines[idx]
        # Look for date pattern: YYYY-MM-DD at start of line
        if line.strip() and line[0:4].isdigit() and '-' in line[0:10]:
            try:
                date_str = line.split()[0]
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                first_date = date_obj
                first_date_line_idx = idx
                break  # Found the most recent date (at top)
            except:
                continue
    
    if first_date is None:
        print("❌ Could not find any date entries in verification file")
        return 0
    
    print(f"📅 Last verification entry: {first_date.strftime('%Y-%m-%d')}")
    
    # Calculate dates to add (from day after first_date to today)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    if first_date.date() >= today.date():
        print("✅ Verification list is already up to date")
        return 0
    
    # Fetch market data - need extra days for RSI calculation
    # Start 30 days before to ensure we have enough data for RSI(14) + SMA(7)
    start_date = first_date - timedelta(days=30)
    end_date = datetime.now()  # Use current datetime to include today's data if available
    
    print(f"📊 Fetching market data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
    
    try:
        df = yf.download('SPY', start=start_date, end=end_date, interval='1d', progress=False)
        
        if df.empty:
            print("⚠️  No new market data available")
            return 0
        
        # Handle multi-index columns from yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Calculate indicators using shared module (SINGLE SOURCE OF TRUTH)
        close = df['Adj Close'] if 'Adj Close' in df.columns else df['Close']
        df['RSI'], df['RSI_SMA_7'] = compute_rsi_with_sma(close, rsi_period=14, sma_period=7)
        
        # Keep original dataframe before filtering
        df_original = df.copy()
        
        # Filter to only valid dates (where we have RSI SMA calculated)
        df = df.dropna(subset=['RSI_SMA_7'])
        
        # Only keep dates AFTER first_date (don't duplicate)
        df = df[df.index > first_date]
        
        if df.empty:
            # Check if this is because we're already up to date or because data isn't available yet
            last_market_date = df_original.index.max() if not df_original.empty else None
            if last_market_date and last_market_date.date() <= first_date.date():
                print(f"⏳ No new market data available yet (last: {last_market_date.strftime('%Y-%m-%d')})")
                print(f"   Current verification up to: {first_date.strftime('%Y-%m-%d')}")
                print(f"   Market data typically available after 5 PM EST")
            else:
                print("✅ No new entries to add (all dates up to date)")
            return 0
        
        # Insert at top of data section (right after header, at first_date_line_idx)
        insert_idx = first_date_line_idx
        
        # Generate new entries (in REVERSE order so newest is at top)
        new_entries = []
        for date, row in reversed(list(df.iterrows())):  # Reverse to put newest first
            date_str = date.strftime('%Y-%m-%d')
            rsi = float(row['RSI'])
            rsi_sma = float(row['RSI_SMA_7'])
            
            # Determine if it's a rainy day
            is_rainy = rsi_sma < 45.0
            rainy_status = "YES" if is_rainy else "NO"
            
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
            marker_text = ', '.join(markers) if markers else ""
            
            # Format entry in dual-source format:
            # Date            Local-RSI  Local-SMA  TV-RSI   TV-SMA   Match    Rainy?   Note
            # 2025-11-25        53.83      43.49    TBD      TBD      ⏳       YES      
            entry = f"{date_str}        {rsi:5.2f}      {rsi_sma:5.2f}    TBD      TBD      ⏳       {rainy_status:8s} {marker_text}"
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
