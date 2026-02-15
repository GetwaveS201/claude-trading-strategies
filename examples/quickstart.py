"""
Quickstart example - Run a backtest programmatically
"""

from pathlib import Path
from backtester.data import DataFeed, generate_sample_data
from backtester.engine import BacktestRunner
from backtester.strategies import MACrossStrategy
from backtester.reporting import Reporter


def main():
    """Run a simple backtest example"""

    print("Backtester Quickstart Example")
    print("=" * 60)

    # 1. Generate or load data
    print("\n1. Loading data...")
    df = generate_sample_data(
        symbol="SPY",
        start_date="2015-01-01",
        end_date="2024-12-31",
        initial_price=200.0,
    )

    # Create data feed
    data_feed = DataFeed(data_dir="", symbol="SPY")
    data_feed.data = df

    print(f"   Loaded {len(data_feed)} bars")

    # 2. Configure backtest
    print("\n2. Configuring backtest...")
    print("   Strategy: MA Cross (fast=20, slow=50)")
    print("   Initial cash: $100,000")
    print("   Commission: $1.00 per fill")
    print("   Slippage: 1 basis point")

    # 3. Run backtest
    print("\n3. Running backtest...")
    runner = BacktestRunner(
        strategy_class=MACrossStrategy,
        data_feed=data_feed,
        initial_cash=100000,
        commission_per_fill=1.0,
        slippage_bps=1.0,
        fast=20,
        slow=50,
    )

    result = runner.run()

    # 4. Generate reports
    print("\n4. Generating reports...")
    output_dir = Path("results") / "quickstart"

    config = {
        "strategy": "ma_cross",
        "symbol": "SPY",
        "initial_cash": 100000,
        "fast": 20,
        "slow": 50,
    }

    reporter = Reporter(result["portfolio"], result["broker"], config)
    metrics = reporter.save_results(output_dir)
    reporter.print_summary()

    print(f"\n5. Results saved to: {output_dir}")
    print("\nFiles created:")
    print(f"   - {output_dir / 'config.json'}")
    print(f"   - {output_dir / 'equity.csv'}")
    print(f"   - {output_dir / 'trades.csv'}")
    print(f"   - {output_dir / 'summary.json'}")
    print(f"   - {output_dir / 'charts' / 'equity_curve.png'}")
    print(f"   - {output_dir / 'charts' / 'drawdown.png'}")

    print("\n" + "=" * 60)
    print("Quickstart complete!")


if __name__ == "__main__":
    main()
