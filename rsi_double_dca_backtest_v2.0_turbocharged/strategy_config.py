"""
Strategy Configuration Module
==============================

Centralized configuration for all strategy parameters.
Uses dataclasses for type safety and immutability.

Usage:
    from strategy_config import get_strategy_config
    
    config = get_strategy_config('VARIANT_2')
    if config.is_rainy_day(rsi_sma=38.5):
        deploy_amount = config.get_deployment_amount()
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Callable
from abc import ABC, abstractmethod
from enum import Enum


class RSIIndicatorType(Enum):
    """Types of RSI indicators for threshold evaluation."""
    RAW_RSI = "raw_rsi"  # Raw RSI(14) value
    RSI_SMA = "rsi_sma"  # 7-day SMA of RSI(14)
    RSI_EMA = "rsi_ema"  # 7-day EMA of RSI(14)


@dataclass(frozen=True)
class StrategyConfig:
    """
    Immutable strategy configuration.
    
    All strategy parameters are defined here. Change these values
    to modify strategy behavior across the entire system.
    """
    
    # Strategy identification
    name: str
    variant_number: int
    
    # Cash deployment amounts (CAD)
    dca_base_amount: float = 150.0
    rainy_extra_amount: float = 150.0
    cash_accumulation_per_payday: float = 30.0
    initial_cash_pool: float = 330.0
    
    # RSI configuration
    rsi_period: int = 14  # RSI calculation period
    rsi_indicator_type: RSIIndicatorType = RSIIndicatorType.RSI_SMA
    rsi_sma_period: int = 7  # SMA period for RSI smoothing
    rsi_threshold: float = 45.0  # Rainy day threshold
    
    # Payday configuration
    payday_days: tuple = field(default=(3, 17))
    trading_exchange: str = 'TSX'
    
    # Expected performance (for documentation)
    expected_hit_rate: float = 0.24  # ~24% of paydays
    backtest_period: str = "Oct 2003 - Nov 2025"
    
    def is_rainy_day(
        self, 
        rsi: Optional[float] = None,
        rsi_sma: Optional[float] = None,
        rsi_ema: Optional[float] = None
    ) -> bool:
        """
        Determine if current market conditions represent a rainy day.
        
        This is the SINGLE SOURCE OF TRUTH for rainy day evaluation.
        All code in the system calls this method.
        
        Args:
            rsi: Raw RSI(14) value
            rsi_sma: 7-day SMA of RSI(14)
            rsi_ema: 7-day EMA of RSI(14)
        
        Returns:
            True if rainy day conditions are met
        
        Raises:
            ValueError: If required indicator is not provided
        
        Example:
            >>> config = get_strategy_config('VARIANT_2')
            >>> config.is_rainy_day(rsi_sma=38.5)
            True  # 38.5 < 45.0
        """
        if self.rsi_indicator_type == RSIIndicatorType.RAW_RSI:
            if rsi is None:
                raise ValueError("Raw RSI value required for this strategy")
            return rsi < self.rsi_threshold
        
        elif self.rsi_indicator_type == RSIIndicatorType.RSI_SMA:
            if rsi_sma is None:
                raise ValueError("RSI SMA value required for this strategy")
            return rsi_sma < self.rsi_threshold
        
        elif self.rsi_indicator_type == RSIIndicatorType.RSI_EMA:
            if rsi_ema is None:
                raise ValueError("RSI EMA value required for this strategy")
            return rsi_ema < self.rsi_threshold
        
        else:
            raise ValueError(f"Unknown indicator type: {self.rsi_indicator_type}")
    
    def get_deployment_amount(self, is_rainy: bool) -> float:
        """
        Calculate total deployment amount for given conditions.
        
        Args:
            is_rainy: Whether it's a rainy day
        
        Returns:
            Total CAD amount to deploy
        
        Example:
            >>> config = get_strategy_config('VARIANT_2')
            >>> config.get_deployment_amount(is_rainy=True)
            300.0  # Base 150 + Rainy 150
        """
        if is_rainy:
            return self.dca_base_amount + self.rainy_extra_amount
        return self.dca_base_amount
    
    def get_indicator_display_name(self) -> str:
        """
        Get human-readable indicator name for display.
        
        Returns:
            Display name (e.g., "RSI SMA(7)")
        """
        if self.rsi_indicator_type == RSIIndicatorType.RAW_RSI:
            return f"RSI({self.rsi_period})"
        elif self.rsi_indicator_type == RSIIndicatorType.RSI_SMA:
            return f"RSI SMA({self.rsi_sma_period})"
        elif self.rsi_indicator_type == RSIIndicatorType.RSI_EMA:
            return f"RSI EMA({self.rsi_sma_period})"
        return "Unknown"
    
    def get_threshold_description(self) -> str:
        """
        Get complete threshold description for documentation.
        
        Returns:
            Description (e.g., "RSI SMA(7) < 45")
        """
        return f"{self.get_indicator_display_name()} < {self.rsi_threshold}"
    
    def update_cash_pool(
        self, 
        current_pool: float, 
        is_payday: bool,
        was_rainy_buy: bool
    ) -> float:
        """
        Calculate new cash pool balance.
        
        Args:
            current_pool: Current cash pool balance
            is_payday: Whether today is a payday
            was_rainy_buy: Whether a rainy buy was executed
        
        Returns:
            New cash pool balance
        """
        if not is_payday:
            return current_pool
        
        # Add payday accumulation
        new_pool = current_pool + self.cash_accumulation_per_payday
        
        # Subtract rainy deployment if executed
        if was_rainy_buy:
            new_pool -= self.rainy_extra_amount
        
        return new_pool


# =============================================================================
# PREDEFINED STRATEGY CONFIGURATIONS
# =============================================================================

STRATEGY_VARIANTS: Dict[str, StrategyConfig] = {
    'VARIANT_1': StrategyConfig(
        name="Weekly $150 RSI < 40",
        variant_number=1,
        dca_base_amount=150.0,
        rainy_extra_amount=150.0,
        rsi_indicator_type=RSIIndicatorType.RAW_RSI,
        rsi_threshold=40.0,
        payday_days=(1, 8, 15, 22),  # Weekly on Mondays
    ),
    
    'VARIANT_2': StrategyConfig(
        name="TURBO - Biweekly $150 RSI SMA(7) < 45",
        variant_number=2,
        dca_base_amount=150.0,
        rainy_extra_amount=150.0,
        cash_accumulation_per_payday=30.0,
        rsi_indicator_type=RSIIndicatorType.RSI_SMA,
        rsi_threshold=45.0,
        rsi_sma_period=7,
        payday_days=(3, 17),
        expected_hit_rate=0.24,
    ),
    
    'VARIANT_3': StrategyConfig(
        name="Weekly $100 RSI SMA(7) < 45",
        variant_number=3,
        dca_base_amount=100.0,
        rainy_extra_amount=100.0,
        cash_accumulation_per_payday=20.0,
        rsi_indicator_type=RSIIndicatorType.RSI_SMA,
        rsi_threshold=45.0,
        rsi_sma_period=7,
        payday_days=(1, 8, 15, 22),  # Weekly
    ),
}


def get_strategy_config(variant: str = 'VARIANT_2') -> StrategyConfig:
    """
    Get strategy configuration by variant name.
    
    Args:
        variant: Variant identifier ('VARIANT_1', 'VARIANT_2', 'VARIANT_3')
    
    Returns:
        StrategyConfig instance
    
    Raises:
        ValueError: If variant not found
    
    Example:
        >>> config = get_strategy_config('VARIANT_2')
        >>> print(config.get_threshold_description())
        'RSI SMA(7) < 45'
    """
    if variant not in STRATEGY_VARIANTS:
        raise ValueError(
            f"Unknown variant: {variant}. "
            f"Available: {list(STRATEGY_VARIANTS.keys())}"
        )
    return STRATEGY_VARIANTS[variant]


def register_strategy_variant(name: str, config: StrategyConfig) -> None:
    """
    Register a custom strategy variant.
    
    Args:
        name: Variant identifier
        config: StrategyConfig instance
    
    Example:
        >>> custom = StrategyConfig(
        ...     name="Custom Strategy",
        ...     variant_number=99,
        ...     rsi_threshold=50.0
        ... )
        >>> register_strategy_variant('CUSTOM', custom)
    """
    STRATEGY_VARIANTS[name] = config


def list_strategy_variants() -> Dict[str, str]:
    """
    List all available strategy variants.
    
    Returns:
        Dict mapping variant ID to strategy name
    """
    return {k: v.name for k, v in STRATEGY_VARIANTS.items()}
