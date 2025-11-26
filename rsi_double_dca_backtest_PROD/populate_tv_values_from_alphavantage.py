#!/usr/bin/env python3
"""
Populate TradingView values in RSI_VERIFICATION_LIST.txt using Alpha Vantage API

This script:
1. Reads RSI_VERIFICATION_LIST.txt and finds all entries with TBD TV values
2. Fetches RSI data from Alpha Vantage API
3. Calculates SMA(7) from the API RSI values
4. Updates the file with real external verification data
5. Auto-verifies match status (✅/❌/⏳)
6. Respects API rate limits (25 calls/day, 5 calls/minute)

Usage:
    export ALPHAVANTAGE_API_KEY='your_api_key'
    python3 populate_tv_values_from_alphavantage.py [--dry-run] [--limit N]

Options:
    --dry-run    Show what would be updated without making changes
    --limit N    Only update N entries (useful for testing or rate limiting)
"""

import os
import sys
import re
import time
import argparse
from datetime import datetime
from fetch_alphavantage_rsi import fetch_alphavantage_rsi, calculate_rsi_sma

# File paths
RSI_FILE = '../RSI_VERIFICATION_LIST.txt'

# Tolerance for match comparison
MATCH_TOLERANCE = 1.0

# Rate limiting
RATE_LIMIT_DELAY = 12  # 5 calls per minute = 12 seconds between calls


def parse_rsi_file():
    """Parse RSI verification file and extract all entries with TBD TV values."""
    with open(RSI_FILE, 'r') as f:
        lines = f.readlines()
    
    entries_to_update = []
    
    for idx, line in enumerate(lines):
        # Match date lines with TBD TV values
        if re.match(r'^2025-\d{2}-\d{2}\s+', line) and 'TBD' in line:
            # Parse the line
            parts = re.split(r'\s{2,}', line.strip())
            if len(parts) >= 6:
                date_str = parts[0]
                local_rsi = float(parts[1])
                local_sma = float(parts[2])
                tv_rsi = parts[3]
                tv_sma = parts[4]
                
                # Only process if TV values are TBD
                if tv_rsi == 'TBD' and tv_sma == 'TBD':
                    entries_to_update.append({
                        'line_idx': idx,
                        'date': date_str,
                        'local_rsi': local_rsi,
                        'local_sma': local_sma,
                        'original_line': line
                    })
    
    return lines, entries_to_update


def update_entry_with_tv_values(entry, tv_rsi, tv_sma):
    """Update an entry with TV values and determine match status."""
    # Determine match status
    rsi_match = abs(entry['local_rsi'] - tv_rsi) <= MATCH_TOLERANCE
    sma_match = abs(entry['local_sma'] - tv_sma) <= MATCH_TOLERANCE
    
    if rsi_match and sma_match:
        match_status = '✅'
    else:
        match_status = '❌'
    
    # Parse original line to preserve format
    parts = re.split(r'\s{2,}', entry['original_line'].strip())
    
    # Reconstruct line with TV values
    rainy = parts[6] if len(parts) > 6 else 'NO'
    note = ' '.join(parts[7:]) if len(parts) > 7 else ''
    
    new_line = f"{entry['date']:14}  {entry['local_rsi']:6.2f}     {entry['local_sma']:6.2f}   {tv_rsi:6.2f}   {tv_sma:6.2f}   {match_status}       {rainy:8}"
    if note:
        new_line += f" {note}"
    
    return new_line + '\n'


def main():
    parser = argparse.ArgumentParser(description='Populate TV values from Alpha Vantage API')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be updated without making changes')
    parser.add_argument('--limit', type=int, help='Only update N entries', default=None)
    args = parser.parse_args()
    
    print("═" * 75)
    print("POPULATE TV VALUES FROM ALPHA VANTAGE API")
    print("═" * 75)
    print()
    
    # Check for API key
    api_key = os.environ.get('ALPHAVANTAGE_API_KEY')
    if not api_key:
        print("❌ ERROR: ALPHAVANTAGE_API_KEY environment variable not set")
        print("   Please set it: export ALPHAVANTAGE_API_KEY='your_api_key'")
        sys.exit(1)
    
    print(f"✅ API Key found: {api_key[:8]}...")
    print()
    
    # Parse RSI file
    print("📖 Reading RSI_VERIFICATION_LIST.txt...")
    lines, entries_to_update = parse_rsi_file()
    print(f"✅ Found {len(entries_to_update)} entries with TBD TV values")
    print()
    
    if len(entries_to_update) == 0:
        print("✅ No entries to update. All TV values already populated.")
        return
    
    # Apply limit if specified
    if args.limit:
        entries_to_update = entries_to_update[:args.limit]
        print(f"⚠️  Limiting to {args.limit} entries (--limit flag)")
        print()
    
    # Fetch RSI data from Alpha Vantage
    print("📡 Fetching RSI data from Alpha Vantage...")
    rsi_data = fetch_alphavantage_rsi(api_key=api_key)
    
    if not rsi_data:
        print("❌ ERROR: Failed to fetch RSI data from Alpha Vantage")
        sys.exit(1)
    
    print(f"✅ Fetched {len(rsi_data)} days of RSI data")
    print()
    
    # Calculate SMA
    print("🧮 Calculating RSI SMA(7)...")
    sma_data = calculate_rsi_sma(rsi_data)
    print(f"✅ Calculated SMA for {len(sma_data)} days")
    print()
    
    # Update entries
    print("🔄 Updating entries...")
    updated_count = 0
    match_count = 0
    mismatch_count = 0
    
    for i, entry in enumerate(entries_to_update):
        date_str = entry['date']
        
        # Get TV values from API
        if date_str not in rsi_data:
            print(f"⚠️  {date_str}: No API data available - skipping")
            continue
        
        if date_str not in sma_data:
            print(f"⚠️  {date_str}: No SMA data available - skipping")
            continue
        
        tv_rsi = rsi_data[date_str]
        tv_sma = sma_data[date_str]
        
        # Update the line
        new_line = update_entry_with_tv_values(entry, tv_rsi, tv_sma)
        
        # Check match status
        match_status = '✅' if '✅' in new_line else '❌'
        if match_status == '✅':
            match_count += 1
        else:
            mismatch_count += 1
        
        # Show update
        print(f"{match_status} {date_str}: RSI {entry['local_rsi']:.2f} vs {tv_rsi:.2f}, SMA {entry['local_sma']:.2f} vs {tv_sma:.2f}")
        
        # Update in lines array
        if not args.dry_run:
            lines[entry['line_idx']] = new_line
        
        updated_count += 1
        
        # Rate limiting (except for last entry)
        if i < len(entries_to_update) - 1:
            time.sleep(RATE_LIMIT_DELAY)
    
    print()
    print("─" * 75)
    print(f"📊 SUMMARY:")
    print(f"   Total entries processed: {updated_count}")
    print(f"   ✅ Matches: {match_count}")
    print(f"   ❌ Mismatches: {mismatch_count}")
    print("─" * 75)
    print()
    
    # Write back to file
    if args.dry_run:
        print("🔍 DRY RUN - No changes made to file")
    else:
        print("💾 Writing updated file...")
        with open(RSI_FILE, 'w') as f:
            f.writelines(lines)
        print("✅ File updated successfully")
    
    print()
    print("═" * 75)


if __name__ == '__main__':
    main()
