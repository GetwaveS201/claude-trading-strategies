"""
Test MAXIMUM_PROFIT_STRATEGY with optimization

This will:
1. Convert the Pine Script logic to Python
2. Test multiple parameter combinations
3. Find the configuration that makes the MOST MONEY
4. Show you the best results
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / "src"))

from backtester.data import DataFeed
from backtester.engine import BacktestRunner, Strategy, Context
from backtester.indicators import EMA, SMA, ATR
from backtester.tradingview_accuracy import create_tradingview_aligned_report
from backtester.reporting import Reporter


class MaximumProfitStrategy(Strategy):
    """
    Maximum Profit Strategy - Optimized for highest returns

    Features:
    - Fast/Slow EMA crossover
    - 200-SMA trend filter
    - Momentum confirmation
    - ATR trailing stops
    - Multiple exit conditions
    """

    def __init__(
        self,
        fast_period: int = 8,
        slow_period: int = 21,
        trend_period: int = 200,
        momentum_period: int = 14,
        momentum_threshold: float = 0.0,
        atr_period: int = 14,
        atr_multiplier: float = 2.0,
        position_pct: float = 200.0,
        use_atr_stops: bool = True,
        use_ema_cross_exit: bool = True,
        use_trend_break_exit: bool = True
    ):
        super().__init__()
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.trend_period = trend_period
        self.momentum_period = momentum_period
        self.momentum_threshold = momentum_threshold
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.position_pct = position_pct
        self.use_atr_stops = use_atr_stops
        self.use_ema_cross_exit = use_ema_cross_exit
        self.use_trend_break_exit = use_trend_break_exit

        # Indicators
        self.fast_ema = EMA(fast_period)
        self.slow_ema = EMA(slow_period)
        self.trend_sma = SMA(trend_period)
        self.atr = ATR(atr_period)

        # State
        self.prev_fast = None
        self.prev_slow = None
        self.price_history = []
        self.entry_price = None
        self.stop_loss = None

    def on_start(self):
        print(f"Maximum Profit Strategy Starting:")
        print(f"  Fast EMA: {self.fast_period}")
        print(f"  Slow EMA: {self.slow_period}")
        print(f"  Trend Filter: {self.trend_period}-SMA")
        print(f"  Leverage: {self.position_pct/100:.1f}x")
        print(f"  ATR Stops: {self.use_atr_stops}")

    def on_bar(self, context: Context):
        # Update indicators
        self.fast_ema.update(context.close)
        self.slow_ema.update(context.close)
        self.trend_sma.update(context.close)
        self.atr.update(context.high, context.low, context.close)

        # Track price history for momentum
        self.price_history.append(context.close)
        if len(self.price_history) > self.momentum_period + 10:
            self.price_history.pop(0)

        # Get current values
        fast = self.fast_ema.get_value()
        slow = self.slow_ema.get_value()
        trend = self.trend_sma.get_value()
        atr_value = self.atr.get_value()

        if fast is None or slow is None or trend is None:
            return

        # Calculate momentum
        if len(self.price_history) >= self.momentum_period + 1:
            old_price = self.price_history[-(self.momentum_period + 1)]
            momentum = (context.close - old_price) / old_price * 100
        else:
            momentum = 0

        # ===================================================================
        # ENTRY LOGIC
        # ===================================================================

        if context.position == 0:
            # Detect bullish crossover
            if self.prev_fast is not None and self.prev_slow is not None:
                bull_cross = self.prev_fast <= self.prev_slow and fast > slow

                # Filters
                above_trend = context.close > trend
                has_momentum = momentum > self.momentum_threshold

                # Entry signal
                if bull_cross and above_trend and has_momentum:
                    context.buy(percent=self.position_pct)
                    self.entry_price = context.close

                    # Set initial stop
                    if self.use_atr_stops and atr_value is not None:
                        self.stop_loss = context.close - (atr_value * self.atr_multiplier)

        # ===================================================================
        # EXIT LOGIC
        # ===================================================================

        elif context.position > 0:
            exit_signal = False

            # Exit 1: EMA cross
            if self.use_ema_cross_exit and self.prev_fast is not None and self.prev_slow is not None:
                bear_cross = self.prev_fast >= self.prev_slow and fast < slow
                if bear_cross:
                    exit_signal = True

            # Exit 2: ATR trailing stop
            if self.use_atr_stops and atr_value is not None and self.stop_loss is not None:
                # Trail stop up
                new_stop = context.close - (atr_value * self.atr_multiplier)
                if new_stop > self.stop_loss:
                    self.stop_loss = new_stop

                # Check if stopped out
                if context.close < self.stop_loss:
                    exit_signal = True

            # Exit 3: Trend break
            if self.use_trend_break_exit:
                if context.close < trend:
                    exit_signal = True

            # Execute exit
            if exit_signal:
                context.sell()
                self.entry_price = None
                self.stop_loss = None

        # Update previous values
        self.prev_fast = fast
        self.prev_slow = slow

    def on_end(self):
        print("Strategy complete")


def test_configuration(params, data_feed, name="Test"):
    """Test a single configuration"""
    try:
        runner = BacktestRunner(
            strategy_class=MaximumProfitStrategy,
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
            'name': name,
            'params': params,
            'return': tv_report['total_return_pct'],
            'bh_return': tv_report['bh_return_pct'],
            'ratio': tv_report['ratio'],
            'trades': tv_report['total_trades'],
            'win_rate': tv_report['win_rate'],
            'max_dd': tv_report['max_drawdown_pct'],
            'status': tv_report['status']
        }
    except Exception as e:
        print(f"Error testing {name}: {e}")
        return None


def main():
    print("=" * 80)
    print("MAXIMUM PROFIT STRATEGY - OPTIMIZATION")
    print("=" * 80)
    print()

    # Load data
    print("Loading data...")
    data_feed = DataFeed(data_dir="data", symbol="SPY")
    data_feed.load()
    print(f"Loaded: {len(data_feed)} bars")
    print(f"Period: {data_feed.data['datetime'].min().date()} to {data_feed.data['datetime'].max().date()}")
    print()

    # Test multiple configurations
    configurations = [
        # Original configuration
        {
            'name': 'Maximum Profit (Default)',
            'params': {
                'fast_period': 8,
                'slow_period': 21,
                'trend_period': 200,
                'momentum_period': 14,
                'momentum_threshold': 0.0,
                'atr_period': 14,
                'atr_multiplier': 2.0,
                'position_pct': 200.0,
                'use_atr_stops': True,
                'use_ema_cross_exit': True,
                'use_trend_break_exit': True
            }
        },
        # More aggressive
        {
            'name': 'Aggressive (3x Leverage)',
            'params': {
                'fast_period': 5,
                'slow_period': 13,
                'trend_period': 150,
                'momentum_period': 14,
                'momentum_threshold': 0.0,
                'atr_period': 14,
                'atr_multiplier': 1.5,
                'position_pct': 300.0,
                'use_atr_stops': True,
                'use_ema_cross_exit': True,
                'use_trend_break_exit': True
            }
        },
        # More conservative
        {
            'name': 'Conservative (1.5x Leverage)',
            'params': {
                'fast_period': 10,
                'slow_period': 30,
                'trend_period': 200,
                'momentum_period': 14,
                'momentum_threshold': 1.0,
                'atr_period': 14,
                'atr_multiplier': 3.0,
                'position_pct': 150.0,
                'use_atr_stops': True,
                'use_ema_cross_exit': True,
                'use_trend_break_exit': True
            }
        },
        # Optimized for ratio
        {
            'name': 'High Ratio (Selective)',
            'params': {
                'fast_period': 8,
                'slow_period': 21,
                'trend_period': 200,
                'momentum_period': 20,
                'momentum_threshold': 2.0,
                'atr_period': 14,
                'atr_multiplier': 2.5,
                'position_pct': 250.0,
                'use_atr_stops': True,
                'use_ema_cross_exit': True,
                'use_trend_break_exit': True
            }
        },
        # Original winning strategy (for comparison)
        {
            'name': 'Original Winner (10/50 EMA 2x)',
            'params': {
                'fast_period': 10,
                'slow_period': 50,
                'trend_period': 200,
                'momentum_period': 14,
                'momentum_threshold': 0.0,
                'atr_period': 14,
                'atr_multiplier': 2.5,
                'position_pct': 200.0,
                'use_atr_stops': False,
                'use_ema_cross_exit': True,
                'use_trend_break_exit': False
            }
        }
    ]

    print("Testing configurations...")
    print()

    results = []
    for config in configurations:
        print(f"\nTesting: {config['name']}")
        print("-" * 60)

        result = test_configuration(config['params'], data_feed, config['name'])

        if result:
            results.append(result)
            print(f"  Return: {result['return']:.2f}%")
            print(f"  B&H: {result['bh_return']:.2f}%")
            print(f"  Ratio: {result['ratio']:.2f}x")
            print(f"  Trades: {result['trades']}")
            print(f"  Win Rate: {result['win_rate']:.1f}%")
            print(f"  Max DD: {result['max_dd']:.2f}%")
            print(f"  Status: {result['status']}")

    # Sort by return (total profit)
    results.sort(key=lambda x: x['return'], reverse=True)

    print("\n" + "=" * 80)
    print("RESULTS SUMMARY - SORTED BY TOTAL RETURN")
    print("=" * 80)
    print()

    print(f"{'Strategy':<35} {'Return':>12} {'Ratio':>8} {'Trades':>8} {'Win%':>6} {'MaxDD':>8}")
    print("-" * 80)

    for r in results:
        ratio_str = f"{r['ratio']:.2f}x" if not pd.isna(r['ratio']) else "N/A"
        print(f"{r['name']:<35} {r['return']:>11.2f}% {ratio_str:>8} {r['trades']:>8} {r['win_rate']:>5.1f}% {r['max_dd']:>7.1f}%")

    # Best strategy
    print("\n" + "=" * 80)
    print("WINNER: HIGHEST TOTAL RETURN")
    print("=" * 80)
    print()

    best = results[0]

    print(f"Strategy: {best['name']}")
    print()
    print("Performance:")
    print(f"  Total Return: {best['return']:.2f}%")
    print(f"  Buy & Hold: {best['bh_return']:.2f}%")
    print(f"  Ratio: {best['ratio']:.2f}x")
    print(f"  Total Trades: {best['trades']}")
    print(f"  Win Rate: {best['win_rate']:.2f}%")
    print(f"  Max Drawdown: {best['max_dd']:.2f}%")
    print(f"  Status: {best['status']}")
    print()

    print("Parameters:")
    for key, value in best['params'].items():
        print(f"  {key}: {value}")
    print()

    # Save best config
    output_dir = Path("results/maximum_profit_test")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run best configuration one more time with full reporting
    print("=" * 80)
    print("Generating full report for best strategy...")
    print("=" * 80)
    print()

    runner = BacktestRunner(
        strategy_class=MaximumProfitStrategy,
        data_feed=data_feed,
        initial_cash=100000.0,
        commission_pct=0.1,
        slippage_bps=0.5,
        **best['params']
    )

    results_final = runner.run()

    config = {
        'symbol': 'SPY',
        'strategy': best['name'],
        **best['params']
    }

    reporter = Reporter(results_final['portfolio'], results_final['broker'], config)
    reporter.save_results(output_dir)

    print(f"Results saved to: {output_dir}")
    print()
    print("Generated files:")
    print(f"  - {output_dir / 'config.json'}")
    print(f"  - {output_dir / 'summary.json'}")
    print(f"  - {output_dir / 'equity.csv'}")
    print(f"  - {output_dir / 'trades.csv'}")
    print(f"  - {output_dir / 'charts' / 'professional_overview.png'}")
    print()

    print("=" * 80)
    print("TESTING COMPLETE")
    print("=" * 80)
    print()
    print(f"Best Strategy: {best['name']}")
    print(f"Total Return: {best['return']:.2f}%")
    print(f"Ratio: {best['ratio']:.2f}x")
    print()

    return best


if __name__ == "__main__":
    import pandas as pd
    best_strategy = main()
