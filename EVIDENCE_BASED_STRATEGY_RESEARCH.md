# Evidence-Based Trading Strategy Research & Design

## Executive Summary

Based on the comprehensive evidence review, I'm designing a **Multi-Factor Equity Strategy** that combines the three most robust equity factors with proper risk controls.

**Why This Approach:**
- Uses factors with **century-scale evidence** (not data-mined)
- Addresses known failure modes (momentum crashes, value drawdowns)
- Implements institutional-grade risk management
- Avoids overfitting through strict validation

**Target Strategy:** Diversified multi-factor equity with crash protection and drawdown guardrails

---

## Evidence Review: What Works and Why

### Top 3 Most Robust Return Sources (by evidence strength)

#### 1. **Momentum** (Cross-Sectional & Time-Series)
**Evidence Quality:** ⭐⭐⭐⭐⭐
- Classic equity momentum (Jegadeesh & Titman, 1993)
- Century-scale trend evidence (Hurst et al., 2017)
- Time-series momentum across 58 futures (Moskowitz et al., 2012)

**Known Edges:**
- 3-12 month formation, 1-12 month holding
- Works across asset classes
- Positive skew in trending markets

**Known Failures:**
- Momentum crashes during sharp rebounds
- Crowded factor unwinds
- Poor execution in illiquid names

**Risk Controls:**
- Volatility scaling (cuts exposure when vol spikes)
- Skip most recent month (avoids micro-reversal)
- Crash-state filters (VIX-based)

#### 2. **Value** (Fundamental Anchors)
**Evidence Quality:** ⭐⭐⭐⭐⭐
- Fama-French (1992): Book-to-market cross-sectional returns
- Long-run evidence across decades
- Behavioral explanation: investor extrapolation errors

**Known Edges:**
- Buy "cheap" vs fundamentals
- Strong mean reversion over years
- Works across markets

**Known Failures:**
- Multi-year drawdowns (2007-2020 in growth-led regime)
- "Value traps" (cheap for a reason)
- Structural breaks in accounting

**Risk Controls:**
- Combine with momentum (avoid falling knives)
- Combine with quality (avoid junk)
- Sector/industry neutrality

#### 3. **Quality/Profitability**
**Evidence Quality:** ⭐⭐⭐⭐
- Novy-Marx (2013): Gross profitability
- Fama-French (2015): Added profitability to factor model
- Stabilizes value (avoids "cheap for a reason")

**Known Edges:**
- High profitability/quality firms outperform
- Lower crash risk than pure value
- Complements value and momentum

**Known Failures:**
- Can underperform in "junk rallies"
- Crowding in large-cap quality

**Risk Controls:**
- Use composite quality score (not single metric)
- Combine with value/momentum

---

## Why NOT Other Strategies (For This Implementation)

### ❌ High-Frequency Trading / Market Making
**Why Skip:**
- Requires colocation/low-latency infrastructure
- Winner-take-most dynamics
- Operational/technology risk is central
- Not suitable for retail/small-scale implementation

### ❌ Machine Learning Based
**Why Skip:**
- High overfitting risk ("backtest overfitting probability")
- Requires massive feature sets and careful CV
- Fragile to regime changes
- Complex validation (purging/embargo needed)

### ❌ Statistical Arbitrage (Pairs Trading)
**Why Skip:**
- High capacity constraints
- Crowding risk (2007 quant meltdown)
- Requires tight execution and borrow
- Transaction costs dominate at small scale

### ❌ Options Strategies (For Now)
**Why Defer:**
- Requires options data and greeks
- Execution spreads are material
- Tail risk needs explicit hedging
- Better as overlay once core equity working

---

## Proposed Strategy: "Evidence-Based Multi-Factor Equity"

### Core Design Principles

**1. Use Only Well-Documented Factors**
- Momentum (12-month, skip recent month)
- Value (book-to-market, earnings yield, composite)
- Quality (profitability, avoid junk)

**2. Implement Known Risk Controls**
- Volatility scaling (momentum crash protection)
- Drawdown guardrails (10%/15% rules)
- Sector caps (avoid concentration)
- Turnover budget (control costs)

**3. Strict Validation (Avoid Overfitting)**
- Walk-forward out-of-sample
- Multiple testing correction
- Stress tests (2008, 2020, 2022)
- Realistic transaction costs

**4. Regime Awareness**
- VIX-based crash filter
- Volatility-based exposure scaling
- Combine with SPY trend (200-SMA)

---

## Strategy Specification

### Universe
- **SPY** (simplest implementation)
- Alternative: Top 500 U.S. large/mid-cap liquid equities

### Signals

#### Signal 1: Momentum (40% weight)
```
Formation: 12-month return, skip most recent month
Score: Standardized (z-score) vs historical distribution
Risk Adjustment: Scale by inverse realized volatility
```

**Pine Script Implementation:**
```pinescript
// 12-month momentum, skip recent month
mom_return = (close / close[252] - 1) - (close / close[21] - 1)
mom_zscore = (mom_return - ta.sma(mom_return, 252)) / ta.stdev(mom_return, 252)

// Volatility scaling
realized_vol = ta.stdev(close / close[1] - 1, 20) * math.sqrt(252)
mom_score = mom_zscore / realized_vol
```

#### Signal 2: Value (40% weight)
```
Proxy for SPY: Relative P/E vs historical average
Better: Use sector-neutral value within S&P 500
Score: Standardized vs 5-year history
```

**Pine Script Implementation (Simplified for SPY):**
```pinescript
// Use price-to-SMA ratio as value proxy
// Lower = cheaper = higher value score
price_to_trend = close / ta.sma(close, 252)
value_zscore = -(price_to_trend - ta.sma(price_to_trend, 252*5)) / ta.stdev(price_to_trend, 252*5)
value_score = value_zscore
```

#### Signal 3: Quality/Trend Strength (20% weight)
```
Proxy: Strength of uptrend (smoothness, consistency)
Measure: % of time above moving average
Score: Higher = better quality trend
```

**Pine Script Implementation:**
```pinescript
// Trend quality: % days above 50-SMA in last 6 months
days_above_sma = 0
for i = 0 to 126
    if close[i] > ta.sma(close[i], 50)
        days_above_sma := days_above_sma + 1
quality_score = (days_above_sma / 126 - 0.5) * 2  // Normalize -1 to +1
```

### Composite Score
```
Normal Market:
  Composite = 0.40 * Momentum + 0.40 * Value + 0.20 * Quality

Risk-Off (VIX > 25 OR SPY < 200-SMA):
  Composite = 0.70 * Momentum + 0.20 * Value + 0.10 * Quality
  (Shift to momentum in crashes - momentum has positive skew in trends)
```

---

## Risk Management Framework (6 Layers)

### Layer 1: Crash Filter (Regime Detection)
**3 Filters (ANY triggers risk-off):**

| Filter | Threshold | Action |
|--------|-----------|--------|
| VIX Level | > 25 | Cut leverage 50% |
| Realized Vol | > 20% annual | Cut leverage 50% |
| SPY Trend | < 200-SMA | Cut leverage 50% |

**Evidence:** Risk-managed momentum (Barroso & Santa-Clara, 2015)

### Layer 2: Volatility Scaling
**Dynamic Leverage:**
```
Base Leverage = 2.0x
Target Vol = 12% annual
Current Vol = Realized vol (20-day)

Leverage = min(Base * (Target / Current), 3.0x)

If Risk-Off: Leverage *= 0.5
```

**Evidence:** Volatility targeting improves risk-adjusted returns

### Layer 3: Drawdown Guardrails
**2-Tier Protection:**

| Drawdown | Action | Duration |
|----------|--------|----------|
| 10-15% | Cut all positions to 50% | Until DD < 8% |
| > 15% | Go completely FLAT | 20 trading days |

**Evidence:** Systematic drawdown management prevents blowups

### Layer 4: Transaction Cost Control
**Turnover Budget:**
```
Max Turnover: 200% per year (rebalance monthly = ~16% per month)
If turnover exceeds budget: widen rebalance threshold
Commission: 0.1% per trade
Slippage: 2 bps (using market orders)
```

**Evidence:** Frazzini et al. (2018) - anomalies survive realistic costs

### Layer 5: Position Sizing Discipline
**ATR-Based Stops:**
```
Stop Distance = 2.5 * ATR(20)
Risk per Trade = 1% of equity

Position Size = (Equity * 0.01) / Stop Distance
Max Leverage = 3.0x (capped)
```

### Layer 6: Multiple Testing Correction
**Validation Standards:**
```
Parameter Variations Tested: ~20 combinations
Required t-stat (Bonferroni): > 3.0 (vs normal 1.96)
Out-of-Sample Periods: 4 (pre-2008, 2008-2012, 2013-2019, 2020-2025)
Minimum Sharpe (adjusted): > 0.8 (after selection bias correction)
```

**Evidence:** Harvey et al. (2016) - higher t-stats needed for "factor zoo"

---

## Backtest Design (Robust Validation)

### Data Requirements

**Price Data:**
- SPY daily OHLC (2000-2025, 25 years)
- Survivorship-bias-free (SPY naturally is)
- Adjusted for splits/dividends

**Benchmark Data:**
- Buy & Hold SPY
- Kenneth French factors (for decomposition)

### Walk-Forward Validation

**Training Windows:**
```
Period 1: 2000-2007 (train) → 2008-2012 (test)
Period 2: 2000-2012 (train) → 2013-2019 (test)
Period 3: 2000-2019 (train) → 2020-2025 (test)
Period 4: 2000-2025 (full sample)
```

**Pass Criteria:**
- Positive Sharpe in ALL OOS periods
- Ratio > 1.5x in full sample
- Max DD < 30% in any period
- No single period accounts for >50% of returns

### Stress Tests (Crisis Regimes)

**Required Scenarios:**

| Event | Date | Test |
|-------|------|------|
| Dot-com Crash | 2000-2002 | Value should hold up |
| Financial Crisis | 2008-2009 | Crash filter should trigger |
| Flash Crash | 2010 | Execution/stop logic |
| Taper Tantrum | 2013 | Momentum crash risk |
| COVID Crash | Feb-Mar 2020 | Crash filter + guardrails |
| Ukraine Invasion | Feb 2022 | Regime detection |
| 2022 Bear | Full 2022 | Multi-factor diversification |

**Pass Criteria for Each:**
- Drawdown < 25% during crisis
- Recovery < 12 months
- Risk-off triggered appropriately

### Cost Sensitivity Analysis

**Test Scenarios:**

| Scenario | Commission | Slippage | Expected Impact |
|----------|-----------|----------|-----------------|
| Baseline | 0.10% | 2 bps | Reference |
| Low Cost | 0.05% | 1 bp | +5% CAGR |
| High Cost | 0.20% | 5 bps | -3% CAGR |
| Extreme | 0.30% | 10 bps | -8% CAGR |

**Pass Criteria:**
- Positive returns in all cost scenarios
- Ratio > 1.0x even in "Extreme" scenario

---

## Performance Expectations (Research-Based)

### Realistic Targets (SPY 2000-2025)

**Conservative Estimate:**
```
CAGR: 12-15% (vs SPY ~8%)
Volatility: 15-18% (vs SPY ~15%)
Sharpe: 0.7-1.0
Max Drawdown: 20-25% (vs SPY ~55% in 2008)
Ratio vs B&H: 1.5-2.0x
Win Rate: 55-60%
```

**Optimistic (if validation passes):**
```
CAGR: 15-20%
Sharpe: 1.0-1.3
Max DD: 15-20%
Ratio: 2.0-2.5x
```

**Failure Modes to Watch:**
- Long value drawdown (2015-2020)
- Momentum crash (2009 rebound)
- Regime shift (growth-led 2010s)
- Cost underestimation

---

## Implementation Plan

### Phase 1: Research (Weeks 1-4)

**Week 1: Data & Baseline**
- [ ] Download SPY daily data (2000-2025)
- [ ] Download VIX daily data
- [ ] Calculate baseline Buy & Hold
- [ ] Set up backtesting framework

**Week 2: Signal Construction**
- [ ] Build momentum signal (12-month, skip 1)
- [ ] Build value proxy (price-to-trend)
- [ ] Build quality signal (trend consistency)
- [ ] Validate signals vs literature

**Week 3: Risk Controls**
- [ ] Implement crash filter (VIX/Vol/Trend)
- [ ] Implement volatility scaling
- [ ] Implement drawdown guardrails
- [ ] Test each layer independently

**Week 4: Validation**
- [ ] Walk-forward OOS tests
- [ ] Stress tests (2008, 2020, 2022)
- [ ] Cost sensitivity analysis
- [ ] Multiple testing correction

### Phase 2: Pine Script Implementation (Weeks 5-6)

**Week 5: Core Strategy**
- [ ] Translate signals to Pine Script
- [ ] Implement composite scoring
- [ ] Add crash filter logic
- [ ] Add dynamic leverage

**Week 6: Risk Management**
- [ ] Add drawdown guardrails
- [ ] Add ATR-based stops
- [ ] Add performance table
- [ ] Final validation in TradingView

### Phase 3: Live Testing (Weeks 7-8)

**Week 7: Paper Trading**
- [ ] Run strategy in TradingView alerts
- [ ] Track paper performance vs backtest
- [ ] Monitor slippage/costs
- [ ] Refine execution

**Week 8: Small Capital**
- [ ] Start with 10% of intended capital
- [ ] Monitor live vs paper
- [ ] Verify cost model
- [ ] Scale if validated

---

## Deliverables

### Research Report
- [ ] Evidence review summary
- [ ] Strategy specification
- [ ] Backtest results (all periods)
- [ ] Validation report (OOS, stress tests)
- [ ] Cost sensitivity analysis
- [ ] Risk of overfitting assessment (PBO)

### Code Artifacts
- [ ] Pine Script strategy (`EVIDENCE_BASED_MULTIFACTOR.pine`)
- [ ] Python backtest engine (validation)
- [ ] Parameter sensitivity analyzer
- [ ] Performance dashboard

### Documentation
- [ ] Strategy whitepaper
- [ ] Risk management playbook
- [ ] Execution guidelines
- [ ] Monitoring checklist

---

## Key Differences from Previous Approach

### ❌ What We're NOT Doing:
1. ~~Testing 100 parameter combinations~~ → Use literature-standard parameters
2. ~~Picking best backtest~~ → Validate OOS with strict t-stats
3. ~~Single-signal strategy~~ → Multi-factor diversification
4. ~~Ignoring known failures~~ → Address momentum crashes, value drawdowns
5. ~~Fixed leverage~~ → Dynamic volatility scaling
6. ~~No drawdown protection~~ → Explicit guardrails

### ✅ What We ARE Doing:
1. **Use century-scale evidence** (momentum, value, quality)
2. **Implement known risk controls** (volatility scaling, crash filters)
3. **Strict validation** (walk-forward, stress tests, cost sensitivity)
4. **Multiple testing correction** (higher t-stat hurdles)
5. **Regime awareness** (VIX/Vol/Trend filters)
6. **Realistic costs** (0.1% commission, 2 bps slippage)

---

## Next Steps

**Immediate Actions:**

1. **Download Data** (SPY daily 2000-2025, VIX)
2. **Build Python Validator** (walk-forward framework)
3. **Test Parameter Stability** (12-month mom vs 9-month vs 6-month)
4. **Run Stress Tests** (2008, 2020, 2022)
5. **Implement in Pine Script** (if validation passes)

**Decision Points:**

- **If OOS Sharpe < 0.5 in any period:** Investigate failure mode
- **If Max DD > 30% in stress test:** Strengthen guardrails
- **If costs destroy returns:** Reduce turnover or abandon
- **If multiple testing fails:** Do NOT proceed to live

**Success Criteria for Green Light:**

✅ Positive Sharpe in ALL 4 OOS periods
✅ Ratio > 1.5x in full sample
✅ Max DD < 25% in worst crisis
✅ Returns survive "High Cost" scenario
✅ t-stat > 3.0 after multiple testing correction

**Only proceed to Pine Script if ALL criteria pass.**

---

## References (Evidence Base)

1. **Jegadeesh & Titman (1993)** - "Returns to Buying Winners and Selling Losers"
2. **Fama & French (1992, 2015)** - Size, Value, Profitability factors
3. **Moskowitz et al. (2012)** - "Time Series Momentum"
4. **Asness et al. (2013)** - "Value and Momentum Everywhere"
5. **Barroso & Santa-Clara (2015)** - "Momentum Has Its Moments"
6. **Novy-Marx (2013)** - "The Other Side of Value: Gross Profitability"
7. **Harvey et al. (2016)** - "...and the Cross-Section of Expected Returns" (multiple testing)
8. **Bailey et al. (2014)** - "The Deflated Sharpe Ratio" (selection bias)
9. **Frazzini et al. (2018)** - "Durable Alpha after Costs"
10. **Hurst et al. (2017)** - "A Century of Evidence on Trend-Following"

---

*This is a research-based approach using institutional-grade evidence and validation.*
*NOT trial-and-error. Built on decades of academic research.*
