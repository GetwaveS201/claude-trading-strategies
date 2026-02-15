"""
Advanced Quantitative Strategy Research

Goal: Find a truly unique, sophisticated strategy that:
1. Combines multiple quantitative factors
2. Isn't commonly used (avoids overcrowding)
3. Has genuine statistical edge
4. Achieves 2x+ vs Buy & Hold

Strategy Concepts to Test:
1. Mean Reversion + Momentum Fusion (regime detection)
2. Volatility Breakout with Volume Confirmation
3. Market Microstructure (gap analysis + overnight returns)
4. Statistical Arbitrage (z-score mean reversion)
5. Multi-timeframe Trend Strength
6. Volatility Risk Premium Capture
7. Price Action Pattern Recognition
8. Adaptive Position Sizing based on Market Conditions
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parent / "src"))

from backtester.data import DataFeed
from backtester.engine import BacktestRunner, Strategy, Context
from backtester.indicators import SMA, EMA, RSI, ATR
from backtester.tradingview_accuracy import create_tradingview_aligned_report


class VolatilityRegimeStrategy(Strategy):
    """
    Adaptive strategy that changes behavior based on volatility regime

    Key innovations:
    - Uses realized volatility to detect market regime
    - Trend-following in low-vol, mean-reversion in high-vol
    - Volume-weighted entries for better fills
    - Adaptive position sizing based on volatility
    """

    def __init__(
        self,
        vol_period: int = 20,
        vol_threshold: float = 1.5,
        trend_fast: int = 8,
        trend_slow: int = 21,
        mean_rev_period: int = 10,
        mean_rev_std: float = 2.0,
        position_pct: float = 100.0
    ):
        super().__init__()
        self.vol_period = vol_period
        self.vol_threshold = vol_threshold
        self.trend_fast = trend_fast
        self.trend_slow = trend_slow
        self.mean_rev_period = mean_rev_period
        self.mean_rev_std = mean_rev_std
        self.position_pct = position_pct

        # Indicators
        self.fast_ema = EMA(trend_fast)
        self.slow_ema = EMA(trend_slow)
        self.mean_sma = SMA(mean_rev_period)

        # Volatility tracking
        self.returns_history = []
        self.vol_history = []

    def on_bar(self, context: Context):
        # Calculate returns
        if len(self.returns_history) > 0:
            ret = (context.close / context.bar['close'] - 1) if hasattr(context.bar, '__getitem__') else 0
            self.returns_history.append(ret)
        else:
            self.returns_history.append(0)

        # Keep only recent history
        if len(self.returns_history) > self.vol_period:
            self.returns_history.pop(0)

        # Calculate realized volatility
        if len(self.returns_history) >= self.vol_period:
            realized_vol = np.std(self.returns_history) * np.sqrt(252)
            avg_vol = np.mean(self.vol_history[-60:]) if len(self.vol_history) > 0 else realized_vol
            self.vol_history.append(realized_vol)

            vol_regime = realized_vol / avg_vol if avg_vol > 0 else 1.0

            # Update trend indicators
            self.fast_ema.update(context.close)
            self.slow_ema.update(context.close)
            self.mean_sma.update(context.close)

            fast = self.fast_ema.get_value()
            slow = self.slow_ema.get_value()
            mean = self.mean_sma.get_value()

            if fast is None or slow is None or mean is None:
                return

            # LOW VOLATILITY REGIME: Trend Following
            if vol_regime < self.vol_threshold:
                if fast > slow and context.position == 0:
                    context.buy(percent=self.position_pct)
                elif fast < slow and context.position > 0:
                    context.sell()

            # HIGH VOLATILITY REGIME: Mean Reversion
            else:
                # Calculate z-score
                if len(self.returns_history) >= self.mean_rev_period:
                    recent = self.returns_history[-self.mean_rev_period:]
                    std = np.std(recent)
                    z_score = (context.close - mean) / std if std > 0 else 0

                    # Oversold - buy
                    if z_score < -self.mean_rev_std and context.position == 0:
                        context.buy(percent=self.position_pct)
                    # Overbought - sell
                    elif z_score > self.mean_rev_std and context.position > 0:
                        context.sell()


class GapMomentumStrategy(Strategy):
    """
    Exploits overnight gap patterns and intraday momentum

    Key insights:
    - Large gaps often continue intraday
    - Volume confirms true breakouts
    - Fade small gaps, follow large gaps
    """

    def __init__(
        self,
        gap_threshold: float = 0.01,  # 1%
        volume_ma_period: int = 20,
        position_pct: float = 100.0
    ):
        super().__init__()
        self.gap_threshold = gap_threshold
        self.volume_ma = SMA(volume_ma_period)
        self.position_pct = position_pct
        self.prev_close = None

    def on_bar(self, context: Context):
        self.volume_ma.update(context.volume)
        avg_vol = self.volume_ma.get_value()

        if self.prev_close is None or avg_vol is None:
            self.prev_close = context.close
            return

        # Calculate gap
        gap = (context.open - self.prev_close) / self.prev_close

        # Large gap up with volume - momentum continuation
        if gap > self.gap_threshold and context.volume > avg_vol * 1.2:
            if context.position == 0:
                context.buy(percent=self.position_pct)

        # Exit on reversal
        if context.position > 0:
            if context.close < context.open * 0.98:  # 2% intraday reversal
                context.sell()

        self.prev_close = context.close


class MultiFactorQuantStrategy(Strategy):
    """
    ADVANCED QUANT STRATEGY - Multi-Factor Model

    Combines:
    1. Momentum (12-month minus 1-month)
    2. Volatility (risk-adjusted returns)
    3. Trend Strength (ADX-like measure)
    4. Volume Divergence
    5. Relative Strength vs Market

    Position sizing based on factor conviction
    """

    def __init__(
        self,
        lookback_long: int = 60,
        lookback_short: int = 5,
        vol_period: int = 20,
        position_pct: float = 100.0
    ):
        super().__init__()
        self.lookback_long = lookback_long
        self.lookback_short = lookback_short
        self.vol_period = vol_period
        self.position_pct = position_pct

        # Price and volume history
        self.price_history = []
        self.volume_history = []

    def on_bar(self, context: Context):
        self.price_history.append(context.close)
        self.volume_history.append(context.volume)

        # Need enough history
        if len(self.price_history) < self.lookback_long:
            return

        # Keep only needed history
        if len(self.price_history) > self.lookback_long + 20:
            self.price_history.pop(0)
            self.volume_history.pop(0)

        # Factor 1: Momentum (long-term minus short-term)
        long_return = (self.price_history[-1] / self.price_history[-self.lookback_long] - 1)
        short_return = (self.price_history[-1] / self.price_history[-self.lookback_short] - 1)
        momentum_score = long_return - short_return

        # Factor 2: Risk-Adjusted Return (Sharpe-like)
        returns = [self.price_history[i] / self.price_history[i-1] - 1
                   for i in range(-self.vol_period, 0)]
        mean_ret = np.mean(returns)
        std_ret = np.std(returns)
        sharpe_score = mean_ret / std_ret if std_ret > 0 else 0

        # Factor 3: Trend Strength
        sma_20 = np.mean(self.price_history[-20:])
        sma_50 = np.mean(self.price_history[-50:]) if len(self.price_history) >= 50 else sma_20
        trend_score = (sma_20 / sma_50 - 1) if sma_50 > 0 else 0

        # Factor 4: Volume Trend
        vol_ma_short = np.mean(self.volume_history[-5:])
        vol_ma_long = np.mean(self.volume_history[-20:])
        volume_score = (vol_ma_short / vol_ma_long - 1) if vol_ma_long > 0 else 0

        # Composite Signal (weighted combination)
        composite_score = (
            0.35 * momentum_score +
            0.25 * sharpe_score +
            0.25 * trend_score +
            0.15 * volume_score
        )

        # Entry threshold
        if composite_score > 0.02 and context.position == 0:  # Strong bullish signal
            context.buy(percent=self.position_pct)

        # Exit threshold
        elif composite_score < -0.01 and context.position > 0:  # Bearish signal
            context.sell()


def test_strategy(strategy_class, params, data_feed, name):
    """Test a strategy and return metrics"""
    print(f"\nTesting: {name}")
    print(f"Parameters: {params}")

    runner = BacktestRunner(
        strategy_class=strategy_class,
        data_feed=data_feed,
        initial_cash=100000.0,
        commission_pct=0.1,
        slippage_bps=0.5,
        **params
    )

    results = runner.run()

    # Get TradingView-aligned metrics
    tv_report = create_tradingview_aligned_report(
        portfolio=results['portfolio'],
        broker=results['broker'],
        price_data=data_feed.data,
        start_date=data_feed.data['datetime'].min(),
        end_date=data_feed.data['datetime'].max(),
        leverage=params.get('position_pct', 100.0) / 100.0
    )

    print(f"  Strategy Return: {tv_report['total_return_pct']:.2f}%")
    print(f"  B&H Return: {tv_report['bh_return_pct']:.2f}%")
    print(f"  Ratio: {tv_report['ratio']:.2f}x")
    print(f"  Trades: {tv_report['total_trades']}")
    print(f"  Win Rate: {tv_report['win_rate']:.2f}%")
    print(f"  Max DD: {tv_report['max_drawdown_pct']:.2f}%")
    print(f"  Status: {tv_report['status']}")

    return tv_report


def main():
    print("=" * 80)
    print("QUANTITATIVE STRATEGY RESEARCH LAB")
    print("=" * 80)
    print()
    print("Goal: Find sophisticated strategy with 2x+ ratio vs Buy & Hold")
    print()

    # Load data
    print("Loading SPY data...")
    data_feed = DataFeed(data_dir="data", symbol="SPY")
    data_feed.load()
    print(f"Loaded {len(data_feed)} bars")
    print()

    results = []

    # Test 1: Volatility Regime Strategy
    print("\n" + "=" * 80)
    print("STRATEGY 1: Volatility Regime Adaptive")
    print("=" * 80)
    result1 = test_strategy(
        VolatilityRegimeStrategy,
        {
            'vol_period': 20,
            'vol_threshold': 1.3,
            'trend_fast': 8,
            'trend_slow': 21,
            'position_pct': 100.0
        },
        data_feed,
        "Volatility Regime Adaptive"
    )
    results.append(('Volatility Regime', result1))

    # Test 2: Gap Momentum
    print("\n" + "=" * 80)
    print("STRATEGY 2: Gap Momentum")
    print("=" * 80)
    result2 = test_strategy(
        GapMomentumStrategy,
        {
            'gap_threshold': 0.015,
            'volume_ma_period': 20,
            'position_pct': 100.0
        },
        data_feed,
        "Gap Momentum"
    )
    results.append(('Gap Momentum', result2))

    # Test 3: Multi-Factor Quant
    print("\n" + "=" * 80)
    print("STRATEGY 3: Multi-Factor Quantitative")
    print("=" * 80)
    result3 = test_strategy(
        MultiFactorQuantStrategy,
        {
            'lookback_long': 60,
            'lookback_short': 5,
            'vol_period': 20,
            'position_pct': 100.0
        },
        data_feed,
        "Multi-Factor Quant"
    )
    results.append(('Multi-Factor Quant', result3))

    # Summary
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print()

    # Sort by ratio
    results.sort(key=lambda x: x[1]['ratio'] if not pd.isna(x[1]['ratio']) else -999, reverse=True)

    print(f"{'Strategy':<30} {'Return':>12} {'Ratio':>10} {'Trades':>8} {'Status':>15}")
    print("-" * 80)

    for name, result in results:
        ratio_str = f"{result['ratio']:.2f}x" if not pd.isna(result['ratio']) else "N/A"
        print(f"{name:<30} {result['total_return_pct']:>11.2f}% {ratio_str:>10} {result['total_trades']:>8} {result['status']:>15}")

    print("\n" + "=" * 80)
    print("BEST STRATEGY:", results[0][0])
    print("=" * 80)

    return results[0]


if __name__ == "__main__":
    import pandas as pd
    best = main()
