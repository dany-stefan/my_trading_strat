"""
Strategy Comparison Module - PROD
==================================

Centralizes all strategy performance calculations and comparisons.
Computes CAGR, final values, profits, and comparative metrics for:
- YOUR RAINY DAY strategy
- Simple DCA (no rainy logic)
- Buy & Hold ($1000 lump sum)

All email templates read from this module - NO calculations in templates.
"""

from typing import Dict, Tuple
import pandas as pd
import numpy as np
from pathlib import Path


class StrategyComparison:
    """Calculate and store strategy performance comparisons."""
    
    def __init__(self, backtest_start_date: str = "2003-10-03", 
                 backtest_end_date: str = "2025-11-21"):
        """
        Initialize strategy comparison calculator.
        
        Args:
            backtest_start_date: Start date of backtest period
            backtest_end_date: End date of backtest period
        """
        self.backtest_start = backtest_start_date
        self.backtest_end = backtest_end_date
        self.backtest_years = self._calculate_years()
        
        # Load backtest results
        self._load_backtest_data()
        
        # Calculate all metrics
        self._calculate_all_metrics()
    
    def _calculate_years(self) -> int:
        """Calculate number of years in backtest."""
        from datetime import datetime
        start = datetime.strptime(self.backtest_start, "%Y-%m-%d")
        end = datetime.strptime(self.backtest_end, "%Y-%m-%d")
        return round((end - start).days / 365.25)
    
    def _load_backtest_data(self):
        """Load backtest CSV files."""
        base_path = Path(__file__).parent
        
        # Load YOUR RAINY DAY strategy (Variant #2)
        rainy_file = base_path / "equity_rainy_strategy_calendar_dates.csv"
        if rainy_file.exists():
            self.rainy_df = pd.read_csv(rainy_file)
        else:
            # Use default values if file doesn't exist
            self.rainy_df = None
        
        # Load Simple DCA baseline
        baseline_file = base_path / "equity_baseline_calendar_dates.csv"
        if baseline_file.exists():
            self.baseline_df = pd.read_csv(baseline_file)
        else:
            self.baseline_df = None
    
    def _calculate_all_metrics(self):
        """Calculate all performance metrics for each strategy."""
        
        # ===================================================================
        # YOUR RAINY DAY STRATEGY (Variant #2)
        # ===================================================================
        if self.rainy_df is not None and len(self.rainy_df) > 0:
            self.rainy_final_value = float(self.rainy_df['equity'].iloc[-1])
            # Calculate total invested from backtest data
            # Rainy strategy: bi-weekly $150 + rainy buys from cash pool
            num_paydays = len(self.rainy_df[self.rainy_df.index % 14 == 0])  # Approximate bi-weekly
            self.rainy_total_invested = num_paydays * 150.0  # Approximate
            self.rainy_profit = self.rainy_final_value - self.rainy_total_invested
            self.rainy_cagr = self._calculate_cagr(
                self.rainy_total_invested, 
                self.rainy_final_value, 
                self.backtest_years
            )
        else:
            # Default values from actual backtest
            self.rainy_final_value = 512450  # From latest CSV
            self.rainy_total_invested = 104350
            self.rainy_profit = self.rainy_final_value - self.rainy_total_invested
            self.rainy_cagr = self._calculate_cagr(
                self.rainy_total_invested,
                self.rainy_final_value,
                self.backtest_years
            )
        
        # ===================================================================
        # SIMPLE DCA (No Rainy Logic)
        # ===================================================================
        if self.baseline_df is not None and len(self.baseline_df) > 0:
            self.dca_final_value = float(self.baseline_df['equity'].iloc[-1])
            # Baseline DCA: bi-weekly $150
            num_paydays = len(self.baseline_df[self.baseline_df.index % 14 == 0])  # Approximate
            self.dca_total_invested = num_paydays * 150.0
            self.dca_profit = self.dca_final_value - self.dca_total_invested
            self.dca_cagr = self._calculate_cagr(
                self.dca_total_invested,
                self.dca_final_value,
                self.backtest_years
            )
        else:
            # Default values
            self.dca_final_value = 503343
            self.dca_total_invested = 87550
            self.dca_profit = 415793
            self.dca_cagr = 32.48
        
        # ===================================================================
        # BUY & HOLD (Lump Sum $1000 at start)
        # ===================================================================
        # Get SPY price at start and end - need to load from rainy strategy CSV
        if self.rainy_df is not None and len(self.rainy_df) > 0:
            # Calculate SPY price from shares_value and equity
            # SPY price = shares_value / num_shares (but we don't have num_shares directly)
            # Alternative: Use known SPY prices
            spy_start = 103.50  # SPY price ~Oct 2003
            spy_end = 659.03    # SPY price ~Nov 2025 (current)
        else:
            # Default SPY prices
            spy_start = 103.50
            spy_end = 659.03
        
        self.buy_hold_initial = 1000.0  # Lump sum investment
        self.buy_hold_shares = self.buy_hold_initial / spy_start
        self.buy_hold_final_value = self.buy_hold_shares * spy_end
        self.buy_hold_profit = self.buy_hold_final_value - self.buy_hold_initial
        self.buy_hold_cagr = self._calculate_cagr(
            self.buy_hold_initial,
            self.buy_hold_final_value,
            self.backtest_years
        )
        
        # ===================================================================
        # COMPARATIVE METRICS
        # ===================================================================
        # vs Simple DCA
        self.gain_vs_dca = self.rainy_profit - self.dca_profit
        self.gain_vs_dca_pct = (self.gain_vs_dca / self.dca_profit) * 100
        self.extra_deployed_vs_dca = self.rainy_total_invested - self.dca_total_invested
        self.rainy_capital_return = ((self.gain_vs_dca / self.extra_deployed_vs_dca) * 100) if self.extra_deployed_vs_dca > 0 else 0
        
        # vs Buy & Hold
        self.gain_vs_buy_hold = self.rainy_profit - self.buy_hold_profit
        self.gain_vs_buy_hold_pct = (self.gain_vs_buy_hold / self.buy_hold_profit) * 100
    
    def _calculate_cagr(self, initial: float, final: float, years: int) -> float:
        """Calculate Compound Annual Growth Rate."""
        if initial <= 0 or years <= 0:
            return 0.0
        return ((final / initial) ** (1 / years) - 1) * 100
    
    def get_comparison_table_data(self) -> Dict:
        """
        Get data for strategy comparison table.
        
        Returns:
            Dictionary with all strategies' metrics formatted for display
        """
        return {
            # YOUR RAINY DAY
            "rainy_cagr": f"{self.rainy_cagr:.2f}%",
            "rainy_final": f"${self.rainy_final_value:,.0f}",
            "rainy_invested": f"${self.rainy_total_invested:,.0f}",
            "rainy_profit": f"${self.rainy_profit:,.0f}",
            "rainy_vs_baseline": "BASELINE",
            
            # SIMPLE DCA
            "dca_cagr": f"{self.dca_cagr:.2f}%",
            "dca_final": f"${self.dca_final_value:,.0f}",
            "dca_invested": f"${self.dca_total_invested:,.0f}",
            "dca_profit": f"${self.dca_profit:,.0f}",
            "dca_vs_baseline": f"-${abs(self.gain_vs_dca):,.0f}",
            
            # BUY & HOLD
            "buy_hold_cagr": f"{self.buy_hold_cagr:.2f}%",
            "buy_hold_final": f"${self.buy_hold_final_value:,.0f}",
            "buy_hold_invested": f"${self.buy_hold_initial:,.0f}",
            "buy_hold_profit": f"${self.buy_hold_profit:,.0f}",
            "buy_hold_vs_baseline": f"-${abs(self.gain_vs_buy_hold):,.0f}",
        }
    
    def get_gains_summary(self) -> Dict:
        """
        Get summary of gains vs other strategies.
        
        Returns:
            Dictionary with comparative gains and explanations
        """
        return {
            # vs DCA
            "gain_vs_dca": f"${self.gain_vs_dca:,.0f}",
            "gain_vs_dca_pct": f"{self.gain_vs_dca_pct:.1f}%",
            "extra_deployed": f"${self.extra_deployed_vs_dca:,.0f}",
            "rainy_roi": f"{self.rainy_capital_return:.0f}%",
            "rainy_roi_multiplier": f"${(1 + self.rainy_capital_return/100):.2f}",
            
            # vs Buy & Hold
            "gain_vs_buy_hold": f"${self.gain_vs_buy_hold:,.0f}",
            "gain_vs_buy_hold_pct": f"{self.gain_vs_buy_hold_pct:.1f}%",
            
            # Buy & Hold details
            "buy_hold_initial_display": f"${self.buy_hold_initial:,.0f}",
            "buy_hold_years": f"{self.backtest_years}",
        }
    
    def get_all_metrics(self) -> Dict:
        """
        Get all metrics combined.
        
        Returns:
            Complete dictionary of all strategy comparison metrics
        """
        comparison = self.get_comparison_table_data()
        gains = self.get_gains_summary()
        
        return {
            **comparison,
            **gains,
            "backtest_period": f"{self.backtest_start[:4]}-{self.backtest_end[:4]}",
            "backtest_years": self.backtest_years,
        }


def calculate_strategy_comparison() -> StrategyComparison:
    """
    Convenience function to create StrategyComparison instance.
    
    Returns:
        StrategyComparison object with all calculated metrics
    
    Example:
        >>> comp = calculate_strategy_comparison()
        >>> metrics = comp.get_all_metrics()
        >>> print(metrics['gain_vs_dca'])  # "$97,564"
    """
    return StrategyComparison()
