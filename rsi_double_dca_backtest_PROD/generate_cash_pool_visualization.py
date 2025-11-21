"""
Cash Pool Accumulation Visualization
=====================================
Generates graph showing:
- Cash pool accumulation over time
- Hit/miss markers (green = rainy buy deployed, red = missed opportunity or no cash)
- RSI SMA(7) < 45 periods shown as colored bands
- Cumulative cash labels at data points
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
from strategy_config import get_strategy_config

# Load strategy configuration
strategy_config = get_strategy_config('VARIANT_2')

# Load RSI vs SMA payday analysis data
df = pd.read_csv('rsi_vs_sma_payday_analysis.csv')
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')

# Simulation variables
cash_pool = strategy_config.initial_cash_pool
cash_history = []
hit_miss_markers = []
rainy_periods = []  # For background bands

print(f"Starting cash pool: ${cash_pool:.2f}")
print(f"Strategy: {strategy_config.name}")
print(f"Threshold: {strategy_config.get_threshold_description()}")
print()

# Simulate cash pool over time
for idx, row in df.iterrows():
    date = row['date']
    rsi_sma = row['rsi_sma']
    is_rainy = row['sma_rainy']  # Boolean: True if RSI SMA(7) < 45
    
    # Record current cash pool state BEFORE payday
    cash_before = cash_pool
    
    # Check if it's a rainy day and we have enough cash
    if pd.notna(is_rainy) and is_rainy:
        # Rainy day detected
        if cash_pool >= strategy_config.rainy_extra_amount:
            # HIT: We have enough cash to deploy
            deployment = strategy_config.rainy_extra_amount
            cash_pool -= deployment
            cash_pool += strategy_config.cash_accumulation_per_payday
            hit_miss_markers.append({
                'date': date,
                'type': 'hit',
                'cash': cash_pool,
                'rsi_sma': rsi_sma
            })
        else:
            # MISS: Not enough cash
            cash_pool += strategy_config.cash_accumulation_per_payday
            hit_miss_markers.append({
                'date': date,
                'type': 'miss_no_cash',
                'cash': cash_pool,
                'rsi_sma': rsi_sma
            })
    else:
        # Not rainy, just accumulate
        cash_pool += strategy_config.cash_accumulation_per_payday
        if pd.notna(is_rainy):  # Valid data but not rainy
            hit_miss_markers.append({
                'date': date,
                'type': 'miss_not_rainy',
                'cash': cash_pool,
                'rsi_sma': rsi_sma
            })
    
    # Record cash history
    cash_history.append({
        'date': date,
        'cash_pool': cash_pool,
        'rsi_sma': rsi_sma,
        'is_rainy': is_rainy if pd.notna(is_rainy) else False
    })

# Convert to DataFrame
cash_df = pd.DataFrame(cash_history)
markers_df = pd.DataFrame(hit_miss_markers)

print(f"Total paydays: {len(cash_df)}")
print(f"Rainy days: {cash_df['is_rainy'].sum()}")
print(f"Hits: {len(markers_df[markers_df['type'] == 'hit'])}")
print(f"Misses (no cash): {len(markers_df[markers_df['type'] == 'miss_no_cash'])}")
print(f"Misses (not rainy): {len(markers_df[markers_df['type'] == 'miss_not_rainy'])}")
print()

# Create the visualization
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), sharex=True, 
                                gridspec_kw={'height_ratios': [3, 1]})

# ========== TOP PANEL: Cash Pool with Markers ==========
ax1.plot(cash_df['date'], cash_df['cash_pool'], 
         color='#2E86AB', linewidth=2, label='Cash Pool Balance', zorder=2)

# Add hit/miss markers
hits = markers_df[markers_df['type'] == 'hit']
misses_no_cash = markers_df[markers_df['type'] == 'miss_no_cash']
misses_not_rainy = markers_df[markers_df['type'] == 'miss_not_rainy']

# Green markers for hits (rainy buy deployed)
if not hits.empty:
    ax1.scatter(hits['date'], hits['cash'], 
                color='#06A77D', s=100, marker='o', 
                label=f'Hit (Rainy Buy) [{len(hits)}]', 
                zorder=5, edgecolors='white', linewidths=1.5)

# Red markers for misses (not enough cash)
if not misses_no_cash.empty:
    ax1.scatter(misses_no_cash['date'], misses_no_cash['cash'], 
                color='#D62828', s=80, marker='x', 
                label=f'Miss (No Cash) [{len(misses_no_cash)}]', 
                zorder=4, linewidths=2)

# Gray markers for non-rainy days
if not misses_not_rainy.empty:
    ax1.scatter(misses_not_rainy['date'], misses_not_rainy['cash'], 
                color='#CCCCCC', s=30, marker='.', 
                label=f'Not Rainy [{len(misses_not_rainy)}]', 
                zorder=3, alpha=0.3)

# Add cumulative cash labels (sample every 20th point to avoid clutter)
sample_indices = range(0, len(cash_df), max(1, len(cash_df) // 25))
for idx in sample_indices:
    row = cash_df.iloc[idx]
    ax1.annotate(f'${row["cash_pool"]:.0f}', 
                 xy=(row['date'], row['cash_pool']),
                 xytext=(0, 8), textcoords='offset points',
                 ha='center', fontsize=7, color='#555555',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                          edgecolor='none', alpha=0.7))

ax1.set_ylabel('Cash Pool Balance (CAD)', fontsize=12, fontweight='bold')
ax1.set_title(f'Cash Pool Accumulation Over Time\n{strategy_config.name}', 
              fontsize=14, fontweight='bold', pad=15)
ax1.legend(loc='upper left', frameon=True, fontsize=10)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.set_ylim(bottom=0)

# ========== BOTTOM PANEL: RSI SMA(7) with Rainy Bands ==========
# Plot RSI SMA(7) line
valid_rsi = cash_df.dropna(subset=['rsi_sma'])
ax2.plot(valid_rsi['date'], valid_rsi['rsi_sma'], 
         color='#6A4C93', linewidth=1.5, label='RSI SMA(7)', zorder=2)

# Add threshold line
ax2.axhline(y=strategy_config.rsi_threshold, color='#D62828', 
            linestyle='--', linewidth=2, label=f'Threshold ({strategy_config.rsi_threshold})', 
            zorder=1)

# Shade rainy periods (RSI SMA < threshold)
rainy_mask = valid_rsi['rsi_sma'] < strategy_config.rsi_threshold
rainy_dates = valid_rsi[rainy_mask]['date']
rainy_rsi = valid_rsi[rainy_mask]['rsi_sma']

# Create filled regions for rainy periods
if not rainy_dates.empty:
    ax2.fill_between(rainy_dates, 0, 100, 
                     where=(rainy_rsi < strategy_config.rsi_threshold),
                     color='#FFA69E', alpha=0.2, label='Rainy Period (RSI SMA < 45)',
                     zorder=0)

# Mark hits on RSI chart (rainy days where we deployed)
if not hits.empty:
    # Find corresponding RSI values for hit dates
    hit_rsi_data = cash_df[cash_df['date'].isin(hits['date'])]
    ax2.scatter(hit_rsi_data['date'], hit_rsi_data['rsi_sma'],
                color='#06A77D', s=80, marker='v',
                label=f'Deployed Extra ${strategy_config.rainy_extra_amount:.0f}',
                zorder=5, edgecolors='white', linewidths=1.5)

ax2.set_ylabel('RSI SMA(7)', fontsize=12, fontweight='bold')
ax2.set_xlabel('Date', fontsize=12, fontweight='bold')
ax2.set_ylim(0, 100)
ax2.legend(loc='upper left', frameon=True, fontsize=10)
ax2.grid(True, alpha=0.3, linestyle='--')

# Format x-axis for dates
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax2.xaxis.set_major_locator(mdates.YearLocator(2))
ax2.xaxis.set_minor_locator(mdates.YearLocator(1))
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

# Tight layout
plt.tight_layout()

# Save figure
output_file = 'cash_pool_analysis.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✅ Visualization saved: {output_file}")
print()

# Print summary statistics
print("=" * 60)
print("CASH POOL SIMULATION SUMMARY")
print("=" * 60)
print(f"Start date: {cash_df['date'].min().strftime('%Y-%m-%d')}")
print(f"End date: {cash_df['date'].max().strftime('%Y-%m-%d')}")
print(f"Total paydays: {len(cash_df)}")
print(f"Final cash pool: ${cash_df['cash_pool'].iloc[-1]:.2f}")
print()
print(f"Total rainy days (RSI SMA < {strategy_config.rsi_threshold}): {cash_df['is_rainy'].sum()}")
print(f"Rainy buys deployed (hits): {len(hits)}")
print(f"Rainy days missed (no cash): {len(misses_no_cash)}")
print(f"Hit rate: {len(hits) / cash_df['is_rainy'].sum() * 100:.1f}%")
print()
print(f"Min cash pool: ${cash_df['cash_pool'].min():.2f}")
print(f"Max cash pool: ${cash_df['cash_pool'].max():.2f}")
print(f"Avg cash pool: ${cash_df['cash_pool'].mean():.2f}")
print("=" * 60)
