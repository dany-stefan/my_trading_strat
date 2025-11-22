"""
Market Metrics Calculator Module
=================================

Centralized calculations for all market-related metrics used in email templates.
Provides computed values for 200MA thresholds, market regime classification,
and other derived metrics.
"""

from typing import Optional, Dict, Tuple


class MarketMetrics:
    """Calculate and store market metrics for email template."""
    
    def __init__(self, price: float, spy_200ma: Optional[float] = None, vix: Optional[float] = None, rsi_sma: Optional[float] = None):
        """
        Initialize market metrics calculator.
        
        Args:
            price: Current SPY price
            spy_200ma: 200-day moving average (optional)
            vix: VIX volatility index (optional)
            rsi_sma: RSI SMA(7) smoothed value (optional)
        """
        self.price = price
        self.spy_200ma = spy_200ma
        self.vix = vix
        self.rsi_sma = rsi_sma
        
        # Calculate all derived metrics
        self._calculate_metrics()
    
    def _calculate_metrics(self):
        """Calculate all derived metrics."""
        # 200MA threshold calculations
        if self.spy_200ma:
            self.ma_plus_5_pct = self.spy_200ma * 1.05
            self.ma_minus_5_pct = self.spy_200ma * 0.95
            self.deviation_pct = ((self.price - self.spy_200ma) / self.spy_200ma) * 100
        else:
            self.ma_plus_5_pct = None
            self.ma_minus_5_pct = None
            self.deviation_pct = None
        
        # Market regime determination
        self.market_regime = self._determine_regime()
        self.regime_emoji = self._get_regime_emoji()
        
        # Adaptive RSI threshold based on regime
        self.adaptive_threshold = self._calculate_adaptive_threshold()
        
        # VIX-based metrics
        self.vix_level = self._determine_vix_level()
        self.volatility_sizing = self._calculate_volatility_sizing()
    
    def _determine_regime(self) -> str:
        """
        Determine market regime based on 200MA deviation.
        
        Returns:
            "BULL", "BEAR", "NEUTRAL", or "UNKNOWN"
        """
        if not self.spy_200ma or self.deviation_pct is None:
            # When 200MA not available, use VIX as fallback
            if self.vix is not None:
                if self.vix < 15:
                    return "NEUTRAL"  # Low VIX = calm market
                elif self.vix > 30:
                    return "BEAR"  # High VIX = fear/bearish
                else:
                    return "NEUTRAL"  # Medium VIX = neutral
            return "NEUTRAL"  # Default to NEUTRAL instead of UNKNOWN
        
        if self.deviation_pct > 5:
            return "BULL"
        elif self.deviation_pct < -5:
            return "BEAR"
        else:
            return "NEUTRAL"
    
    def _get_regime_emoji(self) -> str:
        """Get emoji representing current regime."""
        regime_emojis = {
            "BULL": "🐂",
            "BEAR": "🐻",
            "NEUTRAL": "⚖️",
            "UNKNOWN": "❓"
        }
        return regime_emojis.get(self.market_regime, "⚖️")
    
    def _calculate_adaptive_threshold(self) -> float:
        """
        Calculate adaptive RSI threshold based on regime.
        
        Returns:
            RSI threshold (42.0 for BULL, 48.0 for BEAR, 45.0 for NEUTRAL/UNKNOWN)
        """
        threshold_map = {
            "BULL": 42.0,      # More selective in bull markets
            "BEAR": 48.0,      # More aggressive in bear markets
            "NEUTRAL": 45.0,   # Standard threshold
            "UNKNOWN": 45.0    # Default to standard
        }
        return threshold_map.get(self.market_regime, 45.0)
    
    def _determine_vix_level(self) -> Optional[str]:
        """
        Determine VIX level category.
        
        Returns:
            "Low", "Medium", "High", or None if VIX unavailable
        """
        if self.vix is None:
            return None
        
        if self.vix < 15:
            return "Low"
        elif self.vix < 25:
            return "Medium"
        else:
            return "High"
    
    def _calculate_volatility_sizing(self) -> float:
        """
        Calculate rainy day amount based on VIX volatility.
        
        Returns:
            Rainy amount in CAD (150, 180, or 210)
        """
        if self.vix is None:
            return 150.0  # Default
        
        if self.vix < 15:
            return 150.0  # Standard
        elif self.vix < 25:
            return 180.0  # +20%
        else:
            return 210.0  # +40%
    
    def get_regime_description(self) -> str:
        """Get human-readable regime description with threshold."""
        descriptions = {
            "BULL": f"Bull Market (SPY > 200MA +5%)",
            "BEAR": f"Bear Market (SPY < 200MA -5%)",
            "NEUTRAL": f"Neutral Market (SPY ±5% of 200MA)",
            "UNKNOWN": f"Market Regime Unknown (200MA data unavailable)"
        }
        return descriptions.get(self.market_regime, "Neutral Market")
    
    def get_regime_threshold_line(self) -> str:
        """Get regime explanation line for email."""
        if self.market_regime == "BULL":
            return f"BULL (SPY > 200MA +5%) → Selective RSI < 42"
        elif self.market_regime == "BEAR":
            return f"BEAR (SPY < 200MA -5%) → Aggressive RSI < 48"
        else:  # NEUTRAL or UNKNOWN
            return f"NEUTRAL (±5% 200MA) → Standard RSI < 45"
    
    def get_vix_sizing_line(self) -> str:
        """Get VIX-based sizing explanation line."""
        if self.vix_level == "Low":
            return "Low VIX (<15) → Standard rainy $150"
        elif self.vix_level == "Medium":
            return "Medium VIX (15-25) → Enhanced rainy $180 (+20%)"
        elif self.vix_level == "High":
            return "High VIX (>25) → Max rainy $210 (+40%)"
        else:
            return "VIX unavailable → Default rainy $150"
    
    def get_all_metrics(self) -> Dict:
        """
        Get all calculated metrics as dictionary.
        
        Returns:
            Dictionary with all metric values formatted for template
        """
        return {
            # Price metrics
            "price": self.price,
            "spy_200ma": self.spy_200ma,
            "ma_plus_5_pct": self.ma_plus_5_pct,
            "ma_minus_5_pct": self.ma_minus_5_pct,
            "deviation_pct": self.deviation_pct,
            
            # Regime metrics
            "market_regime": self.market_regime,
            "regime_emoji": self.regime_emoji,
            "adaptive_threshold": self.adaptive_threshold,
            
            # VIX metrics
            "vix": self.vix,
            "vix_level": self.vix_level,
            "volatility_sizing": self.volatility_sizing,
            
            # RSI metrics
            "rsi_sma": self.rsi_sma,
            
            # Display strings
            "regime_description": self.get_regime_description(),
            "regime_threshold_line": self.get_regime_threshold_line(),
            "vix_sizing_line": self.get_vix_sizing_line(),
            
            # Formatted display values
            "price_display": f"${self.price:.2f}",
            "spy_200ma_display": f"${self.spy_200ma:.2f}" if self.spy_200ma else "N/A",
            "ma_plus_5_display": f"${self.ma_plus_5_pct:.2f}" if self.ma_plus_5_pct else "N/A",
            "ma_minus_5_display": f"${self.ma_minus_5_pct:.2f}" if self.ma_minus_5_pct else "N/A",
            "deviation_display": f"{self.deviation_pct:+.1f}%" if self.deviation_pct is not None else "N/A",
            "vix_display": f"{self.vix:.1f}" if self.vix is not None else "N/A",
            "vix_level_display": self.vix_level or "N/A",
            "rsi_sma_display": f"{self.rsi_sma:.2f}" if self.rsi_sma is not None else "N/A"
        }


def calculate_market_metrics(price: float, spy_200ma: Optional[float] = None, 
                            vix: Optional[float] = None, rsi_sma: Optional[float] = None) -> MarketMetrics:
    """
    Convenience function to create MarketMetrics instance.
    
    Args:
        price: Current SPY price
        spy_200ma: 200-day moving average (optional)
        vix: VIX volatility index (optional)
        rsi_sma: RSI SMA(7) smoothed value (optional)
    
    Returns:
        MarketMetrics instance with all calculated values
    
    Example:
        >>> metrics = calculate_market_metrics(450.0, 428.50, 18.5, 38.5)
        >>> print(metrics.market_regime)  # "BULL"
        >>> print(metrics.adaptive_threshold)  # 42.0
        >>> print(metrics.volatility_sizing)  # 180.0
    """
    return MarketMetrics(price, spy_200ma, vix, rsi_sma)
