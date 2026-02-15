"""
TradingView Accuracy Module

Ensures 1:1 parity between Python backtester and TradingView Pine Script results
by matching TradingView's exact calculation methodology.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime


class TradingViewAlignedMetrics:
    """
    Calculate metrics using TradingView's exact methodology

    Key differences from standard calculations:
    1. Equity tracking: TradingView uses strategy.equity which includes unrealized P&L
    2. Fill timing: process_orders_on_close=false means fills happen at NEXT bar open
    3. Commission calculation: Applied to gross fill value before slippage
    4. Leverage accounting: 200% position = 2x leverage, requires margin_long=50
    5. Return calculation: (final_equity / initial_capital - 1) * 100
    """

    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital

    def calculate_buy_and_hold(
        self,
        price_data: pd.DataFrame,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Calculate Buy & Hold benchmark exactly as TradingView does

        Args:
            price_data: DataFrame with 'datetime' and 'close' columns
            start_date: First bar in date range
            end_date: Last bar in date range

        Returns:
            Dict with B&H metrics
        """
        # Filter to date range
        mask = (price_data['datetime'] >= start_date) & (price_data['datetime'] <= end_date)
        filtered = price_data[mask].copy()

        if len(filtered) == 0:
            return {
                'bh_first_close': 0.0,
                'bh_last_close': 0.0,
                'bh_return_pct': 0.0,
                'bh_bars': 0
            }

        first_close = filtered['close'].iloc[0]
        last_close = filtered['close'].iloc[-1]

        # TradingView formula: ((close / firstCloseInRange) - 1) * 100
        bh_return_pct = ((last_close / first_close) - 1) * 100 if first_close > 0 else 0.0

        return {
            'bh_first_close': first_close,
            'bh_last_close': last_close,
            'bh_return_pct': bh_return_pct,
            'bh_bars': len(filtered)
        }

    def calculate_strategy_return(self, final_equity: float) -> float:
        """
        Calculate strategy return exactly as TradingView does

        TradingView: ((strategy.equity / strategy.initial_capital) - 1) * 100
        """
        return ((final_equity / self.initial_capital) - 1) * 100

    def calculate_ratio(self, strategy_return_pct: float, bh_return_pct: float) -> float:
        """
        Calculate Strategy/B&H ratio exactly as TradingView does

        Returns NA if B&H <= 0, otherwise stratReturnPct / bhReturnPct
        """
        if bh_return_pct <= 0:
            return float('nan')
        return strategy_return_pct / bh_return_pct

    def calculate_max_drawdown_tv(self, equity_history: List[Dict]) -> float:
        """
        Calculate max drawdown using TradingView's running peak method

        TradingView method:
        var float peakEquity = strategy.initial_capital
        if strategy.equity > peakEquity
            peakEquity := strategy.equity
        currentDD = ((peakEquity - strategy.equity) / peakEquity) * 100
        """
        peak_equity = self.initial_capital
        max_dd = 0.0

        for snapshot in equity_history:
            equity = snapshot['equity']

            # Update peak
            if equity > peak_equity:
                peak_equity = equity

            # Calculate current drawdown
            current_dd = ((peak_equity - equity) / peak_equity) * 100 if peak_equity > 0 else 0.0

            # Update max
            if current_dd > max_dd:
                max_dd = current_dd

        return max_dd

    def calculate_win_rate_tv(self, trades: List[Dict]) -> Dict[str, Any]:
        """
        Calculate win rate using TradingView's method

        TradingView:
        - Iterates through strategy.closedtrades
        - Counts wins (profit > 0) and losses (profit <= 0)
        - winRate = (wins / total) * 100
        """
        if not trades:
            return {
                'wins': 0,
                'losses': 0,
                'win_rate': 0.0,
                'total_trades': 0
            }

        wins = sum(1 for t in trades if t['pnl'] > 0)
        losses = len(trades) - wins
        win_rate = (wins / len(trades)) * 100 if len(trades) > 0 else 0.0

        return {
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'total_trades': len(trades)
        }

    def verify_accuracy(
        self,
        python_metrics: Dict[str, Any],
        tradingview_metrics: Dict[str, Any],
        tolerance: float = 0.01  # 1% tolerance
    ) -> Dict[str, Any]:
        """
        Verify that Python results match TradingView results within tolerance

        Args:
            python_metrics: Metrics from Python backtester
            tradingview_metrics: Metrics from TradingView
            tolerance: Acceptable difference (default 1%)

        Returns:
            Dict with verification results
        """
        results = {
            'matches': True,
            'differences': {}
        }

        # Compare key metrics
        comparisons = [
            ('total_return_pct', 'Strategy Return %'),
            ('bh_return_pct', 'Buy & Hold Return %'),
            ('ratio', 'Ratio'),
            ('max_drawdown_pct', 'Max Drawdown %'),
            ('total_trades', 'Total Trades'),
            ('win_rate', 'Win Rate %')
        ]

        for py_key, tv_name in comparisons:
            if py_key not in python_metrics or tv_name not in tradingview_metrics:
                continue

            py_val = python_metrics[py_key]
            tv_val = tradingview_metrics[tv_name]

            # Skip NaN comparisons
            if pd.isna(py_val) or pd.isna(tv_val):
                continue

            # Calculate percent difference
            if tv_val != 0:
                pct_diff = abs((py_val - tv_val) / tv_val)
            else:
                pct_diff = abs(py_val - tv_val)

            if pct_diff > tolerance:
                results['matches'] = False
                results['differences'][py_key] = {
                    'python': py_val,
                    'tradingview': tv_val,
                    'difference_pct': pct_diff * 100
                }

        return results

    def format_metrics_tv_style(self, metrics: Dict[str, Any]) -> str:
        """
        Format metrics to match TradingView's table display

        Returns formatted string matching TradingView's output
        """
        lines = []
        lines.append("=" * 50)
        lines.append("TradingView-Style Metrics")
        lines.append("=" * 50)

        # Strategy Return
        strat_ret = metrics.get('total_return_pct', 0.0)
        lines.append(f"Strategy Return %: {strat_ret:,.2f}%")

        # Buy & Hold Return
        bh_ret = metrics.get('bh_return_pct', 0.0)
        lines.append(f"Buy & Hold Return %: {bh_ret:,.2f}%")

        # Ratio
        ratio = metrics.get('ratio', 0.0)
        if pd.isna(ratio):
            lines.append("Ratio (Strat/BH): N/A")
        else:
            lines.append(f"Ratio (Strat/BH): {ratio:.2f}x")

        # Leverage
        leverage = metrics.get('leverage', 2.0)
        lines.append(f"Leverage Used: {leverage:.1f}x")

        # Max Drawdown
        max_dd = metrics.get('max_drawdown_pct', 0.0)
        lines.append(f"Max Drawdown %: {max_dd:.2f}%")

        # Trades
        trades = metrics.get('total_trades', 0)
        lines.append(f"Total Trades: {trades}")

        # Win Rate
        win_rate = metrics.get('win_rate', 0.0)
        lines.append(f"Win Rate %: {win_rate:.2f}%")

        # Wins/Losses
        wins = metrics.get('wins', 0)
        losses = metrics.get('losses', 0)
        lines.append(f"Wins / Losses: {wins} / {losses}")

        # Status
        status = metrics.get('status', 'N/A')
        lines.append(f"STATUS: {status}")

        lines.append("=" * 50)

        return "\n".join(lines)


class TradingViewFillModel:
    """
    Fill model that exactly matches TradingView's execution

    TradingView defaults (when process_orders_on_close=false):
    - Orders placed on bar t
    - Orders fill at OPEN of bar t+1
    - Commission applied to gross value
    - Slippage applied as additional cost
    """

    def __init__(
        self,
        commission_pct: float = 0.1,  # TradingView default
        slippage_ticks: int = 2,       # TradingView default
        tick_size: float = 0.01        # For SPY
    ):
        self.commission_pct = commission_pct
        self.slippage_ticks = slippage_ticks
        self.tick_size = tick_size

    def calculate_fill_costs(
        self,
        fill_price: float,
        quantity: int,
        side: str
    ) -> Dict[str, float]:
        """
        Calculate costs exactly as TradingView does

        Args:
            fill_price: Price at which order fills
            quantity: Number of shares
            side: 'BUY' or 'SELL'

        Returns:
            Dict with commission, slippage, and total cost
        """
        gross_value = fill_price * quantity

        # Commission: strategy.commission.percent
        commission = gross_value * (self.commission_pct / 100.0)

        # Slippage: strategy.slippage ticks
        slippage = self.slippage_ticks * self.tick_size * quantity

        # Total cost (for buys) or reduction in proceeds (for sells)
        total_cost = commission + slippage

        return {
            'fill_price': fill_price,
            'gross_value': gross_value,
            'commission': commission,
            'slippage': slippage,
            'total_cost': total_cost,
            'net_price': fill_price + (total_cost / quantity) if side == 'BUY' else fill_price - (total_cost / quantity)
        }

    def get_fill_price(
        self,
        current_bar: Dict,
        next_bar: Dict,
        order_type: str = 'MARKET'
    ) -> float:
        """
        Get fill price based on TradingView's logic

        For market orders with process_orders_on_close=false:
        - Fill at next bar's OPEN
        """
        if order_type == 'MARKET':
            return next_bar['open']

        # For limit/stop orders, would need additional logic
        return next_bar['open']


def create_tradingview_aligned_report(
    portfolio,
    broker,
    price_data: pd.DataFrame,
    start_date: datetime,
    end_date: datetime,
    leverage: float = 2.0
) -> Dict[str, Any]:
    """
    Generate a report that exactly matches TradingView's output

    Args:
        portfolio: Portfolio object from backtest
        broker: Broker object from backtest
        price_data: Full price DataFrame
        start_date: Backtest start date
        end_date: Backtest end date
        leverage: Leverage multiplier used

    Returns:
        Dict with TradingView-aligned metrics
    """
    tv_metrics = TradingViewAlignedMetrics(initial_capital=portfolio.initial_cash)

    # Calculate Buy & Hold
    bh_metrics = tv_metrics.calculate_buy_and_hold(price_data, start_date, end_date)

    # Calculate Strategy Return
    final_equity = portfolio.equity_history[-1]['equity'] if portfolio.equity_history else portfolio.initial_cash
    strategy_return = tv_metrics.calculate_strategy_return(final_equity)

    # Calculate Ratio
    ratio = tv_metrics.calculate_ratio(strategy_return, bh_metrics['bh_return_pct'])

    # Calculate Max Drawdown
    max_dd = tv_metrics.calculate_max_drawdown_tv(portfolio.equity_history)

    # Build trades list
    from .reporting import PerformanceMetrics
    perf = PerformanceMetrics(portfolio, broker)
    trades = perf.trades_df.to_dict('records') if not perf.trades_df.empty else []

    # Calculate Win Rate
    win_metrics = tv_metrics.calculate_win_rate_tv(trades)

    # Pass/Fail Logic
    min_trades = 30
    max_dd_allowed = 50.0
    pass_threshold = 2.0

    status = "PASS"
    if pd.isna(ratio):
        status = "FAIL: BH <= 0"
    elif ratio < pass_threshold:
        status = f"FAIL: Ratio<{pass_threshold:.1f}"
    elif win_metrics['total_trades'] < min_trades:
        status = f"FAIL: Trades<{min_trades}"
    elif max_dd > max_dd_allowed:
        status = f"FAIL: DD>{max_dd_allowed:.0f}%"

    # Combine all metrics
    return {
        'initial_equity': portfolio.initial_cash,
        'final_equity': final_equity,
        'total_return_pct': strategy_return,
        'bh_return_pct': bh_metrics['bh_return_pct'],
        'ratio': ratio,
        'leverage': leverage,
        'max_drawdown_pct': max_dd,
        'total_trades': win_metrics['total_trades'],
        'wins': win_metrics['wins'],
        'losses': win_metrics['losses'],
        'win_rate': win_metrics['win_rate'],
        'status': status,
        'start_date': start_date.strftime("%Y-%m-%d"),
        'end_date': end_date.strftime("%Y-%m-%d"),
    }
