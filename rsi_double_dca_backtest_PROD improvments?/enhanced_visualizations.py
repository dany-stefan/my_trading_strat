"""
Enhanced Visualization Suite
============================

Professional-grade charts inspired by:
- Bloomberg Terminal
- TradingView
- Portfolio Visualizer
- Quantopian

New visualizations:
1. Interactive performance dashboard
2. Regime-based performance breakdown
3. Monte Carlo cash pool simulation
4. Consecutive rainy day heatmap
5. RSI distribution analysis
6. Drawdown comparison chart
7. Rolling performance metrics
8. Opportunity cost analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle
import seaborn as sns
from datetime import datetime, timedelta
from typing import Tuple, List, Optional
import warnings
warnings.filterwarnings('ignore')

# Set professional style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Color scheme (Bloomberg-inspired)
COLORS = {
    'primary': '#00A4E4',      # Sky blue
    'secondary': '#FF6B35',    # Coral
    'success': '#00D9A3',      # Mint green
    'danger': '#FF3B3F',       # Red
    'warning': '#FFA400',      # Orange
    'dark': '#1E2224',         # Dark gray
    'light': '#E8EAED',        # Light gray
    'bull': '#26A69A',         # Teal (bull market)
    'bear': '#EF5350',         # Red (bear market)
    'neutral': '#78909C',      # Blue-gray (sideways)
}


def create_interactive_dashboard(
    equity_df: pd.DataFrame,
    rainy_buys_df: pd.DataFrame,
    cash_pool_df: pd.DataFrame,
    output_path: str = "dashboard_interactive.png"
):
    """
    Create comprehensive performance dashboard.
    
    Layout:
    - Top: Equity curve with rainy day markers
    - Middle Left: Cash pool evolution with hit/miss markers
    - Middle Right: Rolling Sharpe ratio
    - Bottom: RSI timeline with rainy periods highlighted
    """
    fig = plt.figure(figsize=(20, 14))
    gs = GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.25)
    
    # === Panel 1: Equity Curve (Full Width) ===
    ax1 = fig.add_subplot(gs[0, :])
    
    ax1.plot(equity_df.index, equity_df['equity'], 
             linewidth=2.5, color=COLORS['primary'], label='Portfolio Value')
    ax1.fill_between(equity_df.index, 0, equity_df['equity'], 
                      alpha=0.1, color=COLORS['primary'])
    
    # Mark rainy day buys
    for _, row in rainy_buys_df.iterrows():
        ax1.axvline(row['date'], color=COLORS['success'], 
                   alpha=0.3, linewidth=1, linestyle='--')
        ax1.scatter(row['date'], equity_df.loc[row['date'], 'equity'], 
                   s=200, color=COLORS['success'], marker='^', 
                   zorder=5, edgecolors='white', linewidths=2)
    
    ax1.set_title('Portfolio Equity Curve with Rainy Day Buys', 
                 fontsize=16, fontweight='bold', pad=15)
    ax1.set_ylabel('Portfolio Value (CAD)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left', fontsize=11)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # === Panel 2: Cash Pool Evolution ===
    ax2 = fig.add_subplot(gs[1, 0])
    
    ax2.plot(cash_pool_df.index, cash_pool_df['cash_pool'], 
            linewidth=2, color=COLORS['warning'], label='Cash Pool')
    ax2.axhline(150, color=COLORS['danger'], linestyle='--', 
               linewidth=1.5, alpha=0.7, label='Min for Rainy Buy ($150)')
    ax2.fill_between(cash_pool_df.index, 0, cash_pool_df['cash_pool'], 
                     alpha=0.2, color=COLORS['warning'])
    
    # Mark successful vs missed rainy days
    for _, row in rainy_buys_df.iterrows():
        if row['cash_before'] >= 150:
            ax2.scatter(row['date'], row['cash_before'], 
                       s=150, color=COLORS['success'], marker='o', 
                       label='Hit' if _ == 0 else '', zorder=5)
        else:
            ax2.scatter(row['date'], row['cash_before'], 
                       s=150, color=COLORS['danger'], marker='x', 
                       label='Miss' if _ == 0 else '', zorder=5)
    
    ax2.set_title('Cash Pool Dynamics & Rainy Day Execution', 
                 fontsize=14, fontweight='bold')
    ax2.set_ylabel('Cash Pool (CAD)', fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='best', fontsize=10)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # === Panel 3: Rolling Sharpe Ratio ===
    ax3 = fig.add_subplot(gs[1, 1])
    
    # Calculate rolling Sharpe (252-day window)
    returns = equity_df['equity'].pct_change()
    rolling_sharpe = (returns.rolling(252).mean() / returns.rolling(252).std()) * np.sqrt(252)
    
    ax3.plot(rolling_sharpe.index, rolling_sharpe, 
            linewidth=2, color=COLORS['secondary'], label='Rolling Sharpe (1Y)')
    ax3.axhline(1.0, color=COLORS['dark'], linestyle='--', 
               linewidth=1, alpha=0.5, label='Sharpe = 1.0')
    ax3.axhline(2.0, color=COLORS['success'], linestyle='--', 
               linewidth=1, alpha=0.5, label='Sharpe = 2.0')
    ax3.fill_between(rolling_sharpe.index, 0, rolling_sharpe, 
                     where=(rolling_sharpe > 1.0), alpha=0.2, 
                     color=COLORS['success'], interpolate=True)
    
    ax3.set_title('Rolling Sharpe Ratio (Risk-Adjusted Performance)', 
                 fontsize=14, fontweight='bold')
    ax3.set_ylabel('Sharpe Ratio', fontsize=11)
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc='best', fontsize=10)
    ax3.set_ylim(-1, 4)
    
    # === Panel 4: RSI Timeline (Full Width) ===
    ax4 = fig.add_subplot(gs[2, :])
    
    # Plot RSI SMA
    rsi_df = equity_df[['rsi_sma']].copy()
    ax4.plot(rsi_df.index, rsi_df['rsi_sma'], 
            linewidth=1.5, color=COLORS['dark'], alpha=0.7, label='RSI SMA(7)')
    ax4.axhline(45, color=COLORS['danger'], linestyle='--', 
               linewidth=2, alpha=0.8, label='Rainy Threshold (45)')
    
    # Shade rainy periods
    ax4.fill_between(rsi_df.index, 0, 100, 
                    where=(rsi_df['rsi_sma'] < 45), 
                    alpha=0.15, color=COLORS['danger'], 
                    label='Rainy Periods', interpolate=True)
    
    # Mark rainy day buys
    for _, row in rainy_buys_df.iterrows():
        ax4.scatter(row['date'], row['rsi_sma'], 
                   s=100, color=COLORS['success'], marker='o', 
                   zorder=5, edgecolors='white', linewidths=1.5)
    
    ax4.set_title('RSI SMA(7) Timeline with Rainy Day Buy Points', 
                 fontsize=14, fontweight='bold')
    ax4.set_ylabel('RSI SMA(7)', fontsize=11)
    ax4.set_xlabel('Date', fontsize=11, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.legend(loc='upper right', fontsize=10)
    ax4.set_ylim(0, 100)
    
    # Format x-axis
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax4.xaxis.set_major_locator(mdates.YearLocator(2))
    
    plt.suptitle('Strategy Performance Dashboard', 
                fontsize=20, fontweight='bold', y=0.995)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Interactive dashboard saved: {output_path}")
    plt.close()


def create_regime_performance_breakdown(
    equity_df: pd.DataFrame,
    output_path: str = "regime_performance.png"
):
    """
    Show performance breakdown by market regime (bull/bear/sideways).
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Calculate 200-day MA
    equity_df['ma_200'] = equity_df['spy_price'].rolling(200).mean()
    equity_df['distance_from_ma'] = (equity_df['spy_price'] - equity_df['ma_200']) / equity_df['ma_200']
    
    # Classify regimes
    equity_df['regime'] = 'Normal'
    equity_df.loc[equity_df['distance_from_ma'] > 0.05, 'regime'] = 'Bull'
    equity_df.loc[equity_df['distance_from_ma'] < -0.05, 'regime'] = 'Bear'
    
    # Calculate returns by regime
    equity_df['returns'] = equity_df['equity'].pct_change()
    
    regime_stats = equity_df.groupby('regime').agg({
        'returns': ['mean', 'std', 'count']
    })
    regime_stats.columns = ['Mean Return', 'Volatility', 'Days']
    regime_stats['Sharpe'] = (regime_stats['Mean Return'] / regime_stats['Volatility']) * np.sqrt(252)
    regime_stats['Annualized Return'] = ((1 + regime_stats['Mean Return']) ** 252) - 1
    
    # Chart 1: Returns by regime
    regimes = ['Bull', 'Normal', 'Bear']
    colors_regime = [COLORS['bull'], COLORS['neutral'], COLORS['bear']]
    
    returns_data = [regime_stats.loc[r, 'Annualized Return'] * 100 if r in regime_stats.index else 0 
                   for r in regimes]
    
    bars = ax1.bar(regimes, returns_data, color=colors_regime, alpha=0.8, edgecolor='white', linewidth=2)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom', 
                fontsize=12, fontweight='bold')
    
    ax1.set_title('Annualized Returns by Market Regime', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Annualized Return (%)', fontsize=11)
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.axhline(0, color='black', linewidth=0.8)
    
    # Chart 2: Time distribution by regime
    days_data = [regime_stats.loc[r, 'Days'] if r in regime_stats.index else 0 
                for r in regimes]
    total_days = sum(days_data)
    percentages = [(d/total_days)*100 for d in days_data]
    
    ax2.pie(percentages, labels=regimes, colors=colors_regime, autopct='%1.1f%%',
           startangle=90, textprops={'fontsize': 12, 'fontweight': 'bold'},
           wedgeprops={'edgecolor': 'white', 'linewidth': 2})
    ax2.set_title('Time Spent in Each Market Regime', fontsize=14, fontweight='bold')
    
    plt.suptitle('Market Regime Analysis (Based on 200-Day MA)', 
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Regime performance breakdown saved: {output_path}")
    plt.close()


def create_monte_carlo_cash_pool_simulation(
    initial_pool: float = 450.0,
    accumulation: float = 40.0,
    rainy_amount: float = 150.0,
    rainy_frequency: float = 0.224,
    n_simulations: int = 1000,
    n_execution_days: int = 491,
    output_path: str = "monte_carlo_cash_pool.png"
):
    """
    Monte Carlo simulation of cash pool evolution.
    Shows probability of having sufficient funds for rainy days.
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))
    
    # Run simulations
    np.random.seed(42)
    all_paths = []
    miss_counts = []
    
    for _ in range(n_simulations):
        cash_pool = initial_pool
        path = [cash_pool]
        misses = 0
        
        for day in range(n_execution_days):
            # Add accumulation
            cash_pool += accumulation
            
            # Check if rainy day
            if np.random.random() < rainy_frequency:
                if cash_pool >= rainy_amount:
                    cash_pool -= rainy_amount  # Execute rainy buy
                else:
                    misses += 1  # Miss!
            
            path.append(cash_pool)
        
        all_paths.append(path)
        miss_counts.append(misses)
    
    # Convert to array
    paths_array = np.array(all_paths)
    
    # Plot percentile bands
    days = np.arange(n_execution_days + 1)
    p10 = np.percentile(paths_array, 10, axis=0)
    p50 = np.percentile(paths_array, 50, axis=0)
    p90 = np.percentile(paths_array, 90, axis=0)
    
    ax1.fill_between(days, p10, p90, alpha=0.2, color=COLORS['primary'], 
                    label='10th-90th Percentile')
    ax1.plot(days, p50, linewidth=3, color=COLORS['primary'], 
            label='Median (50th Percentile)')
    ax1.axhline(rainy_amount, color=COLORS['danger'], linestyle='--', 
               linewidth=2, alpha=0.7, label=f'Min for Rainy Buy (${rainy_amount})')
    
    # Plot a few sample paths
    for i in range(10):
        ax1.plot(days, all_paths[i], linewidth=0.5, alpha=0.3, color=COLORS['dark'])
    
    ax1.set_title(f'Monte Carlo Cash Pool Simulation ({n_simulations:,} Paths)', 
                 fontsize=14, fontweight='bold')
    ax1.set_ylabel('Cash Pool (CAD)', fontsize=11)
    ax1.set_xlabel('Execution Day', fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left', fontsize=11)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Histogram of misses
    ax2.hist(miss_counts, bins=30, color=COLORS['secondary'], alpha=0.7, edgecolor='white')
    ax2.axvline(np.mean(miss_counts), color=COLORS['danger'], linestyle='--', 
               linewidth=2, label=f'Mean: {np.mean(miss_counts):.1f} misses')
    ax2.axvline(13, color=COLORS['success'], linestyle='--', 
               linewidth=2, label='Historical: 13 misses')
    
    ax2.set_title('Distribution of Missed Rainy Days Across Simulations', 
                 fontsize=14, fontweight='bold')
    ax2.set_xlabel('Number of Misses', fontsize=11)
    ax2.set_ylabel('Frequency', fontsize=11)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.legend(loc='upper right', fontsize=11)
    
    # Add statistics text
    textstr = f'''Simulation Results:
    Initial Pool: ${initial_pool:,.0f}
    Accumulation: ${accumulation}/day
    Rainy Frequency: {rainy_frequency:.1%}
    
    Avg Misses: {np.mean(miss_counts):.1f}
    Min Misses: {np.min(miss_counts)}
    Max Misses: {np.max(miss_counts)}
    
    Prob of ≤5 misses: {(np.array(miss_counts) <= 5).mean():.1%}
    Prob of ≤10 misses: {(np.array(miss_counts) <= 10).mean():.1%}
    '''
    
    ax2.text(0.97, 0.97, textstr, transform=ax2.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Monte Carlo simulation saved: {output_path}")
    plt.close()


def create_consecutive_rainy_day_heatmap(
    rainy_buys_df: pd.DataFrame,
    all_execution_days: pd.DatetimeIndex,
    rsi_sma_series: pd.Series,
    output_path: str = "consecutive_rainy_heatmap.png"
):
    """
    Calendar heatmap showing RSI levels and consecutive rainy day patterns.
    """
    fig, ax = plt.subplots(figsize=(20, 8))
    
    # Create calendar matrix (year x execution day)
    years = sorted(all_execution_days.year.unique())
    max_days_per_year = 24  # Bi-weekly = ~24 per year
    
    # Initialize matrix
    matrix = np.full((len(years), max_days_per_year), np.nan)
    rainy_matrix = np.zeros((len(years), max_days_per_year), dtype=bool)
    
    # Fill matrix
    for idx, date in enumerate(all_execution_days):
        year_idx = years.index(date.year)
        day_in_year = len(all_execution_days[(all_execution_days.year == date.year) & 
                                             (all_execution_days <= date)]) - 1
        
        if day_in_year < max_days_per_year and date in rsi_sma_series.index:
            matrix[year_idx, day_in_year] = rsi_sma_series.loc[date]
            rainy_matrix[year_idx, day_in_year] = (rsi_sma_series.loc[date] < 45)
    
    # Create heatmap
    im = ax.imshow(matrix, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=100)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('RSI SMA(7) Level', fontsize=12, fontweight='bold')
    
    # Mark rainy days with red borders
    for i in range(len(years)):
        for j in range(max_days_per_year):
            if rainy_matrix[i, j]:
                rect = Rectangle((j-0.5, i-0.5), 1, 1, fill=False, 
                                edgecolor='red', linewidth=3)
                ax.add_patch(rect)
    
    # Labels
    ax.set_xticks(range(max_days_per_year))
    ax.set_xticklabels(range(1, max_days_per_year + 1), fontsize=9)
    ax.set_yticks(range(len(years)))
    ax.set_yticklabels(years, fontsize=10)
    
    ax.set_xlabel('Execution Day of Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Year', fontsize=12, fontweight='bold')
    ax.set_title('RSI SMA(7) Heatmap: Consecutive Rainy Day Patterns (Red Borders = Rainy Days)', 
                fontsize=14, fontweight='bold', pad=15)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Consecutive rainy day heatmap saved: {output_path}")
    plt.close()


# Example usage guard
if __name__ == "__main__":
    print("Enhanced Visualization Suite")
    print("=" * 50)
    print("Import these functions in your backtest script to generate professional charts.")
    print("\nAvailable functions:")
    print("  - create_interactive_dashboard()")
    print("  - create_regime_performance_breakdown()")
    print("  - create_monte_carlo_cash_pool_simulation()")
    print("  - create_consecutive_rainy_day_heatmap()")
