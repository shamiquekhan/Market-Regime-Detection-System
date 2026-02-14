# Changelog

All notable changes to the Market Regime Detection System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-02-14

### Added

#### Core Functionality
- **Hidden Markov Model (HMM)** implementation for temporal regime detection
- **Gaussian Mixture Model (GMM)** implementation for clustering-based regimes
- **20+ Technical Indicators** including returns, volatility, RSI, MACD, Bollinger Bands
- **Advanced Volatility Estimators** (Parkinson, Garman-Klass)
- **NSE/BSE Data Integration** via Yahoo Finance API
- Support for **NIFTY50, SENSEX, NIFTY Bank, NIFTY IT** indices

#### Evaluation Suite (NEW!)
- **Sharpe Ratio** calculation with risk-free rate adjustment for India (6.5%)
- **Calmar Ratio** (Return / Max Drawdown) computation
- **Transition Matrix Stability** analysis with persistence metrics
- **AIC/BIC Model Selection** criteria for comparing models
- **Backtesting Engine** with strategy simulation
- **Buy & Hold Comparison** baseline
- **Quality Scoring System** (Excellent/Good/Fair/Poor)
- **Comprehensive Evaluation Reports** combining all metrics

#### Dashboard (Streamlit)
- **Swiss Minimalist Design** - Clean, typography-focused UI
- **Interactive Charts** with Plotly:
  - Price chart with regime overlay
  - Regime distribution pie chart
  - Cumulative returns comparison (Strategy vs Buy & Hold)
  - Transition matrix heatmap
- **Real-time Metrics Display**:
  - Current price, volatility, RSI
  - Sharpe ratio, Calmar ratio, Max drawdown
  - Regime persistence
- **Model Evaluation Section** with comprehensive metrics
- **Export Functionality** - Download regime data as CSV
- **Multi-page Architecture** with Regime Analysis page

#### Documentation
- **README.md** - Complete project documentation (400+ lines)
- **EVALUATION_GUIDE.md** - Detailed evaluation metrics guide
- **QUICKSTART.md** - 5-minute setup guide
- **API.md** - Complete API reference
- **CONTRIBUTING.md** - Contribution guidelines
- **CHANGELOG.md** - This file

### Features

#### Data Collection
- Automatic index symbol mapping (NIFTY50 → ^NSEI)
- Historical data fetching with date range selection
- Multi-stock data fetching capability
- India VIX integration
- Data caching for performance

#### Feature Engineering
- Multiple return windows (1d, 5d, 21d)
- Multiple volatility windows (21d, 63d)
- Momentum indicators (RSI, MACD, Stochastic)
- Trend indicators (SMA, EMA, Bollinger Bands)
- Volume analysis (Volume Ratio, OBV)
- Configurable indicator parameters

#### Machine Learning
- Flexible regime count configuration (2-6 regimes)
- Automatic model training and prediction
- Transition probability matrix extraction
- Regime probability estimation
- Model persistence and loading

#### Evaluation
- Sharpe ratio >1.2 = "Excellent - Deployable"
- Sharpe ratio 0.8-1.2 = "Good - Consider Deployment"
- Sharpe ratio 0.5-0.8 = "Fair - Needs Improvement"
- Sharpe ratio <0.5 = "Poor - Rework Model"
- Automatic quality assessment
- Strategy simulation with configurable regime assignments

### Technical

#### Code Quality
- **Modular Architecture** - Clean separation of concerns
- **Type Hints** throughout codebase
- **Google-style Docstrings** for all functions
- **PEP 8 Compliance** with 100-char line length
- **Error Handling** with informative messages

#### Performance
- Efficient feature computation using vectorized operations
- Optimized model training with `n_iter` limits
- Data caching to minimize API calls
- Parallel processing capability (prepared for future)

#### Dependencies
- Python 3.9+ compatible (tested on 3.9, 3.10, 3.11, 3.14)
- streamlit>=1.28.0
- yfinance>=0.2.28
- hmmlearn>=0.3.0
- scikit-learn>=1.3.0
- pandas>=2.0.0
- numpy>=1.24.0
- plotly>=5.16.0

### UI/UX

#### Design System
- **Typography**: Inter font family, 2.75rem headlines
- **Color Palette**: Monochrome (#000000, #FFFFFF, #666666) + Red accent (#FF0000)
- **Layout**: Swiss-style grid system with 2-3rem padding
- **Borders**: Sharp corners (0px radius), 1px solid lines
- **Spacing**: Generous whitespace, 3rem section dividers

#### Interaction
- Sidebar configuration panel
- One-click data loading
- One-click regime detection
- Smooth scrolling to results
- Responsive design (desktop optimized)

### Testing
- Unit tests for data collection module
- Unit tests for feature engineering
- Unit tests for HMM and GMM models
- Unit tests for evaluation metrics
- Fixtures for test data

### Documentation
- Complete README with installation, usage, API reference
- Evaluation guide with metric definitions and thresholds
- Quick start guide for 5-minute setup
- API documentation with examples
- Contributing guidelines
- Code of conduct

---

## [Unreleased]

### Planned for 1.1.0

#### Features
- [ ] Out-of-sample validation UI
- [ ] Walk-forward analysis
- [ ] Event validation (COVID crash, elections)
- [ ] Regime probability smoothing plots
- [ ] Confusion matrix visualization
- [ ] Multi-model comparison table

#### Improvements
- [ ] Real-time NSE API integration (replace yfinance)
- [ ] Improved error handling with user-friendly messages
- [ ] Performance optimization for large datasets
- [ ] Regime switch notifications

#### Documentation
- [ ] Video tutorials
- [ ] Blog post walkthroughs
- [ ] Jupyter notebook examples

### Planned for 2.0.0

#### Major Features
- [ ] LSTM regime detection model
- [ ] Transformer-based models
- [ ] Multi-asset regime detection (stocks + bonds + commodities)
- [ ] Portfolio optimization based on regimes
- [ ] Alert system (email/SMS on regime change)
- [ ] Auto-rebalancing integration

#### Infrastructure
- [ ] Docker containerization
- [ ] Cloud deployment (AWS/Azure)
- [ ] CI/CD pipeline
- [ ] Automated testing
- [ ] Performance benchmarks

### Planned for 3.0.0

#### Live Trading
- [ ] Zerodha API integration
- [ ] Upstox API integration
- [ ] Real-time order execution
- [ ] Position management
- [ ] Risk management system

#### Advanced Features
- [ ] Options strategy recommendations
- [ ] Sector rotation based on regimes
- [ ] Mobile app (React Native)
- [ ] Multi-language support (Hindi)
- [ ] Custom indicator builder

---

## Known Issues

### Version 1.0.0

#### Minor Issues
- Yahoo Finance API occasional rate limiting (wait 60 seconds)
- Streamlit caching may cause stale data (use Ctrl+F5 to refresh)
- Large datasets (>10 years) may slow down dashboard

#### Workarounds
- **Rate limiting**: Add delays between data fetches
- **Stale data**: Clear Streamlit cache or reload page
- **Performance**: Use smaller date ranges or enable caching

---

## Deprecations

None in version 1.0.0

---

## Security

### Version 1.0.0
- No known security vulnerabilities
- Dependencies regularly updated
- No sensitive data storage

---

## Migration Guide

### Upgrading from Pre-1.0 to 1.0.0

If you were using development versions:

1. **Update requirements**:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

2. **Update imports** (if using as library):
   ```python
   # Old
   from src.evaluation.evaluator import evaluate_model
   
   # New
   from src.evaluation.regime_evaluation import RegimeEvaluator
   ```

3. **Update configuration** (if using custom configs):
   - Rename `n_components` to `n_states` for HMM
   - Update `risk_free_rate` to 0.065 for India

4. **Regenerate outputs**:
   - Retrain models with new evaluation suite
   - Re-export CSV files with updated regime labels

---

## Credits

### Version 1.0.0 Contributors

- **tubakhxn** - Project creator, lead developer
- **Community** - Feature requests, bug reports, testing

### Libraries & Tools

- Streamlit team for amazing dashboard framework
- hmmlearn developers for HMM implementation
- scikit-learn contributors for ML utilities
- Yahoo Finance for market data access
- Plotly for interactive visualizations

---

## Links

- **Repository**: https://github.com/yourusername/Market-Regime-Detection-System
- **Documentation**: [README.md](README.md)
- **Issues**: https://github.com/yourusername/Market-Regime-Detection-System/issues
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

---

**Last Updated**: February 14, 2026  
**Current Version**: 1.0.0  
**Status**: Production-Ready
