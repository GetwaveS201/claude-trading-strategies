"""
Walk-forward analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Type
from pathlib import Path
import json

from .engine import BacktestRunner, Strategy
from .data import DataFeed
from .reporting import PerformanceMetrics
from .optimize import grid_search, rank_results


def walk_forward_analysis(
    strategy_class: Type[Strategy],
    data_feed: DataFeed,
    param_grid: Dict[str, List[Any]],
    train_days: int = 756,  # ~3 years
    test_days: int = 252,   # ~1 year
    initial_cash: float = 100000.0,
    commission_per_fill: float = 1.0,
    slippage_bps: float = 1.0,
    optimize_metric: str = "sharpe_ratio",
) -> Dict[str, Any]:
    """
    Run walk-forward analysis

    Process:
    1. Split data into rolling windows
    2. For each window:
       - Train: optimize params on training period
       - Test: run best params on out-of-sample test period
    3. Stitch together OOS results

    Args:
        strategy_class: Strategy class
        data_feed: DataFeed with loaded data
        param_grid: Parameter grid for optimization
        train_days: Training window size in days
        test_days: Test window size in days
        initial_cash: Starting capital
        commission_per_fill: Commission per fill
        slippage_bps: Slippage in basis points
        optimize_metric: Metric to optimize on

    Returns:
        Dict with walk-forward results
    """
    if data_feed.data is None:
        raise ValueError("DataFeed has no data loaded")

    df = data_feed.data
    total_days = len(df)

    print(f"Walk-Forward Analysis")
    print(f"  Total bars: {total_days}")
    print(f"  Train days: {train_days}")
    print(f"  Test days: {test_days}")
    print(f"  Optimize by: {optimize_metric}")
    print()

    # Calculate windows
    windows = []
    start_idx = 0

    while start_idx + train_days + test_days <= total_days:
        train_start = start_idx
        train_end = start_idx + train_days
        test_start = train_end
        test_end = min(test_start + test_days, total_days)

        windows.append({
            "train_start": train_start,
            "train_end": train_end,
            "test_start": test_start,
            "test_end": test_end,
        })

        # Roll forward by test_days
        start_idx += test_days

    if len(windows) == 0:
        raise ValueError(
            f"Not enough data for walk-forward. "
            f"Need at least {train_days + test_days} bars, have {total_days}"
        )

    print(f"Generated {len(windows)} walk-forward windows\n")

    # Run walk-forward
    oos_results = []
    oos_equity = []
    best_params_list = []

    for i, window in enumerate(windows, 1):
        print(f"Window {i}/{len(windows)}")
        print(f"  Train: {window['train_start']} to {window['train_end']}")
        print(f"  Test:  {window['test_start']} to {window['test_end']}")

        # Create training data feed
        train_data = df.iloc[window["train_start"]:window["train_end"]].copy()
        train_feed = DataFeed(data_dir="", symbol=data_feed.symbol)
        train_feed.data = train_data

        # Optimize on training data
        print("  Optimizing...")
        train_results = grid_search(
            strategy_class=strategy_class,
            data_feed=train_feed,
            param_grid=param_grid,
            initial_cash=initial_cash,
            commission_per_fill=commission_per_fill,
            slippage_bps=slippage_bps,
        )

        # Get best params
        top = rank_results(train_results, rank_by=optimize_metric, top_n=1)
        if len(top) == 0:
            print("  No valid results in training, skipping window")
            continue

        best_params = top.iloc[0].to_dict()

        # Extract just the strategy params
        param_names = list(param_grid.keys())
        best_strategy_params = {k: best_params[k] for k in param_names if k in best_params}

        print(f"  Best params: {best_strategy_params}")
        print(f"  Train {optimize_metric}: {best_params[optimize_metric]:.2f}")

        best_params_list.append({
            "window": i,
            "params": best_strategy_params,
            "train_metric": best_params[optimize_metric],
        })

        # Test on OOS data
        test_data = df.iloc[window["test_start"]:window["test_end"]].copy()
        test_feed = DataFeed(data_dir="", symbol=data_feed.symbol)
        test_feed.data = test_data

        print("  Testing OOS...")
        runner = BacktestRunner(
            strategy_class=strategy_class,
            data_feed=test_feed,
            initial_cash=initial_cash,
            commission_per_fill=commission_per_fill,
            slippage_bps=slippage_bps,
            **best_strategy_params,
        )

        result = runner.run()

        # Calculate OOS metrics
        metrics_calc = PerformanceMetrics(result["portfolio"], result["broker"])
        oos_metrics = metrics_calc.calculate_metrics()

        print(f"  Test {optimize_metric}: {oos_metrics[optimize_metric]:.2f}")
        print()

        oos_results.append({
            "window": i,
            **oos_metrics,
        })

        # Collect OOS equity curve
        for record in result["portfolio"].equity_history:
            oos_equity.append({
                "window": i,
                "timestamp": record["timestamp"],
                "equity": record["equity"],
            })

    # Combine results
    oos_df = pd.DataFrame(oos_results)
    oos_equity_df = pd.DataFrame(oos_equity)

    # Calculate aggregate OOS metrics
    if len(oos_df) > 0:
        aggregate_metrics = {
            "num_windows": len(oos_df),
            "avg_cagr": oos_df["cagr"].mean(),
            "avg_sharpe": oos_df["sharpe_ratio"].mean(),
            "avg_max_dd": oos_df["max_drawdown_pct"].mean(),
            "avg_win_rate": oos_df["win_rate_pct"].mean(),
            "total_trades": oos_df["num_trades"].sum(),
        }
    else:
        aggregate_metrics = {}

    return {
        "windows": windows,
        "oos_results": oos_df,
        "oos_equity": oos_equity_df,
        "best_params": best_params_list,
        "aggregate_metrics": aggregate_metrics,
    }


def print_walkforward_summary(wf_results: Dict[str, Any]):
    """Print walk-forward summary"""
    print("\n" + "=" * 80)
    print("WALK-FORWARD ANALYSIS SUMMARY")
    print("=" * 80)

    agg = wf_results["aggregate_metrics"]

    if not agg:
        print("No results")
        return

    print(f"Number of Windows:  {agg.get('num_windows', 0)}")
    print(f"Avg CAGR:           {agg.get('avg_cagr', 0):.2f}%")
    print(f"Avg Sharpe:         {agg.get('avg_sharpe', 0):.2f}")
    print(f"Avg Max DD:         {agg.get('avg_max_dd', 0):.2f}%")
    print(f"Avg Win Rate:       {agg.get('avg_win_rate', 0):.2f}%")
    print(f"Total Trades:       {agg.get('total_trades', 0)}")

    print("\n" + "=" * 80)
    print("PER-WINDOW RESULTS")
    print("=" * 80)

    oos_df = wf_results["oos_results"]
    for _, row in oos_df.iterrows():
        print(f"\nWindow {int(row['window'])}")
        print(f"  CAGR:         {row['cagr']:.2f}%")
        print(f"  Sharpe:       {row['sharpe_ratio']:.2f}")
        print(f"  Max DD:       {row['max_drawdown_pct']:.2f}%")
        print(f"  Win Rate:     {row['win_rate_pct']:.2f}%")
        print(f"  Trades:       {int(row['num_trades'])}")

    print("\n" + "=" * 80)


def save_walkforward_results(wf_results: Dict[str, Any], output_dir: Path):
    """Save walk-forward results"""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save OOS results
    oos_df = wf_results["oos_results"]
    if len(oos_df) > 0:
        oos_df.to_csv(output_dir / "walkforward_results.csv", index=False)

    # Save OOS equity curve
    oos_equity_df = wf_results["oos_equity"]
    if len(oos_equity_df) > 0:
        oos_equity_df.to_csv(output_dir / "walkforward_equity.csv", index=False)

    # Save aggregate metrics
    with open(output_dir / "walkforward_summary.json", "w") as f:
        json.dump(wf_results["aggregate_metrics"], f, indent=2, default=str)

    # Save best params per window
    with open(output_dir / "walkforward_params.json", "w") as f:
        json.dump(wf_results["best_params"], f, indent=2, default=str)

    print(f"\nResults saved to {output_dir}")
