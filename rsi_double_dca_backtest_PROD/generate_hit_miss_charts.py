"""
Generate Hit/Miss Marker Charts for PROD Email Attachments
===========================================================

Creates three visualization charts:
1. Cash Pool with hit/miss rainy buy markers
2. SPY Price with hit/miss buy markers
3. RSI with hit/miss buy markers

These charts are attached to the PROD monitoring email.
"""

from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from trading_calendar import get_calendar
from strategy_config import get_strategy_config

# =============================================================================
# PARAMETERS
# =============================================================================
START_DATE = "2003-01-01"
INDEX_TICKER = "SPY"
FX_TICKER = "CADUSD=X"
INITIAL_LUMP_SUM = 1000.0

# Get strategy configuration
strategy_config = get_strategy_config('VARIANT_2')

DCA_BASE_AMOUNT = strategy_config.dca_base_amount
CASH_ACCUMULATION = strategy_config.cash_accumulation_per_payday
RAINY_AMOUNT = strategy_config.rainy_extra_amount
RSI_THRESHOLD = strategy_config.rsi_threshold
RSI_PERIOD = strategy_config.rsi_period
RSI_SMA_PERIOD = strategy_config.rsi_sma_period
INITIAL_CASH_POOL = strategy_config.initial_cash_pool

# Execution days (payday is 1st/15th, execution is 3rd/17th)
EXECUTION_DAYS = [3, 17]

# Get TSX calendar
tsx_calendar = get_calendar('TSX')


def fetch_data():
    """Fetch SPY and FX data."""
    print("Fetching market data...")
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    def fetch_series(ticker: str, start: str, end: str) -> pd.Series:
        try:
            df = yf.download(ticker, start=start, end=end, interval="1d", progress=False)
            if df.empty:
                return pd.Series(dtype=float)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            col = "Adj Close" if "Adj Close" in df.columns else "Close"
            s = df[col].copy()
            s.name = ticker
            return s
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            return pd.Series(dtype=float)
    
    spy = fetch_series(INDEX_TICKER, START_DATE, end_date)
    fx = fetch_series(FX_TICKER, START_DATE, end_date)
    prices = pd.concat([spy, fx], axis=1)
    prices = prices.dropna(subset=[INDEX_TICKER, FX_TICKER])
    prices.index = pd.to_datetime(prices.index)
    
    if prices.empty:
        raise SystemExit("No overlapping SPY and FX data fetched.")
    
    prices["SPY_CAD"] = prices[INDEX_TICKER] / prices[FX_TICKER]
    return prices


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Calculate RSI indicator."""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def get_execution_schedule(prices_index):
    """Generate execution schedule matching monitor script logic."""
    dates = pd.to_datetime(prices_index)
    start = dates.min()
    end = dates.max()
    
    execution_schedule = []
    current = start
    
    while current <= end:
        for day in EXECUTION_DAYS:
            candidate = current.replace(day=day)
            if candidate > end:
                break
            
            # Find next trading day
            actual = candidate
            attempts = 0
            while actual not in dates and attempts < 10:
                actual += timedelta(days=1)
                attempts += 1
            
            if actual in dates and actual not in execution_schedule:
                execution_schedule.append(actual)
        
        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1, day=1)
        else:
            current = current.replace(month=current.month + 1, day=1)
    
    return sorted(execution_schedule)


def simulate_strategy(prices, execution_schedule):
    """Run strategy simulation and track all events."""
    shares = 0.0
    cash_pool = INITIAL_CASH_POOL
    contributions = INITIAL_LUMP_SUM
    
    # Initial lump sum
    first_price = prices.iloc[0]["SPY_CAD"]
    if first_price > 0:
        shares = INITIAL_LUMP_SUM / first_price
    
    execution_set = set(execution_schedule)
    
    equity_records = []
    rainy_hits = []  # Successful rainy buys
    rainy_misses = []  # Rainy days with insufficient cash
    base_buys = []  # Non-rainy execution days
    
    for dt, row in prices.iterrows():
        price_cad = row["SPY_CAD"]
        price_usd = row[INDEX_TICKER]
        rsi_sma = row["RSI_SMA"]
        rsi = row["RSI"]
        
        # Execution day logic
        if dt in execution_set:
            # Base investment (always)
            if price_cad > 0:
                shares += DCA_BASE_AMOUNT / price_cad
                contributions += DCA_BASE_AMOUNT
            
            # Check for rainy day
            is_rainy = rsi_sma < RSI_THRESHOLD
            
            if is_rainy:
                # Deploy extra if we have cash
                if cash_pool >= RAINY_AMOUNT:
                    shares += RAINY_AMOUNT / price_cad
                    contributions += RAINY_AMOUNT
                    cash_before = cash_pool
                    cash_pool -= RAINY_AMOUNT
                    
                    rainy_hits.append({
                        "date": dt,
                        "rsi_sma": rsi_sma,
                        "rsi": rsi,
                        "price_usd": price_usd,
                        "price_cad": price_cad,
                        "cash_before": cash_before,
                        "cash_after": cash_pool
                    })
                else:
                    # Insufficient cash - missed opportunity
                    rainy_misses.append({
                        "date": dt,
                        "rsi_sma": rsi_sma,
                        "rsi": rsi,
                        "price_usd": price_usd,
                        "price_cad": price_cad,
                        "cash_pool": cash_pool
                    })
            else:
                # Not rainy - regular base buy
                base_buys.append({
                    "date": dt,
                    "rsi_sma": rsi_sma,
                    "rsi": rsi,
                    "price_usd": price_usd,
                    "price_cad": price_cad,
                    "cash_pool": cash_pool
                })
            
            # Add cash savings
            cash_pool += CASH_ACCUMULATION
        
        # Track equity
        equity_records.append({
            "date": dt,
            "equity": shares * price_cad + cash_pool,
            "shares_value": shares * price_cad,
            "cash_pool": cash_pool
        })
    
    eq_df = pd.DataFrame(equity_records).set_index("date")
    
    return {
        "equity_curve": eq_df,
        "rainy_hits": pd.DataFrame(rainy_hits),
        "rainy_misses": pd.DataFrame(rainy_misses),
        "base_buys": pd.DataFrame(base_buys)
    }


def create_cash_pool_chart(equity_df, rainy_hits, rainy_misses):
    """Create cash pool chart with hit/miss markers."""
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Plot cash pool over time
    ax.plot(equity_df.index, equity_df['cash_pool'], 
            color='#2E86AB', linewidth=2, label='Cash Pool', zorder=1)
    
    # Add hit markers (green - successful rainy buys)
    if not rainy_hits.empty:
        hit_dates = rainy_hits['date']
        hit_cash = [equity_df.loc[d, 'cash_pool'] if d in equity_df.index else None 
                    for d in hit_dates]
        ax.scatter(hit_dates, hit_cash, color='#06A77D', s=120, marker='o', 
                   label=f'✓ Rainy Buy (n={len(rainy_hits)})', zorder=3, 
                   edgecolors='white', linewidths=1.5)
    
    # Add miss markers (red - insufficient cash)
    if not rainy_misses.empty:
        miss_dates = rainy_misses['date']
        miss_cash = [equity_df.loc[d, 'cash_pool'] if d in equity_df.index else None 
                     for d in miss_dates]
        ax.scatter(miss_dates, miss_cash, color='#D00000', s=120, marker='x', 
                   label=f'✗ Missed (n={len(rainy_misses)})', zorder=3, linewidths=2.5)
    
    ax.set_title('Cash Pool Evolution - Hit/Miss Rainy Day Tracking', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Year', fontsize=13, fontweight='bold')
    ax.set_ylabel('Cash Pool (CAD)', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='best', fontsize=11, framealpha=0.95)
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig('cash_pool_hit_miss.png', dpi=300, bbox_inches='tight')
    print("✓ Generated: cash_pool_hit_miss.png")
    plt.close()


def create_spy_price_chart(prices, rainy_hits, rainy_misses, base_buys):
    """Create SPY price chart with buy markers."""
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Plot SPY price
    ax.plot(prices.index, prices[INDEX_TICKER], 
            color='#1F77B4', linewidth=1.5, label='SPY Price', alpha=0.8, zorder=1)
    
    # Add rainy buy hit markers (green)
    if not rainy_hits.empty:
        ax.scatter(rainy_hits['date'], rainy_hits['price_usd'], 
                   color='#06A77D', s=100, marker='^', 
                   label=f'✓ Rainy Buy (n={len(rainy_hits)})', zorder=3, 
                   edgecolors='white', linewidths=1.2)
    
    # Add rainy buy miss markers (red)
    if not rainy_misses.empty:
        ax.scatter(rainy_misses['date'], rainy_misses['price_usd'], 
                   color='#D00000', s=100, marker='v', 
                   label=f'✗ Missed Rainy (n={len(rainy_misses)})', zorder=3, 
                   edgecolors='white', linewidths=1.2)
    
    # Add base buy markers (gray - small)
    if not base_buys.empty:
        # Sample to avoid clutter (show every 10th)
        sample_buys = base_buys.iloc[::10]
        ax.scatter(sample_buys['date'], sample_buys['price_usd'], 
                   color='#6C757D', s=20, marker='o', alpha=0.4,
                   label=f'Base Buys (showing 1/10)', zorder=2)
    
    ax.set_title('SPY Price - Buy Decisions with Hit/Miss Markers', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Year', fontsize=13, fontweight='bold')
    ax.set_ylabel('SPY Price (USD)', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='best', fontsize=11, framealpha=0.95)
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    plt.xticks(rotation=45, ha='right')
    
    # Log scale for better visibility
    ax.set_yscale('log')
    
    plt.tight_layout()
    plt.savefig('spy_price_hit_miss.png', dpi=300, bbox_inches='tight')
    print("✓ Generated: spy_price_hit_miss.png")
    plt.close()


def create_rsi_chart(prices, rainy_hits, rainy_misses, base_buys):
    """Create RSI chart with buy markers."""
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Plot RSI SMA(7)
    ax.plot(prices.index, prices['RSI_SMA'], 
            color='#FF6B6B', linewidth=2, label='RSI SMA(7)', zorder=1)
    
    # Add threshold line
    ax.axhline(y=RSI_THRESHOLD, color='#495057', linestyle='--', 
               linewidth=2, label=f'Threshold ({RSI_THRESHOLD})', zorder=2)
    
    # Add oversold/overbought zones
    ax.axhspan(0, 30, alpha=0.1, color='green', label='Oversold Zone')
    ax.axhspan(70, 100, alpha=0.1, color='red', label='Overbought Zone')
    
    # Add rainy buy hit markers
    if not rainy_hits.empty:
        ax.scatter(rainy_hits['date'], rainy_hits['rsi_sma'], 
                   color='#06A77D', s=120, marker='o', 
                   label=f'✓ Rainy Buy (n={len(rainy_hits)})', zorder=4, 
                   edgecolors='white', linewidths=1.5)
    
    # Add rainy buy miss markers
    if not rainy_misses.empty:
        ax.scatter(rainy_misses['date'], rainy_misses['rsi_sma'], 
                   color='#D00000', s=120, marker='x', 
                   label=f'✗ Missed Rainy (n={len(rainy_misses)})', zorder=4, 
                   linewidths=2.5)
    
    # Add base buy markers (sample)
    if not base_buys.empty:
        sample_buys = base_buys.iloc[::10]
        ax.scatter(sample_buys['date'], sample_buys['rsi_sma'], 
                   color='#6C757D', s=30, marker='o', alpha=0.4,
                   label=f'Base Buys (showing 1/10)', zorder=3)
    
    ax.set_title('RSI SMA(7) - Rainy Day Trigger with Hit/Miss Markers', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Year', fontsize=13, fontweight='bold')
    ax.set_ylabel('RSI SMA(7)', fontsize=13, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='best', fontsize=10, framealpha=0.95, ncol=2)
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig('rsi_hit_miss.png', dpi=300, bbox_inches='tight')
    print("✓ Generated: rsi_hit_miss.png")
    plt.close()


def main():
    """Main execution."""
    print("=" * 80)
    print("GENERATING HIT/MISS MARKER CHARTS")
    print("=" * 80)
    
    # Fetch data
    prices = fetch_data()
    
    # Compute RSI
    print("Computing RSI indicators...")
    prices['RSI'] = compute_rsi(prices[INDEX_TICKER], RSI_PERIOD)
    prices['RSI_SMA'] = prices['RSI'].rolling(window=RSI_SMA_PERIOD).mean()
    prices = prices.dropna(subset=['RSI_SMA'])
    
    # Get execution schedule
    execution_schedule = get_execution_schedule(prices.index)
    print(f"Execution days: {len(execution_schedule)}")
    
    # Run simulation
    print("Running strategy simulation...")
    results = simulate_strategy(prices, execution_schedule)
    
    # Generate charts
    print("\nGenerating charts...")
    create_cash_pool_chart(
        results['equity_curve'], 
        results['rainy_hits'], 
        results['rainy_misses']
    )
    
    create_spy_price_chart(
        prices,
        results['rainy_hits'], 
        results['rainy_misses'],
        results['base_buys']
    )
    
    create_rsi_chart(
        prices,
        results['rainy_hits'], 
        results['rainy_misses'],
        results['base_buys']
    )
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total rainy buy hits: {len(results['rainy_hits'])}")
    print(f"Total rainy buy misses: {len(results['rainy_misses'])}")
    print(f"Total base buys: {len(results['base_buys'])}")
    print(f"Hit rate: {len(results['rainy_hits']) / (len(results['rainy_hits']) + len(results['rainy_misses'])) * 100:.1f}%")
    print("\n✅ All charts generated successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
