"""
Test strategies against SPY until we find one that beats buy & hold by 2x
"""

import sys
from pathlib import Path
from backtester.data import DataFeed
from backtester.engine import BacktestRunner
from backtester.strategies.trend_breakout_atr import TrendBreakoutATRStrategy
from backtester.reporting import PerformanceMetrics
import itertools


def test_strategy(strategy_class, params, data_feed, initial_cash=100000):
    """Run a single backtest and return metrics"""
    runner = BacktestRunner(
        strategy_class=strategy_class,
        data_feed=data_feed,
        initial_cash=initial_cash,
        commission_per_fill=1.0,
        slippage_bps=1.0,
        **params,
    )

    result = runner.run()
    metrics_calc = PerformanceMetrics(result["portfolio"], result["broker"])
    metrics = metrics_calc.calculate_metrics()

    return metrics, result


def calculate_buy_hold_return(data_feed):
    """Calculate buy & hold return for the period"""
    if data_feed.data is None or len(data_feed.data) == 0:
        return 0.0

    first_close = data_feed.data.iloc[0]["close"]
    last_close = data_feed.data.iloc[-1]["close"]

    return ((last_close / first_close) - 1) * 100


def main():
    """Test strategies until we beat 2x buy & hold"""

    print("=" * 80)
    print("SEARCHING FOR 2X SPY STRATEGY")
    print("=" * 80)

    # Load SPY data (full 10 year range for more trades)
    print("\n1. Loading SPY data...")
    data_feed = DataFeed(data_dir="./data", symbol="SPY")

    # First try sample data, if not enough generate longer data
    try:
        data_feed.load(start_date="2015-01-01", end_date="2015-12-31")
    except:
        from backtester.data import generate_sample_data
        print("   Generating synthetic 10-year data...")
        df = generate_sample_data(symbol="SPY", start_date="2015-01-01", end_date="2024-12-31", initial_price=200)
        data_feed.data = df
    print(f"   Loaded {len(data_feed)} bars")

    # Calculate buy & hold benchmark
    bh_return = calculate_buy_hold_return(data_feed)
    print(f"\n2. Buy & Hold Return: {bh_return:.2f}%")
    print(f"   Target (2x): {bh_return * 2:.2f}%")

    if bh_return <= 0:
        print("\n   ERROR: Buy & Hold is negative. Cannot achieve 2x.")
        return

    # Parameter grid for optimization
    param_sets = [
        # Conservative: Long EMA, moderate breakout
        {
            "trend_length": 200,
            "breakout_length": 20,
            "atr_stop_mult": 2.0,
            "atr_trail_mult": 3.0,
            "min_atr_pct": 1.0,
        },
        # Faster trend: Shorter EMA
        {
            "trend_length": 100,
            "breakout_length": 20,
            "atr_stop_mult": 2.0,
            "atr_trail_mult": 3.0,
            "min_atr_pct": 1.0,
        },
        # Faster breakout
        {
            "trend_length": 200,
            "breakout_length": 10,
            "atr_stop_mult": 2.0,
            "atr_trail_mult": 3.0,
            "min_atr_pct": 1.0,
        },
        # Tighter stops
        {
            "trend_length": 200,
            "breakout_length": 20,
            "atr_stop_mult": 1.5,
            "atr_trail_mult": 2.5,
            "min_atr_pct": 1.0,
        },
        # Wider stops
        {
            "trend_length": 200,
            "breakout_length": 20,
            "atr_stop_mult": 3.0,
            "atr_trail_mult": 4.0,
            "min_atr_pct": 1.0,
        },
        # Very fast
        {
            "trend_length": 50,
            "breakout_length": 10,
            "atr_stop_mult": 2.0,
            "atr_trail_mult": 3.0,
            "min_atr_pct": 0.5,
        },
        # Medium
        {
            "trend_length": 150,
            "breakout_length": 15,
            "atr_stop_mult": 2.5,
            "atr_trail_mult": 3.5,
            "min_atr_pct": 0.8,
        },
        # No vol filter
        {
            "trend_length": 200,
            "breakout_length": 20,
            "atr_stop_mult": 2.0,
            "atr_trail_mult": 3.0,
            "min_atr_pct": 0.0,
        },
    ]

    print(f"\n3. Testing {len(param_sets)} parameter combinations...\n")

    best_ratio = 0.0
    best_params = None
    best_metrics = None

    for i, params in enumerate(param_sets, 1):
        print(f"   [{i}/{len(param_sets)}] Testing: {params}")

        # Reset data feed
        try:
            data_feed.load(start_date="2015-01-01", end_date="2015-12-31")
        except:
            from backtester.data import generate_sample_data
            df = generate_sample_data(symbol="SPY", start_date="2015-01-01", end_date="2024-12-31", initial_price=200)
            data_feed.data = df

        # Run backtest
        metrics, result = test_strategy(
            TrendBreakoutATRStrategy, params, data_feed, initial_cash=100000
        )

        # Calculate ratio
        strat_return = metrics["total_return_pct"]
        ratio = strat_return / bh_return if bh_return > 0 else 0.0

        print(
            f"      Return: {strat_return:.2f}% | "
            f"Ratio: {ratio:.2f}x | "
            f"Trades: {metrics['num_trades']} | "
            f"Sharpe: {metrics['sharpe_ratio']:.2f} | "
            f"MaxDD: {metrics['max_drawdown_pct']:.2f}%"
        )

        # Check if this is the best
        if ratio > best_ratio:
            best_ratio = ratio
            best_params = params
            best_metrics = metrics

        # Check if we found 2x
        if ratio >= 2.0 and metrics["num_trades"] >= 30:
            print(f"\n   FOUND 2X STRATEGY!")
            print(f"      Ratio: {ratio:.2f}x")
            print(f"      Parameters: {params}")
            break

    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)

    if best_ratio >= 2.0 and best_metrics["num_trades"] >= 30:
        print("\nSUCCESS: Found strategy that beats 2x buy & hold!\n")
    else:
        print("\nBest found (but < 2x):\n")

    print(f"Buy & Hold Return:    {bh_return:.2f}%")
    print(f"Strategy Return:      {best_metrics['total_return_pct']:.2f}%")
    print(f"Ratio (Strat/BH):     {best_ratio:.2f}x")
    print(f"CAGR:                 {best_metrics['cagr']:.2f}%")
    print(f"Max Drawdown:         {best_metrics['max_drawdown_pct']:.2f}%")
    print(f"Sharpe Ratio:         {best_metrics['sharpe_ratio']:.2f}")
    print(f"Total Trades:         {best_metrics['num_trades']}")
    print(f"Win Rate:             {best_metrics['win_rate_pct']:.2f}%")
    print(f"Profit Factor:        {best_metrics['profit_factor']:.2f}")

    print(f"\nBest Parameters:")
    for key, value in best_params.items():
        print(f"  {key}: {value}")

    if best_ratio < 2.0:
        print(
            f"\nDid not achieve 2x (got {best_ratio:.2f}x). "
            f"Trend-following may not beat 2x on this data."
        )
        print(
            f"   Consider: mean reversion, multi-timeframe, or leveraged approach."
        )

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
