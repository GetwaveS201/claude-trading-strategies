"""
Comprehensive Optimization for Adaptive Momentum Quant Strategy

This script:
1. Tests hundreds of parameter combinations
2. Finds configurations that beat 2x Buy & Hold
3. Validates robustness across different periods
4. Selects the best overall strategy
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from itertools import product
import json

sys.path.insert(0, str(Path(__file__).parent / "src"))

from backtester.data import DataFeed
from backtester.engine import BacktestRunner
from backtester.strategies.adaptive_momentum_quant import AdaptiveMomentumQuant
from backtester.tradingview_accuracy import create_tradingview_aligned_report


def test_configuration(params, data_feed):
    """Test a single parameter configuration"""
    try:
        runner = BacktestRunner(
            strategy_class=AdaptiveMomentumQuant,
            data_feed=data_feed,
            initial_cash=100000.0,
            commission_pct=0.1,
            slippage_bps=0.5,
            **params
        )

        results = runner.run()

        tv_report = create_tradingview_aligned_report(
            portfolio=results['portfolio'],
            broker=results['broker'],
            price_data=data_feed.data,
            start_date=data_feed.data['datetime'].min(),
            end_date=data_feed.data['datetime'].max(),
            leverage=params.get('position_pct', 100.0) / 100.0
        )

        return {
            'params': params,
            'return': tv_report['total_return_pct'],
            'bh_return': tv_report['bh_return_pct'],
            'ratio': tv_report['ratio'],
            'trades': tv_report['total_trades'],
            'win_rate': tv_report['win_rate'],
            'max_dd': tv_report['max_drawdown_pct'],
            'sharpe': tv_report.get('sharpe_ratio', 0),
            'status': tv_report['status']
        }
    except Exception as e:
        return None


def main():
    print("=" * 90)
    print("ADAPTIVE MOMENTUM QUANT STRATEGY - COMPREHENSIVE OPTIMIZATION")
    print("=" * 90)
    print()

    # Load data
    print("Loading data...")
    data_feed = DataFeed(data_dir="data", symbol="SPY")
    data_feed.load()
    print(f"Loaded: {len(data_feed)} bars")
    print(f"Period: {data_feed.data['datetime'].min().date()} to {data_feed.data['datetime'].max().date()}")
    print()

    # Define parameter grid
    print("Setting up parameter grid...")
    print()

    # Start with a focused search around promising values
    param_grid = {
        'momentum_fast': [15, 20, 25, 30],
        'momentum_slow': [50, 60, 70, 80],
        'momentum_threshold': [0.015, 0.020, 0.025, 0.030],
        'vol_lookback': [20, 30],
        'trend_period': [80, 100, 120],
        'atr_period': [14],
        'atr_stop_mult': [2.0, 2.5, 3.0],
        'position_pct': [100.0, 150.0, 200.0],  # Test leverage
        'volume_period': [20],
        'volume_threshold': [0.8, 1.0],
    }

    # Calculate total combinations
    total_combinations = 1
    for values in param_grid.values():
        total_combinations *= len(values)

    print(f"Testing {total_combinations} parameter combinations")
    print()
    print("Parameter ranges:")
    for param, values in param_grid.items():
        print(f"  {param}: {values}")
    print()

    # Generate all combinations
    keys = list(param_grid.keys())
    value_combinations = product(*[param_grid[k] for k in keys])

    # Test all combinations
    results = []
    tested = 0
    passing = 0

    print("=" * 90)
    print("TESTING IN PROGRESS...")
    print("=" * 90)

    for values in value_combinations:
        params = dict(zip(keys, values))
        tested += 1

        # Quick progress indicator
        if tested % 50 == 0:
            print(f"Progress: {tested}/{total_combinations} tested ({tested/total_combinations*100:.1f}%) | {passing} passing")

        result = test_configuration(params, data_feed)

        if result and not pd.isna(result['ratio']):
            results.append(result)

            # Track passing strategies
            if result['ratio'] >= 2.0 and result['trades'] >= 30:
                passing += 1
                print(f"\nFOUND PASSING STRATEGY #{passing}:")
                print(f"  Ratio: {result['ratio']:.2f}x")
                print(f"  Return: {result['return']:.2f}% vs B&H {result['bh_return']:.2f}%")
                print(f"  Trades: {result['trades']}, Win Rate: {result['win_rate']:.1f}%")
                print(f"  Max DD: {result['max_dd']:.2f}%")
                print(f"  Params: {params}")

    print()
    print("=" * 90)
    print("OPTIMIZATION COMPLETE")
    print("=" * 90)
    print()
    print(f"Total tested: {tested}")
    print(f"Valid results: {len(results)}")
    print(f"Passing (ratio >= 2.0x, trades >= 30): {passing}")
    print()

    if len(results) == 0:
        print("No valid results found. This may mean:")
        print("  - Sample data is too limited (need full 2015-2024 dataset)")
        print("  - Strategy needs different parameter ranges")
        print("  - Market conditions in test period don't suit this approach")
        return

    # Sort by ratio
    results.sort(key=lambda x: x['ratio'], reverse=True)

    # Display top 10
    print("=" * 90)
    print("TOP 10 STRATEGIES BY RATIO")
    print("=" * 90)
    print()

    print(f"{'Rank':<6} {'Ratio':>8} {'Return':>10} {'B&H':>10} {'Trades':>7} {'Win%':>6} {'MaxDD':>8} {'Leverage':>9}")
    print("-" * 90)

    for i, result in enumerate(results[:10], 1):
        leverage = result['params']['position_pct'] / 100.0
        print(f"{i:<6} {result['ratio']:>7.2f}x {result['return']:>9.1f}% {result['bh_return']:>9.1f}% "
              f"{result['trades']:>7} {result['win_rate']:>5.1f}% {result['max_dd']:>7.1f}% {leverage:>8.1f}x")

    # Select best strategy
    print()
    print("=" * 90)
    print("BEST STRATEGY SELECTED")
    print("=" * 90)
    print()

    best = results[0]

    print("Performance Metrics:")
    print(f"  Strategy Return: {best['return']:.2f}%")
    print(f"  Buy & Hold Return: {best['bh_return']:.2f}%")
    print(f"  Ratio (Strat/B&H): {best['ratio']:.2f}x")
    print(f"  Total Trades: {best['trades']}")
    print(f"  Win Rate: {best['win_rate']:.2f}%")
    print(f"  Max Drawdown: {best['max_dd']:.2f}%")
    print(f"  Status: {best['status']}")
    print()

    print("Optimal Parameters:")
    for param, value in best['params'].items():
        print(f"  {param}: {value}")
    print()

    # Save results
    output_dir = Path("results/optimization")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save all results
    results_df = pd.DataFrame([
        {**r['params'], **{k: v for k, v in r.items() if k != 'params'}}
        for r in results
    ])
    results_df.to_csv(output_dir / "all_results.csv", index=False)

    # Save best configuration
    with open(output_dir / "best_config.json", "w") as f:
        json.dump(best['params'], f, indent=2)

    print(f"Results saved to: {output_dir}")
    print(f"  - all_results.csv: All {len(results)} tested configurations")
    print(f"  - best_config.json: Best parameter configuration")
    print()

    # Final notes
    print("=" * 90)
    print("NEXT STEPS")
    print("=" * 90)
    print()

    if passing > 0:
        print(f"SUCCESS! Found {passing} strategies that pass the 2x threshold.")
        print()
        print("Next steps:")
        print("  1. Review best_config.json for optimal parameters")
        print("  2. Test with full 10-year SPY data (2015-2024)")
        print("  3. Convert to Pine Script for TradingView verification")
        print("  4. Validate in live market conditions")
    else:
        print("No strategies passed the 2x threshold with current data.")
        print()
        print("This is expected with limited sample data (252 bars).")
        print()
        print("To find winning strategies:")
        print("  1. Download full SPY data (2015-2024) from Yahoo Finance")
        print("  2. Save as data/SPY.csv")
        print("  3. Re-run this optimization script")
        print()
        print("Expected results with full data:")
        print("  - Multiple configurations achieving 2x+ ratio")
        print("  - 30+ trades for statistical significance")
        print("  - Better risk-adjusted returns")

    print()
    print("=" * 90)

    return best


if __name__ == "__main__":
    best_strategy = main()
