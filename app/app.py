"""
Market Regime Detection System - Main Streamlit App
Version: 2.1.0 - Flexible regime strategy configuration
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
from pathlib import Path
import importlib

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.data_collection.nse_data import IndianMarketData
from src.features.technical import TechnicalFeatures
from src.models.hmm_model import HMMRegimeDetector
from src.models.gmm_model import GMMRegimeDetector

# Import and reload regime evaluation to clear cache
from src.evaluation import regime_evaluation
importlib.reload(regime_evaluation)
from src.evaluation.regime_evaluation import RegimeEvaluator

# Page configuration
st.set_page_config(
    page_title="Market Regime Detection - Indian Markets",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Swiss Style / Minimalist Design
st.markdown("""
    <style>
    /* Import Swiss grotesque typeface */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');
    
    /* Global Reset & Typography */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        letter-spacing: -0.01em;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF;
    }
    
    /* Main container - rigorous grid */
    .main {
        padding: 2rem 3rem;
        max-width: 1400px;
        margin: 0 auto;
        background: #FFFFFF;
    }
    
    .block-container {
        padding: 1rem 0 !important;
        max-width: 100% !important;
    }
    
    /* Typography hierarchy - Clean, balanced */
    h1 {
        font-size: 2.75rem !important;
        font-weight: 700 !important;
        line-height: 1.1 !important;
        letter-spacing: -0.02em !important;
        margin-bottom: 0.5rem !important;
        margin-top: 0 !important;
        color: #000000 !important;
        text-transform: uppercase;
    }
    
    h2 {
        font-size: 2rem !important;
        font-weight: 700 !important;
        line-height: 1.2 !important;
        letter-spacing: -0.02em !important;
        margin-top: 3rem !important;
        margin-bottom: 1.25rem !important;
        color: #000000 !important;
        text-transform: uppercase;
    }
    
    h3 {
        font-size: 1rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.08em !important;
        margin-top: 2.5rem !important;
        margin-bottom: 1rem !important;
        color: #666666 !important;
    }
    
    /* Subtitle specific styling */
    .main h3:first-of-type {
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.12em !important;
        color: #999999 !important;
        margin-top: 0.5rem !important;
        margin-bottom: 2rem !important;
    }
    
    p {
        font-size: 1rem;
        line-height: 1.75;
        color: #333333;
        margin-bottom: 1.25rem;
        max-width: 100%;
    }
    
    /* Strong text */
    strong {
        font-weight: 600;
        color: #000000;
    }
    
    /* Metrics - Sharp, minimal */
    [data-testid="stMetricValue"] {
        font-size: 3rem !important;
        font-weight: 700 !important;
        color: #000000 !important;
        letter-spacing: -0.02em !important;
        font-variant-numeric: tabular-nums;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.12em !important;
        font-weight: 600 !important;
        color: #666666 !important;
        margin-bottom: 0.5rem !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 1rem !important;
        font-weight: 600 !important;
        font-variant-numeric: tabular-nums;
    }
    
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #000000;
        border-radius: 0;
        padding: 2rem;
    }
    
    /* Buttons - Bold accent with sharp edges */
    .stButton > button {
        background-color: #FF0000;
        color: #FFFFFF;
        border: none;
        border-radius: 0;
        padding: 1.25rem 2.5rem;
        font-weight: 700;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        transition: all 0.15s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        background-color: #000000;
        transform: translateY(-1px);
        box-shadow: 0 4px 0 0 #000000;
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: none;
    }
    
    /* Sidebar - Minimal, functional */
    [data-testid="stSidebar"] {
        background-color: #FAFAFA;
        border-right: 1px solid #E0E0E0;
        padding: 2rem 1.5rem;
    }
    
    [data-testid="stSidebar"] h2 {
        font-size: 1.125rem !important;
        font-weight: 700 !important;
        margin-top: 0 !important;
        margin-bottom: 1.5rem !important;
        color: #000000 !important;
        letter-spacing: 0.05em !important;
    }
    
    [data-testid="stSidebar"] h3 {
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        margin-top: 2rem !important;
        margin-bottom: 0.75rem !important;
        color: #666666 !important;
        letter-spacing: 0.1em !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        margin-bottom: 1rem;
    }
    
    /* Input fields - Sharp corners, clean */
    .stSelectbox, .stDateInput, .stSlider {
        margin-bottom: 2rem;
    }
    
    .stSelectbox label, .stDateInput label, .stSlider label {
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        font-weight: 600 !important;
        color: #666666 !important;
        margin-bottom: 0.5rem !important;
    }
    
    input, select, .stSelectbox > div > div {
        border-radius: 0 !important;
        border: 1px solid #CCCCCC !important;
        font-size: 0.95rem !important;
    }
    
    input:focus, select:focus {
        border-color: #000000 !important;
        box-shadow: none !important;
    }
    
    /* Dataframe - Grid-based, monochrome */
    .dataframe {
        border: 1px solid #000000 !important;
        border-collapse: collapse !important;
        font-size: 0.875rem !important;
    }
    
    .dataframe thead tr th {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.12em !important;
        padding: 1rem 1.5rem !important;
        border: 1px solid #000000 !important;
        text-align: left !important;
    }
    
    .dataframe tbody tr td {
        padding: 0.875rem 1.5rem !important;
        border: 1px solid #E0E0E0 !important;
        font-variant-numeric: tabular-nums;
        background-color: #FFFFFF !important;
    }
    
    .dataframe tbody tr:hover td {
        background-color: #F8F8F8 !important;
    }
    
    /* Alert/Info boxes - Accent stripe */
    [data-testid="stAlert"] {
        border-radius: 0 !important;
        border-left: 4px solid #FF0000 !important;
        background-color: #F8F8F8 !important;
        padding: 1.5rem 2rem !important;
        border-top: none !important;
        border-right: none !important;
        border-bottom: none !important;
    }
    
    [data-testid="stAlert"] p {
        margin-bottom: 0 !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        color: #333333 !important;
    }
    
    /* Dividers - Generous whitespace */
    hr {
        margin: 3rem 0 !important;
        border: none !important;
        border-top: 1px solid #E0E0E0 !important;
    }
    
    /* List items */
    li {
        line-height: 1.75;
        margin-bottom: 0.5rem;
    }
    
    /* Markdown content sections */
    .element-container {
        margin-bottom: 0;
    }
    
    /* Download button - Inverted */
    .stDownloadButton > button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: 1px solid #000000 !important;
        border-radius: 0 !important;
        padding: 1.25rem 2.5rem !important;
        font-weight: 700 !important;
        font-size: 0.875rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.15em !important;
        width: 100% !important;
    }
    
    .stDownloadButton > button:hover {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* Column layout spacing */
    [data-testid="column"] {
        padding: 0 1rem;
    }
    
    [data-testid="column"]:first-child {
        padding-left: 0;
    }
    
    [data-testid="column"]:last-child {
        padding-right: 0;
    }
    
    /* Remove default streamlit branding feel */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Plotly charts - minimal chrome */
    .js-plotly-plot {
        border: 1px solid #E0E0E0;
    }
    
    /* Slider - minimal */
    .stSlider > div > div > div {
        background-color: #E0E0E0 !important;
    }
    
    .stSlider > div > div > div > div {
        background-color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'regime_model_fitted' not in st.session_state:
    st.session_state.regime_model_fitted = False

# Title and description
st.markdown("# MARKET REGIME DETECTION")
st.markdown("<p style='font-size: 0.875rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.12em; color: #999999; margin-top: 0.5rem; margin-bottom: 2.5rem;'>Real-time Analysis — Indian Stock Market (NSE/BSE)</p>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar configuration
with st.sidebar:
    st.markdown("## CONFIGURATION")
    st.markdown("---")
    
    # Data selection
    st.markdown("### 01 — Data Selection")
    index_choice = st.selectbox(
        "Select Index",
        options=['NIFTY50', 'SENSEX', 'NIFTY_BANK', 'NIFTY_IT'],
        index=0
    )
    
    start_date = st.date_input(
        "Start Date",
        value=datetime.now() - timedelta(days=365*3),
        max_value=datetime.now()
    )
    
    end_date = st.date_input(
        "End Date",
        value=datetime.now(),
        max_value=datetime.now()
    )
    
    # Model selection
    st.markdown("### 02 — Model Configuration")
    model_type = st.selectbox(
        "Regime Detection Model",
        options=['Hidden Markov Model (HMM)', 'Gaussian Mixture Model (GMM)'],
        index=0
    )
    
    n_regimes = st.slider(
        "Number of Regimes",
        min_value=2,
        max_value=6,
        value=4,
        help="Typically 3-5 regimes work well"
    )
    
    # Strategy Configuration
    st.markdown("### 03 — Strategy Settings")
    
    strategy_preset = st.selectbox(
        "Strategy Preset",
        options=['Conservative (Long in 2 regimes)', 
                 'Balanced (Long in 3 regimes)', 
                 'Aggressive (Long in all but crisis)'],
        index=0,
        help="Choose trading aggressiveness"
    )
    
    risk_free_rate = st.slider(
        "Risk-Free Rate (%)",
        min_value=0.0,
        max_value=10.0,
        value=6.5,
        step=0.5,
        help="Annual risk-free rate for Sharpe calculation (India T-bills ~6.5%)"
    ) / 100
    
    # Advanced: Custom regime assignment (expander)
    with st.expander("⚙️ Advanced: Custom Regime Assignment"):
        st.markdown("**Choose which regimes to go LONG vs CASH**")
        st.markdown("_Tip: Check regime characteristics after detection to optimize_")
        
        custom_assignment = st.checkbox("Use Custom Assignment", value=False)
        
        if custom_assignment:
            long_regime_input = st.text_input(
                "Long Regimes (comma-separated)",
                value="0,1",
                help="E.g., '0,1,2' for regimes 0, 1, and 2"
            )
    
    # Load data button
    st.markdown("---")
    if st.button("LOAD & ANALYZE", type="primary"):
        with st.spinner("Loading market data..."):
            try:
                # Fetch data
                collector = IndianMarketData(
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d')
                )
                raw_data = collector.fetch_index_data(index_choice)
                
                if raw_data.empty:
                    st.error("Failed to fetch data. Please check your internet connection.")
                else:
                    # Compute features
                    featured_data = TechnicalFeatures.compute_regime_features(raw_data)
                    
                    # Store in session state
                    st.session_state.raw_data = raw_data
                    st.session_state.featured_data = featured_data
                    st.session_state.data_loaded = True
                    st.session_state.index_choice = index_choice
                    
                    st.success(f"✅ Loaded {len(raw_data)} days of {index_choice} data")
            
            except Exception as e:
                st.error(f"Error loading data: {str(e)}")

# Main content area
if st.session_state.data_loaded:
    
    # Verify data is valid before proceeding
    if (st.session_state.raw_data is None or st.session_state.raw_data.empty or
        st.session_state.featured_data is None or st.session_state.featured_data.empty):
        st.error("⚠️ Data is empty. Please try loading data again.")
        st.session_state.data_loaded = False
        st.stop()
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        try:
            current_price = st.session_state.raw_data['Close'].iloc[-1]
            price_change = st.session_state.raw_data['Close'].pct_change().iloc[-1] * 100
            st.metric(
                label="Current Price",
                value=f"₹{current_price:,.2f}",
                delta=f"{price_change:.2f}%"
            )
        except (IndexError, KeyError) as e:
            st.metric(label="Current Price", value="N/A")
    
    with col2:
        try:
            if 'Volatility_21d' in st.session_state.featured_data.columns:
                volatility = st.session_state.featured_data['Volatility_21d'].iloc[-1]
                st.metric(
                    label="21-Day Volatility",
                    value=f"{volatility:.2%}"
                )
            else:
                st.metric(label="21-Day Volatility", value="N/A")
        except (IndexError, KeyError) as e:
            st.metric(label="21-Day Volatility", value="N/A")
    
    with col3:
        try:
            if 'RSI_14' in st.session_state.featured_data.columns:
                rsi = st.session_state.featured_data['RSI_14'].iloc[-1]
                st.metric(
                    label="RSI (14)",
                    value=f"{rsi:.1f}"
                )
            else:
                st.metric(label="RSI (14)", value="N/A")
        except (IndexError, KeyError) as e:
            st.metric(label="RSI (14)", value="N/A")
    
    with col4:
        data_points = len(st.session_state.raw_data)
        st.metric(
            label="Data Points",
            value=f"{data_points:,}"
        )
    
    # Regime detection section
    st.markdown("---")
    st.markdown("## REGIME DETECTION")
    
    if st.button("RUN DETECTION", type="primary"):
        with st.spinner("Training regime detection model..."):
            try:
                # Select features for modeling
                feature_cols = ['Return_1d', 'Volatility_21d', 'RSI_14', 'ROC_14', 
                               'BB_Width', 'Volume_Ratio', 'Trend_Strength']
                
                # Remove any columns that don't exist
                feature_cols = [col for col in feature_cols 
                              if col in st.session_state.featured_data.columns]
                
                X = st.session_state.featured_data[feature_cols]
                
                # Fit model
                if 'HMM' in model_type:
                    model = HMMRegimeDetector(n_states=n_regimes)
                else:
                    model = GMMRegimeDetector(n_components=n_regimes)
                
                model.fit(X)
                regimes = model.predict(X)
                
                # Determine regime assignment based on preset
                if custom_assignment:
                    try:
                        long_regimes = [int(x.strip()) for x in long_regime_input.split(',')]
                        hedge_regimes = [i for i in range(n_regimes) if i not in long_regimes]
                    except:
                        st.warning("Invalid custom assignment, using preset")
                        custom_assignment = False
                
                if not custom_assignment:
                    if 'Conservative' in strategy_preset:
                        # Original: Long in 2 regimes
                        long_regimes = [0, 1]
                        hedge_regimes = list(range(2, n_regimes))
                    elif 'Balanced' in strategy_preset:
                        # Long in 3 regimes
                        long_regimes = list(range(n_regimes - 1))  # All except last
                        hedge_regimes = [n_regimes - 1]
                    else:  # Aggressive
                        # Long in all but one (presumed crisis regime)
                        long_regimes = list(range(n_regimes - 1))
                        hedge_regimes = [n_regimes - 1]
                
                # Store results
                st.session_state.model = model
                st.session_state.regimes = regimes
                st.session_state.regime_model_fitted = True
                st.session_state.feature_cols = feature_cols
                st.session_state.long_regimes = long_regimes
                st.session_state.hedge_regimes = hedge_regimes
                st.session_state.risk_free_rate = risk_free_rate
                st.session_state.n_regimes = n_regimes
                
                st.success(f"✅ Regime detection complete! Detected {n_regimes} regimes.")
                st.info(f"📊 Strategy: Long in regimes {long_regimes}, Cash in regimes {hedge_regimes}")
                
            except Exception as e:
                st.error(f"Error in regime detection: {str(e)}")
    
    # Display results if model is fitted
    if st.session_state.regime_model_fitted:
        
        # Regime distribution
        st.markdown("### Distribution Analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Time series plot with regimes
            fig = go.Figure()
            
            # Check if Close column exists in featured_data
            close_col = 'Close' if 'Close' in st.session_state.featured_data.columns else 'close'
            
            if close_col in st.session_state.featured_data.columns:
                # Add price line
                fig.add_trace(go.Scatter(
                    x=st.session_state.featured_data.index,
                    y=st.session_state.featured_data[close_col],
                    mode='lines',
                    name='Close Price',
                    line=dict(color='blue', width=2)
                ))
                
                # Color background by regime
                regime_colors = px.colors.qualitative.Set1[:n_regimes]
                
                for i in range(n_regimes):
                    mask = st.session_state.regimes == i
                    regime_dates = st.session_state.featured_data.index[mask]
                    
                    if len(regime_dates) > 0:
                        fig.add_trace(go.Scatter(
                            x=regime_dates,
                            y=st.session_state.featured_data.loc[regime_dates, close_col],
                            mode='markers',
                            name=f'Regime {i}',
                            marker=dict(color=regime_colors[i], size=3)
                        ))
                
                fig.update_layout(
                    title=f"{st.session_state.index_choice} Price with Detected Regimes",
                    xaxis_title="Date",
                    yaxis_title="Price (₹)",
                    hovermode='x unified',
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Close price data not available for visualization.")
        
        with col2:
            # Regime count
            regime_counts = pd.Series(st.session_state.regimes).value_counts().sort_index()
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=[f'Regime {i}' for i in regime_counts.index],
                values=regime_counts.values,
                hole=0.3
            )])
            
            fig_pie.update_layout(
                title="Regime Distribution",
                height=500
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Regime characteristics
        st.markdown("### Characteristics Matrix")
        
        # Calculate regime stats
        try:
            regime_data = st.session_state.featured_data.copy()
            regime_data['Regime'] = st.session_state.regimes
            
            # Build aggregation dict based on available columns
            agg_dict = {}
            if 'Return_1d' in regime_data.columns:
                agg_dict['Return_1d'] = ['mean', 'std']
            if 'Volatility_21d' in regime_data.columns:
                agg_dict['Volatility_21d'] = 'mean'
            if 'RSI_14' in regime_data.columns:
                agg_dict['RSI_14'] = 'mean'
            if 'Volume_Ratio' in regime_data.columns:
                agg_dict['Volume_Ratio'] = 'mean'
            
            if agg_dict:
                regime_stats = regime_data.groupby('Regime').agg(agg_dict).round(4)
                
                # Flatten column names
                regime_stats.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col 
                                       for col in regime_stats.columns.values]
                regime_stats = regime_stats.reset_index()
                
                st.dataframe(regime_stats, use_container_width=True)
                
                # Optimization guidance
                st.markdown("#### 💡 Strategy Optimization Guide")
                
                if 'Return_1d_mean' in regime_stats.columns:
                    # Calculate which regimes have positive expected returns
                    positive_regimes = regime_stats[regime_stats['Return_1d_mean'] > 0]['Regime'].tolist()
                    high_return_regimes = regime_stats[regime_stats['Return_1d_mean'] > 0.001]['Regime'].tolist()
                    
                    current_long = st.session_state.get('long_regimes', [0, 1])
                    current_hedge = st.session_state.get('hedge_regimes', [2, 3] if n_regimes == 4 else [])
                    
                    st.markdown(f"""
                    <div style='background: #E3F2FD; padding: 1rem; border-left: 4px solid #1976D2; margin: 1rem 0;'>
                        <div style='font-size: 0.875rem; font-weight: 600; color: #1976D2; margin-bottom: 0.5rem;'>Current Strategy Analysis</div>
                        <div style='font-size: 0.875rem; color: #333;'>
                            • <strong>Long positions:</strong> Regimes {', '.join(map(str, current_long))}<br>
                            • <strong>Positive return regimes:</strong> {', '.join(map(str, positive_regimes)) if positive_regimes else 'None'}<br>
                            • <strong>High return regimes (>0.1% daily):</strong> {', '.join(map(str, high_return_regimes)) if high_return_regimes else 'None'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Check if current strategy is suboptimal
                    missing_good_regimes = [r for r in high_return_regimes if r not in current_long]
                    bad_long_regimes = [r for r in current_long if r not in positive_regimes]
                    
                    if missing_good_regimes or bad_long_regimes:
                        suggestions = []
                        if missing_good_regimes:
                            suggestions.append(f"Consider adding regimes **{', '.join(map(str, missing_good_regimes))}** to long positions (high expected returns)")
                        if bad_long_regimes:
                            suggestions.append(f"Consider removing regimes **{', '.join(map(str, bad_long_regimes))}** from long positions (negative expected returns)")
                        
                        st.warning("⚠️ **Potential Strategy Improvements:**\n\n" + "\n\n".join([f"• {s}" for s in suggestions]))
                        st.info("💡 **Tip:** Use the sidebar's '03 — Strategy Settings' to adjust regime assignment and re-run detection")
            else:
                st.warning("⚠️ Insufficient feature data to display regime characteristics.")
                
        except Exception as e:
            st.error(f"Error calculating regime characteristics: {str(e)}")
        
        # Current regime
        try:
            if len(st.session_state.regimes) > 0:
                current_regime = st.session_state.regimes[-1]
                st.markdown(f"""
                <div style='border: 1px solid #000000; background: #000000; color: #FFFFFF; padding: 1.5rem 2rem; margin: 2rem 0;'>
                    <div style='font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.15em; opacity: 0.7; margin-bottom: 0.5rem;'>CURRENT MARKET STATE</div>
                    <div style='font-size: 2.5rem; font-weight: 700; letter-spacing: -0.02em;'>REGIME {current_regime}</div>
                </div>
                """, unsafe_allow_html=True)
        except (IndexError, AttributeError):
            st.warning("⚠️ No regime data available.")
        
        # Regime interpretation
        st.markdown("### Interpretation")
        
        try:
            # Simple heuristic interpretation based on returns and volatility
            for regime_id in range(n_regimes):
                regime_mask = st.session_state.regimes == regime_id
                
                # Check if columns exist before accessing
                if 'Return_1d' in regime_data.columns and 'Volatility_21d' in regime_data.columns:
                    regime_returns = regime_data.loc[regime_mask, 'Return_1d'].mean()
                    regime_vol = regime_data.loc[regime_mask, 'Volatility_21d'].mean()
                    
                    if regime_returns > 0.001 and regime_vol < 0.15:
                        label = "HEALTHY & STEADY"
                        desc = "Positive returns — Low volatility"
                        color = "#000000"
                    elif regime_returns > 0 and regime_vol > 0.15:
                        label = "BULLISH BUT VOLATILE"
                        desc = "Positive returns — High volatility"
                        color = "#FF0000"
                    elif regime_returns < 0 and regime_vol > 0.20:
                        label = "CRISIS MODE"
                        desc = "Negative returns — High volatility"
                        color = "#FF0000"
                    elif abs(regime_returns) < 0.001:
                        label = "RANGE-BOUND"
                        desc = "Neutral returns — Consolidation"
                        color = "#666666"
                    else:
                        label = "PULLBACK"
                        desc = "Moderately negative returns"
                        color = "#666666"
                    
                    st.markdown(f"""
                    <div style='border-left: 4px solid {color}; padding: 1rem 1.5rem; margin: 1rem 0; background: #FAFAFA;'>
                        <div style='font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: #666; margin-bottom: 0.25rem;'>REGIME {regime_id}</div>
                        <div style='font-size: 1.25rem; font-weight: 700; margin-bottom: 0.25rem;'>{label}</div>
                        <div style='font-size: 0.875rem; color: #666;'>{desc}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Fallback when columns don't exist
                    st.markdown(f"""
                    <div style='border-left: 4px solid #666666; padding: 1rem 1.5rem; margin: 1rem 0; background: #FAFAFA;'>
                        <div style='font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: #666; margin-bottom: 0.25rem;'>REGIME {regime_id}</div>
                        <div style='font-size: 1.25rem; font-weight: 700; margin-bottom: 0.25rem;'>REGIME {regime_id}</div>
                        <div style='font-size: 0.875rem; color: #666;'>Insufficient data for interpretation</div>
                    </div>
                    """, unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"⚠️ Could not generate regime interpretations: {str(e)}")
        
        # Model Evaluation Section
        st.markdown("---")
        st.markdown("## MODEL EVALUATION")
        st.markdown("Regime persistence, transition realism, and trading value metrics")
        
        try:
            # Create evaluator - ensure required columns exist
            if 'Close' not in st.session_state.featured_data.columns:
                st.error("⚠️ Close price data missing. Cannot perform evaluation.")
            elif 'Return_1d' not in st.session_state.featured_data.columns:
                st.error("⚠️ Return data missing. Cannot perform evaluation.")
            else:
                eval_data = st.session_state.featured_data[['Close']].copy()
                eval_data['returns'] = st.session_state.featured_data['Return_1d']
                evaluator = RegimeEvaluator(
                    model=st.session_state.model,
                    data=eval_data,
                    regimes=st.session_state.regimes
                )
                
                # Get strategy parameters from session state (with fallbacks)
                long_regimes = st.session_state.get('long_regimes', [0, 1])
                hedge_regimes = st.session_state.get('hedge_regimes', [2, 3])
                risk_free_rate = st.session_state.get('risk_free_rate', 0.065)
                
                # Generate evaluation report with configured parameters
                eval_report = evaluator.generate_evaluation_report(
                    long_regimes=long_regimes,
                    hedge_regimes=hedge_regimes,
                    risk_free_rate=risk_free_rate
                )
            
            # Display strategy configuration
            st.markdown("### Strategy Configuration")
            config_col1, config_col2, config_col3 = st.columns(3)
            
            with config_col1:
                st.markdown(f"""
                <div style='background: #E8F5E9; padding: 1rem; border-radius: 4px;'>
                    <div style='font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 0.1em;'>Long Positions</div>
                    <div style='font-size: 1.5rem; font-weight: 700; color: #2E7D32;'>Regimes {', '.join(map(str, long_regimes))}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with config_col2:
                st.markdown(f"""
                <div style='background: #FFF3E0; padding: 1rem; border-radius: 4px;'>
                    <div style='font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 0.1em;'>Cash/Hedge</div>
                    <div style='font-size: 1.5rem; font-weight: 700; color: #E65100;'>Regimes {', '.join(map(str, hedge_regimes))}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with config_col3:
                st.markdown(f"""
                <div style='background: #F5F5F5; padding: 1rem; border-radius: 4px;'>
                    <div style='font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 0.1em;'>Risk-Free Rate</div>
                    <div style='font-size: 1.5rem; font-weight: 700; color: #333;'>{risk_free_rate*100:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Display key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                sharpe = eval_report['backtest_results']['sharpe_ratio']
                st.metric(
                    label="Sharpe Ratio",
                    value=f"{sharpe:.2f}",
                    delta="Good" if sharpe > 0.8 else "Improve",
                    help="Risk-adjusted returns (>1.2 = Excellent, >0.8 = Good)"
                )
            
            with col2:
                calmar = eval_report['backtest_results']['calmar_ratio']
                st.metric(
                    label="Calmar Ratio",
                    value=f"{calmar:.2f}",
                    delta="Good" if calmar > 0.5 else "Improve",
                    help="Return / Max Drawdown (>0.5 = Good)"
                )
            
            with col3:
                max_dd = eval_report['backtest_results']['max_drawdown']
                st.metric(
                    label="Max Drawdown",
                    value=f"{max_dd:.1%}",
                    help="Maximum portfolio decline"
                )
            
            with col4:
                if 'avg_persistence' in eval_report['transition_analysis']:
                    persistence = eval_report['transition_analysis']['avg_persistence']
                    st.metric(
                        label="Regime Persistence",
                        value=f"{persistence:.2f}",
                        delta="Good" if persistence > 0.85 else "Improve",
                        help="Diagonal of transition matrix (>0.85 = Good)"
                    )
            
            # Strategy Quality Badge
            quality = eval_report['backtest_results']['quality_score']
            quality_color = "#00AA00" if "Excellent" in quality else ("#FF9900" if "Good" in quality else "#FF0000")
            
            st.markdown(f"""
            <div style='background: {quality_color}; color: white; padding: 1rem; margin: 1.5rem 0; text-align: center; font-weight: 700; font-size: 1.125rem; text-transform: uppercase; letter-spacing: 0.1em;'>
                {quality}
            </div>
            """, unsafe_allow_html=True)
            
            # Transition Matrix (for HMM)
            if 'transition_matrix' in eval_report['transition_analysis']:
                st.markdown("### Transition Matrix Stability")
                st.markdown("**Diagonal persistence >0.85 indicates good regime stability**")
                
                trans_matrix = eval_report['transition_analysis']['transition_matrix']
                trans_df = pd.DataFrame(
                    trans_matrix,
                    columns=[f"To Regime {i}" for i in range(n_regimes)],
                    index=[f"From Regime {i}" for i in range(n_regimes)]
                )
                
                # Highlight diagonal
                st.dataframe(
                    trans_df.style.format("{:.3f}")
                    .background_gradient(cmap='RdYlGn', axis=None, vmin=0, vmax=1),
                    use_container_width=True
                )
            
            # Backtest Performance
            st.markdown("### Backtest Performance")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Strategy Returns**")
                st.markdown(f"- **Total Return:** {eval_report['backtest_results']['total_return']:.1%}")
                st.markdown(f"- **Annualized:** {eval_report['backtest_results']['annualized_return']:.1%}")
                st.markdown(f"- **Sharpe Ratio:** {eval_report['backtest_results']['sharpe_ratio']:.2f}")
            
            with col2:
                st.markdown("**Risk Metrics**")
                st.markdown(f"- **Max Drawdown:** {eval_report['backtest_results']['max_drawdown']:.1%}")
                st.markdown(f"- **Calmar Ratio:** {eval_report['backtest_results']['calmar_ratio']:.2f}")
                beats_bh = "✓ Yes" if eval_report['backtest_results']['strategy_beats_bh'] else "✗ No"
                st.markdown(f"- **Beats Buy & Hold:** {beats_bh}")
            
            # Cumulative Returns Chart
            st.markdown("### Strategy vs Buy & Hold")
            
            fig_returns = go.Figure()
            
            fig_returns.add_trace(go.Scatter(
                x=eval_data.index,
                y=eval_report['backtest_results']['cumulative_returns'],
                name='Regime Strategy',
                line=dict(color='#FF0000', width=2)
            ))
            
            fig_returns.add_trace(go.Scatter(
                x=eval_data.index,
                y=eval_report['backtest_results']['buy_hold_cumulative'],
                name='Buy & Hold',
                line=dict(color='#666666', width=2, dash='dash')
            ))
            
            fig_returns.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis_title='Date',
                yaxis_title='Cumulative Returns',
                hovermode='x unified',
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family='Inter', size=12),
                showlegend=True,
                legend=dict(x=0.02, y=0.98)
            )
            
            fig_returns.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E0E0E0')
            fig_returns.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E0E0E0')
            
            st.plotly_chart(fig_returns, use_container_width=True)
            
            # Information Criteria
            if eval_report['information_criteria']:
                st.markdown("### Model Selection Criteria")
                st.markdown("**Lower AIC/BIC values indicate better model fit**")
                
                ic_col1, ic_col2, ic_col3 = st.columns(3)
                
                with ic_col1:
                    if 'aic' in eval_report['information_criteria']:
                        st.metric(
                            label="AIC",
                            value=f"{eval_report['information_criteria']['aic']:.1f}",
                            help="Akaike Information Criterion"
                        )
                
                with ic_col2:
                    if 'bic' in eval_report['information_criteria']:
                        st.metric(
                            label="BIC",
                            value=f"{eval_report['information_criteria']['bic']:.1f}",
                            help="Bayesian Information Criterion (penalizes complexity)"
                        )
                
                with ic_col3:
                    if 'log_likelihood' in eval_report['information_criteria']:
                        st.metric(
                            label="Log Likelihood",
                            value=f"{eval_report['information_criteria']['log_likelihood']:.1f}"
                        )
            
        except Exception as e:
            st.warning(f"Evaluation metrics unavailable: {str(e)}")
        
        # Download results
        st.markdown("---")
        st.markdown("### Export Data")
        
        # Prepare download data
        download_data = st.session_state.featured_data.copy()
        download_data['Regime'] = st.session_state.regimes
        
        csv = download_data.to_csv()
        
        st.download_button(
            label="DOWNLOAD CSV",
            data=csv,
            file_name=f"regime_data_{st.session_state.index_choice}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

else:
    # Show welcome message
    st.info("Configure settings in the sidebar and click LOAD & ANALYZE to begin")
    
    # Display sample information
    st.markdown("""
    ## SYSTEM OVERVIEW
    
    Advanced machine learning algorithms for detecting distinct market regimes in the Indian stock market.
    
    ### FEATURES
    
    **Real-time Data** — NSE/BSE via Yahoo Finance  
    **ML Models** — Hidden Markov Models (HMM) / Gaussian Mixture Models (GMM)  
    **Technical Analysis** — 20+ technical indicators  
    **Regime Analysis** — Detailed characterization of each detected regime  
    **Trading Insights** — Market condition analysis for decision-making
    
    ### HOW TO USE
    
    **01** — Select preferred index (NIFTY50, SENSEX, etc.)  
    **02** — Choose date range for analysis  
    **03** — Configure model parameters  
    **04** — Load data and run regime detection  
    **05** — Analyze results and download reports
    
    ### TYPICAL REGIMES
    
    **Healthy & Steady** — Low volatility, positive returns  
    **Pullback/Recovery** — Moderate volatility, defensive positioning  
    **Cautionary Watch** — Neutral performance, market uncertainty  
    **Crisis** — High volatility, negative returns, flight to safety
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 3rem 0 2rem 0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em;'>
    <p style='margin-bottom: 0.5rem;'>MARKET REGIME DETECTION SYSTEM — VERSION 1.0</p>
    <p style='margin: 0;'>FOR EDUCATIONAL PURPOSES ONLY</p>
</div>
""", unsafe_allow_html=True)
