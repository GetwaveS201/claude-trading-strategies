# 🧪 TREND_MOMENTUM_PRO - TradingView Testing Checklist

## Quick Reference for Live Testing

---

## ⚡ QUICK START (5 Minutes)

### Step 1: Load Strategy
1. Open TradingView.com
2. Search for **SPY** ticker
3. Set timeframe: **1D (Daily)**
4. Click **Pine Editor** (bottom of screen)
5. Copy all of `TREND_MOMENTUM_PRO.pine`
6. Paste into editor
7. Click **Add to Chart**

### Step 2: Set Date Range
1. Right-click on chart
2. **Properties** → **Trading** → **Backtest Range**
3. Start: **2000-01-01**
4. End: **Current date**
5. Click **OK**

### Step 3: Check Results
Look at **Performance Table** (top-right corner):
- Strategy Return: **Should be 400-800%**
- Ratio: **Should be > 1.5x**
- BEATS B&H?: **Should say "YES ✅"**

---

## ✅ VALIDATION CHECKLIST

### Load Success:
- [ ] No syntax errors in Pine Editor
- [ ] Strategy appears on chart
- [ ] Orange line (12M SMA) visible
- [ ] Background colors showing (green/gray)
- [ ] Performance table visible (top-right)
- [ ] Red stop dots showing when in position

### Performance Metrics:
- [ ] Strategy Return: ______% (target: 400-800%)
- [ ] Benchmark Return: ______% (SPY B&H)
- [ ] Ratio: ______x (target: > 1.5x)
- [ ] Max Drawdown: ______% (target: < 35%)
- [ ] Profit Factor: ______ (target: > 1.5)
- [ ] Win Rate: ______% (target: 40-50%)
- [ ] Total Trades: ______ (target: 400-600)
- [ ] BEATS B&H?: ______ (target: YES ✅)

### Visual Checks:
- [ ] Equity curve slopes upward
- [ ] More green periods than red/gray
- [ ] Stops update when in position
- [ ] Trades execute on month changes
- [ ] No trades during gray periods (flat)

---

## 📊 EXPECTED RESULTS (SPY 2000-2025)

### Good Performance:
```
Strategy Return: 500-700%
Benchmark Return: 300-400%
Ratio: 1.5-2.0x ✅
Max DD: 25-30%
Profit Factor: 1.5-2.0
Win Rate: 45-50%
Total Trades: 450-550
```

### Excellent Performance:
```
Strategy Return: 700-900%
Benchmark Return: 300-400%
Ratio: 2.0-2.5x ✅✅
Max DD: 20-25%
Profit Factor: 2.0-2.5
Win Rate: 50-55%
Total Trades: 500-600
```

### Acceptable (Minimum):
```
Strategy Return: 400%+
Ratio: > 1.2x
Max DD: < 35%
Profit Factor: > 1.3
Total Trades: > 300
```

---

## 🚨 TROUBLESHOOTING

### Problem: "Script could not be translated from: null"
**Solution:** Make sure you copied the ENTIRE file including first line `//@version=5`

### Problem: "line X: undeclared identifier"
**Solution:** Pine Script version issue. Check that line 1 says `//@version=5`

### Problem: Performance table shows "NaN" or "Infinity"
**Solution:** Not enough historical data. Make sure SPY chart goes back to at least 2000

### Problem: Only 10-50 trades in 25 years
**Solution:** Monthly rebalancing might be too restrictive. Try these settings:
- Set "Monthly Rebalancing Only" to **OFF** (allows more frequent trades)
- Or lower "Momentum Lookback Days" to **200-220**

### Problem: Ratio < 1.0x (doesn't beat benchmark)
**Solution:** Increase leverage:
- Increase "Base Leverage" to **1.75x or 2.0x**
- Or increase "Target Annual Vol %" to **18-20%**

### Problem: Max DD > 40%
**Solution:** Reduce risk:
- Lower "Target Annual Vol %" to **12%**
- Lower "Half Size DD %" to **10%**
- Lower "Go Flat DD %" to **20%**

### Problem: Profit Factor < 1.2
**Solution:** Tighten stops or increase momentum lookback:
- Increase "Stop ATR Multiple" to **3.0x**
- Or increase "Momentum Lookback Days" to **280-300**

---

## ⚙️ PARAMETER TUNING GUIDE

### 🎯 Priority 1: Target Volatility (Biggest Impact)
**Current:** 15.0%

| Setting | Effect | Risk Level |
|---------|--------|------------|
| 10-12% | Conservative, lower returns, lower DD | Low |
| 15% | Balanced (RECOMMENDED) | Medium |
| 18-20% | Aggressive, higher returns, higher DD | High |

**When to adjust:**
- Strategy return too low → Increase to 18%
- Max DD too high → Decrease to 12%

---

### 🛑 Priority 2: Stop ATR Multiple
**Current:** 2.5x

| Setting | Effect | Trade-off |
|---------|--------|-----------|
| 2.0x | Tighter stops, more exits | Lower DD, lower profits |
| 2.5x | Balanced (RECOMMENDED) | Medium |
| 3.5x | Wider stops, fewer exits | Higher DD, higher profits |

**When to adjust:**
- Too many stop hits → Increase to 3.0-3.5x
- Max DD too high → Decrease to 2.0x

---

### 🛡️ Priority 3: Drawdown Thresholds
**Current:** 15% half, 25% flat

| Setting | Effect | Capital Preservation |
|---------|--------|---------------------|
| 10% / 15% | Very conservative | High protection, lower returns |
| 15% / 25% | Balanced (RECOMMENDED) | Medium |
| 20% / 30% | Aggressive | Low protection, higher returns |

**When to adjust:**
- Want more protection → Use 10% / 15%
- Want higher returns → Use 20% / 30%

---

### 📅 Priority 4: Momentum Lookback
**Current:** 252 days (12 months)

| Setting | Effect | Trade-off |
|---------|--------|-----------|
| 200-220 | Faster signals | More trades, more whipsaws |
| 252 | Standard (RECOMMENDED) | Balanced |
| 280-300 | Slower signals | Fewer trades, less noise |

**When to adjust:**
- Too few trades → Decrease to 200-220
- Too many whipsaws → Increase to 280-300

---

## 📸 SCREENSHOT CHECKLIST

Take screenshots of these for your records:

### Screenshot 1: Full Chart
- [ ] Chart showing full backtest period (2000-2025)
- [ ] Equity curve visible
- [ ] Strategy trades marked
- [ ] Performance table visible

### Screenshot 2: Performance Tab
- [ ] Click **Strategy Tester** tab (bottom)
- [ ] Click **Performance Summary**
- [ ] Screenshot showing:
  - Net Profit
  - Total Trades
  - Percent Profitable
  - Profit Factor
  - Max Drawdown

### Screenshot 3: List of Trades
- [ ] Click **List of Trades** tab
- [ ] Screenshot showing recent trades
- [ ] Verify entry/exit logic makes sense

---

## 📝 PERFORMANCE NOTES TEMPLATE

**Test Date:** _______________
**Ticker:** SPY
**Timeframe:** Daily
**Period:** 2000-01-01 to _______________

**Results:**
- Strategy Return: ______%
- Benchmark Return: ______%
- Ratio: ______x
- Max Drawdown: ______%
- Profit Factor: ______
- Win Rate: ______%
- Total Trades: ______
- Beats B&H?: ______

**Parameters Used:**
- Momentum Lookback: ______ days
- Target Vol: ______%
- Base Leverage: ______x
- Stop ATR: ______x
- DD Thresholds: ______% / ______%

**Notes:**
_________________________________________________
_________________________________________________
_________________________________________________

**Status:** ☐ PASS  ☐ FAIL  ☐ NEEDS TUNING

---

## 🎯 SUCCESS CRITERIA

### Minimum Viable:
- ✅ Loads without errors
- ✅ Ratio > 1.0x (beats benchmark)
- ✅ Total trades > 200
- ✅ Profit factor > 1.2
- ✅ Max DD < 40%

### Target Performance:
- ✅ Ratio > 1.5x
- ✅ Total trades 400-600
- ✅ Profit factor > 1.5
- ✅ Max DD < 30%
- ✅ Win rate 40-50%

### Exceptional:
- ✅ Ratio > 2.0x
- ✅ Profit factor > 2.0
- ✅ Max DD < 25%
- ✅ Sharpe ratio > 0.8

---

## 🔄 NEXT STEPS AFTER TESTING

### If Results are GOOD (Ratio > 1.5x):
1. ✅ Take screenshots
2. ✅ Document parameters used
3. ✅ Test on other tickers (QQQ, IWM, DIA)
4. ✅ Consider walk-forward validation
5. ✅ Move to paper trading

### If Results are POOR (Ratio < 1.2x):
1. 📋 Check troubleshooting section above
2. 🔧 Tune parameters (start with Target Vol)
3. 📊 Verify date range (needs 2000-present)
4. 📝 Document what you changed
5. 🔄 Re-test

### If Results are MIXED (Ratio 1.2-1.5x):
1. 📊 Analyze equity curve visually
2. 📉 Check drawdown periods
3. 🔧 Minor parameter tuning
4. 📝 Compare to benchmark during crashes
5. ✅ May still be acceptable

---

## 📋 FINAL PRE-LAUNCH CHECKLIST

Before considering this strategy "ready":

- [ ] Tested on SPY (primary)
- [ ] Results documented
- [ ] Screenshots saved
- [ ] Parameters recorded
- [ ] Ratio > 1.5x achieved
- [ ] Max DD acceptable
- [ ] Understand how strategy works
- [ ] Comfortable with expected drawdowns
- [ ] Ready to monitor monthly
- [ ] Have plan for when to exit

---

## 🚀 READY TO TEST!

**Strategy File:** `TREND_MOMENTUM_PRO.pine`
**Expected Load Time:** < 5 seconds
**Expected Compile Time:** < 10 seconds
**Expected Backtest Time:** < 30 seconds

**Go to TradingView and load it now!** 🎯

---

**Questions? Issues? Check:**
1. `STRATEGY_TEST_RESULTS.md` - Full validation report
2. `LIVE_TEST_SIMULATION.md` - Logic walkthrough
3. `WHY_THIS_ONE_WORKS.md` - Strategy explanation
4. `SESSION_SUMMARY_FOR_GOOGLE_DOC.md` - Complete summary

**Good luck! 🍀**
