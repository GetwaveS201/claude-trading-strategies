# 🎯 TradingView Backtesting Accuracy Guide

**How to ensure your Pine Script strategies produce 100% accurate, realistic backtest results**

---

## 📋 Table of Contents

1. [Why Accuracy Matters](#why-accuracy-matters)
2. [Common Accuracy Problems](#common-accuracy-problems)
3. [TradingView Settings](#tradingview-settings)
4. [Pine Script Best Practices](#pine-script-best-practices)
5. [Preventing Lookahead Bias](#preventing-lookahead-bias)
6. [Realistic Order Execution](#realistic-order-execution)
7. [Cost Modeling](#cost-modeling)
8. [Validation Checklist](#validation-checklist)
9. [Examples](#examples)
10. [Troubleshooting](#troubleshooting)

---

## Why Accuracy Matters

### The Problem

Many backtests look amazing but fail in live trading because:

❌ **Lookahead bias** - Using future data that wouldn't be available
❌ **Repainting** - Signals change after the bar closes
❌ **Unrealistic fills** - Orders execute at impossible prices
❌ **Missing costs** - Ignoring commissions and slippage
❌ **Overfitting** - Strategy optimized to past data

### The Solution

✅ Follow TradingView's built-in safeguards
✅ Use proper Pine Script syntax
✅ Model realistic execution
✅ Include all costs
✅ Validate on out-of-sample data

---

## Common Accuracy Problems

### Problem 1: Repainting Indicators

**BAD - Repaints:**
```pinescript
// security() without lookahead parameter
higher_tf = request.security(syminfo.tickerid, "D", close)

// Indicator recalculates on historical bars
pivot = ta.pivothigh(high, 5, 5)  // Looks into future!
```

**GOOD - Non-Repainting:**
```pinescript
// Explicitly disable lookahead
higher_tf = request.security(syminfo.tickerid, "D", close, lookahead=barmerge.lookahead_off)

// Use confirmed pivots only
pivot = ta.pivothigh(high, 5, 5)[5]  // Offset by right bars
```

### Problem 2: Lookahead Bias

**BAD - Uses Future Data:**
```pinescript
// Calculates on close, but uses high/low from same bar
if close > high[0]  // This is the same bar!
    strategy.entry("Long", strategy.long)
```

**GOOD - Uses Only Past Data:**
```pinescript
// Only use confirmed past bars
if close > high[1]  // Previous bar's high
    strategy.entry("Long", strategy.long)
```

### Problem 3: Unrealistic Fills

**BAD - Fills at Close:**
```pinescript
// Enters at close price (impossible in real trading)
if crossover(fast_ma, slow_ma)
    strategy.entry("Long", strategy.long)
```

**GOOD - Fills at Next Open:**
```pinescript
// TradingView fills market orders at NEXT bar's open
// This is automatic - just don't use limit orders incorrectly
if crossover(fast_ma, slow_ma)
    strategy.entry("Long", strategy.long)  // Fills at next open ✅
```

### Problem 4: Missing Costs

**BAD - No Costs:**
```pinescript
//@version=5
strategy("My Strategy", overlay=true)
// No commission or slippage specified!
```

**GOOD - Includes Costs:**
```pinescript
//@version=5
strategy("My Strategy",
     overlay=true,
     commission_type=strategy.commission.percent,
     commission_value=0.1,        // 0.1% per trade
     slippage=2)                  // 2 ticks slippage
```

---

## TradingView Settings

### Strategy Properties (Essential)

```pinescript
//@version=5
strategy("Accurate Strategy",
     overlay=true,

     // Order Execution
     calc_on_order_fills=false,          // Don't recalc on fills
     calc_on_every_tick=false,           // Only on bar close

     // Initial Capital
     initial_capital=100000,             // Starting capital
     default_qty_type=strategy.percent_of_equity,
     default_qty_value=100,              // 100% of equity

     // Costs (CRITICAL!)
     commission_type=strategy.commission.percent,
     commission_value=0.1,               // 0.1% commission
     slippage=2,                         // 2 ticks slippage

     // Pyramiding
     pyramiding=0,                       // No pyramiding (safer)

     // Fills
     process_orders_on_close=false,      // Fill at next open

     // Currency
     currency=currency.USD)
```

### Property Settings - Right Click on Chart

**Properties → Trading:**

1. **Backtest Range:**
   - Start: 2000-01-01 (or your start date)
   - End: Current date
   - Use at least 10+ years for reliable results

2. **Verify Trade Execution:**
   - Click: "Strategy Tester" tab (bottom)
   - Click: "List of Trades"
   - Check: Entry/Exit prices are realistic
   - Check: Dates make sense

3. **Performance Summary:**
   - Net Profit: Total P&L
   - Total Trades: Should be reasonable (not thousands)
   - Percent Profitable: 40-60% is realistic
   - Profit Factor: > 1.5 is good
   - Max Drawdown: Should be tolerable

---

## Pine Script Best Practices

### 1. Use Explicit Lookahead Settings

**Always specify lookahead for security():**
```pinescript
// Higher timeframe data
htf_close = request.security(syminfo.tickerid, "D", close,
     lookahead=barmerge.lookahead_off)

// Multiple timeframe analysis
weekly_sma = request.security(syminfo.tickerid, "W", ta.sma(close, 20),
     lookahead=barmerge.lookahead_off)
```

### 2. Avoid Repainting Indicators

**Bad - Repaints:**
```pinescript
// Pivot high recalculates on historical bars
pivot = ta.pivothigh(high, 10, 10)
if not na(pivot)
    strategy.entry("Long", strategy.long)
```

**Good - Confirmed Only:**
```pinescript
// Wait for pivot to be confirmed
pivot = ta.pivothigh(high, 10, 10)[10]  // Offset by right bars
if not na(pivot)
    strategy.entry("Long", strategy.long)
```

### 3. Proper Order Timing

**Market Orders (Recommended):**
```pinescript
// Generates signal on bar close
// Fills at NEXT bar's open (automatic)
if ta.crossover(fast_ma, slow_ma)
    strategy.entry("Long", strategy.long)
```

**Limit Orders (Advanced):**
```pinescript
// Place limit order
limit_price = close * 0.99  // 1% below current price
strategy.entry("Long", strategy.long, limit=limit_price)

// Order stays active until filled or cancelled
// Fills when price reaches limit
```

**Stop Orders:**
```pinescript
// Stop loss at 2% below entry
stop_price = strategy.position_avg_price * 0.98
strategy.exit("Stop", "Long", stop=stop_price)
```

### 4. Non-Repainting Moving Averages

**Always Fine:**
```pinescript
// These never repaint
sma_20 = ta.sma(close, 20)
ema_50 = ta.ema(close, 50)
rsi_14 = ta.rsi(close, 14)
```

**Be Careful:**
```pinescript
// These CAN repaint if used wrong
highest_20 = ta.highest(high, 20)      // OK - uses confirmed data
pivot = ta.pivothigh(high, 5, 5)       // NEEDS OFFSET!
```

### 5. Position Sizing

**Fixed Dollar Amount:**
```pinescript
shares = 10000 / close  // $10,000 position
strategy.entry("Long", strategy.long, qty=shares)
```

**Percent of Equity:**
```pinescript
// Already set in strategy properties
default_qty_type=strategy.percent_of_equity
default_qty_value=100  // Use 100% of equity

// Just enter without qty parameter
strategy.entry("Long", strategy.long)
```

**Risk-Based:**
```pinescript
// Risk 2% of capital per trade
risk_percent = 0.02
account_risk = strategy.equity * risk_percent

// Calculate shares based on stop distance
stop_distance = close - stop_price
shares = account_risk / stop_distance

strategy.entry("Long", strategy.long, qty=shares)
```

---

## Preventing Lookahead Bias

### Rule 1: Only Use Past Data

**Bad:**
```pinescript
// Uses current bar's high (haven't seen it yet!)
if close > high
    strategy.entry("Long", strategy.long)
```

**Good:**
```pinescript
// Uses previous bar's high (known data)
if close > high[1]
    strategy.entry("Long", strategy.long)
```

### Rule 2: Be Careful with [0] Index

```pinescript
// [0] = Current bar (still forming!)
// [1] = Previous bar (confirmed)
// [2] = 2 bars ago (confirmed)

current_close = close[0]   // Still changing!
previous_close = close[1]  // Fixed, safe to use
```

### Rule 3: Indicators Need Time

```pinescript
// SMA needs 20 bars to be valid
sma_20 = ta.sma(close, 20)

// Check if valid before using
if not na(sma_20)
    // Only trade after SMA is ready
    if close > sma_20
        strategy.entry("Long", strategy.long)
```

### Rule 4: Variables Don't Repaint

```pinescript
// Variables store values and don't change
var float entry_price = na

if strategy.position_size == 0 and bullish_signal
    strategy.entry("Long", strategy.long)
    entry_price := close  // Stores entry price

// entry_price won't change on historical bars ✅
```

---

## Realistic Order Execution

### How TradingView Fills Orders

**Market Orders:**
1. Signal generated on bar close (e.g., 4:00 PM)
2. Order submitted
3. Order fills at NEXT bar's open (e.g., next day 9:30 AM)
4. You pay slippage + commission

**Limit Orders:**
1. Order placed with limit price
2. Waits for price to reach limit
3. Fills when limit price is touched
4. May not fill if price doesn't reach limit

**Stop Orders:**
1. Stop price set
2. Triggers when price crosses stop
3. Becomes market order
4. Fills at next available price (with slippage)

### Example: Realistic Execution

```pinescript
//@version=5
strategy("Realistic Execution",
     overlay=true,
     commission_type=strategy.commission.percent,
     commission_value=0.1,
     slippage=2)

sma_fast = ta.sma(close, 20)
sma_slow = ta.sma(close, 50)

// Entry signal on bar close
if ta.crossover(sma_fast, sma_slow)
    // Fills at NEXT bar's open + slippage
    strategy.entry("Long", strategy.long)

// Exit signal on bar close
if ta.crossunder(sma_fast, sma_slow)
    // Fills at NEXT bar's open + slippage
    strategy.close("Long")
```

**What Happens:**
- Signal at 4:00 PM on Day 1
- Order fills at 9:30 AM on Day 2 (next open)
- Price = Day 2 open + 2 ticks slippage
- Cost = 0.1% commission

---

## Cost Modeling

### Commission Types

**Percent of Trade:**
```pinescript
commission_type=strategy.commission.percent,
commission_value=0.1  // 0.1% of trade value
```

**Per Share:**
```pinescript
commission_type=strategy.commission.cash_per_contract,
commission_value=0.005  // $0.005 per share
```

**Per Trade:**
```pinescript
commission_type=strategy.commission.cash_per_order,
commission_value=1.0  // $1.00 per order
```

### Realistic Commission Examples

**Retail Broker:**
```pinescript
commission_type=strategy.commission.cash_per_order,
commission_value=0  // $0 commission (Robinhood, Webull)
slippage=2          // But still have slippage!
```

**Active Trader:**
```pinescript
commission_type=strategy.commission.cash_per_contract,
commission_value=0.005  // $0.005/share
slippage=1              // Better fills
```

**Professional:**
```pinescript
commission_type=strategy.commission.percent,
commission_value=0.02  // 0.02% (2 basis points)
slippage=0.5           // Tight spreads
```

### Slippage

**What is slippage?**
- Difference between expected and actual fill price
- Measured in ticks
- Higher volume = less slippage

**Realistic Slippage:**
```pinescript
// Liquid stocks (SPY, AAPL)
slippage=1  // 1 tick

// Most stocks
slippage=2  // 2 ticks

// Less liquid
slippage=5  // 5 ticks

// Penny stocks
slippage=10  // 10 ticks or more
```

---

## Validation Checklist

### ✅ Before You Trust Your Backtest

**Code Quality:**
- [ ] Using `//@version=5`
- [ ] Commission set (0.1% minimum)
- [ ] Slippage set (2 ticks minimum)
- [ ] No lookahead bias
- [ ] No repainting indicators
- [ ] All security() calls use `lookahead_off`

**Settings:**
- [ ] Backtest period: 10+ years
- [ ] Initial capital: Realistic ($10k-$100k)
- [ ] Position sizing: Makes sense
- [ ] Pyramiding: Off or controlled
- [ ] calc_on_every_tick: FALSE

**Results Validation:**
- [ ] Total trades: 50-500 (not thousands)
- [ ] Win rate: 35-65% (not 90%+)
- [ ] Profit factor: 1.3-3.0 (not 10+)
- [ ] Max drawdown: Tolerable (<40%)
- [ ] Avg trade: Positive but reasonable

**Visual Inspection:**
- [ ] Check trade list for realistic prices
- [ ] Verify equity curve looks smooth
- [ ] No sudden huge jumps in equity
- [ ] Drawdown periods make sense
- [ ] Trade frequency is reasonable

**Out-of-Sample Test:**
- [ ] Test on different time period
- [ ] Test on different ticker (QQQ, IWM)
- [ ] Performance should be similar
- [ ] If it fails, strategy is overfit

---

## Examples

### Example 1: Fully Accurate Strategy

```pinescript
//@version=5
strategy("Accurate SMA Cross",
     overlay=true,
     initial_capital=100000,
     default_qty_type=strategy.percent_of_equity,
     default_qty_value=100,
     commission_type=strategy.commission.percent,
     commission_value=0.1,
     slippage=2,
     calc_on_order_fills=false,
     calc_on_every_tick=false,
     process_orders_on_close=false)

// Non-repainting indicators
sma_fast = ta.sma(close, 20)
sma_slow = ta.sma(close, 50)

// Wait for indicators to be ready
if not na(sma_slow)

    // Entry: Fast crosses above slow
    if ta.crossover(sma_fast, sma_slow)
        strategy.entry("Long", strategy.long)

    // Exit: Fast crosses below slow
    if ta.crossunder(sma_fast, sma_slow)
        strategy.close("Long")

// Plot indicators
plot(sma_fast, "Fast SMA", color=color.blue)
plot(sma_slow, "Slow SMA", color=color.red)
```

**Why This is Accurate:**
✅ All settings properly configured
✅ No lookahead bias
✅ No repainting
✅ Realistic commissions and slippage
✅ Waits for indicators to be ready
✅ Simple, clear logic

### Example 2: With Stops and Targets

```pinescript
//@version=5
strategy("Accurate with Stops",
     overlay=true,
     initial_capital=100000,
     commission_type=strategy.commission.percent,
     commission_value=0.1,
     slippage=2)

// ATR for stops
atr = ta.atr(14)
sma_50 = ta.sma(close, 50)

// Entry
if close > sma_50 and not na(atr)
    strategy.entry("Long", strategy.long)

    // Set stop and target
    stop_price = close - (2 * atr)
    target_price = close + (3 * atr)

    strategy.exit("Exit", "Long",
         stop=stop_price,
         limit=target_price)

plot(sma_50, "SMA 50", color=color.orange)
```

**Why This is Accurate:**
✅ Uses ATR for dynamic stops
✅ Stop/target set when position opens
✅ Stops are realistic (2 ATR)
✅ Risk/reward makes sense (1:1.5)

### Example 3: Position Sizing

```pinescript
//@version=5
strategy("Risk-Based Sizing",
     overlay=true,
     initial_capital=100000,
     commission_type=strategy.commission.percent,
     commission_value=0.1,
     slippage=2)

// Inputs
risk_per_trade = input.float(2.0, "Risk Per Trade %") / 100
atr_mult = input.float(2.0, "ATR Stop Multiple")

// Indicators
atr = ta.atr(14)
sma_50 = ta.sma(close, 50)

// Calculate position size
if close > sma_50 and not na(atr)
    // Risk amount
    risk_amount = strategy.equity * risk_per_trade

    // Stop distance
    stop_distance = atr * atr_mult

    // Shares = Risk / Stop Distance
    shares = risk_amount / stop_distance

    // Enter with calculated size
    strategy.entry("Long", strategy.long, qty=shares)

    // Set stop
    stop_price = close - stop_distance
    strategy.exit("Stop", "Long", stop=stop_price)
```

**Why This is Accurate:**
✅ Risks fixed % per trade (2%)
✅ Position size based on stop distance
✅ Won't risk more than specified
✅ Professional risk management

---

## Troubleshooting

### Problem: Strategy shows 1000+ trades

**Cause:** Trading too frequently, maybe on every bar

**Fix:**
```pinescript
// Add condition to limit trades
var int bars_since_trade = 0
bars_since_trade := bars_since_trade + 1

if bullish_signal and bars_since_trade > 5
    strategy.entry("Long", strategy.long)
    bars_since_trade := 0
```

### Problem: Win rate is 90%+

**Cause:** Likely has lookahead bias or repainting

**Fix:**
- Review all indicators for [0] vs [1]
- Check security() calls for lookahead parameter
- Verify no repainting functions

### Problem: Huge profit factor (>5)

**Cause:** Probably unrealistic - check costs and fills

**Fix:**
- Increase commission to 0.1% minimum
- Increase slippage to 2 ticks minimum
- Check if stops are too tight

### Problem: Strategy fails on different ticker

**Cause:** Overfit to one symbol

**Fix:**
- Test on multiple symbols (SPY, QQQ, IWM)
- Use adaptive parameters (ATR-based stops)
- Don't over-optimize

### Problem: Backtest looks perfect, live trading fails

**Causes:**
- Didn't include costs
- Used repainting indicators
- Optimized parameters to past data
- Market conditions changed

**Prevention:**
- Always include commission and slippage
- Test out-of-sample
- Use simple, robust strategies
- Expect lower returns in live trading

---

## Best Practices Summary

### ✅ DO:

1. **Set Costs:**
   - Commission: 0.1% minimum
   - Slippage: 2 ticks minimum

2. **Use Past Data Only:**
   - close[1] not close[0]
   - Confirm indicators are ready

3. **Disable Lookahead:**
   - All security() calls: `lookahead_off`

4. **Test Out-of-Sample:**
   - Different time periods
   - Different symbols

5. **Keep It Simple:**
   - Simple strategies are more robust
   - Complex doesn't mean better

### ❌ DON'T:

1. **Don't Use Future Data:**
   - No close > high on same bar
   - No peeking ahead

2. **Don't Ignore Costs:**
   - Real trading has costs
   - They add up quickly

3. **Don't Over-Optimize:**
   - Perfect backtest = overfit
   - Simple is better

4. **Don't Trust One Test:**
   - Test multiple periods
   - Test multiple symbols

5. **Don't Use Repainting:**
   - Pivots need offset
   - security() needs lookahead_off

---

## Final Checklist

Before trusting your backtest:

✅ Commission set to 0.1% or higher
✅ Slippage set to 2 ticks or higher
✅ No lookahead bias (all past data)
✅ No repainting indicators
✅ Win rate is 35-65% (not 90%)
✅ Profit factor is 1.3-3.0 (not 10)
✅ Total trades is reasonable (50-500)
✅ Tested on 10+ years of data
✅ Tested out-of-sample (different period)
✅ Tested on different symbol
✅ Equity curve looks smooth
✅ Max drawdown is tolerable (<40%)

---

**If all checkboxes pass, your backtest is likely accurate!** ✅

**Remember:** Even accurate backtests don't guarantee future profits. Always start with paper trading before risking real money.

---

**See our strategies folder for examples of properly coded, non-repainting strategies:**
- `strategies/TREND_MOMENTUM_PRO.pine` - Fully accurate implementation
- All strategies follow these best practices
