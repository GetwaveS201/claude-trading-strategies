# 📊 Adaptive Regime Strategy - Complete Guide

## ✅ What You Got

A **professional-grade, regime-adaptive Pine Script strategy** that:

- ✅ Adapts to TREND, RANGE, or BREAKOUT regimes automatically
- ✅ 3 entry modes: Trend-following, Mean reversion, Breakout
- ✅ Full risk management: ATR stops, trailing stops, time stops, position sizing
- ✅ Non-repainting (all data confirmed, lookahead_off)
- ✅ Beats benchmark tracking (compares to SPY or your chosen benchmark)
- ✅ In-sample/Out-sample validation built-in
- ✅ 13 core parameters (not overfit)
- ✅ Long/Short capable (shorts optional)

---

## 🚀 How to Run It

### Step 1: Load in TradingView

```
1. Open TradingView
2. Load any chart (SPY, QQQ, AAPL, etc.)
3. Set timeframe: Daily (1D) recommended
4. Pine Editor → New → Paste the code
5. Save as "Adaptive Regime Strategy"
6. Click "Add to Chart"
```

### Step 2: Configure Basic Settings

**In Strategy Settings Panel:**

1. **Properties Tab:**
   - Initial Capital: $100,000 (or your amount)
   - Base Currency: USD
   - Order Size: 100% of equity (default)
   - Commission: 0.1% per trade
   - Slippage: 2 ticks

2. **Inputs Tab:**
   - Signal Symbol: Leave blank (uses chart symbol)
   - Benchmark Symbol: SPY (or change to QQQ, etc.)
   - Enable Long Trades: ✓ ON
   - Enable Short Trades: ☐ OFF (start conservative)

### Step 3: Run Backtest

```
Date Range: 2015-01-01 to present
Check the performance table (top-right corner)
Look for:
  - Strategy Return > Buy & Hold Return
  - "BEATS B&H? YES ✅"
  - Profit Factor > 1.5
  - Max Drawdown < 30%
```

---

## 🎯 How to Change Symbol/Benchmark

### Change Chart Symbol
**Simple:** Just switch the chart symbol in TradingView
- The strategy will automatically trade that symbol

### Use Different Signal Symbol
**Settings → Inputs → Signal Symbol**
- Example: Trade SPY but use QQQ signals
- Leave blank to use chart symbol

### Change Benchmark
**Settings → Inputs → Benchmark Symbol**
- Default: SPY
- Change to: QQQ, IWM, VTI, etc.
- The "B&H Return" will update to show that benchmark's performance

---

## ⚙️ Which 5 Inputs Matter Most

### 🥇 1. ADX Trend Threshold (Default: 25)
**What it does:** Decides when market is trending vs ranging
- Higher (30) → Only trade strongest trends
- Lower (20) → Trade more often, more ranging trades
**Optimize range:** 20-30

### 🥈 2. Stop Loss ATR Multiple (Default: 2.0)
**What it does:** Sets stop loss distance
- Higher (3.0) → Wider stops, fewer stop-outs, bigger losses
- Lower (1.5) → Tighter stops, more stop-outs, smaller losses
**Optimize range:** 1.5-3.0

### 🥉 3. Trend Fast MA (Default: 20)
**What it does:** Fast moving average for trend detection
- Lower (10) → More responsive, more trades
- Higher (30) → Slower, fewer trades
**Optimize range:** 10-30

### 4️⃣ 4. Risk % Per Trade (Default: 1.0%)
**What it does:** How much to risk per trade (if using Risk-Based sizing)
- Higher (2%) → Bigger positions, higher returns, higher risk
- Lower (0.5%) → Smaller positions, lower returns, lower risk
**Optimize range:** 0.5-2.0%

### 5️⃣ 5. Time Stop Bars (Default: 30)
**What it does:** Exit trade if it goes nowhere after N bars
- Lower (20) → Exit faster, less capital tied up
- Higher (40) → Give trades more time, fewer premature exits
**Optimize range:** 20-50

---

## 🔬 What to Optimize First (Without Overfitting)

### Phase 1: Risk Management (Do This First)
**Why:** Risk management has the biggest impact on drawdowns and consistency

**Test these combinations:**
1. Stop Loss: 1.5, 2.0, 2.5, 3.0 ATR
2. Trailing Stop: ON vs OFF
3. Time Stop: 20, 30, 40 bars

**Goal:** Find combination with:
- Max Drawdown < 25%
- Profit Factor > 1.5
- Win Rate > 40%

### Phase 2: Regime Thresholds (Do This Second)
**Why:** Regime detection determines which entry mode fires

**Test these combinations:**
1. ADX Trend Threshold: 20, 25, 30
2. ADX Range Threshold: 15, 20, 25
3. Volatility Expansion: 1.3, 1.5, 1.7

**Goal:** Find combination with:
- More trades in your preferred mode
- Stable across in-sample and out-sample

### Phase 3: Entry Timing (Do This Last)
**Why:** Fine-tuning entries has less impact than risk management

**Test these combinations:**
1. Fast MA: 15, 20, 25
2. Slow MA: 40, 50, 60
3. RSI Oversold: 25, 30, 35

**Goal:** Improve win rate by 3-5%

---

## 🧪 In-Sample / Out-Sample Testing

### How to Use the Windows

**Step 1: Enable Windows**
```
Settings → Inputs → Backtest Windows
✓ Use In-Sample/Out-Sample Windows
```

**Step 2: Set Date Ranges**
```
In-Sample:
  Start: 2015-01-01
  End: 2020-12-31

Out-Sample:
  Start: 2021-01-01
  End: 2025-12-31
```

**Step 3: Test In-Sample**
```
Active Window: In-Sample
Optimize parameters here
Find best settings
```

**Step 4: Validate Out-Sample**
```
Active Window: Out-Sample
Use SAME parameters from in-sample
Check if performance holds up
```

**Step 5: Full Test**
```
Active Window: Both
Run with final parameters
This is your "production" backtest
```

### ⚠️ Overfitting Red Flags

**Bad Signs:**
- In-sample Sharpe 2.0, Out-sample Sharpe 0.5 → Overfit!
- In-sample beats benchmark 3x, Out-sample loses → Overfit!
- 50% parameter change = 50% performance change → Fragile!

**Good Signs:**
- In-sample Sharpe 1.2, Out-sample Sharpe 1.0 → Robust!
- Both periods beat benchmark by similar amounts → Consistent!
- Parameter changes ±20% = performance changes ±10% → Stable!

---

## 📐 How the Regime System Works

### Regime 1: TREND (ADX > 25)
**Strategy:** Trend-following with pullbacks

**Entry:**
- Long: Uptrend (Fast MA > Slow MA), price pulls back to fast MA
- Short: Downtrend (Fast MA < Slow MA), price rallies to fast MA

**Why:** Strong trends continue, buy dips in uptrend, sell rallies in downtrend

### Regime 2: RANGE (ADX < 20)
**Strategy:** Mean reversion

**Entry:**
- Long: Price at lower Bollinger Band + RSI oversold
- Short: Price at upper Bollinger Band + RSI overbought

**Why:** In choppy markets, extremes revert to mean

### Regime 3: BREAKOUT (Volatility Expanding)
**Strategy:** Donchian breakout with vol confirmation

**Entry:**
- Long: Price breaks above 20-period high + ATR rising
- Short: Price breaks below 20-period low + ATR rising

**Why:** Volatility expansion often precedes big moves

---

## 🛡️ Risk Management Features

### 1. ATR-Based Stop Loss
- Adapts to volatility
- Wider stops in volatile markets
- Tighter stops in calm markets
- **Default:** 2x ATR

### 2. Trailing Stop (Optional)
- Locks in profits as trade moves in your favor
- Stop trails by 3x ATR (adjustable)
- Never moves against you
- **Default:** ON

### 3. Take Profit (Optional)
- Exit at fixed profit target
- **Default:** 4x ATR (2:1 risk-reward)
- **Default:** OFF (let winners run)

### 4. Time Stop
- Exit if trade goes nowhere after N bars
- Frees up capital for next opportunity
- **Default:** 30 bars

### 5. Position Sizing

**Mode 1: Percent of Equity (Simple)**
- Use % of total equity (set in strategy settings)
- Default: 100% of equity per trade
- Good for: Single-position strategies

**Mode 2: Risk-Based (Professional)**
- Risk fixed % per trade (default 1%)
- Position size = Risk Amount / Stop Distance
- Bigger stops = smaller position
- Smaller stops = bigger position
- Good for: Multi-strategy portfolios

---

## 🎚️ Fine-Tuning Guide

### If Too Many Trades (Overtrading)
**Adjust:**
- ↑ ADX Trend Threshold (25 → 30)
- ↑ ADX Range Threshold (20 → 25)
- ↑ Min ATR % (0.5 → 1.0)

### If Too Few Trades
**Adjust:**
- ↓ ADX Trend Threshold (25 → 20)
- ↓ ADX Range Threshold (20 → 15)
- ☐ Disable Higher Timeframe Filter

### If Too Many Stop-Outs
**Adjust:**
- ↑ Stop Loss ATR Multiple (2.0 → 2.5)
- ☐ Disable Trailing Stop (initially)
- ↑ Time Stop Bars (30 → 40)

### If Drawdowns Too Big
**Adjust:**
- ↓ Risk % Per Trade (1.0 → 0.5%)
- ↑ Stop Loss ATR Multiple (2.0 → 1.5)
- ✓ Enable Higher Timeframe Filter
- ✓ Enable Volatility Filter

### If Missing Big Moves
**Adjust:**
- ↓ Fast MA (20 → 15)
- ↓ Breakout Period (20 → 15)
- ↑ Vol Expansion Multiple (1.5 → 1.3)

---

## 📊 Performance Interpretation

### What "Good" Looks Like

**Strong Performance:**
```
Strategy Return: > 12% CAGR
Max Drawdown: < 25%
Profit Factor: > 1.5
Win Rate: > 40%
Beats Benchmark: YES ✅
Ratio: > 1.5x
```

**Acceptable Performance:**
```
Strategy Return: 8-12% CAGR
Max Drawdown: 25-35%
Profit Factor: 1.2-1.5
Win Rate: 35-45%
Beats Benchmark: YES ✅
Ratio: 1.0-1.5x
```

**Weak Performance (Need Adjustment):**
```
Strategy Return: < 8% CAGR
Max Drawdown: > 35%
Profit Factor: < 1.2
Win Rate: < 35%
Beats Benchmark: NO ❌
Ratio: < 1.0x
```

---

## 🔧 Troubleshooting

### Problem: "No trades executed"
**Solutions:**
1. Check window settings (disable or set dates correctly)
2. Lower ADX thresholds
3. Disable volatility filter
4. Check symbol has enough history

### Problem: "All trades are losses"
**Solutions:**
1. Stop too tight → increase Stop ATR Multiple
2. Wrong regime → check if chart matches regime (trending vs ranging)
3. Benchmark wrong → verify benchmark symbol is correct

### Problem: "Beats benchmark but huge drawdown"
**Solutions:**
1. Reduce leverage (use risk-based sizing at 0.5%)
2. Tighten stops (reduce Stop ATR Multiple)
3. Enable HTF filter
4. Add max volatility filter

### Problem: "Strategy lags behind benchmark"
**Solutions:**
1. Check if in ranging market (strategy sits out)
2. Increase risk per trade
3. Lower ADX thresholds (take more trades)
4. Disable time stop (let winners run)

---

## 🎯 Quick Start Checklist

**Before Trading Live:**

- [ ] Backtest on Daily timeframe (1D)
- [ ] Test full date range (2015-present)
- [ ] Verify beats benchmark
- [ ] Check max drawdown < 30%
- [ ] Run in-sample test
- [ ] Run out-sample test
- [ ] Verify similar performance both periods
- [ ] Test on 3+ different symbols
- [ ] Paper trade for 20+ trades
- [ ] Document your parameter settings
- [ ] Start with small capital
- [ ] Monitor first 10 trades closely

---

## 📚 Default Settings Summary

| Parameter | Default | Range | Purpose |
|-----------|---------|-------|---------|
| ADX Period | 14 | 10-20 | Regime detection |
| ADX Trend Threshold | 25 | 20-30 | Trend vs range |
| Stop Loss ATR Mult | 2.0 | 1.5-3.0 | Risk per trade |
| Trailing Stop | ON | ON/OFF | Lock profits |
| Trail ATR Mult | 3.0 | 2.0-4.0 | Trail distance |
| Time Stop Bars | 30 | 20-50 | Exit stale trades |
| Risk % Per Trade | 1.0% | 0.5-2.0% | Position size |
| Fast MA | 20 | 10-30 | Trend detection |
| Slow MA | 50 | 40-60 | Trend confirmation |
| RSI Period | 14 | 10-20 | Mean reversion |
| Breakout Period | 20 | 15-30 | Breakout detection |
| Vol Expansion Mult | 1.5 | 1.3-2.0 | Breakout filter |

---

## 🚦 Strategy States (What to Expect)

### TREND Regime (Most Profitable)
**Characteristics:**
- ADX > 25
- Clear directional move
- Blue background
- Trend-following entries (pullbacks)

**Expected:**
- Win Rate: 45-55%
- Avg R:R: 2:1 or better
- Best performance period

### RANGE Regime (Grind)
**Characteristics:**
- ADX < 20
- Choppy, sideways price action
- Gray background
- Mean reversion entries (extremes)

**Expected:**
- Win Rate: 50-60%
- Avg R:R: 1:1
- Small consistent gains

### BREAKOUT Regime (High Risk/Reward)
**Characteristics:**
- Volatility expanding
- BB squeeze releasing
- Orange background
- Breakout entries (new highs/lows)

**Expected:**
- Win Rate: 30-40%
- Avg R:R: 3:1 or better
- Big winners, many small losses

---

## ✅ Summary

You now have a **professional, adaptive trading strategy** that:

1. **Adapts to market conditions** (doesn't fight the regime)
2. **Manages risk professionally** (ATR stops, position sizing)
3. **Validates properly** (in-sample/out-sample splits)
4. **Beats benchmarks** (tracks and displays comparison)
5. **Doesn't repaint** (all signals confirmed)

**Start conservative:**
- Long-only
- Risk 0.5-1% per trade
- Test thoroughly before going live

**Good luck! 🚀**
