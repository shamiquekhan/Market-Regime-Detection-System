"""
Detailed Regime Analysis Page
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

st.set_page_config(page_title="Regime Analysis", page_icon="�", layout="wide")

# Swiss Style CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, sans-serif;
        letter-spacing: -0.02em;
    }
    
    h1 {
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        line-height: 0.95 !important;
        letter-spacing: -0.04em !important;
        color: #000000 !important;
    }
    
    h2 {
        font-size: 2rem !important;
        font-weight: 700 !important;
        margin-top: 3rem !important;
        color: #000000 !important;
    }
    
    h3 {
        font-size: 1.25rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em !important;
        margin-top: 2rem !important;
        color: #000000 !important;
    }
    
    .main {
        padding: 3rem 4rem;
    }
    
    hr {
        margin: 3rem 0;
        border: none;
        border-top: 1px solid #E0E0E0;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("# REGIME ANALYSIS")
st.markdown("### Detailed Transition & Duration Analysis")
st.markdown("---")

# Check if data is loaded
if not st.session_state.get('regime_model_fitted', False):
    st.warning("Please run regime detection on the main page first")
    st.stop()

# Regime transition analysis
st.markdown("## TRANSITION ANALYSIS")

regimes = st.session_state.regimes
n_regimes = len(np.unique(regimes))

# Calculate transition matrix
transition_matrix = np.zeros((n_regimes, n_regimes))

for i in range(len(regimes) - 1):
    current_regime = regimes[i]
    next_regime = regimes[i + 1]
    transition_matrix[current_regime, next_regime] += 1

# Normalize rows to get probabilities
row_sums = transition_matrix.sum(axis=1, keepdims=True)
row_sums[row_sums == 0] = 1  # Avoid division by zero
transition_probs = transition_matrix / row_sums

# Display transition matrix
st.markdown("### Transition Probability Matrix")

fig_trans = go.Figure(data=go.Heatmap(
    z=transition_probs,
    x=[f'To Regime {i}' for i in range(n_regimes)],
    y=[f'From Regime {i}' for i in range(n_regimes)],
    colorscale='Blues',
    text=transition_probs,
    texttemplate='%{text:.2%}',
    textfont={"size": 12},
    colorbar=dict(title="Probability")
))

fig_trans.update_layout(
    title="Regime Transition Probabilities",
    xaxis_title="Next Regime",
    yaxis_title="Current Regime",
    height=500
)

st.plotly_chart(fig_trans, use_container_width=True)

# Regime duration analysis
st.markdown("---")
st.markdown("## DURATION ANALYSIS")

# Calculate regime durations
regime_changes = np.where(regimes[:-1] != regimes[1:])[0] + 1
regime_durations = np.diff(np.concatenate([[0], regime_changes, [len(regimes)]]))
regime_ids = regimes[np.concatenate([[0], regime_changes])]

duration_df = pd.DataFrame({
    'Regime': regime_ids,
    'Duration': regime_durations
})

# Plot duration distribution
fig_dur = px.box(
    duration_df,
    x='Regime',
    y='Duration',
    title='Regime Duration Distribution (in days)',
    labels={'Regime': 'Regime', 'Duration': 'Duration (days)'}
)

st.plotly_chart(fig_dur, use_container_width=True)

# Summary statistics
st.markdown("### Duration Statistics")
duration_stats = duration_df.groupby('Regime')['Duration'].describe()
st.dataframe(duration_stats, use_container_width=True)

# Volatility by regime
st.markdown("---")
st.markdown("## VOLATILITY ANALYSIS")

regime_data = st.session_state.featured_data.copy()
regime_data['Regime'] = regimes

col1, col2 = st.columns(2)

with col1:
    # Box plot of returns by regime
    fig_ret = px.box(
        regime_data,
        x='Regime',
        y='Return_1d',
        title='Daily Returns by Regime',
        labels={'Regime': 'Regime', 'Return_1d': 'Daily Return'}
    )
    st.plotly_chart(fig_ret, use_container_width=True)

with col2:
    # Box plot of volatility by regime
    fig_vol = px.box(
        regime_data,
        x='Regime',
        y='Volatility_21d',
        title='21-Day Volatility by Regime',
        labels={'Regime': 'Regime', 'Volatility_21d': 'Volatility'}
    )
    st.plotly_chart(fig_vol, use_container_width=True)
