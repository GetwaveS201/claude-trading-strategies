# ⚡ QUICK REFERENCE - Adaptive Regime Strategy

## 🚀 How to Run It

```
1. Open TradingView
2. Load chart (SPY, QQQ, or any symbol)
3. Set timeframe to Daily (1D)
4. Pine Editor → Paste code → Save
5. Add to Chart
6. Check performance table (top-right)
```

---

## 🎯 How to Change Symbol/Benchmark

**Change Trading Symbol:**
- Just switch the chart symbol

**Use Different Signal Symbol:**
- Settings → Signal Symbol → Enter symbol (e.g., "QQQ")
- Leave blank to use chart symbol

**Change Benchmark:**
- Settings → Benchmark Symbol → Enter symbol (e.g., "SPY", "QQQ", "IWM")

---

## ⚙️ Top 5 Most Important Inputs

| Input | Default | What It Does | Optimize Range |
|-------|---------|--------------|----------------|
| **ADX Trend Threshold** | 25 | When market is trending | 20-30 |
| **Stop Loss ATR Multiple** | 2.0 | Stop loss distance | 1.5-3.0 |
| **Trend Fast MA** | 20 | Trend detection speed | 10-30 |
| **Risk % Per Trade** | 1.0% | Position size (risk-based) | 0.5-2.0% |
| **Time Stop Bars** | 30 | Exit after N bars | 20-50 |

---

## 🔧 What to Optimize First (No Overfitting)

### Priority 1: Risk Management
```
Test:
- Stop Loss: 1.5, 2.0, 2.5, 3.0 ATR
- Trailing Stop: ON vs OFF
- Time Stop: 20, 30, 40 bars

Goal:
- Max DD < 25%
- Profit Factor > 1.5
```

### Priority 2: Regime Thresholds
```
Test:
- ADX Trend: 20, 25, 30
- ADX Range: 15, 20, 25
- Vol Expansion: 1.3, 1.5, 1.7

Goal:
- Stable in-sample AND out-sample
```

### Priority 3: Entry Timing
```
Test:
- Fast MA: 15, 20, 25
- Slow MA: 40, 50, 60
- RSI Oversold: 25, 30, 35

Goal:
- Improve win rate 3-5%
```

---

## 📊 Performance Targets

### ✅ GOOD Performance
```
Strategy Return: > 12% CAGR
Max Drawdown: < 25%
Profit Factor: > 1.5
Win Rate: > 40%
Beats Benchmark: YES ✅
Ratio: > 1.5x
```

### ⚠️ WEAK Performance (Needs Work)
```
Strategy Return: < 8% CAGR
Max Drawdown: > 35%
Profit Factor: < 1.2
Win Rate: < 35%
Beats Benchmark: NO ❌
Ratio: < 1.0x
```

---

## 🛠️ Quick Fixes

### Too Many Trades?
```
↑ ADX Trend Threshold (25 → 30)
↑ Min ATR % (0.5 → 1.0)
```

### Too Few Trades?
```
↓ ADX Trend Threshold (25 → 20)
☐ Disable HTF Filter
```

### Too Many Stop-Outs?
```
↑ Stop Loss ATR (2.0 → 2.5)
☐ Disable Trailing Stop
```

### Drawdowns Too Big?
```
↓ Risk % Per Trade (1.0 → 0.5%)
↑ Stop Loss ATR (2.0 → 1.5)
✓ Enable HTF Filter
```

---

## 🧪 In-Sample / Out-Sample Testing

```
Step 1: Enable Windows
  ✓ Use In-Sample/Out-Sample Windows

Step 2: Set Dates
  In-Sample: 2015-2020
  Out-Sample: 2021-2025

Step 3: Test In-Sample
  Active Window: In-Sample
  Optimize here

Step 4: Validate Out-Sample
  Active Window: Out-Sample
  Same parameters!

Step 5: Full Test
  Active Window: Both
  Final production test
```

---

## 📋 Pre-Live Checklist

- [ ] Backtest on Daily (1D) timeframe
- [ ] Full date range 2015-present
- [ ] Beats benchmark ✅
- [ ] Max DD < 30%
- [ ] In-sample test complete
- [ ] Out-sample test complete
- [ ] Similar performance both periods
- [ ] Tested on 3+ symbols
- [ ] Paper traded 20+ trades
- [ ] Parameters documented
- [ ] Starting with small capital

---

## 🎯 Key Features

✅ Regime-adaptive (TREND/RANGE/BREAKOUT)
✅ 3 entry modes (trend/mean-rev/breakout)
✅ Full risk management (stops, sizing, time)
✅ Non-repainting (lookahead_off)
✅ Benchmark tracking (beats B&H display)
✅ In-sample/out-sample validation
✅ Long/short capable
✅ 13 parameters (not overfit)

---

## 📞 Support

**Files:**
- `ADAPTIVE_REGIME_STRATEGY.pine` - Main strategy
- `ADAPTIVE_STRATEGY_GUIDE.md` - Full guide
- `QUICK_REFERENCE.md` - This file

**Test on:** SPY, QQQ, IWM, AAPL (Daily, 1D)

**Good luck! 🚀**
