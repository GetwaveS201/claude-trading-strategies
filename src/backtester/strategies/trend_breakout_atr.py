"""
Trend Breakout ATR Strategy - Pine Script Conversion

Buy when price breaks above Donchian high while above EMA trend
Exit on trailing ATR stop or trend flip
"""

from ..engine import Strategy, Context
from ..indicators import EMA, ATR, RollingHigh, RollingLow


class TrendBreakoutATRStrategy(Strategy):
    """
    Trend-following breakout strategy with ATR-based stops

    Parameters:
        trend_length: EMA length for trend filter (default: 200)
        breakout_length: Donchian channel lookback (default: 20)
        atr_length: ATR calculation period (default: 14)
        atr_stop_mult: ATR multiplier for initial stop (default: 2.0)
        atr_trail_mult: ATR multiplier for trailing stop (default: 3.0)
        min_atr_pct: Minimum ATR% for volatility filter (default: 1.0)
        risk_pct: Risk % per trade (default: 1.0)
    """

    def __init__(
        self,
        trend_length: int = 200,
        breakout_length: int = 20,
        atr_length: int = 14,
        atr_stop_mult: float = 2.0,
        atr_trail_mult: float = 3.0,
        min_atr_pct: float = 1.0,
        risk_pct: float = 1.0,
    ):
        super().__init__(
            trend_length=trend_length,
            breakout_length=breakout_length,
            atr_length=atr_length,
            atr_stop_mult=atr_stop_mult,
            atr_trail_mult=atr_trail_mult,
            min_atr_pct=min_atr_pct,
            risk_pct=risk_pct,
        )
        self.trend_length = trend_length
        self.breakout_length = breakout_length
        self.atr_length = atr_length
        self.atr_stop_mult = atr_stop_mult
        self.atr_trail_mult = atr_trail_mult
        self.min_atr_pct = min_atr_pct
        self.risk_pct = risk_pct

        # Indicators
        self.trend_ema = EMA(trend_length)
        self.atr = ATR(atr_length)
        self.rolling_high = RollingHigh(breakout_length)

        # State
        self.prev_high = None
        self.entry_price = None
        self.trail_stop = None

    def on_start(self):
        """Initialize strategy"""
        print(
            f"Starting Trend Breakout ATR Strategy "
            f"(EMA={self.trend_length}, Breakout={self.breakout_length}, "
            f"ATR={self.atr_length}x{self.atr_stop_mult}/{self.atr_trail_mult})"
        )

    def on_bar(self, context: Context):
        """Process each bar"""
        # Update indicators
        self.trend_ema.update(context.close)
        self.atr.update(context.high, context.low, context.close)
        self.rolling_high.update(context.high)

        # Get current values
        ema = self.trend_ema.get_value()
        atr = self.atr.get_value()
        highest = self.rolling_high.get_value()

        # Need indicators ready
        if ema is None or atr is None or highest is None:
            return

        # Calculate ATR%
        atr_pct = (atr / context.close) * 100

        # Trend condition
        bull_trend = context.close > ema

        # Volatility filter
        vol_ok = atr_pct >= self.min_atr_pct

        # Entry: breakout of prior highest high
        breakout = False
        if self.prev_high is not None:
            if context.close > self.prev_high:
                breakout = True

        # Entry logic
        if breakout and bull_trend and vol_ok and context.position == 0:
            # ATR-based position sizing
            stop_distance = atr * self.atr_stop_mult
            context.buy(risk_pct=self.risk_pct, stop_distance=stop_distance)
            self.entry_price = context.close
            self.trail_stop = context.close - (atr * self.atr_trail_mult)

        # Exit logic
        if context.position > 0:
            # Update trailing stop
            if context.close > self.entry_price:
                self.trail_stop = max(
                    self.trail_stop, context.close - (atr * self.atr_trail_mult)
                )

            # Exit conditions
            exit_on_stop = context.close <= self.trail_stop
            exit_on_trend = context.close < ema

            if exit_on_stop or exit_on_trend:
                context.sell()
                self.entry_price = None
                self.trail_stop = None

        # Update previous high
        self.prev_high = highest

    def on_end(self):
        """Cleanup"""
        pass
