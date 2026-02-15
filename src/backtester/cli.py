"""
Command-line interface for backtester
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

from .data import DataFeed
from .engine import BacktestRunner
from .reporting import Reporter
from .strategies import STRATEGIES
from .optimize import grid_search, print_top_results
from .walkforward import walk_forward_analysis, print_walkforward_summary, save_walkforward_results


def run_backtest(args):
    """Run a single backtest"""
    # Load data
    print(f"Loading data: {args.symbol} from {args.data}")
    data_feed = DataFeed(data_dir=args.data, symbol=args.symbol)
    data_feed.load(start_date=args.start, end_date=args.end)
    print(f"Loaded {len(data_feed)} bars\n")

    # Get strategy
    if args.strategy not in STRATEGIES:
        print(f"Error: Unknown strategy '{args.strategy}'")
        print(f"Available strategies: {list(STRATEGIES.keys())}")
        sys.exit(1)

    strategy_class = STRATEGIES[args.strategy]

    # Parse strategy params
    strategy_params = {}
    if args.params:
        for param in args.params:
            key, value = param.split("=")
            # Try to convert to int/float
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass
            strategy_params[key] = value

    # Run backtest
    print(f"Running backtest: {args.strategy}")
    runner = BacktestRunner(
        strategy_class=strategy_class,
        data_feed=data_feed,
        initial_cash=args.cash,
        commission_per_fill=args.commission,
        slippage_bps=args.slippage,
        **strategy_params,
    )

    result = runner.run()

    # Generate reports
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("results") / run_id

    config = {
        "strategy": args.strategy,
        "symbol": args.symbol,
        "start_date": args.start,
        "end_date": args.end,
        "initial_cash": args.cash,
        "commission": args.commission,
        "slippage_bps": args.slippage,
        "strategy_params": strategy_params,
    }

    reporter = Reporter(result["portfolio"], result["broker"], config)
    metrics = reporter.save_results(output_dir)
    reporter.print_summary()

    print(f"\nResults saved to: {output_dir}")


def run_sweep(args):
    """Run parameter sweep"""
    # Load data
    print(f"Loading data: {args.symbol} from {args.data}")
    data_feed = DataFeed(data_dir=args.data, symbol=args.symbol)
    data_feed.load(start_date=args.start, end_date=args.end)
    print(f"Loaded {len(data_feed)} bars\n")

    # Get strategy
    if args.strategy not in STRATEGIES:
        print(f"Error: Unknown strategy '{args.strategy}'")
        sys.exit(1)

    strategy_class = STRATEGIES[args.strategy]

    # Parse param grid
    param_grid = {}
    if args.strategy == "ma_cross":
        if args.fast:
            param_grid["fast"] = [int(x) for x in args.fast.split(",")]
        if args.slow:
            param_grid["slow"] = [int(x) for x in args.slow.split(",")]
    elif args.strategy == "rsi_meanrev":
        if args.rsi_period:
            param_grid["rsi_period"] = [int(x) for x in args.rsi_period.split(",")]
        if args.oversold:
            param_grid["oversold"] = [float(x) for x in args.oversold.split(",")]
        if args.overbought:
            param_grid["overbought"] = [float(x) for x in args.overbought.split(",")]

    if not param_grid:
        print("Error: No parameters specified for sweep")
        sys.exit(1)

    print(f"Parameter grid: {param_grid}\n")

    # Run grid search
    results_df = grid_search(
        strategy_class=strategy_class,
        data_feed=data_feed,
        param_grid=param_grid,
        initial_cash=args.cash,
        commission_per_fill=args.commission,
        slippage_bps=args.slippage,
    )

    # Save results
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("results") / f"sweep_{run_id}"
    output_dir.mkdir(parents=True, exist_ok=True)

    results_df.to_csv(output_dir / "sweep_results.csv", index=False)

    # Print top results
    print_top_results(results_df, metric="sharpe_ratio", top_n=args.top_n)
    print_top_results(results_df, metric="cagr", top_n=args.top_n)

    print(f"\nFull results saved to: {output_dir / 'sweep_results.csv'}")


def run_walkforward(args):
    """Run walk-forward analysis"""
    # Load data
    print(f"Loading data: {args.symbol} from {args.data}")
    data_feed = DataFeed(data_dir=args.data, symbol=args.symbol)
    data_feed.load(start_date=args.start, end_date=args.end)
    print(f"Loaded {len(data_feed)} bars\n")

    # Get strategy
    if args.strategy not in STRATEGIES:
        print(f"Error: Unknown strategy '{args.strategy}'")
        sys.exit(1)

    strategy_class = STRATEGIES[args.strategy]

    # Build param grid
    param_grid = {}
    if args.strategy == "ma_cross":
        param_grid["fast"] = args.fast_values or [10, 20, 30]
        param_grid["slow"] = args.slow_values or [50, 100, 200]
    elif args.strategy == "rsi_meanrev":
        param_grid["rsi_period"] = args.rsi_period_values or [10, 14, 20]
        param_grid["oversold"] = args.oversold_values or [20, 30, 40]
        param_grid["overbought"] = args.overbought_values or [60, 70, 80]

    print(f"Parameter grid: {param_grid}\n")

    # Run walk-forward
    wf_results = walk_forward_analysis(
        strategy_class=strategy_class,
        data_feed=data_feed,
        param_grid=param_grid,
        train_days=args.train_days,
        test_days=args.test_days,
        initial_cash=args.cash,
        commission_per_fill=args.commission,
        slippage_bps=args.slippage,
        optimize_metric=args.optimize_by,
    )

    # Print summary
    print_walkforward_summary(wf_results)

    # Save results
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("results") / f"walkforward_{run_id}"
    save_walkforward_results(wf_results, output_dir)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Stock Backtesting Engine")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a backtest")
    run_parser.add_argument("--data", required=True, help="Data directory")
    run_parser.add_argument("--strategy", required=True, help="Strategy name")
    run_parser.add_argument("--symbol", required=True, help="Symbol to trade")
    run_parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    run_parser.add_argument("--end", help="End date (YYYY-MM-DD)")
    run_parser.add_argument("--cash", type=float, default=100000, help="Initial cash")
    run_parser.add_argument("--commission", type=float, default=1.0, help="Commission per fill")
    run_parser.add_argument("--slippage", type=float, default=1.0, help="Slippage (bps)")
    run_parser.add_argument("--params", nargs="*", help="Strategy params (key=value)")

    # Sweep command
    sweep_parser = subparsers.add_parser("sweep", help="Run parameter sweep")
    sweep_parser.add_argument("--data", required=True, help="Data directory")
    sweep_parser.add_argument("--strategy", required=True, help="Strategy name")
    sweep_parser.add_argument("--symbol", required=True, help="Symbol to trade")
    sweep_parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    sweep_parser.add_argument("--end", help="End date (YYYY-MM-DD)")
    sweep_parser.add_argument("--cash", type=float, default=100000, help="Initial cash")
    sweep_parser.add_argument("--commission", type=float, default=1.0, help="Commission per fill")
    sweep_parser.add_argument("--slippage", type=float, default=1.0, help="Slippage (bps)")
    sweep_parser.add_argument("--top_n", type=int, default=10, help="Top N results to show")
    # MA cross params
    sweep_parser.add_argument("--fast", help="Fast MA periods (comma-separated)")
    sweep_parser.add_argument("--slow", help="Slow MA periods (comma-separated)")
    # RSI params
    sweep_parser.add_argument("--rsi_period", help="RSI periods (comma-separated)")
    sweep_parser.add_argument("--oversold", help="Oversold levels (comma-separated)")
    sweep_parser.add_argument("--overbought", help="Overbought levels (comma-separated)")

    # Walk-forward command
    wf_parser = subparsers.add_parser("walkforward", help="Run walk-forward analysis")
    wf_parser.add_argument("--data", required=True, help="Data directory")
    wf_parser.add_argument("--strategy", required=True, help="Strategy name")
    wf_parser.add_argument("--symbol", required=True, help="Symbol to trade")
    wf_parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    wf_parser.add_argument("--end", help="End date (YYYY-MM-DD)")
    wf_parser.add_argument("--train_days", type=int, default=756, help="Training days")
    wf_parser.add_argument("--test_days", type=int, default=252, help="Test days")
    wf_parser.add_argument("--cash", type=float, default=100000, help="Initial cash")
    wf_parser.add_argument("--commission", type=float, default=1.0, help="Commission per fill")
    wf_parser.add_argument("--slippage", type=float, default=1.0, help="Slippage (bps)")
    wf_parser.add_argument("--optimize_by", default="sharpe_ratio", help="Metric to optimize")
    wf_parser.add_argument("--fast_values", nargs="+", type=int, help="Fast MA values")
    wf_parser.add_argument("--slow_values", nargs="+", type=int, help="Slow MA values")
    wf_parser.add_argument("--rsi_period_values", nargs="+", type=int, help="RSI period values")
    wf_parser.add_argument("--oversold_values", nargs="+", type=float, help="Oversold values")
    wf_parser.add_argument("--overbought_values", nargs="+", type=float, help="Overbought values")

    args = parser.parse_args()

    if args.command == "run":
        run_backtest(args)
    elif args.command == "sweep":
        run_sweep(args)
    elif args.command == "walkforward":
        run_walkforward(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
