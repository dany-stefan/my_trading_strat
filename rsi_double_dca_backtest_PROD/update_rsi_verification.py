"""
RSI Verification List Updater
==============================

Updates RSI_VERIFICATION_LIST.txt with missing dates from the last entry to today.
Called by monitor_strategy.py to keep verification list current.

Now includes automatic TradingView (Alpha Vantage) data fetching for dual-source verification.
Automatically backfills TBD entries from previous days on each run.
"""

import os
import re
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, timezone
from pathlib import Path
from rsi_indicators import compute_rsi_with_sma
from fetch_alphavantage_rsi import fetch_alphavantage_rsi, calculate_rsi_sma
from payday_scheduler import get_scheduler
from strategy_config import get_strategy_config


def update_verification_list(verification_file_path=None, trigger_source=None):
    """
    Update RSI_VERIFICATION_LIST.txt with missing dates, backfill TBD values, and re-evaluate matches.
    
    This function performs a complete update workflow:
    1. Fetch Alpha Vantage data once for all operations
    2. Backfill any TBD entries from previous days with Alpha Vantage data
    3. Re-evaluate all pending match statuses (⏳ → ✅/❌)
    4. Add new entries for any missing dates (with Alpha Vantage data if available)
    
    Args:
        verification_file_path: Path to RSI_VERIFICATION_LIST.txt
                               (defaults to ../RSI_VERIFICATION_LIST.txt)
        trigger_source: String describing what triggered the update
                       (e.g., "Daily RSI Workflow (Auto)", "Bi-weekly Email (Manual)", "Local ZIP Script")
    
    Returns:
        int: Number of new entries added
    """
    # Initialize payday scheduler for marking execution days
    strategy_config = get_strategy_config('VARIANT_2')
    payday_scheduler = get_scheduler(
        scheduler_type='BIWEEKLY_TSX',
        days=list(strategy_config.payday_days),
        exchange=strategy_config.trading_exchange
    )
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
    
    # Convert to EST (UTC-5)
    from datetime import timezone, timedelta
    est = timezone(timedelta(hours=-5))
    update_time = datetime.now(est).strftime('%Y-%m-%d %I:%M:%S %p EST')
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
    
    # STEP 1: Fetch Alpha Vantage data once for all operations
    api_key = os.environ.get('ALPHAVANTAGE_API_KEY')
    av_rsi_data = None
    av_sma_data = None
    
    if api_key:
        print("🔑 Alpha Vantage API key found - fetching most recent 12 days of external verification data...")
        try:
            av_rsi_data = fetch_alphavantage_rsi(api_key=api_key)
            if av_rsi_data:
                av_sma_data = calculate_rsi_sma(av_rsi_data)
                print(f"✅ Fetched Alpha Vantage data: {len(av_rsi_data)} RSI values, {len(av_sma_data)} SMA values")
        except Exception as e:
            print(f"⚠️  Failed to fetch Alpha Vantage data: {e}")
            print("   Will proceed without external verification")
    else:
        print("⚠️  ALPHAVANTAGE_API_KEY not set - will add entries with TBD for TV values")
    
    # STEP 2: Backfill TBD entries from previous days
    tbd_backfilled = 0
    if av_rsi_data and av_sma_data:
        print("\n🔄 Backfilling TBD entries (including today)...")
        for idx, line in enumerate(lines):
            # Look for lines with TBD values
            if 'TBD' in line and line.strip() and line[0:4].isdigit():
                try:
                    parts = re.split(r'\s{2,}', line.strip())
                    if len(parts) >= 6:
                        date_str = parts[0]
                        local_rsi = float(parts[1])
                        local_sma = float(parts[2])
                        tv_rsi = parts[3]
                        tv_sma = parts[4]
                        rainy = parts[6] if len(parts) > 6 else 'NO'
                        note = ' '.join(parts[7:]) if len(parts) > 7 else ''
                        
                        # Check if we have Alpha Vantage data for this date
                        if tv_rsi == 'TBD' and tv_sma == 'TBD':
                            if date_str in av_rsi_data and date_str in av_sma_data:
                                tv_rsi_val = av_rsi_data[date_str]
                                tv_sma_val = av_sma_data[date_str]
                                
                                # Check if values match (within 1.0 tolerance)
                                rsi_match = abs(local_rsi - tv_rsi_val) <= 1.0
                                sma_match = abs(local_sma - tv_sma_val) <= 1.0
                                
                                if rsi_match and sma_match:
                                    match_status = '✅'
                                else:
                                    match_status = '❌'
                                
                                # Reconstruct line with TV values - consistent formatting
                                new_line = f"{date_str}        {local_rsi:5.2f}      {local_sma:5.2f}    {tv_rsi_val:5.2f}    {tv_sma_val:5.2f}   {match_status}       {rainy:8}"
                                if note:
                                    new_line += f" {note}"
                                
                                lines[idx] = new_line
                                tbd_backfilled += 1
                                print(f"{match_status} Backfilled {date_str}: TV-RSI={tv_rsi_val:.2f}, TV-SMA={tv_sma_val:.2f}")
                except (ValueError, IndexError) as e:
                    continue
        
        if tbd_backfilled > 0:
            print(f"✅ Backfilled {tbd_backfilled} TBD entries")
    
    # STEP 3: Re-evaluate pending matches (⏳) after backfilling
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
                            print(f"✅ Re-evaluated {date_str}: Local={local_rsi:.2f}/{local_sma:.2f} matches TV={tv_rsi_val:.2f}/{tv_sma_val:.2f}")
                        else:
                            # Update to ❌ (mismatch)
                            updated_line = line.replace('⏳', '❌')
                            lines[idx] = updated_line
                            pending_updates += 1
                            print(f"❌ Re-evaluated {date_str}: Local={local_rsi:.2f}/{local_sma:.2f} vs TV={tv_rsi_val:.2f}/{tv_sma_val:.2f}")
            except (ValueError, IndexError):
                continue
    
    # Write file if we backfilled or updated pending matches
    if tbd_backfilled > 0 or pending_updates > 0:
        print(f"\n📝 Writing updates: {tbd_backfilled} backfilled, {pending_updates} re-evaluated")
        updated_content = '\n'.join(lines)
        with open(verification_file_path, 'w') as f:
            f.write(updated_content)
    
    # STEP 3.5: Re-evaluate most recent entry with fresh local calculations (7 PM EST workflow)
    # Always update the most recent trading day's local RSI/SMA values with fresh calculations
    todays_entry_updated = False
    
    # Use Eastern Time for date calculations (workflow runs at 7 PM EST)
    est = timezone(timedelta(hours=-5))
    now_est = datetime.now(est)
    today_date_str = now_est.strftime('%Y-%m-%d')
    
    print(f"\n🔄 Re-evaluating most recent entry with fresh local calculations (using EST: {today_date_str})...")
    
    # Fetch FULL historical data like the backtest (SINGLE SOURCE OF TRUTH)
    # RSI(14) and RSI SMA(7) need sufficient historical data for accuracy
    backtest_start_date = '2003-01-01'
    fresh_end_date = (now_est + timedelta(days=1)).strftime('%Y-%m-%d')  # Include tomorrow in case
    
    try:
        fresh_df = yf.download('SPY', start=backtest_start_date, end=fresh_end_date, interval='1d', progress=False)
        
        if not fresh_df.empty:
            # Handle multi-index columns
            if isinstance(fresh_df.columns, pd.MultiIndex):
                fresh_df.columns = fresh_df.columns.get_level_values(0)
            
            # Calculate fresh indicators using shared module (SINGLE SOURCE OF TRUTH)
            # Use same column preference as backtest (Adj Close preferred)
            close = fresh_df['Adj Close'] if 'Adj Close' in fresh_df.columns else fresh_df['Close']
            fresh_df['RSI'], fresh_df['RSI_SMA_7'] = compute_rsi_with_sma(close, rsi_period=14, sma_period=7)
            
            # Get the most recent available trading day
            if not fresh_df.empty:
                most_recent_date = fresh_df.index.max()
                most_recent_date_str = most_recent_date.strftime('%Y-%m-%d')
                
                print(f"📅 Most recent available trading day: {most_recent_date_str}")
                
                # Find and update the most recent entry
                for idx, line in enumerate(lines):
                    if line.strip() and line.startswith(most_recent_date_str):
                        try:
                            parts = re.split(r'\s{2,}', line.strip())
                            if len(parts) >= 6:
                                date_str = parts[0]
                                old_local_rsi = float(parts[1])
                                old_local_sma = float(parts[2])
                                tv_rsi_str = parts[3]
                                tv_sma_str = parts[4]
                                current_status = parts[5]
                                rainy = parts[6] if len(parts) > 6 else 'NO'
                                note = ' '.join(parts[7:]) if len(parts) > 7 else ''
                                
                                # Get fresh local values for the most recent trading day
                                recent_row = fresh_df.loc[fresh_df.index.strftime('%Y-%m-%d') == most_recent_date_str]
                                if not recent_row.empty:
                                    fresh_local_rsi = float(recent_row['RSI'].iloc[0])
                                    fresh_local_sma = float(recent_row['RSI_SMA_7'].iloc[0])
                                    
                                    # Update with fresh local calculations
                                    new_line = f"{date_str}        {fresh_local_rsi:5.2f}      {fresh_local_sma:5.2f}    {tv_rsi_str}    {tv_sma_str}   {current_status}       {rainy:8}"
                                    if note:
                                        new_line += f" {note}"
                                    
                                    lines[idx] = new_line
                                    todays_entry_updated = True
                                    
                                    # Re-evaluate match status if we have TV values
                                    if tv_rsi_str != 'TBD' and tv_sma_str != 'TBD':
                                        tv_rsi_val = float(tv_rsi_str)
                                        tv_sma_val = float(tv_sma_str)
                                        
                                        rsi_match = abs(fresh_local_rsi - tv_rsi_val) <= 1.0
                                        sma_match = abs(fresh_local_sma - tv_sma_val) <= 1.0
                                        
                                        if rsi_match and sma_match:
                                            new_status = '✅'
                                        else:
                                            new_status = '❌'
                                        
                                        # Update status if it changed
                                        if new_status != current_status:
                                            new_line = f"{date_str}        {fresh_local_rsi:5.2f}      {fresh_local_sma:5.2f}    {tv_rsi_str}    {tv_sma_str}   {new_status}       {rainy:8}"
                                            if note:
                                                new_line += f" {note}"
                                            lines[idx] = new_line
                                            print(f"🔄 Most recent entry status changed: {current_status} → {new_status} (Fresh Local={fresh_local_rsi:.2f}/{fresh_local_sma:.2f} vs TV={tv_rsi_val:.2f}/{tv_sma_val:.2f})")
                                        else:
                                            print(f"✅ Most recent entry re-verified: Still {new_status} (Fresh Local={fresh_local_rsi:.2f}/{fresh_local_sma:.2f} matches TV={tv_rsi_val:.2f}/{tv_sma_val:.2f})")
                                    else:
                                        print(f"🔄 Most recent local values updated: RSI {old_local_rsi:.2f}→{fresh_local_rsi:.2f}, SMA {old_local_sma:.2f}→{fresh_local_sma:.2f} (TV values still TBD)")
                                    
                                    break  # Found and updated the most recent entry
                        except (ValueError, IndexError) as e:
                            print(f"⚠️  Error parsing most recent entry: {e}")
                            continue
                
                if todays_entry_updated:
                    # Write the updated file with fresh local values
                    updated_content = '\n'.join(lines)
                    with open(verification_file_path, 'w') as f:
                        f.write(updated_content)
                    print("✅ Most recent entry updated with fresh local calculations")
                else:
                    print(f"ℹ️  Most recent entry ({most_recent_date_str}) not found in verification list")
            else:
                print(f"⚠️  No fresh market data available")
        else:
            print("⚠️  Could not fetch fresh market data for re-evaluation")
    except Exception as e:
        print(f"⚠️  Error fetching fresh data for re-evaluation: {e}")
    
    # STEP 4: Add new entries with Alpha Vantage data
    # Find the last (most recent) date entry - NOW AT TOP after header
    # Use 'lines' which has the pending updates applied
    first_date = None
    first_date_line_idx = None
    header_end_idx = None
    
    # Find where data entries start (after "VERIFICATION ENTRIES" header)
    for idx, line in enumerate(lines):
        if 'VERIFICATION ENTRIES' in line:
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
    
    # Calculate dates to add (from day after first_date to today) - using EST
    est = timezone(timedelta(hours=-5))
    today = datetime.now(est).replace(hour=0, minute=0, second=0, microsecond=0)
    
    if first_date.date() >= today.date():
        print("✅ Verification list is already up to date")
        # Still return total updates from backfilling/re-evaluation
        total_updates = tbd_backfilled + pending_updates + (1 if todays_entry_updated else 0)
        return total_updates
    
    # Fetch market data - MUST use FULL HISTORY to match backtest (SINGLE SOURCE OF TRUTH)
    # Backtest uses ALL data from 2003, so we must too for consistency
    backtest_start_date = '2003-01-01'
    end_date = datetime.now(est)  # Use current datetime in EST to include today's data if available
    
    print(f"📊 Fetching FULL market data from {backtest_start_date} to {end_date.strftime('%Y-%m-%d')}...")
    print(f"   (Using full history to match backtest - SINGLE SOURCE OF TRUTH)")
    
    try:
        df = yf.download('SPY', start=backtest_start_date, end=end_date, interval='1d', progress=False)
        
        if df.empty:
            print("⚠️  No new market data available")
            return 0
        
        # Handle multi-index columns from yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Calculate indicators using shared module (SINGLE SOURCE OF TRUTH)
        # IMPORTANT: Use same column preference as backtest (Adj Close preferred)
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
                # Return backfilled/re-evaluated count even if no new entries
                total_updates = tbd_backfilled + pending_updates + (1 if todays_entry_updated else 0)
                return total_updates
            else:
                print("✅ No new entries to add (all dates up to date)")
                # Return backfilled/re-evaluated count
                total_updates = tbd_backfilled + pending_updates + (1 if todays_entry_updated else 0)
                return total_updates
        
        # Insert at top of data section (right after header, at first_date_line_idx)
        insert_idx = first_date_line_idx
        
        # Generate new entries (in REVERSE order so newest is at top)
        new_entries = []
        for date, row in reversed(list(df.iterrows())):  # Reverse to put newest first
            date_str = date.strftime('%Y-%m-%d')
            rsi = float(row['RSI'])
            rsi_sma = float(row['RSI_SMA_7'])
            
            # Fetch TradingView (Alpha Vantage) values if available
            tv_rsi = "TBD"
            tv_sma = "TBD"
            match_status = "⏳"
            
            if av_rsi_data and av_sma_data:
                if date_str in av_rsi_data and date_str in av_sma_data:
                    tv_rsi_val = av_rsi_data[date_str]
                    tv_sma_val = av_sma_data[date_str]
                    
                    # Check if values match (within 1.0 tolerance)
                    rsi_match = abs(rsi - tv_rsi_val) <= 1.0
                    sma_match = abs(rsi_sma - tv_sma_val) <= 1.0
                    
                    if rsi_match and sma_match:
                        match_status = "✅"
                    else:
                        match_status = "❌"
                    
                    # Format TV values
                    tv_rsi = f"{tv_rsi_val:6.2f}"
                    tv_sma = f"{tv_sma_val:6.2f}"
            
            # Determine if it's a rainy day
            is_rainy = rsi_sma < 45.0
            rainy_status = "YES" if is_rainy else "NO"
            
            # Check day markers using payday scheduler logic
            # The scheduler handles weekend/holiday rollover automatically
            markers = []
            
            # Create datetime object for the current date (at midnight EST)
            date_datetime = datetime.combine(date.date(), datetime.min.time()).replace(tzinfo=timezone(timedelta(hours=-5)))
            
            # Helper function to check if a target date rolled to the current date
            def rolled_to_current(target_day):
                """Check if target_day (e.g., 1, 3, 15, 17) rolled to current date due to weekend/holiday."""
                try:
                    target_date = date_datetime.replace(day=target_day)
                    actual_date = payday_scheduler._get_actual_payday(target_date)
                    return date_datetime.date() == actual_date.date()
                except ValueError:
                    return False
            
            # Payday markers (1st and 15th)
            if rolled_to_current(1):
                markers.append("Payday 1st")
            if rolled_to_current(15):
                markers.append("Payday 15th")
            
            # Deployment day markers (3rd and 17th)
            if rolled_to_current(3):
                markers.append("Deploy 3rd")
            if rolled_to_current(17):
                markers.append("Deploy 17th")
            
            # Combine markers
            marker_text = ', '.join(markers) if markers else ""
            
            # Format entry in dual-source format with TV values if available - consistent formatting:
            # Date            Local-RSI  Local-SMA  TV-RSI   TV-SMA   Match    Rainy?   Note
            if tv_rsi == "TBD":
                entry = f"{date_str}        {rsi:5.2f}      {rsi_sma:5.2f}    TBD      TBD      ⏳       {rainy_status:8s} {marker_text}"
            else:
                entry = f"{date_str}        {rsi:5.2f}      {rsi_sma:5.2f}    {tv_rsi_val:5.2f}    {tv_sma_val:5.2f}   {match_status}       {rainy_status:8s} {marker_text}"
            
            new_entries.append(entry)
        
        if not new_entries:
            # Check if we had any updates from backfilling or re-evaluation
            total_updates = tbd_backfilled + pending_updates + (1 if todays_entry_updated else 0)
            if total_updates > 0:
                print(f"✅ No new entries added, but {total_updates} entries were updated (backfilled/re-evaluated)")
            else:
                print("✅ No new entries to add")
            return total_updates
        
        # Insert new entries
        lines[insert_idx:insert_idx] = new_entries
        
        # Write updated content
        updated_content = '\n'.join(lines)
        with open(verification_file_path, 'w') as f:
            f.write(updated_content)
        
        print(f"✅ Added {len(new_entries)} new verification entries")
        for entry in new_entries:
            print(f"   {entry}")
        
        # Return total updates: backfilled + re-evaluated + today's fresh update
        total_updates = len(new_entries) + tbd_backfilled + pending_updates + (1 if todays_entry_updated else 0)
        return total_updates
        
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
