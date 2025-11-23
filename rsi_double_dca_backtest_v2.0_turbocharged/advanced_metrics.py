"""
Advanced Strategy Metrics Module
=================================

Comprehensive performance analysis beyond simple CAGR.
Calculates:
- Terminal value
- Max drawdown
- Sharpe ratio / SQN (System Quality Number)
- Volatility (annualized)
- Return curve stability (R²)
- Exposure (% of time capital is at risk)
- Profit factor
- Win/loss distribution

All email templates and reports read from this module.
"""

from typing import Dict, Tuple, List
import pandas as pd
import numpy as np
from pathlib import Path


class AdvancedMetrics:
    """Calculate comprehensive strategy performance metrics."""
    
    def __init__(self, equity_series: pd.Series, dates: pd.Series, 
                 initial_capital: float = 1000.0, risk_free_rate: float = 0.04):
        """
        Initialize advanced metrics calculator.
        
        Args:
            equity_series: Time series of portfolio equity values
            dates: Corresponding dates for equity values
            initial_capital: Starting capital
            risk_free_rate: Annual risk-free rate for Sharpe (default 4%)
        """
        self.equity = equity_series.copy()
        self.dates = pd.to_datetime(dates)
        self.initial_capital = initial_capital
        self.risk_free_rate = risk_free_rate
        
        # Calculate all metrics
        self._calculate_all_metrics()
    
    def _calculate_all_metrics(self):
        """Calculate all performance metrics."""
        
        # Terminal value
        self.terminal_value = float(self.equity.iloc[-1])
        
        # Returns series
        self.returns = self.equity.pct_change().dropna()
        
        # Max drawdown
        self.max_drawdown = self._calculate_max_drawdown()
        
        # Volatility (annualized)
        self.volatility = self._calculate_volatility()
        
        # Sharpe ratio
        self.sharpe_ratio = self._calculate_sharpe_ratio()
        
        # SQN (System Quality Number)
        self.sqn = self._calculate_sqn()
        
        # R² (return curve stability)
        self.r_squared = self._calculate_r_squared()
        
        # Exposure (simplified as 100% for buy-and-hold strategies)
        self.exposure = 100.0
        
        # Profit factor and win/loss
        self.profit_factor, self.win_rate, self.avg_win, self.avg_loss = self._calculate_profit_metrics()
        
        # CAGR
        years = (self.dates.iloc[-1] - self.dates.iloc[0]).days / 365.25
        self.cagr = ((self.terminal_value / self.initial_capital) ** (1 / years) - 1) * 100
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown as percentage."""
        cummax = self.equity.cummax()
        drawdown = (self.equity - cummax) / cummax * 100
        return abs(float(drawdown.min()))
    
    def _calculate_volatility(self) -> float:
        """Calculate annualized volatility."""
        # Assuming daily data, annualize with sqrt(252)
        daily_vol = self.returns.std()
        annualized_vol = daily_vol * np.sqrt(252)
        return float(annualized_vol * 100)  # As percentage
    
    def _calculate_sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio (annualized)."""
        daily_rf = (1 + self.risk_free_rate) ** (1/252) - 1
        excess_returns = self.returns - daily_rf
        
        if len(excess_returns) == 0 or excess_returns.std() == 0:
            return 0.0
        
        sharpe = excess_returns.mean() / excess_returns.std() * np.sqrt(252)
        return float(sharpe)
    
    def _calculate_sqn(self) -> float:
        """
        Calculate System Quality Number (Van Tharp).
        SQN = sqrt(N) * (avg_return / stddev_return)
        """
        if len(self.returns) == 0 or self.returns.std() == 0:
            return 0.0
        
        sqn = np.sqrt(len(self.returns)) * (self.returns.mean() / self.returns.std())
        return float(sqn)
    
    def _calculate_r_squared(self) -> float:
        """Calculate R² for return curve stability."""
        # Fit linear regression to equity curve
        x = np.arange(len(self.equity))
        y = self.equity.values
        
        # Linear regression
        coeffs = np.polyfit(x, y, 1)
        y_pred = np.polyval(coeffs, x)
        
        # R²
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        
        if ss_tot == 0:
            return 0.0
        
        r_squared = 1 - (ss_res / ss_tot)
        return float(r_squared)
    
    def _calculate_profit_metrics(self) -> Tuple[float, float, float, float]:
        """Calculate profit factor, win rate, avg win, avg loss."""
        wins = self.returns[self.returns > 0]
        losses = self.returns[self.returns < 0]
        
        if len(self.returns) == 0:
            return 0.0, 0.0, 0.0, 0.0
        
        # Win rate
        win_rate = (len(wins) / len(self.returns)) * 100
        
        # Average win/loss
        avg_win = float(wins.mean() * 100) if len(wins) > 0 else 0.0
        avg_loss = float(abs(losses.mean()) * 100) if len(losses) > 0 else 0.0
        
        # Profit factor
        total_wins = wins.sum() if len(wins) > 0 else 0
        total_losses = abs(losses.sum()) if len(losses) > 0 else 1e-10
        profit_factor = float(total_wins / total_losses) if total_losses > 0 else 0.0
        
        return profit_factor, win_rate, avg_win, avg_loss
    
    def get_all_metrics(self) -> Dict:
        """
        Get all calculated metrics as dictionary.
        
        Returns:
            Dictionary with all metrics (raw values and formatted strings)
        """
        return {
            # Core values
            "terminal_value": self.terminal_value,
            "cagr": self.cagr,
            "max_drawdown": self.max_drawdown,
            "volatility": self.volatility,
            "sharpe_ratio": self.sharpe_ratio,
            "sqn": self.sqn,
            "r_squared": self.r_squared,
            "exposure": self.exposure,
            "profit_factor": self.profit_factor,
            "win_rate": self.win_rate,
            "avg_win": self.avg_win,
            "avg_loss": self.avg_loss,
            
            # Formatted strings
            "terminal_value_display": f"${self.terminal_value:,.0f}",
            "cagr_display": f"{self.cagr:.2f}%",
            "max_drawdown_display": f"{self.max_drawdown:.2f}%",
            "volatility_display": f"{self.volatility:.2f}%",
            "sharpe_display": f"{self.sharpe_ratio:.2f}",
            "sqn_display": f"{self.sqn:.2f}",
            "r_squared_display": f"{self.r_squared:.3f}",
            "exposure_display": f"{self.exposure:.1f}%",
            "profit_factor_display": f"{self.profit_factor:.2f}",
            "win_rate_display": f"{self.win_rate:.1f}%",
            "avg_win_display": f"{self.avg_win:.3f}%",
            "avg_loss_display": f"{self.avg_loss:.3f}%",
        }
    
    def get_sqn_rating(self) -> str:
        """Get qualitative SQN rating."""
        if self.sqn >= 7.0:
            return "Superb (Holy Grail)"
        elif self.sqn >= 5.0:
            return "Excellent"
        elif self.sqn >= 3.0:
            return "Good"
        elif self.sqn >= 2.0:
            return "Average"
        elif self.sqn >= 1.0:
            return "Below Average"
        else:
            return "Poor"
    
    def get_sharpe_rating(self) -> str:
        """Get qualitative Sharpe ratio rating."""
        if self.sharpe_ratio >= 3.0:
            return "Excellent"
        elif self.sharpe_ratio >= 2.0:
            return "Very Good"
        elif self.sharpe_ratio >= 1.0:
            return "Good"
        elif self.sharpe_ratio >= 0.5:
            return "Acceptable"
        else:
            return "Poor"


def calculate_advanced_metrics(equity_csv_path: str, 
                               initial_capital: float = 1000.0) -> AdvancedMetrics:
    """
    Load equity curve from CSV and calculate advanced metrics.
    
    Args:
        equity_csv_path: Path to CSV file with equity curve
        initial_capital: Initial capital (default 1000)
    
    Returns:
        AdvancedMetrics object with all calculated values
    
    Example:
        >>> metrics = calculate_advanced_metrics("equity_rainy_strategy_calendar_dates.csv")
        >>> all_metrics = metrics.get_all_metrics()
        >>> print(all_metrics['sharpe_display'])  # "2.45"
    """
    df = pd.read_csv(equity_csv_path)
    
    # Determine equity column name
    equity_col = 'equity' if 'equity' in df.columns else 'total_value'
    
    return AdvancedMetrics(
        equity_series=df[equity_col],
        dates=df['date'],
        initial_capital=initial_capital
    )
