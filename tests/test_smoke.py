"""
Smoke test - run a full backtest end-to-end
"""

import pytest
import pandas as pd
from pathlib import Path
import shutil

from src.backtester.data import DataFeed, generate_sample_data
from src.backtester.engine import BacktestRunner
from src.backtester.strategies import MACrossStrategy
from src.backtester.reporting import Reporter


def test_full_backtest_smoke():
    """
    Smoke test: Run a complete backtest and verify outputs are generated
    """
    # Generate sample data
    df = generate_sample_data(
        symbol="SPY",
        start_date="2020-01-01",
        end_date="2023-12-31",
        initial_price=300.0,
    )

    # Create data feed
    feed = DataFeed(data_dir="", symbol="SPY")
    feed.data = df

    # Run backtest
    runner = BacktestRunner(
        strategy_class=MACrossStrategy,
        data_feed=feed,
        initial_cash=100000,
        commission_per_fill=1.0,
        slippage_bps=1.0,
        fast=20,
        slow=50,
    )

    result = runner.run()

    # Verify components exist
    assert result["portfolio"] is not None
    assert result["broker"] is not None
    assert result["strategy"] is not None

    # Verify portfolio has equity history
    assert len(result["portfolio"].equity_history) > 0

    # Generate reports
    output_dir = Path("test_results") / "smoke_test"

    # Clean up if exists
    if output_dir.exists():
        shutil.rmtree(output_dir)

    config = {
        "strategy": "ma_cross",
        "symbol": "SPY",
        "initial_cash": 100000,
    }

    reporter = Reporter(result["portfolio"], result["broker"], config)
    metrics = reporter.save_results(output_dir)

    # Verify files were created
    assert (output_dir / "config.json").exists()
    assert (output_dir / "equity.csv").exists()
    assert (output_dir / "summary.json").exists()
    assert (output_dir / "charts").exists()
    assert (output_dir / "charts" / "equity_curve.png").exists()
    assert (output_dir / "charts" / "drawdown.png").exists()

    # Verify metrics are reasonable
    assert "cagr" in metrics
    assert "sharpe_ratio" in metrics
    assert "max_drawdown_pct" in metrics
    assert "num_trades" in metrics

    # Verify metrics have valid values
    assert isinstance(metrics["cagr"], (int, float))
    assert isinstance(metrics["sharpe_ratio"], (int, float))
    assert isinstance(metrics["num_trades"], int)

    # Clean up
    shutil.rmtree(output_dir)


def test_multiple_strategies():
    """Test that both included strategies can run"""
    from src.backtester.strategies import RSIMeanReversionStrategy

    df = generate_sample_data(
        symbol="SPY",
        start_date="2020-01-01",
        end_date="2022-12-31",
        initial_price=300.0,
    )

    feed = DataFeed(data_dir="", symbol="SPY")
    feed.data = df

    # Test MA Cross
    runner1 = BacktestRunner(
        strategy_class=MACrossStrategy,
        data_feed=feed,
        initial_cash=100000,
        fast=20,
        slow=50,
    )
    result1 = runner1.run()
    assert result1 is not None

    # Reset data feed
    feed.data = df.copy()

    # Test RSI Mean Reversion
    runner2 = BacktestRunner(
        strategy_class=RSIMeanReversionStrategy,
        data_feed=feed,
        initial_cash=100000,
        rsi_period=14,
        oversold=30,
        overbought=70,
    )
    result2 = runner2.run()
    assert result2 is not None


def test_no_trades_scenario():
    """Test backtest handles scenario with no trades"""

    class NoTradeStrategy:
        """Strategy that never trades"""

        def __init__(self):
            pass

        def on_start(self):
            pass

        def on_bar(self, context):
            pass  # Never place orders

        def on_end(self):
            pass

    df = generate_sample_data(
        symbol="SPY",
        start_date="2020-01-01",
        end_date="2021-12-31",
        initial_price=300.0,
    )

    feed = DataFeed(data_dir="", symbol="SPY")
    feed.data = df

    runner = BacktestRunner(
        strategy_class=NoTradeStrategy,
        data_feed=feed,
        initial_cash=100000,
    )

    result = runner.run()

    # Should complete without errors
    assert result is not None
    assert len(result["broker"].filled_orders) == 0

    # Generate report (should handle zero trades)
    from src.backtester.reporting import PerformanceMetrics

    metrics_calc = PerformanceMetrics(result["portfolio"], result["broker"])
    metrics = metrics_calc.calculate_metrics()

    assert metrics["num_trades"] == 0
    assert metrics["final_equity"] == 100000  # No change
