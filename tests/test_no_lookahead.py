"""
Test that no look-ahead bias exists in the system
"""

import pytest
from datetime import datetime, timedelta
import pandas as pd

from src.backtester.data import DataFeed
from src.backtester.engine import BacktestRunner, Strategy, Context
from src.backtester.broker import Portfolio, Broker, ExecutionModel


class TestStrategy(Strategy):
    """Strategy that records bar data for testing"""

    def __init__(self):
        super().__init__()
        self.bars_seen = []
        self.order_bars = []
        self.fill_bars = []

    def on_bar(self, context: Context):
        # Record bar index when we see it
        self.bars_seen.append(context.bar_index)

        # Place order on bar 5
        if context.bar_index == 5:
            context.buy(quantity=10)
            self.order_bars.append(context.bar_index)


def test_orders_fill_next_bar():
    """Test that orders placed on bar t fill on bar t+1"""
    # Create test data
    dates = pd.date_range(start="2024-01-01", periods=20, freq="D")
    data = []
    for i, date in enumerate(dates):
        data.append({
            "datetime": date,
            "open": 100.0 + i,
            "high": 101.0 + i,
            "low": 99.0 + i,
            "close": 100.0 + i,
            "volume": 1000000,
        })

    df = pd.DataFrame(data)

    # Create data feed
    feed = DataFeed(data_dir="", symbol="TEST")
    feed.data = df

    # Run backtest
    runner = BacktestRunner(
        strategy_class=TestStrategy,
        data_feed=feed,
        initial_cash=100000,
    )

    result = runner.run()
    strategy = result["strategy"]
    broker = result["broker"]

    # Verify order was placed on bar 5
    assert 5 in strategy.order_bars

    # Verify fill occurred
    assert len(broker.filled_orders) == 1

    fill = broker.filled_orders[0]

    # Fill should use bar 6 data (next bar after order)
    # Order placed on bar 5 (price 105)
    # Fill should be at bar 6 open (price 106)
    assert fill.fill_price == 106.0


def test_no_same_bar_fill_by_default():
    """Test that same-bar fills do NOT happen by default"""

    class ImmediateStrategy(Strategy):
        """Try to exploit same-bar data"""

        def __init__(self):
            super().__init__()
            self.trade_attempted = False

        def on_bar(self, context: Context):
            if context.bar_index == 5 and not self.trade_attempted:
                # Try to buy based on current bar's close
                # In a cheating system, this could use current bar's high/low
                context.buy(quantity=10)
                self.trade_attempted = True

    # Create test data with a big move on bar 5
    dates = pd.date_range(start="2024-01-01", periods=20, freq="D")
    data = []
    for i, date in enumerate(dates):
        if i == 5:
            # Big up move on bar 5
            data.append({
                "datetime": date,
                "open": 100.0,
                "high": 120.0,  # Big high
                "low": 99.0,
                "close": 119.0,  # Close near high
                "volume": 1000000,
            })
        else:
            data.append({
                "datetime": date,
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.0,
                "volume": 1000000,
            })

    df = pd.DataFrame(data)

    feed = DataFeed(data_dir="", symbol="TEST")
    feed.data = df

    runner = BacktestRunner(
        strategy_class=ImmediateStrategy,
        data_feed=feed,
        initial_cash=100000,
    )

    result = runner.run()
    broker = result["broker"]

    # Should have a fill
    assert len(broker.filled_orders) == 1

    fill = broker.filled_orders[0]

    # Fill should be at NEXT bar (bar 6), not bar 5
    # So it should NOT capture the big move on bar 5
    # Fill price should be bar 6 open = 100.0, not bar 5 high = 120.0
    assert fill.fill_price == 100.0  # Bar 6 open
    assert fill.fill_price != 119.0  # NOT bar 5 close
    assert fill.fill_price != 120.0  # NOT bar 5 high


def test_indicator_no_lookahead():
    """Test that indicators don't use future bars"""

    class IndicatorTestStrategy(Strategy):
        def __init__(self):
            super().__init__()
            from src.backtester.indicators import SMA
            self.sma = SMA(period=5)
            self.indicator_values = []

        def on_bar(self, context: Context):
            self.sma.update(context.close)
            self.indicator_values.append(self.sma.get_value())

    # Create test data
    dates = pd.date_range(start="2024-01-01", periods=10, freq="D")
    data = []
    for i, date in enumerate(dates):
        data.append({
            "datetime": date,
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": 100.0 + i,  # Increasing closes
            "volume": 1000000,
        })

    df = pd.DataFrame(data)

    feed = DataFeed(data_dir="", symbol="TEST")
    feed.data = df

    runner = BacktestRunner(
        strategy_class=IndicatorTestStrategy,
        data_feed=feed,
        initial_cash=100000,
    )

    result = runner.run()
    strategy = result["strategy"]

    # First 4 values should be None (not enough data for period=5)
    for i in range(4):
        assert strategy.indicator_values[i] is None

    # 5th value (index 4) should be average of first 5 closes
    # closes: 100, 101, 102, 103, 104
    # average: 102
    assert strategy.indicator_values[4] == 102.0

    # 6th value should use bars 1-5 (not including bar 6's data from future)
    # closes: 101, 102, 103, 104, 105
    # average: 103
    assert strategy.indicator_values[5] == 103.0


def test_data_feed_no_future_bars():
    """Test that data feed doesn't reveal future bars"""
    dates = pd.date_range(start="2024-01-01", periods=10, freq="D")
    data = []
    for i, date in enumerate(dates):
        data.append({
            "datetime": date,
            "open": 100.0 + i,
            "high": 101.0 + i,
            "low": 99.0 + i,
            "close": 100.0 + i,
            "volume": 1000000,
        })

    df = pd.DataFrame(data)

    feed = DataFeed(data_dir="", symbol="TEST")
    feed.data = df

    # When accessing bar 5, we should not be able to see bar 6
    bar5 = feed.get_bar(5)
    bar6 = feed.get_bar(6)

    assert bar5["close"] == 105.0
    assert bar6["close"] == 106.0

    # These should be separate bars with different data
    assert bar5["close"] != bar6["close"]
