"""
Market Metrics Calculator Module - PROD
========================================

Centralized calculations for all market-related metrics used in PROD email templates.
Provides computed values for RSI evaluation, cash pool calculations, and display formatting.
"""

from typing import Optional, Dict, List
from datetime import datetime, timedelta


class MarketMetrics:
    """Calculate and store market metrics for PROD email template."""
    
    def __init__(self, rsi_sma: float, price: float, cash_pool: float, 
                 total_contributions: float, rainy_buys: List,
                 rsi_threshold: float = 45.0, dca_base_amount: float = 150.0,
                 rainy_amount: float = 150.0, cash_accumulation: float = 30.0,
                 payday_day_of_month_2: int = 15):
        """
        Initialize market metrics calculator for PROD strategy.
        
        Args:
            rsi_sma: RSI SMA(7) smoothed value
            price: Current SPY price
            cash_pool: Current cash pool balance in CAD
            total_contributions: Total contributions to date in CAD
            rainy_buys: List of rainy buy records
            rsi_threshold: RSI threshold for rainy day (default 45.0)
            dca_base_amount: Base DCA amount (default 150.0)
            rainy_amount: Rainy day deployment amount (default 150.0)
            cash_accumulation: Cash saved per payday (default 30.0)
            payday_day_of_month_2: Second payday of month (default 15)
        """
        self.rsi_sma = rsi_sma
        self.price = price
        self.cash_pool = cash_pool
        self.total_contributions = total_contributions
        self.rainy_buys = rainy_buys
        self.rsi_threshold = rsi_threshold
        self.dca_base_amount = dca_base_amount
        self.rainy_amount = rainy_amount
        self.cash_accumulation = cash_accumulation
        self.payday_day_of_month_2 = payday_day_of_month_2
        
        # Calculate all derived metrics
        self._calculate_metrics()
    
    def _calculate_metrics(self):
        """Calculate all derived metrics."""
        # Rainy day evaluation
        self.is_rainy = self.rsi_sma < self.rsi_threshold
        self.can_deploy = self.cash_pool >= self.rainy_amount
        
        # Next payday calculation
        today = datetime.now().date()
        if today.day < self.payday_day_of_month_2:
            self.next_payday_text = f"{self.payday_day_of_month_2}th of this month"
        else:
            next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
            self.next_payday_text = f"1st of {next_month.strftime('%B')}"
        
        # Action and cash calculations
        if self.is_rainy and self.can_deploy:
            # Case 1: Rainy day AND sufficient cash
            self.total_investment_today = self.dca_base_amount + self.rainy_amount
            self.cash_after_deploy = self.cash_pool - self.rainy_amount
            self.new_cash_pool = self.cash_pool - self.rainy_amount + self.cash_accumulation
            self.action_type = "rainy_deploy"
        elif self.is_rainy and not self.can_deploy:
            # Case 2: Rainy day BUT insufficient cash
            self.total_investment_today = self.dca_base_amount
            self.cash_after_deploy = None
            self.new_cash_pool = self.cash_pool + self.cash_accumulation
            self.action_type = "rainy_insufficient"
        else:
            # Case 3: Not rainy
            self.total_investment_today = self.dca_base_amount
            self.cash_after_deploy = None
            self.new_cash_pool = self.cash_pool + self.cash_accumulation
            self.action_type = "save"
        
        # Rainy count
        self.rainy_buys_count = len(self.rainy_buys)
        
        # Initial cash pool note
        self.has_initial_note = self.total_contributions == 0
    
    def get_recommendation(self) -> str:
        """Get recommendation text based on action type."""
        if self.action_type == "rainy_deploy":
            return f"🔥 RECOMMENDATION: Buy extra ${self.rainy_amount:.0f} from cash pool"
        elif self.action_type == "rainy_insufficient":
            return f"⚠️  Rainy day but insufficient cash (need ${self.rainy_amount:.0f}, have ${self.cash_pool:.2f})"
        else:
            return f"💰 RECOMMENDATION: Save your cash for next rainy day"
    
    def get_action_text(self) -> str:
        """Get action text for display."""
        if self.action_type == "rainy_deploy":
            return f"⭐⭐⭐ ACTION REQUIRED: RAINY BUY ${self.rainy_amount:.0f} CAD ⭐⭐⭐\n   (Plus your regular ${self.dca_base_amount:.0f} base = ${self.total_investment_today:.0f} total today)"
        elif self.action_type == "rainy_insufficient":
            return f"⭐⭐⭐ ACTION REQUIRED: BASE BUY ONLY ${self.dca_base_amount:.0f} CAD ⭐⭐⭐\n   (Insufficient cash for rainy buy - keep building pool!)"
        else:
            return f"⭐⭐⭐ ACTION REQUIRED: BASE BUY ONLY ${self.dca_base_amount:.0f} CAD ⭐⭐⭐\n   (Not rainy today - save for next opportunity)"
    
    def get_cash_after_text(self) -> str:
        """Get cash pool after action text."""
        if self.action_type == "rainy_deploy":
            return f"Cash pool after rainy buy: ${self.cash_after_deploy:.2f}\n   Add today's savings: +${self.cash_accumulation:.0f}\n   Final cash pool: ${self.new_cash_pool:.2f}"
        else:
            return f"Cash pool after saving: ${self.new_cash_pool:.2f}"
    
    def get_rainy_status(self) -> str:
        """Get rainy status emoji and text."""
        if self.is_rainy:
            return f"✅ RAINY DAY - RSI SMA(7) < {self.rsi_threshold:.0f}!"
        else:
            return f"⛅ NOT RAINY - RSI SMA(7) ≥ {self.rsi_threshold:.0f}"
    
    def get_decision_result(self) -> str:
        """Get decision result text."""
        if self.is_rainy:
            return f"RSI < {self.rsi_threshold:.0f} → RAINY DAY ✅"
        else:
            return f"RSI ≥ {self.rsi_threshold:.0f} → NOT RAINY ❌"
    
    def get_initial_note(self) -> str:
        """Get initial cash pool note if applicable."""
        if self.has_initial_note:
            return f"\n   📌 NOTE: Starting with ${self.cash_pool:.2f} initial cash pool (enough for 2 rainy buys)"
        return ""
    
    def get_cash_available_line(self) -> str:
        """Get cash available line for decision path (only if rainy)."""
        if self.is_rainy:
            return f"• Cash Available: ${self.cash_pool:.2f}"
        return ""
    
    def get_all_metrics(self) -> Dict:
        """
        Get all calculated metrics as dictionary.
        
        Returns:
            Dictionary with all metric values formatted for template
        """
        return {
            # Core values
            "rsi_sma": self.rsi_sma,
            "price": self.price,
            "cash_pool": self.cash_pool,
            "total_contributions": self.total_contributions,
            "rainy_buys_count": self.rainy_buys_count,
            "rsi_threshold": self.rsi_threshold,
            
            # Calculated values
            "is_rainy": self.is_rainy,
            "can_deploy": self.can_deploy,
            "total_investment_today": self.total_investment_today,
            "new_cash_pool": self.new_cash_pool,
            "cash_after_deploy": self.cash_after_deploy,
            "next_payday_text": self.next_payday_text,
            "action_type": self.action_type,
            
            # Display strings
            "price_display": f"${self.price:.2f}",
            "rsi_sma_display": f"{self.rsi_sma:.2f}",
            "cash_pool_display": f"${self.cash_pool:.2f}",
            "total_contributions_display": f"${self.total_contributions:,.2f}",
            "new_cash_pool_display": f"${self.new_cash_pool:.2f}",
            
            # Text blocks
            "recommendation": self.get_recommendation(),
            "action_text": self.get_action_text(),
            "cash_after_text": self.get_cash_after_text(),
            "rainy_status": self.get_rainy_status(),
            "decision_result": self.get_decision_result(),
            "initial_note": self.get_initial_note(),
            "cash_available_line": self.get_cash_available_line()
        }


def calculate_market_metrics(rsi_sma: float, price: float, cash_pool: float,
                            total_contributions: float, rainy_buys: List,
                            rsi_threshold: float = 45.0,
                            dca_base_amount: float = 150.0,
                            rainy_amount: float = 150.0,
                            cash_accumulation: float = 30.0,
                            payday_day_of_month_2: int = 15) -> MarketMetrics:
    """
    Convenience function to create MarketMetrics instance for PROD.
    
    Args:
        rsi_sma: RSI SMA(7) smoothed value
        price: Current SPY price
        cash_pool: Current cash pool balance
        total_contributions: Total contributions to date
        rainy_buys: List of rainy buy records
        rsi_threshold: RSI threshold (default 45.0)
        dca_base_amount: Base DCA amount (default 150.0)
        rainy_amount: Rainy deployment (default 150.0)
        cash_accumulation: Cash saved per payday (default 30.0)
        payday_day_of_month_2: Second payday day (default 15)
    
    Returns:
        MarketMetrics instance with all calculated values
    
    Example:
        >>> metrics = calculate_market_metrics(34.64, 659.03, 330.0, 0, [])
        >>> print(metrics.is_rainy)  # True
        >>> print(metrics.can_deploy)  # True
        >>> print(metrics.action_type)  # "rainy_deploy"
    """
    return MarketMetrics(rsi_sma, price, cash_pool, total_contributions, rainy_buys,
                        rsi_threshold, dca_base_amount, rainy_amount,
                        cash_accumulation, payday_day_of_month_2)
