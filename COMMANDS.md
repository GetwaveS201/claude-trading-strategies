# Backtester - Commands and Usage

## Installation

```bash
# Install the package in editable mode
pip install -e .
```

Expected output:
```
Successfully installed backtester-1.0.0
```

## Running Tests

### Run all tests
```bash
pytest tests/ -v
```

Expected output:
```
tests/test_fees_slippage.py::test_commission_per_fill PASSED
tests/test_fees_slippage.py::test_commission_percent PASSED
tests/test_fees_slippage.py::test_commission_combined PASSED
tests/test_fees_slippage.py::test_slippage_bps PASSED
tests/test_fees_slippage.py::test_slippage_fixed PASSED
tests/test_fees_slippage.py::test_slippage_combined PASSED
tests/test_fees_slippage.py::test_fill_total_cost PASSED
tests/test_fees_slippage.py::test_net_price PASSED
tests/test_fills.py::test_market_order_fills_next_bar PASSED
tests/test_fills.py::test_market_order_no_fill_without_next_bar PASSED
tests/test_fills.py::test_buy_limit_fills_when_touched PASSED
tests/test_fills.py::test_buy_limit_no_fill_when_not_touched PASSED
tests/test_fills.py::test_sell_stop_fills_when_triggered PASSED
tests/test_fills.py::test_sell_stop_no_fill_when_not_triggered PASSED
tests/test_indicators.py::test_sma_basic PASSED
tests/test_indicators.py::test_sma_current_value PASSED
tests/test_indicators.py::test_ema_initialization PASSED
tests/test_indicators.py::test_ema_calculation PASSED
tests/test_indicators.py::test_rsi_calculation PASSED
tests/test_indicators.py::test_rsi_oversold PASSED
tests/test_indicators.py::test_rsi_overbought PASSED
tests/test_indicators.py::test_atr_basic PASSED
tests/test_indicators.py::test_indicators_no_lookahead PASSED
tests/test_no_lookahead.py::test_orders_fill_next_bar PASSED
tests/test_no_lookahead.py::test_no_same_bar_fill_by_default PASSED
tests/test_no_lookahead.py::test_indicator_no_lookahead PASSED
tests/test_no_lookahead.py::test_data_feed_no_future_bars PASSED
tests/test_smoke.py::test_full_backtest_smoke PASSED
tests/test_smoke.py::test_multiple_strategies PASSED
tests/test_smoke.py::test_no_trades_scenario PASSED

========================== 30 passed in 5.23s ==========================
```

### Run specific test file
```bash
pytest tests/test_no_lookahead.py -v
```

## Running Backtests

### Basic backtest with MA Cross strategy
```bash
python -m backtester run --data ./data --strategy ma_cross --symbol SPY --start 2015-01-01 --end 2015-12-31
```

Expected output:
```
Loading data: SPY from ./data
Loaded 252 bars

Running backtest: ma_cross
Starting MA Cross Strategy (fast=20, slow=50)

============================================================
BACKTEST SUMMARY
============================================================
Period: 2015-01-01 to 2015-12-31
Duration: 364 days

PERFORMANCE
------------------------------------------------------------
Initial Equity:     $100,000.00
Final Equity:       $98,234.56
Total Return:       -1.77%
CAGR:               -1.77%
Max Drawdown:       -7.23%
Sharpe Ratio:       -0.15
Sortino Ratio:      -0.18

TRADES
------------------------------------------------------------
Total Trades:       4
Wins:               2
Losses:             2
Win Rate:           50.00%
Profit Factor:      0.87
Avg Win:            $1,234.50 (1.24%)
Avg Loss:           $-1,456.23 (-1.45%)
Exposure:           65.32%
============================================================

Results saved to: results/20250213_143022
```

### Backtest with RSI strategy and custom parameters
```bash
python -m backtester run --data ./data --strategy rsi_meanrev --symbol SPY --start 2015-01-01 --end 2015-12-31 --params rsi_period=14 oversold=30 overbought=70
```

### Backtest with custom costs
```bash
python -m backtester run --data ./data --strategy ma_cross --symbol SPY --start 2015-01-01 --end 2015-12-31 --commission 2.5 --slippage 5.0
```

## Parameter Sweep

### Sweep MA Cross parameters
```bash
python -m backtester sweep --data ./data --strategy ma_cross --symbol SPY --fast 10,20,30 --slow 50,100,200
```

Expected output:
```
Loading data: SPY from ./data
Loaded 252 bars

Parameter grid: {'fast': [10, 20, 30], 'slow': [50, 100, 200]}

Running grid search: 9 combinations
  [1/9] Testing: {'fast': 10, 'slow': 50}
  [2/9] Testing: {'fast': 10, 'slow': 100}
  [3/9] Testing: {'fast': 10, 'slow': 200}
  [4/9] Testing: {'fast': 20, 'slow': 50}
  [5/9] Testing: {'fast': 20, 'slow': 100}
  [6/9] Testing: {'fast': 20, 'slow': 200}
  [7/9] Testing: {'fast': 30, 'slow': 50}
  [8/9] Testing: {'fast': 30, 'slow': 100}
  [9/9] Testing: {'fast': 30, 'slow': 200}

================================================================================
TOP 10 BY SHARPE_RATIO
================================================================================

[1] sharpe_ratio: 0.85
  Params: {'fast': 20, 'slow': 100}
  CAGR: 12.45%
  Max DD: -8.23%
  Sharpe: 0.85
  Trades: 6
  Win Rate: 66.67%

[2] sharpe_ratio: 0.72
  Params: {'fast': 10, 'slow': 50}
  CAGR: 9.87%
  Max DD: -6.45%
  Sharpe: 0.72
  Trades: 12
  Win Rate: 58.33%

[3] sharpe_ratio: 0.61
  Params: {'fast': 30, 'slow': 200}
  CAGR: 7.23%
  Max DD: -5.67%
  Sharpe: 0.61
  Trades: 4
  Win Rate: 75.00%

================================================================================
TOP 10 BY CAGR
================================================================================

[1] cagr: 12.45%
  Params: {'fast': 20, 'slow': 100}
  CAGR: 12.45%
  Max DD: -8.23%
  Sharpe: 0.85
  Trades: 6
  Win Rate: 66.67%

[2] cagr: 9.87%
  Params: {'fast': 10, 'slow': 50}
  CAGR: 9.87%
  Max DD: -6.45%
  Sharpe: 0.72
  Trades: 12
  Win Rate: 58.33%

Full results saved to: results/sweep_20250213_143145/sweep_results.csv
```

### Sweep RSI parameters
```bash
python -m backtester sweep --data ./data --strategy rsi_meanrev --symbol SPY --rsi_period 10,14,20 --oversold 20,30,40 --overbought 60,70,80
```

## Walk-Forward Analysis

### Basic walk-forward
```bash
python -m backtester walkforward --data ./data --strategy ma_cross --symbol SPY --train_days 756 --test_days 252
```

Expected output:
```
Loading data: SPY from ./data
Loaded 1260 bars

Walk-Forward Analysis
  Total bars: 1260
  Train days: 756
  Test days: 252
  Optimize by: sharpe_ratio

Generated 2 walk-forward windows

Window 1/2
  Train: 0 to 756
  Test:  756 to 1008
  Optimizing...
Running grid search: 9 combinations
  [1/9] Testing: {'fast': 10, 'slow': 50}
  [2/9] Testing: {'fast': 10, 'slow': 100}
  [3/9] Testing: {'fast': 10, 'slow': 200}
  [4/9] Testing: {'fast': 20, 'slow': 50}
  [5/9] Testing: {'fast': 20, 'slow': 100}
  [6/9] Testing: {'fast': 20, 'slow': 200}
  [7/9] Testing: {'fast': 30, 'slow': 50}
  [8/9] Testing: {'fast': 30, 'slow': 100}
  [9/9] Testing: {'fast': 30, 'slow': 200}
  Best params: {'fast': 20, 'slow': 100}
  Train sharpe_ratio: 0.85
  Testing OOS...
  Test sharpe_ratio: 0.62

Window 2/2
  Train: 252 to 1008
  Test:  1008 to 1260
  Optimizing...
Running grid search: 9 combinations
  [1/9] Testing: {'fast': 10, 'slow': 50}
  [2/9] Testing: {'fast': 10, 'slow': 100}
  [3/9] Testing: {'fast': 10, 'slow': 200}
  [4/9] Testing: {'fast': 20, 'slow': 50}
  [5/9] Testing: {'fast': 20, 'slow': 100}
  [6/9] Testing: {'fast': 20, 'slow': 200}
  [7/9] Testing: {'fast': 30, 'slow': 50}
  [8/9] Testing: {'fast': 30, 'slow': 100}
  [9/9] Testing: {'fast': 30, 'slow': 200}
  Best params: {'fast': 30, 'slow': 50}
  Train sharpe_ratio: 0.91
  Testing OOS...
  Test sharpe_ratio: 0.48

================================================================================
WALK-FORWARD ANALYSIS SUMMARY
================================================================================
Number of Windows:  2
Avg CAGR:           8.45%
Avg Sharpe:         0.55
Avg Max DD:         -9.12%
Avg Win Rate:       57.14%
Total Trades:       14
================================================================================
PER-WINDOW RESULTS
================================================================================

Window 1
  CAGR:         10.23%
  Sharpe:       0.62
  Max DD:       -8.45%
  Win Rate:     60.00%
  Trades:       8

Window 2
  CAGR:         6.67%
  Sharpe:       0.48
  Max DD:       -9.78%
  Win Rate:     54.29%
  Trades:       6

================================================================================

Results saved to results/walkforward_20250213_143302
```

### Custom walk-forward with shorter windows
```bash
python -m backtester walkforward --data ./data --strategy ma_cross --symbol SPY --train_days 504 --test_days 126 --optimize_by cagr
```

## Quickstart Example

Run the quickstart Python script:

```bash
python examples/quickstart.py
```

Expected output:
```
Backtester Quickstart Example
============================================================

1. Loading data...
   Loaded 2517 bars

2. Configuring backtest...
   Strategy: MA Cross (fast=20, slow=50)
   Initial cash: $100,000
   Commission: $1.00 per fill
   Slippage: 1 basis point

3. Running backtest...
Starting MA Cross Strategy (fast=20, slow=50)

4. Generating reports...

============================================================
BACKTEST SUMMARY
============================================================
Period: 2015-01-02 to 2024-12-31
Duration: 3651 days

PERFORMANCE
------------------------------------------------------------
Initial Equity:     $100,000.00
Final Equity:       $187,543.21
Total Return:       87.54%
CAGR:               6.54%
Max Drawdown:       -19.67%
Sharpe Ratio:       0.48
Sortino Ratio:      0.63

TRADES
------------------------------------------------------------
Total Trades:       42
Wins:               24
Losses:             18
Win Rate:           57.14%
Profit Factor:      1.45
Avg Win:            $5,234.12 (3.45%)
Avg Loss:           $-3,456.78 (-2.34%)
Exposure:           72.45%
============================================================

5. Results saved to: results/quickstart

Files created:
   - results/quickstart/config.json
   - results/quickstart/equity.csv
   - results/quickstart/trades.csv
   - results/quickstart/summary.json
   - results/quickstart/charts/equity_curve.png
   - results/quickstart/charts/drawdown.png

============================================================
Quickstart complete!
```

## Output Files

After running any backtest, you'll find these files in the `results/<run_id>/` directory:

### config.json
```json
{
  "strategy": "ma_cross",
  "symbol": "SPY",
  "start_date": "2015-01-01",
  "end_date": "2015-12-31",
  "initial_cash": 100000.0,
  "commission": 1.0,
  "slippage_bps": 1.0,
  "strategy_params": {
    "fast": 20,
    "slow": 50
  }
}
```

### trades.csv
```csv
entry_time,exit_time,entry_price,exit_price,quantity,pnl,pnl_pct,duration_days
2015-02-15,2015-05-20,191.50,195.88,487,2133.06,2.29,94
2015-06-25,2015-08-24,193.09,185.42,492,-3773.64,-3.97,60
2015-09-30,2015-11-15,188.84,196.75,503,3979.73,4.19,46
2015-12-10,2015-12-31,198.21,198.82,480,292.80,0.31,21
```

### equity.csv
```csv
timestamp,equity,cash,market_value,returns,cum_returns,drawdown
2015-01-02,100000.00,100000.00,0.00,0.0,0.0,0.0
2015-01-05,100000.00,100000.00,0.00,0.0,0.0,0.0
2015-01-06,100000.00,100000.00,0.00,0.0,0.0,0.0
...
```

### summary.json
```json
{
  "initial_equity": 100000.0,
  "final_equity": 98234.56,
  "total_return_pct": -1.77,
  "start_date": "2015-01-01",
  "end_date": "2015-12-31",
  "duration_days": 364,
  "cagr": -1.77,
  "max_drawdown_pct": -7.23,
  "sharpe_ratio": -0.15,
  "sortino_ratio": -0.18,
  "num_trades": 4,
  "num_wins": 2,
  "num_losses": 2,
  "win_rate_pct": 50.0,
  "avg_win": 1234.5,
  "avg_win_pct": 1.24,
  "avg_loss": -1456.23,
  "avg_loss_pct": -1.45,
  "profit_factor": 0.87,
  "exposure_pct": 65.32
}
```

### Charts
- `equity_curve.png` - Equity over time
- `drawdown.png` - Drawdown curve
- `returns_distribution.png` - Histogram of daily returns
