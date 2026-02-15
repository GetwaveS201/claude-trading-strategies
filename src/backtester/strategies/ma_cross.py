"""
Moving Average Crossover Strategy

Buy when fast MA crosses above slow MA
Sell when fast MA crosses below slow MA
"""

from ..engine import Strategy, Context
from ..indicators import SMA


class MACrossStrategy(Strategy):
    """
    Simple moving average crossover strategy

    Parameters:
        fast: Fast MA period (default: 20)
        slow: Slow MA period (default: 50)
        position_pct: Percent of equity per trade (default: 95)
    """

    def __init__(self, fast: int = 20, slow: int = 50, position_pct: float = 95.0):
        super().__init__(fast=fast, slow=slow, position_pct=position_pct)
        self.fast_period = fast
        self.slow_period = slow
        self.position_pct = position_pct

        # Indicators
        self.fast_ma = SMA(fast)
        self.slow_ma = SMA(slow)

        # State
        self.prev_fast = None
        self.prev_slow = None

    def on_start(self):
        """Initialize strategy"""
        print(f"Starting MA Cross Strategy (fast={self.fast_period}, slow={self.slow_period})")

    def on_bar(self, context: Context):
        """Process each bar"""
        # Update indicators
        self.fast_ma.update(context.close)
        self.slow_ma.update(context.close)

        # Get current values
        fast = self.fast_ma.get_value()
        slow = self.slow_ma.get_value()

        # Need both indicators ready
        if fast is None or slow is None:
            return

        # Check for crossover
        if self.prev_fast is not None and self.prev_slow is not None:
            # Bullish cross: fast crosses above slow
            if self.prev_fast <= self.prev_slow and fast > slow:
                if context.position == 0:
                    # Enter long
                    context.buy(percent=self.position_pct)

            # Bearish cross: fast crosses below slow
            elif self.prev_fast >= self.prev_slow and fast < slow:
                if context.position > 0:
                    # Exit long
                    context.sell()

        # Update previous values
        self.prev_fast = fast
        self.prev_slow = slow

    def on_end(self):
        """Cleanup"""
        pass
