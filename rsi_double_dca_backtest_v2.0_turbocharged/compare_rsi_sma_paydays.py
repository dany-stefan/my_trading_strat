"""
Compare RSI(14) vs RSI SMA(7) rainy day signals on payday schedule
Analyzes overlap and differences on 1st and 15th of each month
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_payday_schedule(start_date, end_date):
    """Generate payday schedule (1st and 15th of each month, adjusted for weekends)."""
    paydays = []
    current = start_date
    
    while current <= end_date:
        # First payday of month (1st)
        payday1 = current.replace(day=1)
        # Adjust if weekend
        while payday1.weekday() >= 5:  # 5=Saturday, 6=Sunday
            payday1 += timedelta(days=1)
        if payday1 >= start_date and payday1 <= end_date:
            paydays.append(payday1)
        
        # Second payday of month (15th)
        payday2 = current.replace(day=15)
        # Adjust if weekend
        while payday2.weekday() >= 5:
            payday2 += timedelta(days=1)
        if payday2 >= start_date and payday2 <= end_date:
            paydays.append(payday2)
        
        # Move to next month
        next_month = current.month + 1
        next_year = current.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        current = current.replace(year=next_year, month=next_month, day=1)
    
    return sorted(set(paydays))


def analyze_rsi_overlap(ticker="SPY", start_date="2003-01-01", end_date="2025-11-21", 
                        rsi_period=14, sma_period=7, threshold=45):
    """Analyze overlap between RSI and RSI SMA rainy day signals on payday schedule."""
    
    print("=" * 80)
    print(f"RSI(14) vs RSI SMA(7) Analysis - Payday Schedule (1st & 15th)")
    print("=" * 80)
    print(f"Period: {start_date} to {end_date}")
    print(f"Threshold: < {threshold}")
    print()
    
    # Fetch data
    print("Fetching SPY data...")
    df = yf.download(ticker, start=start_date, end=end_date, interval="1d", progress=False)
    
    if df.empty:
        print("❌ No data fetched")
        return
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    close = df["Close"] if "Close" in df.columns else df["Adj Close"]
    
    # Calculate RSI
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(rsi_period).mean()
    avg_loss = loss.rolling(rsi_period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # Calculate SMA of RSI
    rsi_sma = rsi.rolling(window=sma_period).mean()
    
    # Create DataFrame with both indicators
    df_signals = pd.DataFrame({
        'close': close,
        'rsi': rsi,
        'rsi_sma': rsi_sma,
        'rsi_rainy': rsi < threshold,
        'sma_rainy': rsi_sma < threshold
    })
    
    # Get payday schedule
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    paydays = get_payday_schedule(start, end)
    
    # Filter for payday dates
    payday_data = []
    for payday in paydays:
        payday_str = payday.strftime("%Y-%m-%d")
        if payday_str in df_signals.index:
            row = df_signals.loc[payday_str]
            payday_data.append({
                'date': payday_str,
                'weekday': payday.strftime('%A'),
                'close': row['close'],
                'rsi': row['rsi'],
                'rsi_sma': row['rsi_sma'],
                'rsi_rainy': row['rsi_rainy'],
                'sma_rainy': row['sma_rainy'],
                'both_rainy': row['rsi_rainy'] and row['sma_rainy'],
                'only_rsi': row['rsi_rainy'] and not row['sma_rainy'],
                'only_sma': row['sma_rainy'] and not row['rsi_rainy'],
                'neither': not row['rsi_rainy'] and not row['sma_rainy']
            })
    
    payday_df = pd.DataFrame(payday_data)
    
    # Calculate statistics
    total_paydays = len(payday_df)
    rsi_rainy_count = payday_df['rsi_rainy'].sum()
    sma_rainy_count = payday_df['sma_rainy'].sum()
    both_rainy_count = payday_df['both_rainy'].sum()
    only_rsi_count = payday_df['only_rsi'].sum()
    only_sma_count = payday_df['only_sma'].sum()
    neither_count = payday_df['neither'].sum()
    
    # Calculate hit rates
    rsi_hit_rate = (rsi_rainy_count / total_paydays) * 100
    sma_hit_rate = (sma_rainy_count / total_paydays) * 100
    overlap_rate = (both_rainy_count / total_paydays) * 100
    
    # Print summary
    print("=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    print(f"Total Paydays Analyzed: {total_paydays}")
    print()
    
    print(f"RSI(14) < {threshold}:")
    print(f"  Count: {rsi_rainy_count}")
    print(f"  Hit Rate: {rsi_hit_rate:.2f}%")
    print()
    
    print(f"RSI SMA(7) < {threshold}:")
    print(f"  Count: {sma_rainy_count}")
    print(f"  Hit Rate: {sma_hit_rate:.2f}%")
    print()
    
    print("=" * 80)
    print("OVERLAP ANALYSIS")
    print("=" * 80)
    print(f"Both Rainy (RSI < {threshold} AND SMA < {threshold}):")
    print(f"  Count: {both_rainy_count}")
    print(f"  Percentage: {overlap_rate:.2f}%")
    print()
    
    print(f"Only RSI Rainy (RSI < {threshold} but SMA >= {threshold}):")
    print(f"  Count: {only_rsi_count}")
    print(f"  Percentage: {(only_rsi_count / total_paydays) * 100:.2f}%")
    print()
    
    print(f"Only SMA Rainy (SMA < {threshold} but RSI >= {threshold}):")
    print(f"  Count: {only_sma_count}")
    print(f"  Percentage: {(only_sma_count / total_paydays) * 100:.2f}%")
    print()
    
    print(f"Neither Rainy:")
    print(f"  Count: {neither_count}")
    print(f"  Percentage: {(neither_count / total_paydays) * 100:.2f}%")
    print()
    
    # Agreement analysis
    agreement = both_rainy_count + neither_count
    disagreement = only_rsi_count + only_sma_count
    agreement_rate = (agreement / total_paydays) * 100
    
    print("=" * 80)
    print("AGREEMENT ANALYSIS")
    print("=" * 80)
    print(f"Agreement (both agree on rainy or not rainy): {agreement} ({agreement_rate:.2f}%)")
    print(f"Disagreement (one says rainy, other doesn't): {disagreement} ({(disagreement / total_paydays) * 100:.2f}%)")
    print()
    
    # If using SMA instead of RSI
    print("=" * 80)
    print("WHAT IF YOU USED SMA INSTEAD OF RSI?")
    print("=" * 80)
    print(f"Original Hit Rate (RSI < {threshold}): {rsi_hit_rate:.2f}%")
    print(f"New Hit Rate (SMA < {threshold}): {sma_hit_rate:.2f}%")
    print(f"Difference: {sma_hit_rate - rsi_hit_rate:+.2f} percentage points")
    print()
    
    if sma_hit_rate > rsi_hit_rate:
        print(f"⬆️  SMA would trigger {sma_rainy_count - rsi_rainy_count} MORE rainy buys")
    elif sma_hit_rate < rsi_hit_rate:
        print(f"⬇️  SMA would trigger {rsi_rainy_count - sma_rainy_count} FEWER rainy buys")
    else:
        print("➡️  Same number of rainy buys")
    print()
    
    # Show some examples of disagreements
    print("=" * 80)
    print("EXAMPLE DISAGREEMENTS (First 10)")
    print("=" * 80)
    disagreements = payday_df[(payday_df['only_rsi']) | (payday_df['only_sma'])].head(10)
    
    if len(disagreements) > 0:
        print(f"{'Date':<12} {'Day':<10} {'RSI':<8} {'SMA':<8} {'RSI?':<10} {'SMA?':<10} {'Type'}")
        print("-" * 80)
        for _, row in disagreements.iterrows():
            signal_type = "RSI only" if row['only_rsi'] else "SMA only"
            print(f"{row['date']:<12} {row['weekday']:<10} {row['rsi']:>7.2f} {row['rsi_sma']:>7.2f} "
                  f"{'YES' if row['rsi_rainy'] else 'NO':<10} {'YES' if row['sma_rainy'] else 'NO':<10} {signal_type}")
    
    print()
    print("=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    
    if agreement_rate > 90:
        print(f"✅ High agreement ({agreement_rate:.1f}%) - Both indicators mostly agree")
    elif agreement_rate > 70:
        print(f"⚠️  Moderate agreement ({agreement_rate:.1f}%) - Some divergence")
    else:
        print(f"❌ Low agreement ({agreement_rate:.1f}%) - Significant divergence")
    
    print()
    print("For your strategy:")
    if abs(sma_hit_rate - rsi_hit_rate) < 2:
        print("→ Hit rate would be SIMILAR if you used SMA instead of RSI")
    elif sma_hit_rate > rsi_hit_rate:
        print("→ Hit rate would be HIGHER if you used SMA (more frequent buying)")
    else:
        print("→ Hit rate would be LOWER if you used SMA (less frequent buying)")
    
    return payday_df


if __name__ == "__main__":
    # Run analysis for 22-year backtest period
    df = analyze_rsi_overlap(
        ticker="SPY",
        start_date="2003-01-01",
        end_date="2025-11-21",
        rsi_period=14,
        sma_period=7,
        threshold=45
    )
    
    # Save detailed results
    if df is not None:
        output_file = "rsi_vs_sma_payday_analysis.csv"
        df.to_csv(output_file, index=False)
        print(f"\n📊 Detailed results saved to: {output_file}")
