# Backtester - Professional Stock Backtesting Engine

A complete, production-ready backtesting engine with strict no-look-ahead guarantees.

## Features

- **Event-driven architecture**: Bar-by-bar simulation with proper order execution timing
- **Multiple order types**: Market, Limit, Stop orders with realistic fill simulation
- **Costs modeling**: Configurable fees and slippage
- **Position sizing**: Fixed shares, percent of equity, or risk-based sizing
- **Technical indicators**: SMA, EMA, RSI, ATR with guaranteed no look-ahead
- **Comprehensive reporting**: Trades, equity curves, metrics, and charts
- **Parameter optimization**: Grid search with performance ranking
- **Walk-forward analysis**: Rolling out-of-sample validation
- **Full test suite**: Unit tests + smoke tests for reliability

## Installation

```bash
pip install -e .
```

## Quick Start

### Run a backtest

```bash
python -m backtester run --data ./data --strategy ma_cross --symbol SPY --start 2015-01-01 --end 2025-01-01
```

### Run parameter sweep

```bash
python -m backtester sweep --data ./data --strategy ma_cross --symbol SPY --fast 10,20,30 --slow 50,100,200
```

### Run walk-forward analysis

```bash
python -m backtester walkforward --data ./data --strategy ma_cross --symbol SPY --train_days 756 --test_days 252
```

## Testing

```bash
pytest tests/ -v
```

## Project Structure

- `src/backtester/` - Core engine
  - `cli.py` - Command-line interface
  - `data.py` - Data loading and validation
  - `engine.py` - Main backtest runner
  - `broker.py` - Portfolio and position management
  - `orders.py` - Order and fill objects
  - `indicators.py` - Technical indicators
  - `reporting.py` - Metrics and chart generation
  - `optimize.py` - Parameter sweep
  - `walkforward.py` - Walk-forward validation
  - `strategies/` - Strategy implementations
- `tests/` - Test suite
- `examples/` - Example scripts
- `data/` - Sample data

## Included Strategies

1. **MA Cross** (`ma_cross`): Moving average crossover
2. **RSI Mean Reversion** (`rsi_meanrev`): Oversold/overbought signals

## Default Settings

- Starting cash: $100,000
- Market orders fill at next bar open
- Fees: $1.00 per fill
- Slippage: 1 basis point (0.01%)
- Daily bars
- Long-only (no shorting)

## Output

Results are saved to `results/<run_id>/`:
- `config.json` - Run configuration
- `trades.csv` - All trades with P&L
- `equity.csv` - Daily equity curve
- `summary.json` - Performance metrics
- `charts/` - PNG visualizations

## Metrics

- CAGR (Compound Annual Growth Rate)
- Maximum Drawdown
- Sharpe Ratio (daily)
- Sortino Ratio (daily)
- Win Rate
- Profit Factor
- Average Win/Loss
- Exposure (% time in market)
- Total Trades

## License

MIT
