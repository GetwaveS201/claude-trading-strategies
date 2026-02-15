"""
Final test: Find a strategy that beats SPY 2x

Tests:
1. Optimized MA Cross (best params from grid)
2. Leveraged strategies (2x exposure)
3. Hybrid approaches
"""

from backtester.data import DataFeed, generate_sample_data
from backtester.engine import BacktestRunner
from backtester.strategies import MACrossStrategy
from backtester.strategies.leveraged_trend import LeveragedTrendStrategy
from backtester.reporting import PerformanceMetrics


def calculate_buy_hold_return(data):
    """Calculate buy & hold return"""
    first_close = data.iloc[0]["close"]
    last_close = data.iloc[-1]["close"]
    return ((last_close / first_close) - 1) * 100


def test_strategy(strategy_class, params, data, initial_cash=100000):
    """Run backtest"""
    feed = DataFeed(data_dir="", symbol="SPY")
    feed.data = data.copy()

    runner = BacktestRunner(
        strategy_class=strategy_class,
        data_feed=feed,
        initial_cash=initial_cash,
        commission_per_fill=1.0,
        slippage_bps=1.0,
        **params,
    )

    result = runner.run()
    metrics_calc = PerformanceMetrics(result["portfolio"], result["broker"])
    return metrics_calc.calculate_metrics()


def main():
    print("=" * 80)
    print("FINAL 2X STRATEGY TEST")
    print("=" * 80)

    # Generate more realistic 10-year data (lower drift = more realistic)
    print("\nGenerating realistic 10-year SPY data...")
    import numpy as np
    import pandas as pd

    np.random.seed(42)
    dates = pd.date_range(start="2015-01-01", end="2024-12-31", freq="D")
    dates = dates[dates.dayofweek < 5]  # Remove weekends
    n = len(dates)

    # More realistic drift: ~10% annual = ~0.04% daily
    returns = np.random.normal(0.0004, 0.01, n)
    prices = 200 * np.exp(np.cumsum(returns))

    data = []
    for i, date in enumerate(dates):
        close = prices[i]
        open_price = close + np.random.normal(0, 0.005 * close)
        high = max(open_price, close) + abs(np.random.normal(0, 0.005 * close))
        low = min(open_price, close) - abs(np.random.normal(0, 0.005 * close))
        volume = int(abs(np.random.normal(100_000_000, 20_000_000)))

        data.append(
            {
                "datetime": date,
                "open": round(open_price, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(close, 2),
                "volume": volume,
            }
        )

    df = pd.DataFrame(data)
    print(f"Generated {len(df)} bars")

    # Calculate buy & hold
    bh_return = calculate_buy_hold_return(df)
    print(f"\nBuy & Hold Return: {bh_return:.2f}%")
    print(f"Target (2x): {bh_return * 2:.2f}%\n")

    results = []

    # Test leveraged strategies
    print("LEVERAGED STRATEGIES (200% exposure)\n")

    leveraged_params = [
        {"fast": 5, "slow": 20, "position_pct": 200},
        {"fast": 10, "slow": 30, "position_pct": 200},
        {"fast": 10, "slow": 50, "position_pct": 200},
        {"fast": 20, "slow": 100, "position_pct": 200},
        {"fast": 15, "slow": 45, "position_pct": 200},
    ]

    for i, params in enumerate(leveraged_params, 1):
        metrics = test_strategy(LeveragedTrendStrategy, params, df)
        ratio = metrics["total_return_pct"] / bh_return
        results.append(
            {
                "strategy": f"Leveraged_2x",
                "params": params,
                "return": metrics["total_return_pct"],
                "ratio": ratio,
                "trades": metrics["num_trades"],
                "sharpe": metrics["sharpe_ratio"],
                "dd": metrics["max_drawdown_pct"],
            }
        )
        print(
            f"[{i}/5] EMA({params['fast']},{params['slow']}) 2x: "
            f"{metrics['total_return_pct']:.1f}% | {ratio:.2f}x | "
            f"{metrics['num_trades']} trades | DD: {metrics['max_drawdown_pct']:.1f}%"
        )

    # Test ultra-fast MA cross (more trades)
    print("\nULTRA-FAST MA CROSS (high frequency)\n")

    fast_params = [
        {"fast": 3, "slow": 10, "position_pct": 95},
        {"fast": 5, "slow": 10, "position_pct": 95},
        {"fast": 3, "slow": 15, "position_pct": 95},
    ]

    for i, params in enumerate(fast_params, 1):
        metrics = test_strategy(MACrossStrategy, params, df)
        ratio = metrics["total_return_pct"] / bh_return
        results.append(
            {
                "strategy": f"MA_UltraFast",
                "params": params,
                "return": metrics["total_return_pct"],
                "ratio": ratio,
                "trades": metrics["num_trades"],
                "sharpe": metrics["sharpe_ratio"],
                "dd": metrics["max_drawdown_pct"],
            }
        )
        print(
            f"[{i}/3] MA({params['fast']},{params['slow']}): "
            f"{metrics['total_return_pct']:.1f}% | {ratio:.2f}x | "
            f"{metrics['num_trades']} trades"
        )

    # Sort by ratio
    results_sorted = sorted(results, key=lambda x: x["ratio"], reverse=True)

    print("\n" + "=" * 80)
    print("BEST RESULTS")
    print("=" * 80)

    for i, r in enumerate(results_sorted[:5], 1):
        status = "PASS" if r["ratio"] >= 2.0 and r["trades"] >= 30 else "FAIL"
        print(f"\n[{i}] {r['strategy']} - {status}")
        print(f"    Return:  {r['return']:.2f}%")
        print(f"    Ratio:   {r['ratio']:.2f}x {'<-- TARGET!' if r['ratio'] >= 2.0 else ''}")
        print(f"    Trades:  {r['trades']} {'(OK)' if r['trades'] >= 30 else '(LOW)'}")
        print(f"    Sharpe:  {r['sharpe']:.2f}")
        print(f"    MaxDD:   {r['dd']:.2f}%")
        print(f"    Params:  {r['params']}")

    # Final verdict
    best = results_sorted[0]
    print("\n" + "=" * 80)
    if best["ratio"] >= 2.0 and best["trades"] >= 30:
        print("SUCCESS: FOUND 2X STRATEGY!")
        print("=" * 80)
        print(f"\nWinning Strategy: {best['strategy']}")
        print(f"Parameters: {best['params']}")
        print(f"Ratio: {best['ratio']:.2f}x")
        print(f"Return: {best['return']:.2f}%")
        print(f"Trades: {best['trades']}")
    else:
        print(f"BEST ACHIEVED: {best['ratio']:.2f}x (need 2.0x)")
        print("=" * 80)
        print("\nREALITY CHECK:")
        print("Beating 2x buy & hold is extremely difficult with simple strategies.")
        print("The leveraged strategy comes closest but may fail quality gates.")
        print("\nTo achieve true 2x:")
        print("- Use options/leverage (increases risk)")
        print("- Market timing (very hard)")
        print("- Accept that on strong trends, B&H is hard to beat 2x")
    print("=" * 80)


if __name__ == "__main__":
    main()
