"""
Parameter optimization via grid search
"""

import itertools
import pandas as pd
from typing import Dict, List, Any, Type
from pathlib import Path

from .engine import BacktestRunner, Strategy
from .data import DataFeed
from .reporting import PerformanceMetrics


def grid_search(
    strategy_class: Type[Strategy],
    data_feed: DataFeed,
    param_grid: Dict[str, List[Any]],
    initial_cash: float = 100000.0,
    commission_per_fill: float = 1.0,
    slippage_bps: float = 1.0,
) -> pd.DataFrame:
    """
    Run grid search over parameter combinations

    Args:
        strategy_class: Strategy class to optimize
        data_feed: DataFeed with loaded data
        param_grid: Dict mapping param names to lists of values
        initial_cash: Starting capital
        commission_per_fill: Commission per fill
        slippage_bps: Slippage in basis points

    Returns:
        DataFrame with results for each parameter combination
    """
    # Generate all parameter combinations
    param_names = list(param_grid.keys())
    param_values = list(param_grid.values())
    combinations = list(itertools.product(*param_values))

    print(f"Running grid search: {len(combinations)} combinations")

    results = []

    for i, combo in enumerate(combinations, 1):
        # Build param dict
        params = dict(zip(param_names, combo))

        print(f"  [{i}/{len(combinations)}] Testing: {params}")

        # Run backtest
        try:
            runner = BacktestRunner(
                strategy_class=strategy_class,
                data_feed=data_feed,
                initial_cash=initial_cash,
                commission_per_fill=commission_per_fill,
                slippage_bps=slippage_bps,
                **params,
            )

            result = runner.run()

            # Calculate metrics
            metrics_calc = PerformanceMetrics(result["portfolio"], result["broker"])
            metrics = metrics_calc.calculate_metrics()

            # Combine params and metrics
            row = {**params, **metrics}
            results.append(row)

        except Exception as e:
            print(f"    ERROR: {e}")
            # Add failed result
            row = {**params, "error": str(e)}
            results.append(row)

    # Convert to DataFrame
    df = pd.DataFrame(results)

    return df


def rank_results(
    results_df: pd.DataFrame,
    rank_by: str = "sharpe_ratio",
    top_n: int = 10,
) -> pd.DataFrame:
    """
    Rank results by a metric

    Args:
        results_df: Results from grid_search
        rank_by: Metric to rank by
        top_n: Number of top results to return

    Returns:
        Top N results sorted by metric
    """
    if rank_by not in results_df.columns:
        raise ValueError(f"Metric '{rank_by}' not found in results")

    # Remove error rows
    if "error" in results_df.columns:
        df = results_df[results_df["error"].isna()].copy()
    else:
        df = results_df.copy()

    # Sort by metric (descending)
    df = df.sort_values(rank_by, ascending=False)

    return df.head(top_n)


def print_top_results(results_df: pd.DataFrame, metric: str, top_n: int = 10):
    """Print top N results"""
    top = rank_results(results_df, rank_by=metric, top_n=top_n)

    print(f"\n{'=' * 80}")
    print(f"TOP {top_n} BY {metric.upper()}")
    print(f"{'=' * 80}")

    if len(top) == 0:
        print("No valid results")
        return

    for i, (idx, row) in enumerate(top.iterrows(), 1):
        print(f"\n[{i}] {metric}: {row[metric]:.2f}")

        # Print params
        param_cols = [c for c in row.index if c not in [
            "error", "initial_equity", "final_equity", "total_return_pct",
            "start_date", "end_date", "duration_days", "cagr",
            "max_drawdown_pct", "sharpe_ratio", "sortino_ratio",
            "num_trades", "num_wins", "num_losses", "win_rate_pct",
            "avg_win", "avg_win_pct", "avg_loss", "avg_loss_pct",
            "profit_factor", "exposure_pct"
        ]]

        print("  Params:", {k: row[k] for k in param_cols if k in row.index})
        print(f"  CAGR: {row.get('cagr', 0):.2f}%")
        print(f"  Max DD: {row.get('max_drawdown_pct', 0):.2f}%")
        print(f"  Sharpe: {row.get('sharpe_ratio', 0):.2f}")
        print(f"  Trades: {row.get('num_trades', 0)}")
        print(f"  Win Rate: {row.get('win_rate_pct', 0):.2f}%")
