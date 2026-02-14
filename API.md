# API Reference - Market Regime Detection System

> **Complete API documentation for programmatic usage**

---

## Table of Contents

- [Data Collection](#data-collection)
- [Feature Engineering](#feature-engineering)
- [Models](#models)
- [Evaluation](#evaluation)
- [Analysis](#analysis)
- [Utilities](#utilities)

---

## Data Collection

### `IndianMarketData`

**Module:** `src.data_collection.nse_data`

Fetches market data from NSE/BSE via Yahoo Finance API.

#### Constructor

```python
from src.data_collection.nse_data import IndianMarketData

collector = IndianMarketData(
    start_date: str,     # Format: 'YYYY-MM-DD'
    end_date: str        # Format: 'YYYY-MM-DD'
)
```

**Parameters:**
- `start_date` (str): Start date for data fetch
- `end_date` (str): End date for data fetch

**Returns:** `IndianMarketData` instance

#### Methods

##### `fetch_index_data(index_name: str) -> pd.DataFrame`

Fetch OHLCV data for specified index.

**Parameters:**
- `index_name` (str): Index identifier
  - `'NIFTY50'` → ^NSEI
  - `'SENSEX'` → ^BSESN
  - `'NIFTY_BANK'` → ^NSEBANK
  - `'NIFTY_IT'` → ^CNXIT

**Returns:** `pd.DataFrame` with columns:
```python
['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
```

**Example:**
```python
collector = IndianMarketData('2020-01-01', '2024-12-31')
data = collector.fetch_index_data('NIFTY50')
print(data.head())
```

##### `fetch_multiple_stocks(symbols: List[str]) -> Dict[str, pd.DataFrame]`

Fetch data for multiple stocks.

**Parameters:**
- `symbols` (List[str]): List of NSE stock symbols (e.g., `['RELIANCE.NS', 'TCS.NS']`)

**Returns:** `Dict[str, pd.DataFrame]` - Symbol → DataFrame mapping

**Example:**
```python
stocks_data = collector.fetch_multiple_stocks([
    'RELIANCE.NS',
    'TCS.NS',
    'INFY.NS'
])
```

##### `get_india_vix() -> pd.DataFrame`

Fetch India VIX (volatility index) data.

**Returns:** `pd.DataFrame` with India VIX values

**Example:**
```python
vix_data = collector.get_india_vix()
```

---

## Feature Engineering

### `TechnicalFeatures`

**Module:** `src.features.technical`

Computes 20+ technical indicators for regime detection.

#### Class Methods

##### `compute_regime_features(data: pd.DataFrame, **kwargs) -> pd.DataFrame`

Compute all regime detection features.

**Parameters:**
- `data` (pd.DataFrame): Raw OHLCV data
- `return_windows` (List[int], optional): Return calculation windows. Default: `[1, 5, 21]`
- `volatility_windows` (List[int], optional): Volatility windows. Default: `[21, 63]`
- `momentum_indicators` (bool, optional): Include RSI, MACD, Stochastic. Default: `True`
- `trend_indicators` (bool, optional): Include MA, Bollinger Bands. Default: `True`

**Returns:** `pd.DataFrame` with 20+ feature columns

**Features Computed:**

**Returns:**
- `Return_1d`, `Return_5d`, `Return_21d`

**Volatility:**
- `Volatility_21d`, `Volatility_63d`
- `Parkinson_Vol`, `Garman_Klass_Vol`

**Momentum:**
- `RSI_14`, `MACD`, `MACD_Signal`, `MACD_Hist`
- `Stochastic_K`, `St ochastic_D`

**Trend:**
- `SMA_20`, `SMA_50`, `SMA_200`
- `EMA_12`, `EMA_26`
- `BB_Upper`, `BB_Lower`, `BB_Width`

**Volume:**
- `Volume_Ratio`, `OBV` (On-Balance Volume)

**Example:**
```python
from src.features.technical import TechnicalFeatures

featured_data = TechnicalFeatures.compute_regime_features(
    data,
    return_windows=[1, 5, 21],
    volatility_windows=[21, 63],
    momentum_indicators=True,
    trend_indicators=True
)
```

### `VolatilityFeatures`

**Module:** `src.features.volatility`

Advanced volatility estimators.

##### `compute_parkinson_volatility(data: pd.DataFrame, window: int = 21) -> pd.Series`

Parkinson's high-low volatility estimator.

**Formula:** `σ = √((High - Low)² / (4 × ln(2)))`

**Parameters:**
- `data` (pd.DataFrame): OHLC data
- `window` (int): Rolling window size

**Returns:** `pd.Series` - Parkinson volatility

##### `compute_garman_klass_volatility(data: pd.DataFrame, window: int = 21) -> pd.Series`

Garman-Klass OHLC volatility estimator.

**Parameters:**
- `data` (pd.DataFrame): OHLC data
- `window` (int): Rolling window size

**Returns:** `pd.Series` - Garman-Klass volatility

---

## Models

### `HMMRegimeDetector`

**Module:** `src.models.hmm_model`

Hidden Markov Model for temporal regime detection.

#### Constructor

```python
from src.models.hmm_model import HMMRegimeDetector

model = HMMRegimeDetector(
    n_states: int = 4,
    covariance_type: str = 'full',
    n_iter: int = 100,
    random_state: int = 42
)
```

**Parameters:**
- `n_states` (int): Number of regimes to detect. Default: 4
- `covariance_type` (str): Covariance structure. Options: `'full'`, `'diag'`, `'spherical'`. Default: `'full'`
- `n_iter` (int): Maximum training iterations. Default: 100
- `random_state` (int): Random seed for reproducibility. Default: 42

#### Methods

##### `fit(X: np.ndarray) -> HMMRegimeDetector`

Train the HMM model.

**Parameters:**
- `X` (np.ndarray): Feature matrix, shape `(n_samples, n_features)`

**Returns:** `self` (trained model)

**Example:**
```python
X = featured_data[['Return_1d', 'Volatility_21d', 'RSI_14']].dropna().values
model.fit(X)
```

##### `predict(X: np.ndarray) -> np.ndarray`

Predict regime labels.

**Parameters:**
- `X` (np.ndarray): Feature matrix

**Returns:** `np.ndarray` - Regime labels, shape `(n_samples,)`

**Example:**
```python
regimes = model.predict(X)
```

##### `predict_proba(X: np.ndarray) -> np.ndarray`

Predict regime probabilities.

**Parameters:**
- `X` (np.ndarray): Feature matrix

**Returns:** `np.ndarray` - Probabilities, shape `(n_samples, n_states)`

**Example:**
```python
probabilities = model.predict_proba(X)
```

##### `get_transition_matrix() -> np.ndarray`

Get regime transition probability matrix.

**Returns:** `np.ndarray` - Transition matrix, shape `(n_states, n_states)`

**Example:**
```python
trans_matrix = model.get_transition_matrix()
print(f"Diagonal persistence: {np.diag(trans_matrix)}")
```

#### Attributes

- `model` - Fitted `hmmlearn.GaussianHMM` instance
- `transmat_` - Transition matrix
- `means_` - Regime mean feature values
- `covars_` - Regime covariance matrices

---

### `GMMRegimeDetector`

**Module:** `src.models.gmm_model`

Gaussian Mixture Model for clustering-based regime detection.

#### Constructor

```python
from src.models.gmm_model import GMMRegimeDetector

model = GMMRegimeDetector(
    n_components: int = 4,
    covariance_type: str = 'full',
    n_init: int = 10,
    random_state: int = 42
)
```

**Parameters:**
- `n_components` (int): Number of regimes. Default: 4
- `covariance_type` (str): Covariance type. Options: `'full'`, `'tied'`, `'diag'`, `'spherical'`. Default: `'full'`
- `n_init` (int): Number of initializations. Default: 10
- `random_state` (int): Random seed. Default: 42

#### Methods

##### `fit(X: np.ndarray) -> GMMRegimeDetector`

Train the GMM model.

**Parameters:**
- `X` (np.ndarray): Feature matrix

**Returns:** `self`

##### `predict(X: np.ndarray) -> np.ndarray`

Assign regime labels.

**Parameters:**
- `X` (np.ndarray): Feature matrix

**Returns:** `np.ndarray` - Regime labels

##### `find_optimal_components(X: np.ndarray, max_components: int = 10) -> Tuple`

Find optimal number of components using AIC/BIC.

**Parameters:**
- `X` (np.ndarray): Feature matrix
- `max_components` (int): Maximum components to test. Default: 10

**Returns:** `Tuple[int, List[float], List[float]]`
- Best number of components
- AIC scores list
- BIC scores list

**Example:**
```python
best_n, aic_scores, bic_scores = model.find_optimal_components(X, max_components=8)
print(f"Optimal components: {best_n}")
```

---

## Evaluation

### `RegimeEvaluator`

**Module:** `src.evaluation.regime_evaluation`

Comprehensive evaluation for regime detection models.

#### Constructor

```python
from src.evaluation.regime_evaluation import RegimeEvaluator

evaluator = RegimeEvaluator(
    model,              # Fitted HMM or GMM model
    data: pd.DataFrame, # Data with 'Close' and 'returns' columns
    regimes: np.ndarray # Predicted regime labels
)
```

**Parameters:**
- `model` - Trained model instance
- `data` (pd.DataFrame): Must contain columns `['Close', 'returns']`
- `regimes` (np.ndarray): Regime predictions

#### Methods

##### `evaluate_transition_stability() -> Dict`

Evaluate regime persistence and transitions.

**Returns:** `Dict` with keys:
- `transition_matrix` (np.ndarray): Transition probabilities
- `diagonal_persistence` (np.ndarray): Diagonal values
- `avg_persistence` (float): Average diagonal
- `persistence_quality` (str): "Good" or "Needs Improvement"
- `empirical_transitions` (np.ndarray): Empirical transition matrix

**Example:**
```python
trans_analysis = evaluator.evaluate_transition_stability()
print(f"Persistence: {trans_analysis['avg_persistence']:.3f}")
```

##### `compute_information_criteria() -> Dict`

Calculate AIC/BIC for model selection.

**Returns:** `Dict` with keys:
- `log_likelihood` (float)
- `aic` (float)
- `bic` (float)

**Example:**
```python
ic = evaluator.compute_information_criteria()
print(f"AIC: {ic['aic']:.1f}, BIC: {ic['bic']:.1f}")
```

##### `backtest_strategy(long_regimes: List[int], hedge_regimes: List[int], risk_free_rate: float) -> Dict`

Backtest trading strategy.

**Parameters:**
- `long_regimes` (List[int]): Regime IDs for long positions. Default: `[0, 1]`
- `hedge_regimes` (List[int]): Regime IDs for cash/hedge. Default: `[2, 3]`
- `risk_free_rate` (float): Annual risk-free rate. Default: `0.065` (6.5%)

**Returns:** `Dict` with keys:
- `sharpe_ratio` (float): Risk-adjusted returns
- `calmar_ratio` (float): Return / Max Drawdown
- `max_drawdown` (float): Worst decline
- `total_return` (float): Total strategy return
- `annualized_return` (float): Annualized return
- `buy_hold_sharpe` (float): Baseline Sharpe
- `strategy_beats_bh` (bool): True if strategy > buy & hold
- `cumulative_returns` (np.ndarray): Cumulative return series
- `buy_hold_cumulative` (np.ndarray): Buy & hold cumulative returns
- `quality_score` (str): "Excellent", "Good", "Fair", or "Poor"

**Example:**
```python
backtest = evaluator.backtest_strategy(
    long_regimes=[0, 1],
    hedge_regimes=[2, 3],
    risk_free_rate=0.065
)

print(f"Sharpe: {backtest['sharpe_ratio']:.2f}")
print(f"Max DD: {backtest['max_drawdown']:.1%}")
print(f"Quality: {backtest['quality_score']}")
```

##### `regime_characteristics_quality() -> Dict`

Validate regime distinctness using silhouette score.

**Returns:** `Dict` with keys:
- `silhouette_score` (float): -1 to 1, higher is better
- `quality` (str): "Good" or "Needs Improvement"
- `regime_stats` (Dict): Per-regime statistics

**Example:**
```python
quality = evaluator.regime_characteristics_quality()
print(f"Silhouette: {quality['silhouette_score']:.3f}")
```

##### `generate_evaluation_report() -> Dict`

Generate comprehensive evaluation report.

**Returns:** `Dict` with all metrics combined:
```python
{
    'transition_analysis': {...},
    'information_criteria': {...},
    'backtest_results': {...},
    'regime_quality': {...}
}
```

**Example:**
```python
report = evaluator.generate_evaluation_report()

# Access specific metrics
sharpe = report['backtest_results']['sharpe_ratio']
persistence = report['transition_analysis']['avg_persistence']
aic = report['information_criteria']['aic']
```

### `compare_models`

**Function:** `src.evaluation.regime_evaluation.compare_models`

Compare multiple models side-by-side.

**Signature:**
```python
from src.evaluation.regime_evaluation import compare_models

comparison_df = compare_models(
    models_dict: Dict[str, Any],      # {"Model Name": model_object}
    data: pd.DataFrame,                # Evaluation data
    regimes_dict: Dict[str, np.ndarray] # {"Model Name": regime_predictions}
) -> pd.DataFrame
```

**Returns:** `pd.DataFrame` with columns:
- `Model` (str)
- `AIC` (float)
- `BIC` (float)
- `Sharpe` (float)
- `Calmar` (float)
- `Max Drawdown` (float)
- `Silhouette` (float)
- `Quality` (str)

**Example:**
```python
models = {
    'HMM_3': hmm_3_states,
    'HMM_4': hmm_4_states,
    'GMM_4': gmm_4_components
}

regimes = {
    'HMM_3': hmm_3_regimes,
    'HMM_4': hmm_4_regimes,
    'GMM_4': gmm_4_regimes
}

comparison = compare_models(models, data, regimes)
print(comparison.sort_values('Sharpe', ascending=False))
```

---

## Analysis

### `RegimeAnalyzer`

**Module:** `src.analysis.regime_analyzer`

Analyze regime characteristics and transitions.

*(Documentation to be added)*

---

## Utilities

### Data Utilities

**Module:** `src.utils.data_utils`

*(Documentation to be added)*

### Plot Utilities

**Module:** `src.utils.plot_utils`

*(Documentation to be added)*

---

## Complete Example

```python
# Full workflow using API
import pandas as pd
import numpy as np
from src.data_collection.nse_data import IndianMarketData
from src.features.technical import TechnicalFeatures
from src.models.hmm_model import HMMRegimeDetector
from src.evaluation.regime_evaluation import RegimeEvaluator

# 1. Data Collection
collector = IndianMarketData('2020-01-01', '2024-12-31')
data = collector.fetch_index_data('NIFTY50')

# 2. Feature Engineering
features = TechnicalFeatures.compute_regime_features(data)

# 3. Prepare training data
feature_cols = ['Return_1d', 'Volatility_21d', 'RSI_14', 'MACD']
X = features[feature_cols].dropna().values

# 4. Train model
model = HMMRegimeDetector(n_states=4)
model.fit(X)
regimes = model.predict(X)

# 5. Evaluation
eval_data = features[['Close']].copy()
eval_data['returns'] = features['Return_1d']

evaluator = RegimeEvaluator(model, eval_data.dropna(), regimes)
report = evaluator.generate_evaluation_report()

# 6. Results
print(f"Sharpe Ratio: {report['backtest_results']['sharpe_ratio']:.2f}")
print(f"Calmar Ratio: {report['backtest_results']['calmar_ratio']:.2f}")
print(f"Persistence: {report['transition_analysis']['avg_persistence']:.3f}")
print(f"Quality: {report['backtest_results']['quality_score']}")

# 7. Export
output = features.copy()
output['Regime'] = regimes
output.to_csv('regime_analysis.csv')
```

---

## Error Handling

All API functions raise appropriate exceptions:

- `ValueError` - Invalid parameters
- `KeyError` - Missing data columns
- `RuntimeError` - Model fitting failure
- `ConnectionError` - Data fetch failure

**Example:**
```python
try:
    data = collector.fetch_index_data('INVALID_INDEX')
except ValueError as e:
    print(f"Invalid index: {e}")
except ConnectionError as e:
    print(f"Network error: {e}")
```

---

## Type Hints

All functions include type hints for better IDE support:

```python
def backtest_strategy(
    self,
    long_regimes: List[int] = [0, 1],
    hedge_regimes: List[int] = [2, 3],
    risk_free_rate: float = 0.065
) -> Dict[str, Any]:
    ...
```

---

## Version Compatibility

- **Python:** 3.9+
- **NumPy:** >=1.24.0
- **Pandas:** >=2.0.0
- **scikit-learn:** >=1.3.0
- **hmmlearn:** >=0.3.0

---

**Last Updated:** February 14, 2026  
**API Version:** 1.0.0
