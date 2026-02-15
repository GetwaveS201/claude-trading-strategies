"""
Leveraged Trend Strategy - Uses 2x position sizing to amplify returns

WARNING: This uses leverage (200% exposure) which increases risk
"""

from ..engine import Strategy, Context
from ..indicators import EMA


class LeveragedTrendStrategy(Strategy):
    """
    Simple leveraged trend-following strategy

    Uses 2x leverage by allocating 200% of equity when in position
    Only enters during strong uptrends
    """

    def __init__(
        self,
        fast: int = 10,
        slow: int = 50,
        position_pct: float = 200.0,  # 2x leverage
    ):
        super().__init__(fast=fast, slow=slow, position_pct=position_pct)
        self.fast_period = fast
        self.slow_period = slow
        self.position_pct = position_pct

        # Indicators
        self.fast_ma = EMA(fast)
        self.slow_ma = EMA(slow)

        # State
        self.prev_fast = None
        self.prev_slow = None

    def on_start(self):
        """Initialize strategy"""
        print(
            f"Starting Leveraged Trend Strategy "
            f"(EMA {self.fast_period}/{self.slow_period}, {self.position_pct}% exposure)"
        )

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
                    # Enter with leverage
                    context.buy(percent=self.position_pct)

            # Bearish cross: fast crosses below slow
            elif self.prev_fast >= self.prev_slow and fast < slow:
                if context.position > 0:
                    # Exit
                    context.sell()

        # Update previous values
        self.prev_fast = fast
        self.prev_slow = slow

    def on_end(self):
        """Cleanup"""
        pass
