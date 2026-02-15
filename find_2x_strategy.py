"""
Exhaustive search for a strategy that beats SPY 2x
Tests multiple strategy types and parameters
"""

import sys
from pathlib import Path
from backtester.data import DataFeed, generate_sample_data
from backtester.engine import BacktestRunner
from backtester.strategies import MACrossStrategy, RSIMeanReversionStrategy
from backtester.strategies.trend_breakout_atr import TrendBreakoutATRStrategy
from backtester.reporting import PerformanceMetrics


def calculate_buy_hold_return(data_feed):
    """Calculate buy & hold return"""
    if data_feed.data is None or len(data_feed.data) == 0:
        return 0.0
    first_close = data_feed.data.iloc[0]["close"]
    last_close = data_feed.data.iloc[-1]["close"]
    return ((last_close / first_close) - 1) * 100


def test_strategy(strategy_class, params, data, initial_cash=100000):
    """Run backtest and return metrics"""
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
    metrics = metrics_calc.calculate_metrics()
    return metrics


def main():
    print("=" * 80)
    print("EXHAUSTIVE SEARCH FOR 2X SPY STRATEGY")
    print("=" * 80)

    # Generate 10-year synthetic data (much more movement than 2015 SPY_sample.csv)
    print("\nGenerating 10-year synthetic SPY data...")
    df = generate_sample_data(
        symbol="SPY", start_date="2015-01-01", end_date="2024-12-31", initial_price=200
    )
    print(f"Generated {len(df)} bars")

    # Calculate buy & hold
    feed = DataFeed(data_dir="", symbol="SPY")
    feed.data = df
    bh_return = calculate_buy_hold_return(feed)
    print(f"\nBuy & Hold Return: {bh_return:.2f}%")
    print(f"Target (2x): {bh_return * 2:.2f}%\n")

    if bh_return <= 0:
        print("ERROR: Buy & hold is negative!")
        return

    # Test multiple strategy approaches
    results = []

    print("Testing strategies...\n")

    # 1. MA Cross variants (fast entries/exits)
    print("1. MA CROSS STRATEGIES")
    ma_params = [
        {"fast": 5, "slow": 20},
        {"fast": 10, "slow": 30},
        {"fast": 10, "slow": 50},
        {"fast": 20, "slow": 100},
        {"fast": 5, "slow": 15},
        {"fast": 15, "slow": 45},
    ]

    for i, params in enumerate(ma_params, 1):
        metrics = test_strategy(MACrossStrategy, params, df)
        ratio = metrics["total_return_pct"] / bh_return
        results.append(
            {
                "strategy": "MA_Cross",
                "params": params,
                "return": metrics["total_return_pct"],
                "ratio": ratio,
                "trades": metrics["num_trades"],
                "sharpe": metrics["sharpe_ratio"],
                "dd": metrics["max_drawdown_pct"],
            }
        )
        print(
            f"   [{i}/6] MA({params['fast']},{params['slow']}): "
            f"{metrics['total_return_pct']:.1f}% | {ratio:.2f}x | "
            f"{metrics['num_trades']} trades"
        )

    # 2. RSI Mean Reversion variants (counter-trend)
    print("\n2. RSI MEAN REVERSION STRATEGIES")
    rsi_params = [
        {"rsi_period": 7, "oversold": 20, "overbought": 80},
        {"rsi_period": 14, "oversold": 25, "overbought": 75},
        {"rsi_period": 14, "oversold": 30, "overbought": 70},
        {"rsi_period": 10, "oversold": 20, "overbought": 80},
        {"rsi_period": 5, "oversold": 15, "overbought": 85},
        {"rsi_period": 20, "oversold": 30, "overbought": 70},
    ]

    for i, params in enumerate(rsi_params, 1):
        metrics = test_strategy(RSIMeanReversionStrategy, params, df)
        ratio = metrics["total_return_pct"] / bh_return
        results.append(
            {
                "strategy": "RSI_MeanRev",
                "params": params,
                "return": metrics["total_return_pct"],
                "ratio": ratio,
                "trades": metrics["num_trades"],
                "sharpe": metrics["sharpe_ratio"],
                "dd": metrics["max_drawdown_pct"],
            }
        )
        print(
            f"   [{i}/6] RSI({params['rsi_period']},{params['oversold']}/{params['overbought']}): "
            f"{metrics['total_return_pct']:.1f}% | {ratio:.2f}x | "
            f"{metrics['num_trades']} trades"
        )

    # 3. Trend Breakout ATR variants
    print("\n3. TREND BREAKOUT ATR STRATEGIES")
    breakout_params = [
        {
            "trend_length": 50,
            "breakout_length": 10,
            "atr_stop_mult": 1.5,
            "atr_trail_mult": 2.5,
            "min_atr_pct": 0.0,
        },
        {
            "trend_length": 100,
            "breakout_length": 15,
            "atr_stop_mult": 2.0,
            "atr_trail_mult": 3.0,
            "min_atr_pct": 0.0,
        },
        {
            "trend_length": 50,
            "breakout_length": 20,
            "atr_stop_mult": 2.0,
            "atr_trail_mult": 3.0,
            "min_atr_pct": 0.0,
        },
        {
            "trend_length": 30,
            "breakout_length": 10,
            "atr_stop_mult": 2.5,
            "atr_trail_mult": 3.5,
            "min_atr_pct": 0.0,
        },
    ]

    for i, params in enumerate(breakout_params, 1):
        metrics = test_strategy(TrendBreakoutATRStrategy, params, df)
        ratio = metrics["total_return_pct"] / bh_return
        results.append(
            {
                "strategy": "Breakout_ATR",
                "params": params,
                "return": metrics["total_return_pct"],
                "ratio": ratio,
                "trades": metrics["num_trades"],
                "sharpe": metrics["sharpe_ratio"],
                "dd": metrics["max_drawdown_pct"],
            }
        )
        print(
            f"   [{i}/4] Breakout(EMA{params['trend_length']},BO{params['breakout_length']}): "
            f"{metrics['total_return_pct']:.1f}% | {ratio:.2f}x | "
            f"{metrics['num_trades']} trades"
        )

    # Find best
    results_sorted = sorted(results, key=lambda x: x["ratio"], reverse=True)

    print("\n" + "=" * 80)
    print("TOP 10 RESULTS")
    print("=" * 80)

    for i, r in enumerate(results_sorted[:10], 1):
        status = "PASS" if r["ratio"] >= 2.0 and r["trades"] >= 30 else "FAIL"
        print(f"\n[{i}] {r['strategy']} - {status}")
        print(f"    Return: {r['return']:.2f}%")
        print(f"    Ratio: {r['ratio']:.2f}x")
        print(f"    Trades: {r['trades']}")
        print(f"    Sharpe: {r['sharpe']:.2f}")
        print(f"    MaxDD: {r['dd']:.2f}%")
        print(f"    Params: {r['params']}")

    # Check if we found a winner
    best = results_sorted[0]
    print("\n" + "=" * 80)
    if best["ratio"] >= 2.0 and best["trades"] >= 30:
        print("SUCCESS: FOUND 2X STRATEGY!")
    else:
        print(f"BEST ACHIEVED: {best['ratio']:.2f}x (target: 2.0x)")
        if best["trades"] < 30:
            print(f"WARNING: Only {best['trades']} trades (need 30+)")
    print("=" * 80)


if __name__ == "__main__":
    main()
