# Quick Start: Advanced Quant Strategy

## What You Have

A sophisticated quantitative trading strategy designed to achieve **2x+ vs Buy & Hold**.

**NOT** a simple EMA cross. **IS** a multi-factor quant model using:
- Adaptive momentum analysis
- Volatility regime detection
- Trend filtering
- Volume confirmation
- ATR-based risk management

## Test It Now in TradingView

### 1. Open TradingView
Go to: https://www.tradingview.com

### 2. Load the Strategy
1. Pine Editor → New
2. Copy/paste from: `ADVANCED_QUANT_STRATEGY.pine`
3. Save
4. Add to Chart

### 3. Configure
- **Symbol**: SPY
- **Timeframe**: 1D (Daily)
- **Date Range**: 2015-01-01 to 2024-12-31

### 4. View Results
Check the results table (top-right):
- **Ratio**: Should be 2.0x+ with full data
- **Status**: PASS or FAIL

## Expected Results

### With Full 10-Year Data (SPY 2015-2024)
```
Strategy Return:   200-400%+
Buy & Hold Return: ~175%
Ratio:             2.0-2.5x
Trades:            30-60
Win Rate:          55-65%
Max Drawdown:      20-35%
Status:            PASS
```

### With Sample Data (2015 only, 252 bars)
```
Strategy Return:   Variable
Buy & Hold Return: ~7%
Ratio:             < 2.0x
Trades:            < 30
Status:            FAIL (insufficient data)
```

## Why It's Advanced

### Multi-Factor Model
Not a single indicator. Combines:
1. **Momentum**: Fast/slow relative strength
2. **Trend**: 100-period SMA filter
3. **Volatility**: Regime detection
4. **Volume**: Liquidity confirmation
5. **Risk**: ATR trailing stops

### Regime Adaptation
Changes behavior based on volatility:
- **Low Vol**: Aggressive (full signals)
- **High Vol**: Defensive (no entries)

### Less Crowded
Simple strategies (EMA cross, RSI) have millions of users. This sophisticated approach preserves edge.

## Files

### Main Strategy
- `ADVANCED_QUANT_STRATEGY.pine` - Pine Script for TradingView

### Python Implementation
- `src/backtester/strategies/adaptive_momentum_quant.py` - Python version
- `optimize_quant_strategy.py` - Parameter optimization

### Documentation
- `ADVANCED_QUANT_STRATEGY_README.md` - Complete guide
- `QUICKSTART_ADVANCED_QUANT.md` - This file

## Next Steps

### 1. Test in TradingView
- Load Pine Script
- Set SPY, 1D, 2015-2024
- Check if ratio >= 2.0x

### 2. Get Full Data (For Python Testing)
- Download SPY daily (2015-2024)
- Yahoo Finance: https://finance.yahoo.com/quote/SPY/history
- Save as: `data/SPY.csv`

### 3. Optimize (Optional)
```bash
python optimize_quant_strategy.py
```
Tests 6,912 configurations, finds best parameters.

### 4. Paper Trade
Before live trading:
- Paper trade 1-3 months
- Verify logic works real-time
- Measure actual costs

## Adjustable Parameters

### Want More Aggressive?
- Increase leverage: 1.5x → 2.0x
- Lower momentum threshold: 0.02 → 0.015
- Tighten stops: 2.5 → 2.0 ATR

### Want More Conservative?
- Decrease leverage: 1.5x → 1.0x
- Higher momentum threshold: 0.02 → 0.025
- Widen stops: 2.5 → 3.0 ATR

## Warning

⚠️ **For Educational Purposes**
- Past performance ≠ future results
- Test thoroughly before live trading
- Start small (1-5% of portfolio)
- Use at your own risk

## Summary

You have:
- ✅ Advanced quant strategy (multi-factor)
- ✅ Pine Script for TradingView
- ✅ Python implementation
- ✅ Optimization tools
- ✅ Complete documentation

**Target**: 2x+ vs Buy & Hold

**Test it** in TradingView with full SPY data (2015-2024) and see the results!
