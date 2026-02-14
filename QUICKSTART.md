# Quick Start Guide - Market Regime Detection System

## Installation & Setup (5 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

This will install all required packages including:
- yfinance (for market data)
- hmmlearn (for HMM models)
- streamlit (for dashboard)
- plotly (for visualizations)
- scikit-learn (for ML utilities)

### Step 2: Run the Application
```bash
streamlit run app/app.py
```

Your browser will automatically open to `http://localhost:8501`

## First Time Usage (10 minutes)

### Example: Analyze NIFTY50 Regimes

1. **Configure Settings** (Left Sidebar):
   - Index: Select "NIFTY50"
   - Start Date: 2021-01-01
   - End Date: Today
   - Model: "Hidden Markov Model (HMM)"
   - Number of Regimes: 4

2. **Load Data**:
   - Click "🔄 Load & Analyze Data"
   - Wait ~10-30 seconds for data download

3. **Run Detection**:
   - Click "🚀 Run Regime Detection"
   - Wait ~5-15 seconds for model training

4. **Analyze Results**:
   - View the price chart with regime overlay
   - Check regime distribution pie chart
   - Review regime characteristics table
   - Identify current market regime

5. **Export Results**:
   - Click "📥 Download Regime Data (CSV)"
   - Save for further analysis

## Understanding the Results

### Regime Characteristics Table
- **Return_1d_mean**: Average daily return in that regime
- **Return_1d_std**: Volatility of returns
- **Volatility_21d**: 21-day realized volatility
- **RSI_14**: Average RSI (momentum indicator)
- **Volume_Ratio**: Volume relative to 20-day average

### Regime Interpretations
- **Green (Healthy)**: Positive returns + Low volatility = Good for long positions
- **Yellow (Volatile)**: Positive returns + High volatility = Caution advised
- **Red (Crisis)**: Negative returns + High volatility = Defensive positioning
- **White (Range-bound)**: Neutral returns = Sideways market

## Advanced Features

### Exploring Different Indices
Try analyzing:
- NIFTY Bank (banking sector)
- NIFTY IT (technology sector)
- SENSEX (BSE benchmark)

### Comparing Models
Run both HMM and GMM on same data:
1. Run HMM → Download results
2. Change model to GMM → Run again
3. Compare regime definitions

### Regime Analysis Page
After running detection, navigate to:
- "🔍 Regime Analysis" (left sidebar)
- View transition probability matrix
- Analyze regime duration statistics
- Compare volatility across regimes

## Troubleshooting

### Data Loading Issues
- Check internet connection
- Try reducing date range
- Clear browser cache

### Model Training Errors
- Ensure sufficient data (minimum 200 days)
- Reduce number of regimes if convergence fails
- Try different model (HMM vs GMM)

### Performance Issues
- Close other browser tabs
- Reduce date range for faster loading
- Use fewer features in model config

## Next Steps

1. **Explore Multi-Page Features**: Navigate through different analysis pages
2. **Customize Features**: Edit `src/features/technical.py` to add indicators
3. **Backtest Strategies**: Use regime data for strategy development
4. **Set Up Automation**: Schedule daily regime detection runs

## Tips for Best Results

✅ **Do:**
- Use at least 2-3 years of historical data
- Start with 4 regimes (optimal for most markets)
- Compare results across different time periods
- Keep feature set diverse (returns, volatility, momentum)

❌ **Don't:**
- Use very short time periods (< 6 months)
- Set too many regimes (> 6)
- Ignore model diagnostics
- Make trading decisions without backtesting

## Support & Resources

- 📖 Full Documentation: See `README.md`
- 🐛 Report Issues: GitHub Issues
- 💬 Questions: Open a discussion on GitHub
- 📧 Contact: your.email@example.com

---

**Remember**: This is a research tool. Always validate results and never trade based solely on regime detection without proper risk management.

Happy Analyzing! 📊🚀
