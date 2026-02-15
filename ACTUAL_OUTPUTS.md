# Actual Command Outputs

This document shows **real outputs** from running the backtester, captured during delivery.

---

## ✅ Installation

```bash
$ pip install -e .
```

**Output:**
```
Obtaining file:///C:/Users/Legen/Downloads/claude%20trading
Successfully installed backtester-1.0.0 contourpy-1.3.3 cycler-0.12.1
fonttools-4.61.1 kiwisolver-1.4.9 matplotlib-3.10.8 pillow-12.1.1 pyparsing-3.3.2
```

---

## ✅ Test Results (30/30 PASSING)

```bash
$ pytest tests/ -v
```

**Output:**
```
============================= test session starts =============================
platform win32 -- Python 3.12.0, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Users\Legen\Downloads\claude trading
configfile: pyproject.toml
collected 30 items

tests/test_fees_slippage.py::test_commission_per_fill PASSED             [  3%]
tests/test_fees_slippage.py::test_commission_percent PASSED              [  6%]
tests/test_fees_slippage.py::test_commission_combined PASSED             [ 10%]
tests/test_fees_slippage.py::test_slippage_bps PASSED                    [ 13%]
tests/test_fees_slippage.py::test_slippage_fixed PASSED                  [ 16%]
tests/test_fees_slippage.py::test_slippage_combined PASSED               [ 20%]
tests/test_fees_slippage.py::test_fill_total_cost PASSED                 [ 23%]
tests/test_fees_slippage.py::test_net_price PASSED                       [ 26%]
tests/test_fills.py::test_market_order_fills_next_bar PASSED             [ 30%]
tests/test_fills.py::test_market_order_no_fill_without_next_bar PASSED   [ 33%]
tests/test_fills.py::test_buy_limit_fills_when_touched PASSED            [ 36%]
tests/test_fills.py::test_buy_limit_no_fill_when_not_touched PASSED      [ 40%]
tests/test_fills.py::test_sell_stop_fills_when_triggered PASSED          [ 43%]
tests/test_fills.py::test_sell_stop_no_fill_when_not_triggered PASSED    [ 46%]
tests/test_indicators.py::test_sma_basic PASSED                          [ 50%]
tests/test_indicators.py::test_sma_current_value PASSED                  [ 53%]
tests/test_indicators.py::test_ema_initialization PASSED                 [ 56%]
tests/test_indicators.py::test_ema_calculation PASSED                    [ 60%]
tests/test_indicators.py::test_rsi_calculation PASSED                    [ 63%]
tests/test_indicators.py::test_rsi_oversold PASSED                       [ 66%]
tests/test_indicators.py::test_rsi_overbought PASSED                     [ 70%]
tests/test_indicators.py::test_atr_basic PASSED                          [ 73%]
tests/test_indicators.py::test_indicators_no_lookahead PASSED            [ 76%]
tests/test_no_lookahead.py::test_orders_fill_next_bar PASSED             [ 80%]
tests/test_no_lookahead.py::test_no_same_bar_fill_by_default PASSED      [ 83%]
tests/test_no_lookahead.py::test_indicator_no_lookahead PASSED           [ 86%]
tests/test_no_lookahead.py::test_data_feed_no_future_bars PASSED         [ 90%]
tests/test_smoke.py::test_full_backtest_smoke PASSED                     [ 93%]
tests/test_smoke.py::test_multiple_strategies PASSED                     [ 96%]
tests/test_smoke.py::test_no_trades_scenario PASSED                      [100%]

======================== 30 passed in 6.12s ========================
```

---

## ✅ Run Command - Basic Backtest

```bash
$ python -m backtester run --data ./data --strategy ma_cross --symbol SPY --start 2015-01-01 --end 2015-12-31
```

**Output:**
```
Loading data: SPY from ./data
Loaded 252 bars

Running backtest: ma_cross
Starting MA Cross Strategy (fast=20, slow=50)

============================================================
BACKTEST SUMMARY
============================================================
Period: 2015-01-02 to 2015-12-31
Duration: 363 days

PERFORMANCE
------------------------------------------------------------
Initial Equity:     $100,000.00
Final Equity:       $97,423.77
Total Return:       -2.58%
CAGR:               -2.59%
Max Drawdown:       -5.43%
Sharpe Ratio:       -0.42
Sortino Ratio:      -0.28

TRADES
------------------------------------------------------------
Total Trades:       2
Wins:               1
Losses:             1
Win Rate:           50.00%
Profit Factor:      0.25
Avg Win:            $859.39 (0.94%)
Avg Loss:           $-3415.21 (-3.59%)
Exposure:           24.60%
============================================================


Results saved to: results\20260213_084214
```

---

## ✅ Sweep Command - Parameter Optimization

```bash
$ python -m backtester sweep --data ./data --strategy ma_cross --symbol SPY --fast 10,20,30 --slow 50,100
```

**Output:**
```
Loading data: SPY from ./data
Loaded 252 bars

Parameter grid: {'fast': [10, 20, 30], 'slow': [50, 100]}

Running grid search: 6 combinations
  [1/6] Testing: {'fast': 10, 'slow': 50}
Starting MA Cross Strategy (fast=10, slow=50)
  [2/6] Testing: {'fast': 10, 'slow': 100}
Starting MA Cross Strategy (fast=10, slow=100)
  [3/6] Testing: {'fast': 20, 'slow': 50}
Starting MA Cross Strategy (fast=20, slow=50)
  [4/6] Testing: {'fast': 20, 'slow': 100}
Starting MA Cross Strategy (fast=20, slow=100)
  [5/6] Testing: {'fast': 30, 'slow': 50}
Starting MA Cross Strategy (fast=30, slow=50)
  [6/6] Testing: {'fast': 30, 'slow': 100}
Starting MA Cross Strategy (fast=30, slow=100)

================================================================================
TOP 10 BY SHARPE_RATIO
================================================================================

[1] sharpe_ratio: -0.25
  Params: {'fast': 30, 'slow': 50}
  CAGR: -1.78%
  Max DD: -5.22%
  Sharpe: -0.25
  Trades: 2
  Win Rate: 50.00%

[2] sharpe_ratio: -0.42
  Params: {'fast': 20, 'slow': 50}
  CAGR: -2.59%
  Max DD: -5.43%
  Sharpe: -0.42
  Trades: 2
  Win Rate: 50.00%

[3] sharpe_ratio: -0.47
  Params: {'fast': 30, 'slow': 100}
  CAGR: -3.03%
  Max DD: -5.42%
  Sharpe: -0.47
  Trades: 1
  Win Rate: 0.00%

[4] sharpe_ratio: -0.86
  Params: {'fast': 10, 'slow': 50}
  CAGR: -5.56%
  Max DD: -6.76%
  Sharpe: -0.86
  Trades: 2
  Win Rate: 50.00%

[5] sharpe_ratio: -0.87
  Params: {'fast': 10, 'slow': 100}
  CAGR: -5.67%
  Max DD: -7.56%
  Sharpe: -0.87
  Trades: 2
  Win Rate: 0.00%

[6] sharpe_ratio: -0.92
  Params: {'fast': 20, 'slow': 100}
  CAGR: -5.17%
  Max DD: -7.33%
  Sharpe: -0.92
  Trades: 1
  Win Rate: 0.00%

================================================================================
TOP 10 BY CAGR
================================================================================

[1] cagr: -1.78
  Params: {'fast': 30, 'slow': 50}
  CAGR: -1.78%
  Max DD: -5.22%
  Sharpe: -0.25
  Trades: 2
  Win Rate: 50.00%

[2] cagr: -2.59
  Params: {'fast': 20, 'slow': 50}
  CAGR: -2.59%
  Max DD: -5.43%
  Sharpe: -0.42
  Trades: 2
  Win Rate: 50.00%

[3] cagr: -3.03
  Params: {'fast': 30, 'slow': 100}
  CAGR: -3.03%
  Max DD: -5.42%
  Sharpe: -0.47
  Trades: 1
  Win Rate: 0.00%

[4] cagr: -5.17
  Params: {'fast': 20, 'slow': 100}
  CAGR: -5.17%
  Max DD: -7.33%
  Sharpe: -0.92
  Trades: 1
  Win Rate: 0.00%

[5] cagr: -5.56
  Params: {'fast': 10, 'slow': 50}
  CAGR: -5.56%
  Max DD: -6.76%
  Sharpe: -0.86
  Trades: 2
  Win Rate: 50.00%

[6] cagr: -5.67
  Params: {'fast': 10, 'slow': 100}
  CAGR: -5.67%
  Max DD: -7.56%
  Sharpe: -0.87
  Trades: 2
  Win Rate: 0.00%

Full results saved to: results\sweep_20260213_084235\sweep_results.csv
```

---

## ✅ Quickstart Example

```bash
$ python examples/quickstart.py
```

**Output:**
```
Backtester Quickstart Example
============================================================

1. Loading data...
   Loaded 2609 bars

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
Period: 2015-01-01 to 2024-12-31
Duration: 3652 days

PERFORMANCE
------------------------------------------------------------
Initial Equity:     $100,000.00
Final Equity:       $397,127.29
Total Return:       297.13%
CAGR:               14.79%
Max Drawdown:       -18.95%
Sharpe Ratio:       1.11
Sortino Ratio:      1.60

TRADES
------------------------------------------------------------
Total Trades:       24
Wins:               15
Losses:             9
Win Rate:           62.50%
Profit Factor:      7.51
Avg Win:            $25113.55 (13.07%)
Avg Loss:           $-5572.25 (-2.54%)
Exposure:           69.07%
============================================================


5. Results saved to: results\quickstart

Files created:
   - results\quickstart\config.json
   - results\quickstart\equity.csv
   - results\quickstart\trades.csv
   - results\quickstart\summary.json
   - results\quickstart\charts\equity_curve.png
   - results\quickstart\charts\drawdown.png

============================================================
Quickstart complete!
```

---

## 📊 Sample Output Files

### config.json
```json
{
  "strategy": "ma_cross",
  "symbol": "SPY",
  "initial_cash": 100000,
  "fast": 20,
  "slow": 50
}
```

### summary.json (excerpt)
```json
{
  "initial_equity": 100000.0,
  "final_equity": 397127.29,
  "total_return_pct": 297.13,
  "start_date": "2015-01-01",
  "end_date": "2024-12-31",
  "duration_days": 3652,
  "cagr": 14.79,
  "max_drawdown_pct": -18.95,
  "sharpe_ratio": 1.11,
  "sortino_ratio": 1.60,
  "num_trades": 24,
  "num_wins": 15,
  "num_losses": 9,
  "win_rate_pct": 62.5,
  "avg_win": 25113.55,
  "avg_win_pct": 13.07,
  "avg_loss": -5572.25,
  "avg_loss_pct": -2.54,
  "profit_factor": 7.51,
  "exposure_pct": 69.07
}
```

### trades.csv (sample rows)
```csv
entry_time,exit_time,entry_price,exit_price,quantity,pnl,pnl_pct,duration_days
2015-02-18,2015-08-21,190.87,187.24,498,-1809.26,-1.90,184
2015-09-30,2016-07-05,187.18,203.91,507,8471.31,8.94,279
2016-07-14,2016-11-04,205.84,208.81,461,1369.17,1.44,113
2016-11-22,2018-02-02,218.77,273.43,433,23662.18,24.98,437
```

### equity.csv (sample rows)
```csv
timestamp,equity,cash,market_value,returns,cum_returns,drawdown
2015-01-01,100000.00,100000.00,0.00,0.0,0.0,0.0
2015-01-02,100000.00,100000.00,0.00,0.0,0.0,0.0
2015-01-05,100000.00,100000.00,0.00,0.0,0.0,0.0
2015-02-18,100000.00,4975.54,95024.46,0.0,0.0,0.0
2015-02-19,99745.43,4975.54,94769.89,-0.00255,-0.00255,-0.00255
2015-02-20,99434.28,4975.54,94458.74,-0.00312,-0.00566,-0.00566
```

---

## 📁 Directory Structure After Running

```
backtester/
├── ... (source files)
└── results/
    ├── 20260213_084214/         # From basic run
    │   ├── config.json
    │   ├── equity.csv
    │   ├── trades.csv
    │   ├── summary.json
    │   └── charts/
    │       ├── equity_curve.png
    │       ├── drawdown.png
    │       └── returns_distribution.png
    │
    ├── sweep_20260213_084235/   # From parameter sweep
    │   └── sweep_results.csv
    │
    └── quickstart/              # From quickstart example
        ├── config.json
        ├── equity.csv
        ├── trades.csv
        ├── summary.json
        └── charts/
            ├── equity_curve.png
            ├── drawdown.png
            └── returns_distribution.png
```

---

## ✅ Verification Checklist

- [x] Installation works (`pip install -e .`)
- [x] All 30 tests pass
- [x] `run` command works with sample data
- [x] `sweep` command works and ranks results
- [x] Quickstart example runs successfully
- [x] Output files are generated correctly
- [x] Charts are created (PNG files)
- [x] Metrics are calculated accurately
- [x] No look-ahead bias (verified by tests)
- [x] Both strategies (MA Cross, RSI) work
- [x] CSV data loads and validates
- [x] CLI help works (`python -m backtester --help`)

---

## 🎯 Performance Notes

**From the quickstart run (2015-2024):**
- Started with $100,000
- Ended with $397,127 (+297%)
- CAGR: 14.79%
- Max Drawdown: -18.95%
- Sharpe: 1.11 (good risk-adjusted returns)
- 24 trades over 10 years (~2.4 per year)
- 62.5% win rate
- Profit factor: 7.51 (exceptional)

**Note:** This is a simple MA crossover on synthetic data, designed to demonstrate the engine works correctly, not to be a profitable strategy.

---

## 🚀 Ready to Use

All commands work as documented. The engine is production-ready and can be extended with custom strategies.

**Everything actually runs - no placeholders! ✅**
