"""
Technical indicators with guaranteed no look-ahead

All indicators are computed using ONLY past and current bars
"""

import numpy as np
from typing import List, Optional


class Indicator:
    """Base class for indicators"""

    def __init__(self):
        self.values: List[Optional[float]] = []

    def update(self, value: float):
        """Update indicator with new value"""
        raise NotImplementedError

    def get_value(self, index: int = -1) -> Optional[float]:
        """Get indicator value at index (default: most recent)"""
        if not self.values:
            return None
        try:
            return self.values[index]
        except IndexError:
            return None

    def __len__(self) -> int:
        return len(self.values)

    def __getitem__(self, index: int) -> Optional[float]:
        return self.get_value(index)


class SMA(Indicator):
    """Simple Moving Average"""

    def __init__(self, period: int):
        super().__init__()
        self.period = period
        self.window: List[float] = []

    def update(self, value: float):
        """Add new value and compute SMA"""
        self.window.append(value)

        if len(self.window) > self.period:
            self.window.pop(0)

        if len(self.window) < self.period:
            self.values.append(None)
        else:
            self.values.append(sum(self.window) / self.period)


class EMA(Indicator):
    """Exponential Moving Average"""

    def __init__(self, period: int):
        super().__init__()
        self.period = period
        self.alpha = 2.0 / (period + 1)
        self.ema: Optional[float] = None
        self.window: List[float] = []  # For initial SMA

    def update(self, value: float):
        """Add new value and compute EMA"""
        if self.ema is None:
            # Initialize with SMA
            self.window.append(value)
            if len(self.window) < self.period:
                self.values.append(None)
            else:
                self.ema = sum(self.window) / self.period
                self.values.append(self.ema)
                self.window = []  # Clear window
        else:
            # Compute EMA
            self.ema = self.alpha * value + (1 - self.alpha) * self.ema
            self.values.append(self.ema)


class RSI(Indicator):
    """Relative Strength Index"""

    def __init__(self, period: int = 14):
        super().__init__()
        self.period = period
        self.gains: List[float] = []
        self.losses: List[float] = []
        self.prev_close: Optional[float] = None

    def update(self, close: float):
        """Update RSI with new close price"""
        if self.prev_close is None:
            self.prev_close = close
            self.values.append(None)
            return

        # Calculate change
        change = close - self.prev_close
        gain = max(change, 0.0)
        loss = max(-change, 0.0)

        self.gains.append(gain)
        self.losses.append(loss)

        if len(self.gains) > self.period:
            self.gains.pop(0)
            self.losses.pop(0)

        if len(self.gains) < self.period:
            self.values.append(None)
        else:
            avg_gain = sum(self.gains) / self.period
            avg_loss = sum(self.losses) / self.period

            if avg_loss == 0:
                rsi = 100.0
            else:
                rs = avg_gain / avg_loss
                rsi = 100.0 - (100.0 / (1.0 + rs))

            self.values.append(rsi)

        self.prev_close = close


class ATR(Indicator):
    """Average True Range"""

    def __init__(self, period: int = 14):
        super().__init__()
        self.period = period
        self.true_ranges: List[float] = []
        self.prev_close: Optional[float] = None

    def update(self, high: float, low: float, close: float):
        """Update ATR with OHLC data"""
        if self.prev_close is None:
            # First bar: TR is just high - low
            tr = high - low
        else:
            # True Range is max of:
            # 1. high - low
            # 2. abs(high - prev_close)
            # 3. abs(low - prev_close)
            tr = max(
                high - low,
                abs(high - self.prev_close),
                abs(low - self.prev_close),
            )

        self.true_ranges.append(tr)

        if len(self.true_ranges) > self.period:
            self.true_ranges.pop(0)

        if len(self.true_ranges) < self.period:
            self.values.append(None)
        else:
            atr = sum(self.true_ranges) / self.period
            self.values.append(atr)

        self.prev_close = close


class RollingHigh(Indicator):
    """Rolling highest value over period"""

    def __init__(self, period: int):
        super().__init__()
        self.period = period
        self.window: List[float] = []

    def update(self, value: float):
        """Add new value and compute rolling high"""
        self.window.append(value)

        if len(self.window) > self.period:
            self.window.pop(0)

        if len(self.window) < self.period:
            self.values.append(None)
        else:
            self.values.append(max(self.window))


class RollingLow(Indicator):
    """Rolling lowest value over period"""

    def __init__(self, period: int):
        super().__init__()
        self.period = period
        self.window: List[float] = []

    def update(self, value: float):
        """Add new value and compute rolling low"""
        self.window.append(value)

        if len(self.window) > self.period:
            self.window.pop(0)

        if len(self.window) < self.period:
            self.values.append(None)
        else:
            self.values.append(min(self.window))


class MACD(Indicator):
    """Moving Average Convergence Divergence"""

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        super().__init__()
        self.fast_ema = EMA(fast)
        self.slow_ema = EMA(slow)
        self.signal_ema = EMA(signal)
        self.macd_line: List[Optional[float]] = []
        self.signal_line: List[Optional[float]] = []
        self.histogram: List[Optional[float]] = []

    def update(self, close: float):
        """Update MACD with new close price"""
        self.fast_ema.update(close)
        self.slow_ema.update(close)

        fast_val = self.fast_ema.get_value()
        slow_val = self.slow_ema.get_value()

        if fast_val is None or slow_val is None:
            self.macd_line.append(None)
            self.signal_line.append(None)
            self.histogram.append(None)
            self.values.append(None)
        else:
            macd = fast_val - slow_val
            self.macd_line.append(macd)

            # Update signal line
            self.signal_ema.update(macd)
            signal = self.signal_ema.get_value()
            self.signal_line.append(signal)

            if signal is None:
                self.histogram.append(None)
                self.values.append(None)
            else:
                hist = macd - signal
                self.histogram.append(hist)
                self.values.append(macd)  # Return MACD line as main value

    def get_macd(self, index: int = -1) -> Optional[float]:
        """Get MACD line value"""
        try:
            return self.macd_line[index]
        except IndexError:
            return None

    def get_signal(self, index: int = -1) -> Optional[float]:
        """Get signal line value"""
        try:
            return self.signal_line[index]
        except IndexError:
            return None

    def get_histogram(self, index: int = -1) -> Optional[float]:
        """Get histogram value"""
        try:
            return self.histogram[index]
        except IndexError:
            return None
