"""
Test indicator calculations
"""

import pytest
from src.backtester.indicators import SMA, EMA, RSI, ATR


def test_sma_basic():
    """Test SMA calculation on known data"""
    sma = SMA(period=3)

    values = [10, 20, 30, 40, 50]

    for val in values:
        sma.update(val)

    # First 2 values should be None (not enough data)
    assert sma.values[0] is None
    assert sma.values[1] is None

    # Third value: (10 + 20 + 30) / 3 = 20
    assert sma.values[2] == 20.0

    # Fourth value: (20 + 30 + 40) / 3 = 30
    assert sma.values[3] == 30.0

    # Fifth value: (30 + 40 + 50) / 3 = 40
    assert sma.values[4] == 40.0


def test_sma_current_value():
    """Test getting current SMA value"""
    sma = SMA(period=3)

    for val in [10, 20, 30, 40]:
        sma.update(val)

    # Most recent value
    assert sma.get_value() == 30.0
    assert sma.get_value(-1) == 30.0

    # Previous value
    assert sma.get_value(-2) == 20.0


def test_ema_initialization():
    """Test EMA initializes with SMA"""
    ema = EMA(period=3)

    values = [10, 20, 30]

    for val in values:
        ema.update(val)

    # First 2 values should be None
    assert ema.values[0] is None
    assert ema.values[1] is None

    # Third value should be SMA: (10 + 20 + 30) / 3 = 20
    assert ema.values[2] == 20.0


def test_ema_calculation():
    """Test EMA calculation after initialization"""
    ema = EMA(period=3)

    values = [10, 20, 30, 40, 50]

    for val in values:
        ema.update(val)

    # After initialization, EMA should be computed
    # alpha = 2 / (3 + 1) = 0.5
    # EMA[2] = 20 (SMA initialization)
    # EMA[3] = 0.5 * 40 + 0.5 * 20 = 30
    # EMA[4] = 0.5 * 50 + 0.5 * 30 = 40
    assert ema.values[3] == 30.0
    assert ema.values[4] == 40.0


def test_rsi_calculation():
    """Test RSI calculation"""
    rsi = RSI(period=14)

    # Simplified test: alternating up/down moves
    prices = [100, 101, 100, 101, 100, 101, 100, 101, 100, 101, 100, 101, 100, 101, 100]

    for price in prices:
        rsi.update(price)

    # RSI should be around 50 for balanced up/down moves
    rsi_val = rsi.get_value()
    assert rsi_val is not None
    assert 40 < rsi_val < 60


def test_rsi_oversold():
    """Test RSI in oversold condition"""
    rsi = RSI(period=5)

    # Downtrend
    prices = [100, 99, 98, 97, 96, 95]

    for price in prices:
        rsi.update(price)

    rsi_val = rsi.get_value()
    assert rsi_val is not None
    assert rsi_val < 50  # Should be low


def test_rsi_overbought():
    """Test RSI in overbought condition"""
    rsi = RSI(period=5)

    # Uptrend
    prices = [100, 101, 102, 103, 104, 105]

    for price in prices:
        rsi.update(price)

    rsi_val = rsi.get_value()
    assert rsi_val is not None
    assert rsi_val > 50  # Should be high


def test_atr_basic():
    """Test ATR calculation"""
    atr = ATR(period=3)

    # bars: [high, low, close]
    bars = [
        (102, 98, 100),
        (103, 99, 101),
        (104, 100, 102),
        (105, 101, 103),
    ]

    for high, low, close in bars:
        atr.update(high, low, close)

    # First bar: TR = high - low = 4
    # Second bar: TR includes prev close
    # Third bar: TR includes prev close
    # ATR should be average of last 3 TRs

    atr_val = atr.get_value()
    assert atr_val is not None
    assert atr_val > 0


def test_indicators_no_lookahead():
    """Test that indicators never use future data"""
    sma = SMA(period=3)

    # Add values one by one
    for i, val in enumerate([10, 20, 30, 40, 50]):
        sma.update(val)

        # Indicator should have exactly i+1 values
        assert len(sma.values) == i + 1

        # Should not have more values than data points
        assert len(sma.values) <= i + 1
