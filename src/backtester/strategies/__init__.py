"""
Built-in trading strategies
"""

from .ma_cross import MACrossStrategy
from .rsi_meanrev import RSIMeanReversionStrategy

__all__ = ["MACrossStrategy", "RSIMeanReversionStrategy"]

# Registry for CLI access
STRATEGIES = {
    "ma_cross": MACrossStrategy,
    "rsi_meanrev": RSIMeanReversionStrategy,
}
