"""
Showcase Professional TradingView-Style Visualizations

Demonstrates the enhanced backtesting engine with professional-grade charts
"""

from pathlib import Path
from backtester.data import generate_sample_data, DataFeed
from backtester.engine import BacktestRunner
from backtester.strategies.leveraged_trend import LeveragedTrendStrategy
from backtester.reporting import Reporter
import numpy as np


def main():
    print("=" * 80)
    print("PROFESSIONAL BACKTESTING VISUALIZATION SHOWCASE")
    print("=" * 80)

    # Generate realistic data
    print("\nGenerating 10-year SPY data...")
    np.random.seed(42)
    df = generate_sample_data(
        symbol="SPY",
        start_date="2015-01-01",
        end_date="2024-12-31",
        initial_price=200
    )
    print(f"Generated {len(df)} bars\n")

    # Run winning 2x strategy
    print("Running validated 2x strategy (EMA 10/50 with 2x leverage)...")

    feed = DataFeed(data_dir="", symbol="SPY")
    feed.data = df

    runner = BacktestRunner(
        strategy_class=LeveragedTrendStrategy,
        data_feed=feed,
        initial_cash=100000,
        commission_per_fill=1.0,
        slippage_bps=1.0,
        fast=10,
        slow=50,
        position_pct=200  # 2x leverage
    )

    result = runner.run()

    # Generate professional reports
    print("Generating professional TradingView-style visualizations...\n")

    output_dir = Path("results/professional_showcase")
    config = {
        "strategy": "Leveraged EMA Cross (2x)",
        "symbol": "SPY",
        "timeframe": "Daily",
        "period": "2015-2024",
        "leverage": "2.0x",
        "fast_ema": 10,
        "slow_ema": 50
    }

    reporter = Reporter(result["portfolio"], result["broker"], config)
    metrics = reporter.save_results(output_dir)

    # Print results
    print("=" * 80)
    print("VISUALIZATION SUMMARY")
    print("=" * 80)

    print(f"\nOutput Directory: {output_dir.absolute()}\n")

    print("PROFESSIONAL CHARTS (TradingView-Style):")
    print("   1. professional_overview.png")
    print("      - Price chart with trade markers (buy/sell triangles)")
    print("      - Equity curve with profit/loss shading")
    print("      - Underwater equity (drawdown chart)")
    print("      - 3-panel integrated view")
    print()
    print("   2. metrics_dashboard.png")
    print("      - Comprehensive performance metrics")
    print("      - Risk analysis")
    print("      - Trading statistics")
    print("      - Trade-by-trade analysis")
    print()
    print("   3. trade_analysis.png")
    print("      - P&L distribution histogram")
    print("      - Trade duration analysis")
    print("      - Cumulative P&L progression")
    print("      - Win/Loss sequence bars")
    print()

    print("LEGACY CHARTS (Compatibility):")
    print("   - equity_curve.png")
    print("   - drawdown.png")
    print("   - returns_distribution.png")
    print()

    print("DATA EXPORTS:")
    print("   - config.json")
    print("   - equity.csv (daily equity curve)")
    print("   - trades.csv (all trades with P&L)")
    print("   - summary.json (performance metrics)")
    print()

    print("=" * 80)
    print("PERFORMANCE METRICS")
    print("=" * 80)

    print(f"\nInitial Capital:   ${metrics['initial_equity']:,.2f}")
    print(f"Final Equity:      ${metrics['final_equity']:,.2f}")
    print(f"Net Profit:        ${metrics['final_equity'] - metrics['initial_equity']:,.2f}")
    print(f"Total Return:      {metrics['total_return_pct']:.2f}%")
    print(f"CAGR:              {metrics['cagr']:.2f}%")
    print()
    print(f"Sharpe Ratio:      {metrics['sharpe_ratio']:.2f}")
    print(f"Sortino Ratio:     {metrics['sortino_ratio']:.2f}")
    print(f"Max Drawdown:      {metrics['max_drawdown_pct']:.2f}%")
    print(f"Profit Factor:     {metrics['profit_factor']:.2f}")
    print()
    print(f"Total Trades:      {metrics['num_trades']}")
    print(f"Win Rate:          {metrics['win_rate_pct']:.2f}%")
    print(f"Avg Win:           ${metrics['avg_win']:.2f} ({metrics['avg_win_pct']:.2f}%)")
    print(f"Avg Loss:          ${metrics['avg_loss']:.2f} ({metrics['avg_loss_pct']:.2f}%)")
    print(f"Exposure:          {metrics['exposure_pct']:.2f}%")

    print()
    print("=" * 80)
    print("SHOWCASE COMPLETE")
    print("=" * 80)
    print(f"\nOpen {output_dir.absolute()}/charts/ to view professional visualizations!")
    print()


if __name__ == "__main__":
    main()
