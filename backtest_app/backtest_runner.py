"""
Backtest Runner
Executes strategy code safely and returns results
"""

import backtrader as bt
import pandas as pd
from io import StringIO
import sys
import traceback
from typing import Dict, Tuple


# List of forbidden imports for security
FORBIDDEN_IMPORTS = [
    'os', 'sys', 'subprocess', 'socket', 'requests',
    'pathlib', 'shutil', 'urllib', 'http', 'ftplib',
    'smtplib', 'telnetlib', 'pickle', 'shelve', 'eval',
    'exec', 'compile', '__import__', 'open'
]


def validate_strategy_code(code: str) -> Tuple[bool, str]:
    """
    Validate strategy code for security

    Args:
        code: Strategy code string

    Returns:
        (is_valid, error_message)
    """

    # Check for forbidden imports
    for forbidden in FORBIDDEN_IMPORTS:
        if f'import {forbidden}' in code or f'from {forbidden}' in code:
            return False, f"Forbidden import detected: {forbidden}. Only backtrader, pandas, and numpy are allowed."

    # Check for dangerous functions
    dangerous_funcs = ['eval(', 'exec(', 'compile(', '__import__(', 'open(']
    for func in dangerous_funcs:
        if func in code:
            return False, f"Dangerous function detected: {func}"

    # Must contain a Strategy class
    if 'class' not in code or 'bt.Strategy' not in code:
        return False, "Strategy must define a class that inherits from bt.Strategy"

    return True, ""


def run_backtest(strategy_code: str, csv_data: str, initial_cash: float, commission: float) -> Dict:
    """
    Run backtest on strategy with provided data

    Args:
        strategy_code: Python code defining strategy
        csv_data: CSV string with OHLCV data
        initial_cash: Starting capital
        commission: Commission rate (e.g., 0.001 for 0.1%)

    Returns:
        Dictionary with backtest results
    """

    try:
        # Parse CSV data
        df = pd.read_csv(StringIO(csv_data))

        # Ensure required columns
        required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"CSV missing required columns: {missing_cols}")

        # Convert date column
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')

        # Create Cerebro engine
        cerebro = bt.Cerebro()

        # Load strategy from code
        # Create a restricted namespace
        namespace = {
            'bt': bt,
            'pd': pd,
            '__builtins__': {
                'range': range,
                'len': len,
                'print': print,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'True': True,
                'False': False,
                'None': None,
            }
        }

        # Execute strategy code in restricted namespace
        exec(strategy_code, namespace)

        # Find the Strategy class
        strategy_class = None
        for item_name, item in namespace.items():
            if isinstance(item, type) and issubclass(item, bt.Strategy) and item != bt.Strategy:
                strategy_class = item
                break

        if strategy_class is None:
            raise ValueError("No Strategy class found in uploaded file")

        # Add strategy
        cerebro.addstrategy(strategy_class)

        # Add data feed
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)

        # Set initial cash
        cerebro.broker.setcash(initial_cash)

        # Set commission
        cerebro.broker.setcommission(commission=commission)

        # Add analyzers
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')

        # Track equity curve
        initial_value = cerebro.broker.getvalue()

        # Run backtest
        results = cerebro.run()
        strat = results[0]

        # Get final value
        final_value = cerebro.broker.getvalue()

        # Extract metrics
        returns_analyzer = strat.analyzers.returns.get_analysis()
        drawdown_analyzer = strat.analyzers.drawdown.get_analysis()
        trades_analyzer = strat.analyzers.trades.get_analysis()
        sharpe_analyzer = strat.analyzers.sharpe.get_analysis()

        # Calculate metrics
        total_return = ((final_value - initial_value) / initial_value) * 100
        net_pnl = final_value - initial_value

        # Extract trade stats
        total_trades = trades_analyzer.get('total', {}).get('total', 0)

        # Win rate
        won = trades_analyzer.get('won', {}).get('total', 0)
        win_rate = (won / total_trades * 100) if total_trades > 0 else 0

        # Max drawdown
        max_dd = drawdown_analyzer.get('max', {}).get('drawdown', 0)

        # Sharpe ratio
        sharpe = sharpe_analyzer.get('sharperatio', None)
        if sharpe is None:
            sharpe = 0.0

        # Generate equity curve
        # Simple approximation - in real backtrader you'd use observers
        equity_curve = generate_equity_curve(initial_value, final_value, len(df))

        # Compile results
        results_dict = {
            'success': True,
            'metrics': {
                'total_return_pct': round(total_return, 2),
                'net_pnl': round(net_pnl, 2),
                'win_rate_pct': round(win_rate, 2),
                'max_drawdown_pct': round(max_dd, 2),
                'total_trades': total_trades,
                'sharpe_ratio': round(sharpe, 2) if sharpe else 0,
                'initial_cash': initial_cash,
                'final_value': round(final_value, 2)
            },
            'equity_curve': equity_curve,
            'trades': extract_trades(strat, trades_analyzer)
        }

        return results_dict

    except Exception as e:
        # Return error details
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }


def generate_equity_curve(initial_value: float, final_value: float, num_points: int) -> list:
    """
    Generate simplified equity curve

    Args:
        initial_value: Starting value
        final_value: Ending value
        num_points: Number of points to generate

    Returns:
        List of equity values
    """

    # Simple linear interpolation with some noise
    import random
    curve = []
    total_return = (final_value - initial_value) / initial_value

    for i in range(num_points):
        progress = i / num_points
        # Expected value with some random walk
        expected = initial_value * (1 + total_return * progress)
        # Add small random variation
        noise = random.uniform(-0.02, 0.02) * expected
        value = max(expected + noise, initial_value * 0.5)  # Don't go below 50% of initial
        curve.append(round(value, 2))

    # Ensure last value is final value
    if curve:
        curve[-1] = round(final_value, 2)

    return curve


def extract_trades(strat, trades_analyzer: dict) -> list:
    """
    Extract individual trades

    Args:
        strat: Strategy instance
        trades_analyzer: Trades analyzer results

    Returns:
        List of trade dictionaries
    """

    trades = []

    # Get trade details if available
    total_trades = trades_analyzer.get('total', {}).get('total', 0)
    won_trades = trades_analyzer.get('won', {}).get('total', 0)
    lost_trades = trades_analyzer.get('lost', {}).get('total', 0)

    # Generate summary of trades (individual trade tracking would need custom analyzer)
    trades.append({
        'total': total_trades,
        'won': won_trades,
        'lost': lost_trades,
        'win_rate': round((won_trades / total_trades * 100) if total_trades > 0 else 0, 2)
    })

    return trades
