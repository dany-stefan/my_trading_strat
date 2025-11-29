"""
Generate comprehensive visualizations for rainy period analysis.

This script creates multiple charts showing:
1. Rainy periods timeline with number of deployments
2. Return on investment by rainy period
3. Amount invested vs current value by period
4. SPY price during rainy deployments
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import yfinance as yf
from datetime import datetime
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']

def load_rainy_data():
    """Load and prepare rainy buys data with SPY prices."""
    rainy_buys = pd.read_csv('rainy_buys_calendar_dates.csv')
    rainy_buys['date'] = pd.to_datetime(rainy_buys['date'])
    
    # Get SPY prices
    spy = yf.Ticker('SPY')
    hist = spy.history(start='2003-10-01', end='2025-11-22')
    
    rainy_buys['spy_price'] = rainy_buys['date'].apply(
        lambda d: hist.loc[hist.index.date == d.date(), 'Close'].values[0] 
        if len(hist.loc[hist.index.date == d.date()]) > 0 
        else None
    )
    
    current_spy = float(hist.iloc[-1]['Close'])
    rainy_buys['shares_bought'] = rainy_buys['amount'] / rainy_buys['spy_price']
    rainy_buys['current_value'] = rainy_buys['shares_bought'] * current_spy
    rainy_buys['year'] = rainy_buys['date'].dt.year
    
    return rainy_buys, current_spy, hist

def create_rainy_periods_timeline(rainy_buys, current_spy):
    """Chart 1: Timeline showing rainy periods with deployment counts."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), sharex=True)
    
    # Group by year
    yearly = rainy_buys.groupby('year').agg({
        'amount': 'sum',
        'spy_price': 'mean',
        'shares_bought': 'sum',
        'current_value': 'sum',
        'date': ['min', 'max', 'count']
    })
    yearly.columns = ['total_invested', 'avg_price', 'total_shares', 'current_value', 
                      'start_date', 'end_date', 'num_buys']
    yearly['gain'] = yearly['current_value'] - yearly['total_invested']
    yearly['return_pct'] = (yearly['gain'] / yearly['total_invested']) * 100
    yearly['period_days'] = (yearly['end_date'] - yearly['start_date']).dt.days
    
    # Top chart: Number of deployments per period
    years = yearly.index.tolist()
    num_buys = yearly['num_buys'].tolist()
    
    colors_map = plt.cm.viridis(np.linspace(0, 1, len(years)))
    bars1 = ax1.bar(years, num_buys, color=colors_map, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for i, (year, count) in enumerate(zip(years, num_buys)):
        ax1.text(year, count + 0.2, str(int(count)), ha='center', va='bottom', 
                fontweight='bold', fontsize=10)
    
    ax1.set_ylabel('Number of Rainy Deployments', fontsize=13, fontweight='bold')
    ax1.set_title('📅 RAINY PERIODS: Deployment Frequency (2004-2025)', 
                  fontsize=16, fontweight='bold', pad=20)
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_ylim(0, max(num_buys) + 1)
    
    # Bottom chart: Period duration (days)
    period_days = yearly['period_days'].tolist()
    bars2 = ax2.bar(years, period_days, color=colors_map, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Add value labels
    for i, (year, days) in enumerate(zip(years, period_days)):
        ax2.text(year, days + 10, f'{int(days)}d', ha='center', va='bottom', 
                fontweight='bold', fontsize=9)
    
    ax2.set_xlabel('Year', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Period Duration (Days)', fontsize=13, fontweight='bold')
    ax2.set_title('⏱️ Duration of Each Rainy Period', fontsize=14, fontweight='bold', pad=15)
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('rainy_periods_timeline.png', dpi=300, bbox_inches='tight')
    print("✅ Created: rainy_periods_timeline.png")
    plt.close()

def create_rainy_returns_chart(rainy_buys, current_spy):
    """Chart 2: Return on investment by rainy period."""
    fig, ax = plt.subplots(figsize=(16, 9))
    
    yearly = rainy_buys.groupby('year').agg({
        'amount': 'sum',
        'current_value': 'sum'
    })
    yearly['gain'] = yearly['current_value'] - yearly['amount']
    yearly['return_pct'] = (yearly['gain'] / yearly['amount']) * 100
    
    years = yearly.index.tolist()
    returns = yearly['return_pct'].tolist()
    
    # Color code by performance
    colors_bars = ['#006400' if r > 500 else '#228B22' if r > 300 else '#32CD32' if r > 100 else '#90EE90' 
                   for r in returns]
    
    bars = ax.barh(years, returns, color=colors_bars, alpha=0.85, edgecolor='black', linewidth=1.5)
    
    # Add value labels
    for i, (year, ret) in enumerate(zip(years, returns)):
        ax.text(ret + 20, year, f'{ret:.0f}%', va='center', ha='left', 
               fontweight='bold', fontsize=11)
    
    ax.set_xlabel('Return on Investment (%)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Rainy Period (Year)', fontsize=13, fontweight='bold')
    ax.set_title('💰 RETURN BY RAINY PERIOD: Each Period\'s Performance (2004-2025)', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)
    ax.invert_yaxis()
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#006400', label='Excellent (>500%)'),
        Patch(facecolor='#228B22', label='Great (300-500%)'),
        Patch(facecolor='#32CD32', label='Good (100-300%)'),
        Patch(facecolor='#90EE90', label='Building (<100%)')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=11)
    
    plt.tight_layout()
    plt.savefig('rainy_periods_returns.png', dpi=300, bbox_inches='tight')
    print("✅ Created: rainy_periods_returns.png")
    plt.close()

def create_investment_vs_value_chart(rainy_buys, current_spy):
    """Chart 3: Amount invested vs current value by period."""
    fig, ax = plt.subplots(figsize=(16, 9))
    
    yearly = rainy_buys.groupby('year').agg({
        'amount': 'sum',
        'current_value': 'sum'
    })
    
    years = yearly.index.tolist()
    invested = yearly['amount'].tolist()
    current_val = yearly['current_value'].tolist()
    
    x = np.arange(len(years))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, invested, width, label='Amount Invested', 
                   color='#FF6B6B', alpha=0.85, edgecolor='black', linewidth=1.5)
    bars2 = ax.bar(x + width/2, current_val, width, label='Current Value', 
                   color='#4ECDC4', alpha=0.85, edgecolor='black', linewidth=1.5)
    
    ax.set_xlabel('Rainy Period (Year)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Amount ($)', fontsize=13, fontweight='bold')
    ax.set_title('📊 INVESTED vs CURRENT VALUE: Growth of Each Rainy Period', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(years, rotation=45, ha='right')
    ax.legend(fontsize=12, loc='upper left')
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for i, (inv, val) in enumerate(zip(invested, current_val)):
        ax.text(i - width/2, inv + 100, f'${inv:.0f}', ha='center', va='bottom', 
               fontsize=8, rotation=90)
        ax.text(i + width/2, val + 100, f'${val:.0f}', ha='center', va='bottom', 
               fontsize=8, rotation=90)
    
    plt.tight_layout()
    plt.savefig('rainy_periods_investment_vs_value.png', dpi=300, bbox_inches='tight')
    print("✅ Created: rainy_periods_investment_vs_value.png")
    plt.close()

def create_spy_price_rainy_deployments(rainy_buys, spy_hist):
    """Chart 4: SPY price with rainy deployment markers."""
    fig, ax = plt.subplots(figsize=(18, 10))
    
    # Plot SPY price
    ax.plot(spy_hist.index, spy_hist['Close'], color='#2C3E50', linewidth=2, 
            label='SPY Price', alpha=0.7)
    
    # Mark rainy deployments
    for year in sorted(rainy_buys['year'].unique()):
        year_data = rainy_buys[rainy_buys['year'] == year]
        color_idx = year % len(colors)
        
        ax.scatter(year_data['date'], year_data['spy_price'], 
                  s=150, alpha=0.8, edgecolors='black', linewidth=2,
                  label=f'{year} ({len(year_data)} buys)', zorder=5)
    
    ax.set_xlabel('Date', fontsize=13, fontweight='bold')
    ax.set_ylabel('SPY Price ($)', fontsize=13, fontweight='bold')
    ax.set_title('🎯 SPY PRICE WITH RAINY DAY DEPLOYMENTS: Buying the Dips (2003-2025)', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.grid(alpha=0.3)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9, ncol=2)
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig('rainy_deployments_on_spy_chart.png', dpi=300, bbox_inches='tight')
    print("✅ Created: rainy_deployments_on_spy_chart.png")
    plt.close()

def create_top_bottom_periods_comparison(rainy_buys, current_spy):
    """Chart 5: Top 5 vs Bottom 5 rainy periods comparison."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    
    yearly = rainy_buys.groupby('year').agg({
        'amount': 'sum',
        'current_value': 'sum',
        'date': 'count'
    })
    yearly.columns = ['invested', 'current_value', 'num_buys']
    yearly['return_pct'] = ((yearly['current_value'] - yearly['invested']) / yearly['invested']) * 100
    yearly_sorted = yearly.sort_values('return_pct', ascending=False)
    
    # Top 5
    top5 = yearly_sorted.head(5)
    years_top = [str(y) for y in top5.index]
    returns_top = top5['return_pct'].tolist()
    
    bars1 = ax1.barh(years_top, returns_top, color='#27AE60', alpha=0.85, 
                     edgecolor='black', linewidth=2)
    
    for i, (year, ret) in enumerate(zip(years_top, returns_top)):
        ax1.text(ret + 30, i, f'{ret:.0f}%', va='center', ha='left', 
                fontweight='bold', fontsize=12)
    
    ax1.set_xlabel('Return (%)', fontsize=12, fontweight='bold')
    ax1.set_title('🏆 TOP 5 RAINY PERIODS', fontsize=14, fontweight='bold', pad=15)
    ax1.grid(axis='x', alpha=0.3)
    ax1.invert_yaxis()
    
    # Bottom 5 (Recent periods still compounding)
    bottom5 = yearly_sorted.tail(5).sort_values('return_pct', ascending=True)
    years_bottom = [str(y) for y in bottom5.index]
    returns_bottom = bottom5['return_pct'].tolist()
    
    bars2 = ax2.barh(years_bottom, returns_bottom, color='#3498DB', alpha=0.85, 
                     edgecolor='black', linewidth=2)
    
    for i, (year, ret) in enumerate(zip(years_bottom, returns_bottom)):
        ax2.text(ret + 3, i, f'{ret:.0f}%', va='center', ha='left', 
                fontweight='bold', fontsize=12)
    
    ax2.set_xlabel('Return (%)', fontsize=12, fontweight='bold')
    ax2.set_title('🔄 RECENT PERIODS (Still Compounding)', fontsize=14, fontweight='bold', pad=15)
    ax2.grid(axis='x', alpha=0.3)
    ax2.invert_yaxis()
    
    plt.suptitle('RAINY PERIOD PERFORMANCE: Best vs Most Recent', 
                 fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('rainy_periods_top_vs_recent.png', dpi=300, bbox_inches='tight')
    print("✅ Created: rainy_periods_top_vs_recent.png")
    plt.close()

def create_cumulative_rainy_value_chart(rainy_buys, current_spy):
    """Chart 6: Cumulative rainy investment value over time."""
    fig, ax = plt.subplots(figsize=(16, 9))
    
    rainy_sorted = rainy_buys.sort_values('date')
    rainy_sorted['cumulative_invested'] = rainy_sorted['amount'].cumsum()
    rainy_sorted['cumulative_value'] = rainy_sorted['current_value'].cumsum()
    
    ax.fill_between(rainy_sorted['date'], 0, rainy_sorted['cumulative_invested'], 
                     alpha=0.3, color='#E74C3C', label='Cumulative Invested')
    ax.fill_between(rainy_sorted['date'], 0, rainy_sorted['cumulative_value'], 
                     alpha=0.3, color='#27AE60', label='Current Value')
    
    ax.plot(rainy_sorted['date'], rainy_sorted['cumulative_invested'], 
            linewidth=3, color='#C0392B', linestyle='--')
    ax.plot(rainy_sorted['date'], rainy_sorted['cumulative_value'], 
            linewidth=3, color='#229954')
    
    ax.set_xlabel('Date', fontsize=13, fontweight='bold')
    ax.set_ylabel('Value ($)', fontsize=13, fontweight='bold')
    ax.set_title('📈 CUMULATIVE RAINY DAY VALUE: Growth Over Time (2004-2025)', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.legend(fontsize=12, loc='upper left')
    ax.grid(alpha=0.3)
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    plt.xticks(rotation=45)
    
    # Add annotations
    final_invested = rainy_sorted['cumulative_invested'].iloc[-1]
    final_value = rainy_sorted['cumulative_value'].iloc[-1]
    gain = final_value - final_invested
    
    ax.text(0.98, 0.95, f'Total Invested: ${final_invested:,.0f}', 
            transform=ax.transAxes, ha='right', va='top',
            bbox=dict(boxstyle='round', facecolor='#E74C3C', alpha=0.7),
            fontsize=11, fontweight='bold', color='white')
    ax.text(0.98, 0.88, f'Current Value: ${final_value:,.0f}', 
            transform=ax.transAxes, ha='right', va='top',
            bbox=dict(boxstyle='round', facecolor='#27AE60', alpha=0.7),
            fontsize=11, fontweight='bold', color='white')
    ax.text(0.98, 0.81, f'Gain: ${gain:,.0f} ({(gain/final_invested)*100:.1f}%)', 
            transform=ax.transAxes, ha='right', va='top',
            bbox=dict(boxstyle='round', facecolor='#3498DB', alpha=0.7),
            fontsize=11, fontweight='bold', color='white')
    
    plt.tight_layout()
    plt.savefig('rainy_cumulative_value_over_time.png', dpi=300, bbox_inches='tight')
    print("✅ Created: rainy_cumulative_value_over_time.png")
    plt.close()

if __name__ == "__main__":
    print("=" * 70)
    print("GENERATING RAINY PERIOD ANALYSIS CHARTS")
    print("=" * 70)
    print()
    
    # Load data
    print("📊 Loading rainy buys data and SPY prices...")
    rainy_buys, current_spy, spy_hist = load_rainy_data()
    print(f"✅ Loaded {len(rainy_buys)} rainy deployments")
    print(f"✅ Current SPY price: ${current_spy:.2f}")
    print()
    
    # Generate all charts
    print("🎨 Creating visualizations...")
    print()
    
    create_rainy_periods_timeline(rainy_buys, current_spy)
    create_rainy_returns_chart(rainy_buys, current_spy)
    create_investment_vs_value_chart(rainy_buys, current_spy)
    create_spy_price_rainy_deployments(rainy_buys, spy_hist)
    create_top_bottom_periods_comparison(rainy_buys, current_spy)
    create_cumulative_rainy_value_chart(rainy_buys, current_spy)
    
    print()
    print("=" * 70)
    print("✅ ALL CHARTS GENERATED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print("Charts created:")
    print("  1. rainy_periods_timeline.png - Deployment frequency & duration")
    print("  2. rainy_periods_returns.png - Return by period (horizontal bar)")
    print("  3. rainy_periods_investment_vs_value.png - Invested vs current value")
    print("  4. rainy_deployments_on_spy_chart.png - SPY price with markers")
    print("  5. rainy_periods_top_vs_recent.png - Top 5 vs Recent 5 comparison")
    print("  6. rainy_cumulative_value_over_time.png - Cumulative growth")
