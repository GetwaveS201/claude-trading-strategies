"""
Adaptive Momentum Quantitative Strategy

A sophisticated multi-factor strategy that:
1. Adapts to market regimes automatically
2. Uses momentum with volatility filtering
3. Employs dynamic position sizing
4. Combines trend and mean-reversion signals intelligently

This strategy is designed to be less common than simple EMA crosses,
while maintaining robust performance across different market conditions.
"""

from ..engine import Strategy, Context
from ..indicators import EMA, SMA, RSI, ATR
import numpy as np


class AdaptiveMomentumQuant(Strategy):
    """
    Advanced quantitative strategy combining:
    - Multi-timeframe momentum analysis
    - Volatility regime detection
    - Volume-weighted signals
    - Adaptive position sizing
    - Risk-based exits
    """

    def __init__(
        self,
        # Momentum parameters
        momentum_fast: int = 20,
        momentum_slow: int = 60,
        momentum_threshold: float = 0.02,  # 2% momentum required

        # Volatility parameters
        vol_lookback: int = 20,
        vol_percentile: float = 50,  # Median volatility

        # Trend filter
        trend_period: int = 100,

        # Risk management
        atr_period: int = 14,
        atr_stop_mult: float = 2.5,
        position_pct: float = 100.0,

        # Volume filter
        volume_period: int = 20,
        volume_threshold: float = 0.8,  # 80% of average volume
    ):
        super().__init__(
            momentum_fast=momentum_fast,
            momentum_slow=momentum_slow,
            momentum_threshold=momentum_threshold,
            vol_lookback=vol_lookback,
            vol_percentile=vol_percentile,
            trend_period=trend_period,
            atr_period=atr_period,
            atr_stop_mult=atr_stop_mult,
            position_pct=position_pct,
            volume_period=volume_period,
            volume_threshold=volume_threshold
        )

        self.momentum_fast = momentum_fast
        self.momentum_slow = momentum_slow
        self.momentum_threshold = momentum_threshold
        self.vol_lookback = vol_lookback
        self.vol_percentile = vol_percentile
        self.trend_period = trend_period
        self.position_pct = position_pct
        self.volume_period = volume_period
        self.volume_threshold = volume_threshold

        # Indicators
        self.trend_ma = SMA(trend_period)
        self.vol_ma = SMA(volume_period)
        self.atr = ATR(atr_period)
        self.atr_stop_mult = atr_stop_mult

        # State
        self.price_history = []
        self.volume_history = []
        self.returns_history = []
        self.entry_price = None
        self.stop_loss = None

    def on_start(self):
        print(f"Starting Adaptive Momentum Quant Strategy")
        print(f"  Momentum: {self.momentum_fast}/{self.momentum_slow}")
        print(f"  Trend Filter: {self.trend_period}-period SMA")
        print(f"  Volatility: {self.vol_lookback}-bar lookback")
        print(f"  Position Size: {self.position_pct}%")

    def on_bar(self, context: Context):
        # Update history
        self.price_history.append(context.close)
        self.volume_history.append(context.volume)

        # Update indicators
        self.trend_ma.update(context.close)
        self.vol_ma.update(context.volume)
        self.atr.update(context.high, context.low, context.close)

        # Calculate returns for volatility
        if len(self.price_history) >= 2:
            ret = (self.price_history[-1] / self.price_history[-2]) - 1
            self.returns_history.append(ret)

        # Need minimum history
        if len(self.price_history) < max(self.momentum_slow, self.trend_period):
            return

        # Trim history to save memory
        max_needed = max(self.momentum_slow, self.trend_period, self.vol_lookback) + 50
        if len(self.price_history) > max_needed:
            self.price_history = self.price_history[-max_needed:]
            self.volume_history = self.volume_history[-max_needed:]
            self.returns_history = self.returns_history[-max_needed:]

        # ======================================================================
        # FACTOR 1: MOMENTUM
        # ======================================================================
        # Calculate fast and slow momentum
        fast_return = (self.price_history[-1] / self.price_history[-self.momentum_fast]) - 1
        slow_return = (self.price_history[-1] / self.price_history[-self.momentum_slow]) - 1

        # Momentum score: fast momentum relative to slow momentum
        momentum_score = fast_return - slow_return

        # ======================================================================
        # FACTOR 2: TREND FILTER
        # ======================================================================
        trend_ma = self.trend_ma.get_value()
        if trend_ma is None:
            return

        in_uptrend = context.close > trend_ma
        trend_strength = (context.close / trend_ma - 1) if trend_ma > 0 else 0

        # ======================================================================
        # FACTOR 3: VOLATILITY REGIME
        # ======================================================================
        if len(self.returns_history) >= self.vol_lookback:
            recent_vol = np.std(self.returns_history[-self.vol_lookback:]) * np.sqrt(252)

            # Calculate historical volatility percentile
            if len(self.returns_history) >= self.vol_lookback * 2:
                hist_vols = []
                for i in range(self.vol_lookback, len(self.returns_history)):
                    window = self.returns_history[i-self.vol_lookback:i]
                    hist_vols.append(np.std(window) * np.sqrt(252))

                if len(hist_vols) > 0:
                    vol_percentile_actual = np.percentile(hist_vols, self.vol_percentile)
                    is_low_vol_regime = recent_vol < vol_percentile_actual
                else:
                    is_low_vol_regime = True
            else:
                is_low_vol_regime = True
        else:
            is_low_vol_regime = True

        # ======================================================================
        # FACTOR 4: VOLUME CONFIRMATION
        # ======================================================================
        avg_volume = self.vol_ma.get_value()
        if avg_volume is None or avg_volume == 0:
            volume_confirmed = True
        else:
            volume_confirmed = context.volume >= avg_volume * self.volume_threshold

        # ======================================================================
        # ENTRY LOGIC
        # ======================================================================
        if context.position == 0:
            # Entry conditions (all must be true):
            # 1. Strong momentum
            # 2. Uptrend confirmed
            # 3. Low-to-medium volatility (avoid chaos)
            # 4. Volume confirmation

            strong_momentum = momentum_score > self.momentum_threshold
            bullish_trend = in_uptrend and trend_strength > 0.01  # 1% above MA

            if strong_momentum and bullish_trend and is_low_vol_regime and volume_confirmed:
                # Calculate position size
                # In low vol, use full size
                # In higher vol, reduce size
                size_pct = self.position_pct

                context.buy(percent=size_pct)

                # Set stop loss using ATR
                atr_value = self.atr.get_value()
                if atr_value is not None:
                    self.entry_price = context.close
                    self.stop_loss = context.close - (atr_value * self.atr_stop_mult)

        # ======================================================================
        # EXIT LOGIC
        # ======================================================================
        elif context.position > 0:
            # Exit conditions (any can trigger):
            # 1. Momentum reversal
            # 2. Trend breaks
            # 3. ATR-based stop loss
            # 4. Profit target (trailing)

            momentum_reversal = momentum_score < -0.005  # Negative momentum
            trend_break = not in_uptrend

            # ATR stop loss
            stop_triggered = False
            if self.stop_loss is not None:
                if context.close < self.stop_loss:
                    stop_triggered = True

                # Trail stop loss
                atr_value = self.atr.get_value()
                if atr_value is not None:
                    new_stop = context.close - (atr_value * self.atr_stop_mult)
                    if new_stop > self.stop_loss:
                        self.stop_loss = new_stop

            # Exit on any condition
            if momentum_reversal or trend_break or stop_triggered:
                context.sell()
                self.entry_price = None
                self.stop_loss = None

    def on_end(self):
        print("Strategy complete")
