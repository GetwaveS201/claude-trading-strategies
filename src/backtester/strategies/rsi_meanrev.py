"""
RSI Mean Reversion Strategy

Buy when RSI crosses below oversold threshold
Sell when RSI crosses above overbought threshold
"""

from ..engine import Strategy, Context
from ..indicators import RSI


class RSIMeanReversionStrategy(Strategy):
    """
    RSI mean reversion strategy

    Parameters:
        rsi_period: RSI period (default: 14)
        oversold: Oversold threshold (default: 30)
        overbought: Overbought threshold (default: 70)
        position_pct: Percent of equity per trade (default: 95)
    """

    def __init__(
        self,
        rsi_period: int = 14,
        oversold: float = 30.0,
        overbought: float = 70.0,
        position_pct: float = 95.0,
    ):
        super().__init__(
            rsi_period=rsi_period,
            oversold=oversold,
            overbought=overbought,
            position_pct=position_pct,
        )
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
        self.position_pct = position_pct

        # Indicator
        self.rsi = RSI(rsi_period)

        # State
        self.prev_rsi = None

    def on_start(self):
        """Initialize strategy"""
        print(
            f"Starting RSI Mean Reversion Strategy "
            f"(period={self.rsi_period}, oversold={self.oversold}, overbought={self.overbought})"
        )

    def on_bar(self, context: Context):
        """Process each bar"""
        # Update RSI
        self.rsi.update(context.close)

        # Get current RSI
        rsi = self.rsi.get_value()

        # Need RSI ready
        if rsi is None:
            return

        # Check for signals
        if self.prev_rsi is not None:
            # Oversold signal: RSI crosses below oversold threshold
            if self.prev_rsi >= self.oversold and rsi < self.oversold:
                if context.position == 0:
                    # Enter long
                    context.buy(percent=self.position_pct)

            # Overbought signal: RSI crosses above overbought threshold
            elif self.prev_rsi <= self.overbought and rsi > self.overbought:
                if context.position > 0:
                    # Exit long
                    context.sell()

        # Update previous RSI
        self.prev_rsi = rsi

    def on_end(self):
        """Cleanup"""
        pass
