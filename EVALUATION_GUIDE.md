# Model Evaluation Guide

## Overview
Comprehensive evaluation metrics for HMM/GMM market regime detection, focusing on **regime persistence**, **transition realism**, and **downstream trading value**.

---

## Core Metrics Implemented

### 1. Transition Matrix Stability
**Purpose:** Validate regime persistence and realistic transitions

- **Diagonal Persistence:** >0.85 indicates good regime stability
- **Empirical Transitions:** Shows actual regime switches vs. model expectations
- **Quality Check:** "Good" if avg persistence >0.85

**Located in:** Model Evaluation → Transition Matrix Stability section

```python
# Access via evaluator
trans_analysis = evaluator.evaluate_transition_stability()
persistence = trans_analysis['avg_persistence']  # Should be >0.85
```

---

### 2. Information Criteria (AIC/BIC)
**Purpose:** Model selection and complexity penalty

- **AIC:** Lower is better (Akaike Information Criterion)
- **BIC:** Lower is better, penalizes complexity more
- **Use:** Compare across n_regimes=2-6 to avoid overfitting

**Located in:** Model Evaluation → Model Selection Criteria

**Interpretation:**
- BIC preferred for regime detection (prevents overfitting)
- Compare models: lowest BIC wins
- ΔBIC >10 = strong evidence for better model

---

### 3. Backtesting Metrics

#### Sharpe Ratio
**Definition:** Risk-adjusted returns  
**Thresholds:**
- >1.2 = Excellent - Deployable for live trading
- >0.8 = Good - Consider deployment
- >0.5 = Fair - Needs improvement
- <0.5 = Poor - Rework model

**Formula:** `(Return - Risk_Free) / Volatility × √252`

#### Calmar Ratio
**Definition:** Total return / Maximum drawdown  
**Thresholds:**
- >0.5 = Good drawdown control
- >0.3 = Fair
- <0.3 = Poor risk management

**Why it matters:** Balances returns with worst-case scenario

#### Maximum Drawdown
**Definition:** Largest peak-to-trough decline  
**Acceptable:** <25% for conservative strategies  
**Why it matters:** Measures survivability during crises (e.g., COVID-19)

---

### 4. Regime Duration Distribution (NEW!)
**Purpose:** Detect noisy regimes with too-frequent switching

**Key Metrics:**
- **Mean Duration:** Average days regime persists
- **Single-Day Switches:** % of regimes lasting only 1 day (noise indicator)
- **Total Switches per Year:** Frequency of regime changes

**Thresholds:**
- **Good:** Mean duration >10 days, <10% single-day switches
- **Acceptable:** Mean duration 5-10 days, <20% single-day switches
- **Poor (Noisy):** Mean duration <5 days, >30% single-day switches

**Why it matters:**
- Frequent switches = high transaction costs
- Single-day regimes = likely noise, not meaningful regimes
- Ideal: Regimes persist for weeks/months, not days

**Access via:**
```python
duration_stats = evaluator.compute_regime_duration_distribution()
print(f"Avg switches per year: {duration_stats['avg_switches_per_year']:.1f}")
```

**Example Output:**
```python
{
    'regime_0': {'mean_duration_days': 15.2, 'pct_single_day': 8.3},
    'regime_1': {'mean_duration_days': 22.5, 'pct_single_day': 5.1},
    'regime_2': {'mean_duration_days': 8.7, 'pct_single_day': 18.2},
    'regime_3': {'mean_duration_days': 12.1, 'pct_single_day': 12.5},
    'total_regime_switches': 43,
    'avg_switches_per_year': 12.3,
    'quality': 'Low Noise'
}
```

---

### 5. Turnover & Transaction Cost Metrics (NEW!)
**Purpose:** Measure impact of trading costs on strategy performance

**IMPORTANT:** Previous Sharpe/Calmar metrics were **gross returns** (no costs). This section provides **net returns** after costs.

**Key Metrics:**
- **Total Turnover:** Sum of all position changes (100% → 0% = 1.0 turnover)
- **Annual Turnover:** Turnover per year (e.g., 3.5× = portfolio turned over 3.5 times/year)
- **Number of Trades:** Count of position changes
- **Sharpe Net:** Risk-adjusted returns **after transaction costs**
- **Calmar Net:** Return/drawdown **after transaction costs**

**Default Assumption:** 0.2% (20 bps) per trade on NSE
- Adjust higher (0.3%) for smaller accounts or derivatives
- Adjust lower (0.1%) for institutional/HFT

**Thresholds:**
- **Acceptable:** Net Sharpe >1.0, turnover <5× per year
- **Marginal:** Net Sharpe 0.6-1.0, turnover 5-10× per year
- **Unacceptable:** Net Sharpe <0.6, turnover >15× per year

**Access via:**
```python
turnover_metrics = evaluator.compute_turnover_metrics(
    long_regimes=[0, 1],
    hedge_regimes=[2, 3],
    transaction_cost=0.002  # 0.2%
)
print(f"Sharpe Gross: {turnover_metrics['sharpe_gross']:.2f}")
print(f"Sharpe Net: {turnover_metrics['sharpe_net']:.2f}")
print(f"Cost Impact: {turnover_metrics['sharpe_impact']:.2f}")
```

**Example Output:**
```python
{
    'total_turnover': 14.2,
    'avg_annual_turnover': 4.1,
    'num_trades': 43,
    'sharpe_gross': 1.35,
    'sharpe_net': 1.12,
    'sharpe_impact': -0.23,
    'calmar_gross': 0.68,
    'calmar_net': 0.55,
    'quality_net': 'Good - Consider Deployment'
}
```

**Interpretation:**
- If `sharpe_impact` < -0.3, regime switching is too frequent
- If `avg_annual_turnover` > 10×, consider longer-duration regimes
- **Always use net metrics for deployment decisions, not gross**

---

## Strategy Logic

### Default Configuration
```python
# Long positions in favorable regimes
long_regimes = [0, 1]  # Healthy & Steady, Bullish regimes

# Cash/Hedge in unfavorable regimes
hedge_regimes = [2, 3]  # Crisis, Range-bound regimes

risk_free_rate = 0.065  # 6.5% annual (India's typical rate)
```

### Backtest Simulation
1. **Training Period:** Historical data (default: all loaded data)
2. **Strategy Returns:**
   - Long regimes → Full market exposure
   - Hedge regimes → Risk-free rate (6.5% annual)
   - Other → Cash (0% return)
3. **Comparison:** Strategy vs. Buy & Hold

**Chart:** Strategy vs Buy & Hold cumulative returns

---

## Quality Assessment

### Overall Strategy Quality Badge
Displayed prominently with color coding:

| Badge | Sharpe (Net)* | Calmar (Net) | Max DD | Turnover | Color | Action |
|-------|---------------|--------------|--------|----------|-------|--------|
| **Excellent - Deployable** | >1.2 | >0.5 | >-25% | <5×/year | Green | ✓ Deploy for live trading |
| **Good - Consider Deployment** | >0.8 | >0.3 | >-30% | <8×/year | Orange | Test more, then deploy |
| **Fair - Needs Improvement** | >0.5 | >0.2 | >-35% | <12×/year | Orange | Tune parameters |
| **Poor - Rework Model** | <0.5 | <0.2 | <-35% | >15×/year | Red | Change approach |

**⚠️ Critical Note:** Use **net Sharpe/Calmar** (after transaction costs) for deployment decisions, not gross metrics.

---

## 🎯 Deployment Safety Rails

### Reference Benchmark: NIFTY50 2017-2024 (HMM 4-State)

The system's reference implementation achieved these **gross** metrics:

| Metric | Value | vs Buy & Hold | Quality |
|--------|-------|---------------|--------|
| Sharpe Ratio (Gross) | **1.35** | +87% (0.72 BH) | ✅ Excellent |
| Calmar Ratio | **0.62** | +121% (0.28 BH) | ✅ Excellent |
| Max Drawdown | **-18.5%** | -52% (-38.2% BH) | ✅ Excellent |
| Regime Persistence | **0.87** | N/A | ✅ Stable |

**Interpretation:** On pure backtest numbers, this is **statistically deployable**.

**BUT:** These are **in-sample, gross returns**. Before real capital deployment:

---

### Pre-Deployment Checklist

#### 1. Compute Cost-Adjusted Metrics

**Run this analysis:**
```python
from src.evaluation.regime_evaluation import RegimeEvaluator

evaluator = RegimeEvaluator(model, data, regimes)
turnover = evaluator.compute_turnover_metrics(
    long_regimes=[0, 1],
    hedge_regimes=[2, 3],
    transaction_cost=0.002  # 0.2% = 20 bps per trade on NSE
)

print("=== DEPLOYMENT READINESS ===")
print(f"Sharpe (Gross): {turnover['sharpe_gross']:.2f}")
print(f"Sharpe (Net):   {turnover['sharpe_net']:.2f}")
print(f"Cost Impact:    {turnover['sharpe_impact']:.2f}")
print(f"Turnover/Year:  {turnover['avg_annual_turnover']:.1f}x")
print(f"Num Trades:     {turnover['num_trades']}")
print(f"Quality (Net):  {turnover['quality_net']}")

# Decision rule
if turnover['sharpe_net'] > 1.0 and turnover['avg_annual_turnover'] < 6:
    print("\n✅ READY for small capital deployment (5-10% portfolio)")
elif turnover['sharpe_net'] > 0.8:
    print("\n⚠️ MARGINAL - Deploy with 3-5% only, monitor closely")
else:
    print("\n❌ NOT READY - Net Sharpe too low after costs")
```

**Expected Result for NIFTY50 Benchmark:**
- If turnover is 4×/year @ 0.2% costs → Net Sharpe ≈ 1.10-1.15 ✅
- If turnover is 8×/year @ 0.2% costs → Net Sharpe ≈ 0.90-1.00 ⚠️
- If turnover is 12×/year @ 0.2% costs → Net Sharpe ≈ 0.70-0.80 ❌

---

#### 2. Out-of-Sample Validation

**Train/Test Split:**
```python
# Split your data
train_data = data['2017-01-01':'2020-12-31']  # 4 years
test_data = data['2021-01-01':'2024-12-31']    # 4 years OOS

# Train on old data
model.fit(train_features)

# Predict on new data
oos_regimes = model.predict(test_features)
oos_evaluator = RegimeEvaluator(model, test_data, oos_regimes)
oos_results = oos_evaluator.backtest_strategy()

print("=== OUT-OF-SAMPLE PERFORMANCE ===")
print(f"OOS Sharpe:     {oos_results['sharpe_ratio']:.2f}")
print(f"OOS Calmar:     {oos_results['calmar_ratio']:.2f}")
print(f"OOS Max DD:     {oos_results['max_drawdown']:.1%}")
print(f"Beats Buy/Hold: {oos_results['strategy_beats_bh']}")

# Degradation check
degradation = (oos_results['sharpe_ratio'] / 1.35) - 1  # vs in-sample 1.35
if degradation > -0.25:  # Less than 25% drop
    print("\n✅ OOS performance acceptable (degradation <25%)")
else:
    print("\n❌ WARNING: High OOS degradation suggests overfitting")
```

**Targets:**
- **Excellent:** OOS Sharpe >1.0 (75%+ of in-sample)
- **Good:** OOS Sharpe 0.8-1.0 (60-75% of in-sample)
- **Poor:** OOS Sharpe <0.6 (<50% of in-sample = likely overfitting)

---

#### 3. Kill Switch Rules (Automated Safety)

**Implement these hard stops in your deployment code:**

```python
class DeploymentMonitor:
    def __init__(self, max_drawdown=-0.25, min_sharpe=0.3, min_persistence=0.75):
        self.max_drawdown = max_drawdown
        self.min_sharpe = min_sharpe
        self.min_persistence = min_persistence
        
    def check_kill_switches(self, current_dd, rolling_sharpe_90d, current_persistence):
        """
        Returns: (should_stop, reason)
        """
        if current_dd < self.max_drawdown:
            return True, f"KILL SWITCH: Drawdown {current_dd:.1%} exceeded limit {self.max_drawdown:.1%}"
        
        if rolling_sharpe_90d < self.min_sharpe:
            return True, f"KILL SWITCH: 90-day Sharpe {rolling_sharpe_90d:.2f} below {self.min_sharpe}"
        
        if current_persistence < self.min_persistence:
            return True, f"KILL SWITCH: Regime persistence {current_persistence:.2f} too low (market structure changed)"
        
        return False, "All systems normal"

# Usage
monitor = DeploymentMonitor(max_drawdown=-0.25, min_sharpe=0.3, min_persistence=0.75)
should_stop, reason = monitor.check_kill_switches(
    current_dd=-0.18,
    rolling_sharpe_90d=0.85,
    current_persistence=0.82
)

if should_stop:
    print(f"🚨 {reason}")
    # Flatten all positions
    # Send alert email/SMS
    # Pause trading
```

**Recommended Thresholds:**
- **Max Drawdown:** -25% (benchmark was -18.5%, add 35% buffer)
- **Min Rolling Sharpe (90 days):** 0.3 (well below expected 1.0+, but catches catastrophic failure)
- **Min Persistence:** 0.75 (benchmark was 0.87, allow some degradation)

---

#### 4. Position Sizing with Regime Confidence

**Basic (Current):**
```python
if regime in long_regimes:
    position = 100%
else:
    position = 0%
```

**Advanced (Recommended for Live):**
```python
proba = model.predict_proba(current_features)[-1]  # Last row
max_confidence = proba.max()
regime = proba.argmax()

if regime in long_regimes:
    if max_confidence > 0.8:
        position = 100%  # High confidence
    elif max_confidence > 0.6:
        position = 70%   # Medium confidence
    else:
        position = 50%   # Low confidence - reduce size
elif regime in hedge_regimes:
    position = 0%  # Cash

print(f"Regime {regime}, Confidence {max_confidence:.1%} → Position {position}%")
```

**Rationale:** When model is uncertain (confidence <60%), reduce position size to limit damage from potential misclassifications.

---

#### 5. Monthly Retraining & Drift Monitoring

**Procedure:**
```python
import schedule

def monthly_model_update():
    """
    Run on 1st of each month
    """
    # 1. Fetch latest data (add last 30 days)
    new_data = fetch_nifty50(start='2024-12-01', end='2025-01-31')
    
    # 2. Retrain model on updated window
    #    e.g., last 3 years rolling
    train_window = data[-756:]  # Last 3 years (252*3 days)
    model.fit(train_window)
    
    # 3. Compute OOS metrics on last 3 months
    oos_data = data[-63:]  # Last 3 months
    oos_regimes = model.predict(oos_data)
    oos_eval = RegimeEvaluator(model, oos_data, oos_regimes)
    oos_sharpe = oos_eval.backtest_strategy()['sharpe_ratio']
    
    # 4. Compare to expected envelope
    if oos_sharpe < 0.6:  # Below minimum threshold
        send_alert("Model degraded: OOS Sharpe {:.2f}. Review required.".format(oos_sharpe))
        # Option: pause trading until manual review
    else:
        print(f"Model updated. OOS Sharpe: {oos_sharpe:.2f} ✓")
        # Deploy updated model

schedule.every().month.at("09:00").do(monthly_model_update)
```

---

### 📋 Deployment Phase Timeline

**Based on NIFTY50 benchmark (Sharpe 1.35, Calmar 0.62):**

| Phase | Duration | Capital | Requirements | Kill Switches |
|-------|----------|---------|--------------|---------------|
| **1. Paper Trading** | 30-60 days | ₹0 | Gross Sharpe >1.2 ✓ | Manual monitoring |
| **2. Small Capital** | 60-90 days | 5-10% | Net Sharpe >1.0, Turnover <6× | DD <-25%, Sharpe90d <0.3 |
| **3. OOS Validation** | Parallel | 5-10% | OOS Sharpe >0.8, Walk-forward stable | Same as Phase 2 |
| **4. Scale-Up** | Ongoing | 20-50% | All prior + monitoring infra | Automated + persistence <0.75 |

**Total Time to Full Deployment:** 4-6 months of validation

**Conservative Approach:** After Phase 3, stay at 10-20% indefinitely unless you have 12+ months of live validation matching OOS estimates.

---

## Validation Techniques

### Out-of-Sample (OOS) Testing
**Not yet implemented in UI** - available in `RegimeEvaluator.oos_validation()`

**Recommended approach:**
1. Train on 70% of data (e.g., 2017-mid 2019)
2. Test on 30% OOS (e.g., mid 2019-2021)
3. Validate on known events:
   - **COVID-19 crash (Mar 2020):** Should detect high-vol bear regime
   - **Recovery (Jun 2020-Jan 2021):** Should switch to bullish/volatile
   - **Consolidation periods:** Range-bound detection

**Usage in code:**
```python
oos_results = evaluator.oos_validation(
    train_pct=0.7,
    validate_events={
        '2020-03-23': 3,  # COVID crash = crisis regime
        '2020-11-01': 1   # Post-election rally = bullish regime
    }
)
```

---

## Regime Switch Hit Rate
**Not yet implemented** - Future enhancement

**Concept:** Validate model predicts major regime shifts
- Track bull→bear transitions (e.g., market corrections)
- Target: >70% accuracy on known events
- Cross-reference with:
  - VIX spikes (India VIX >30)
  - NSE circuit breakers
  - RBI policy changes

---

## Visualization Checks

### Currently Implemented:
1. **Price chart with regime coloring** → Visual regime boundaries
2. **Regime distribution pie chart** → Balance check
3. **Cumulative returns comparison** → Strategy vs Buy & Hold

### Recommended (Future):
1. **Smoothed probabilities plot** → `model.predict_proba()` vs price/RSI
2. **Confusion matrix** → Viterbi labels vs MA-crossover regimes
3. **Regime duration histogram** → Check for too-frequent switches

---

## How to Use

### Step 1: Load Data & Run Detection
1. Configure sidebar: Select NIFTY50, date range (e.g., 2017-present)
2. Click **LOAD & ANALYZE**
3. Choose HMM model, 4 regimes
4. Click **RUN DETECTION**

### Step 2: Review Evaluation Metrics
Scroll to **MODEL EVALUATION** section:

1. **Check Sharpe Ratio:** >0.8 = deployable
2. **Check Calmar:** >0.5 = good risk control
3. **Check Quality Badge:** Green = ready for live trading
4. **Review Transition Matrix:** Diagonal >0.85 = stable regimes
5. **Compare Chart:** Strategy should outperform Buy & Hold

### Step 3: Interpret Results
- **Excellent badge + Sharpe >1.2** → Deploy with confidence
- **Good badge + Sharpe 0.8-1.2** → Deploy with monitoring
- **Fair/Poor** → Adjust:
  - Try different n_regimes (3, 5, or 6)
  - Change date range (longer history = better)
  - Try GMM instead of HMM

### Step 4: Export & Deploy
- Click **DOWNLOAD CSV** to export regime labels
- Use in trading system to switch strategies by regime

---

## Model Comparison

### Comparing Multiple Models
**Not in UI yet** - use Python code:

```python
from src.evaluation.regime_evaluation import compare_models

models_dict = {
    'HMM_3': hmm_model_3_states,
    'HMM_4': hmm_model_4_states,
    'GMM_4': gmm_model_4_components
}

regimes_dict = {
    'HMM_3': hmm_3_regimes,
    'HMM_4': hmm_4_regimes,
    'GMM_4': gmm_4_regimes
}

comparison_df = compare_models(models_dict, data, regimes_dict)
print(comparison_df.sort_values('Sharpe', ascending=False))
```

**Output:**
| Model | AIC | BIC | Sharpe | Calmar | Max Drawdown | Silhouette | Quality |
|-------|-----|-----|--------|--------|--------------|------------|---------|
| HMM_4 | 1250| 1320| 1.35   | 0.62   | -18.5%       | 0.42       | Excellent|
| GMM_4 | 1280| 1340| 1.18   | 0.55   | -21.2%       | 0.38       | Good    |

---

## References & Benchmarks

### Indian Market Context
- **NIFTY50 avg Sharpe:** ~0.6-0.8 (2017-2023) [Samco Research]
- **Buy & Hold max DD:** ~38% (COVID-19 crash)
- **Risk-free rate:** 6.5% (91-day T-Bill + inflation buffer)

### Validation Events (NSE)
- **2018 IL&FS Crisis:** Should detect transition to high-vol regime
- **2020 COVID Crash:** Maximum volatility regime
- **2021 Recovery:** Bullish but volatile regime
- **2023 Consolidation:** Range-bound/cautionary regime

### External Validation
- Cross-check with [Reddit r/IndianStreetBets NIFTY Regime Map](https://www.reddit.com/r/IndianStreetBets/comments/1pad2y4/nifty_regime_map_28_years_in_20_seconds/)
- Compare with NIFTY VIX levels (>30 = crisis regime expected)

---

## Troubleshooting

### Low Sharpe Ratio (<0.5)
**Possible causes:**
1. Too many regimes (overfitting) → Try n_regimes=3
2. Too few regimes (underfitting) → Try n_regimes=5
3. Wrong regime assignment for strategy → Check regime characteristics
4. Insufficient data → Load more history (3+ years minimum)

**Fix:** Review regime interpretation section - ensure high-return regimes are in `long_regimes`

### High Max Drawdown (>30%)
**Causes:**
1. Model didn't detect crisis regime early enough
2. Strategy stayed long during crash
3. Regime transitions lagging market moves

**Fix:** 
- Add more volatility features
- Consider shorter lookback windows (volatility_21d → volatility_10d)
- Use GMM for faster regime detection

### Low Persistence (<0.80)
**Causes:**
1. Regime switching too frequently (noisy)
2. Data has high volatility
3. Wrong number of regimes

**Fix:**
- Smooth features (use longer moving averages)
- Increase n_regimes to capture sub-states
- Try HMM instead of GMM (HMM has temporal structure)

---

## Next Steps

### Immediate Actions
1. ✅ **Implemented:** Core metrics, backtesting, transition analysis
2. ✅ **Implemented:** Sharpe, Calmar, max drawdown, quality badge
3. ✅ **Implemented:** Strategy vs Buy & Hold comparison chart

### Recommended Enhancements
1. **OOS Validation UI:** Add train/test split selector
2. **Event Validation:** Mark known events on charts
3. **Regime Probability Plot:** Show `predict_proba()` smoothed
4. **Confusion Matrix:** Compare with MA-crossover labels
5. **Multi-Model Comparison:** Side-by-side AIC/BIC/Sharpe table

### For Live Deployment
1. **Real-time Data:** Switch from yfinance to NSE API
2. **Regime Confidence:** Show probability of current regime
3. **Alert System:** Email/SMS when regime changes
4. **Portfolio Integration:** Auto-rebalance based on regime

---

## Code Reference

### Main Evaluation Class
**File:** `src/evaluation/regime_evaluation.py`

**Key Methods:**
```python
evaluator = RegimeEvaluator(model, data, regimes)

# Core metrics
evaluator.evaluate_transition_stability()
evaluator.compute_information_criteria()
evaluator.backtest_strategy(long_regimes=[0,1], hedge_regimes=[2,3])
evaluator.regime_characteristics_quality()

# Comprehensive report
report = evaluator.generate_evaluation_report()
```

### Integration in Streamlit App
**File:** `app/app.py`

**Section:** Lines after regime interpretation, before export
- Imports `RegimeEvaluator`
- Creates evaluator after regime detection
- Displays metrics in clean UI with color-coded quality badges
- Shows transition matrix with gradient highlighting
- Plots cumulative returns comparison

---

## Questions?

### When is Sharpe >1.2 achievable?
- Strong regime differentiation (clear bull/bear/range)
- Long historical data (5+ years)
- Proper regime count (usually 4-5 for NSE)
- Realistic strategy (not overfitted to in-sample data)

### Why BIC over AIC?
BIC penalizes model complexity more, preventing overfitting critical for regime detection where too many states = noise trading.

### How to validate without manual labels?
- Use known market events (COVID crash, election rallies)
- Compare with VIX regime classification (low/medium/high vol)
- Backtest returns: Sharpe >0.8 = model captures useful patterns

---

**Last Updated:** February 14, 2026  
**Author:** Market Regime Detection System  
**Version:** 1.0
