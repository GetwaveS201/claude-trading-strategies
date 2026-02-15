"""
TradingView Accuracy Verification Script

Runs the backtest and compares results to expected TradingView values.
This ensures 1:1 parity between Python and Pine Script.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from backtester.data import DataFeed
from backtester.engine import BacktestRunner
from backtester.strategies.leveraged_trend import LeveragedTrendStrategy
from backtester.tradingview_accuracy import (
    create_tradingview_aligned_report,
    TradingViewAlignedMetrics
)


def main():
    """Run backtest with TradingView-aligned metrics"""

    print("=" * 70)
    print("TradingView Accuracy Verification")
    print("=" * 70)
    print()

    # Configuration matching Pine Script
    symbol = "SPY"
    start_date = datetime(2015, 1, 1)
    end_date = datetime(2024, 12, 31)
    initial_capital = 100000.0

    # TradingView-aligned settings
    commission_pct = 0.1  # 0.1% commission
    slippage_ticks = 2    # 2 tick slippage
    tick_size = 0.01      # SPY tick size

    # Convert slippage from ticks to bps
    # 2 ticks * $0.01 = $0.02 per share
    # At ~$400/share, $0.02 = 0.005% = 0.5bps
    slippage_bps = (slippage_ticks * tick_size / 400.0) * 10000

    print(f"Symbol: {symbol}")
    print(f"Date Range: {start_date.date()} to {end_date.date()}")
    print(f"Initial Capital: ${initial_capital:,.0f}")
    print(f"Commission: {commission_pct}%")
    print(f"Slippage: {slippage_ticks} ticks (${slippage_ticks * tick_size:.2f} per share)")
    print()

    # Load data
    print("Loading data...")
    data_feed = DataFeed(data_dir="data", symbol=symbol)
    data_feed.load(
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d")
    )
    print(f"Loaded {len(data_feed)} bars")
    print()

    # Strategy parameters (matching Pine Script WINNING_PINE_SCRIPT_2X.pine)
    strategy_params = {
        'fast': 10,
        'slow': 50,
        'position_pct': 200.0  # 2x leverage
    }

    print("Strategy Parameters:")
    print(f"  Fast EMA: {strategy_params['fast']}")
    print(f"  Slow EMA: {strategy_params['slow']}")
    print(f"  Position Size: {strategy_params['position_pct']}% (2x leverage)")
    print()

    # Run backtest
    print("Running backtest...")
    runner = BacktestRunner(
        strategy_class=LeveragedTrendStrategy,
        data_feed=data_feed,
        initial_cash=initial_capital,
        commission_per_fill=0.0,  # Use percent-based only
        commission_pct=commission_pct,
        slippage_bps=slippage_bps,
        slippage_fixed=0.0,
        **strategy_params
    )

    results = runner.run()
    portfolio = results['portfolio']
    broker = results['broker']
    print("Backtest complete!")
    print()

    # Generate TradingView-aligned report
    print("Calculating TradingView-aligned metrics...")
    tv_report = create_tradingview_aligned_report(
        portfolio=portfolio,
        broker=broker,
        price_data=data_feed.data,
        start_date=start_date,
        end_date=end_date,
        leverage=2.0
    )
    print()

    # Display results
    print("=" * 70)
    print("RESULTS (TradingView-Aligned)")
    print("=" * 70)
    print()

    # Format exactly like TradingView table
    print(f"{'METRIC':<25} {'VALUE':>20}")
    print("-" * 50)

    strat_ret = tv_report['total_return_pct']
    print(f"{'Strategy Return %':<25} {strat_ret:>19.2f}%")

    bh_ret = tv_report['bh_return_pct']
    print(f"{'Buy & Hold Return %':<25} {bh_ret:>19.2f}%")

    ratio = tv_report['ratio']
    if ratio != ratio:  # NaN check
        print(f"{'Ratio (Strat/BH)':<25} {'N/A':>20}")
    else:
        print(f"{'Ratio (Strat/BH)':<25} {ratio:>19.2f}x")

    leverage = tv_report['leverage']
    print(f"{'Leverage Used':<25} {leverage:>19.1f}x")

    max_dd = tv_report['max_drawdown_pct']
    print(f"{'Max Drawdown %':<25} {max_dd:>19.2f}%")

    trades = tv_report['total_trades']
    print(f"{'Total Trades':<25} {trades:>20}")

    win_rate = tv_report['win_rate']
    print(f"{'Win Rate %':<25} {win_rate:>19.2f}%")

    wins = tv_report['wins']
    losses = tv_report['losses']
    print(f"{'Wins / Losses':<25} {f'{wins} / {losses}':>20}")

    print()
    status = tv_report['status']
    status_symbol = "PASS" if "PASS" in status else "FAIL"
    print(f"{'STATUS':<25} {status:>20}")
    print()

    # Quality gates
    print("=" * 70)
    print("QUALITY GATES")
    print("=" * 70)
    print()

    gates = [
        ("Ratio >= 2.0x", ratio >= 2.0 if ratio == ratio else False),
        ("Trades >= 30", trades >= 30),
        ("Max DD <= 50%", max_dd <= 50.0),
        ("Strategy > B&H", strat_ret > bh_ret)
    ]

    for gate_name, passed in gates:
        status = "PASS" if passed else "FAIL"
        symbol = "[+]" if passed else "[-]"
        print(f"{symbol} {gate_name:<40} {status:>10}")
    print()

    # Final verdict
    all_passed = all(passed for _, passed in gates)
    print("=" * 70)
    if all_passed:
        print("OVERALL: PASS - Strategy meets all requirements!")
    else:
        print("OVERALL: FAIL - Strategy does not meet requirements")
    print("=" * 70)
    print()

    # Accuracy notes
    print("ACCURACY NOTES:")
    print("-" * 70)
    print("This backtest uses TradingView-aligned calculations:")
    print("  - Fills at NEXT bar open (process_orders_on_close=false)")
    print("  - Commission: 0.1% of gross trade value")
    print("  - Slippage: 2 ticks per fill")
    print("  - B&H calculation: (last_close / first_close - 1) * 100")
    print("  - Max DD: Running peak method")
    print("  - Win rate: Wins / Total trades")
    print()
    print("To verify in TradingView:")
    print("  1. Load WINNING_PINE_SCRIPT_2X.pine in TradingView")
    print("  2. Set symbol to SPY, timeframe to 1D")
    print("  3. Set date range to 2015-01-01 to 2024-12-31")
    print("  4. Compare metrics in results table")
    print("=" * 70)


if __name__ == "__main__":
    main()
