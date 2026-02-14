"""
Hidden Markov Model for Market Regime Detection
"""

import numpy as np
import pandas as pd
from hmmlearn import hmm
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class HMMRegimeDetector:
    """
    Hidden Markov Model for detecting market regimes
    """
    
    def __init__(self, n_states: int = 4, n_iter: int = 100, random_state: int = 42):
        """
        Initialize HMM
        
        Parameters:
        -----------
        n_states : int
            Number of hidden states (regimes)
        n_iter : int
            Number of EM iterations
        random_state : int
            Random seed for reproducibility
        """
        self.n_states = n_states
        self.n_iter = n_iter
        self.random_state = random_state
        
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        
    def fit(self, features: pd.DataFrame) -> 'HMMRegimeDetector':
        """
        Fit HMM to feature data
        
        Parameters:
        -----------
        features : pd.DataFrame
            Feature matrix for regime detection
            
        Returns:
        --------
        self : HMMRegimeDetector
        """
        self.feature_names = features.columns.tolist()
        
        # Scale features
        X_scaled = self.scaler.fit_transform(features.values)
        
        # Initialize and fit HMM
        self.model = hmm.GaussianHMM(
            n_components=self.n_states,
            covariance_type='full',
            n_iter=self.n_iter,
            random_state=self.random_state
        )
        
        self.model.fit(X_scaled)
        
        return self
    
    def predict(self, features: pd.DataFrame) -> np.ndarray:
        """
        Predict hidden states (regimes)
        
        Parameters:
        -----------
        features : pd.DataFrame
            Feature matrix
            
        Returns:
        --------
        np.ndarray : Predicted regime states
        """
        if self.model is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        X_scaled = self.scaler.transform(features.values)
        states = self.model.predict(X_scaled)
        
        return states
    
    def predict_proba(self, features: pd.DataFrame) -> np.ndarray:
        """
        Predict state probabilities
        
        Parameters:
        -----------
        features : pd.DataFrame
            Feature matrix
            
        Returns:
        --------
        np.ndarray : State probability matrix (n_samples, n_states)
        """
        if self.model is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        X_scaled = self.scaler.transform(features.values)
        
        # Compute forward probabilities
        log_probs = self.model.score_samples(X_scaled)
        probs = np.exp(log_probs)
        
        return probs
    
    def get_transition_matrix(self) -> pd.DataFrame:
        """
        Get state transition probability matrix
        
        Returns:
        --------
        pd.DataFrame : Transition matrix
        """
        if self.model is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        trans_mat = pd.DataFrame(
            self.model.transmat_,
            columns=[f'To_State_{i}' for i in range(self.n_states)],
            index=[f'From_State_{i}' for i in range(self.n_states)]
        )
        
        return trans_mat
    
    def get_regime_characteristics(self, features: pd.DataFrame, states: np.ndarray) -> pd.DataFrame:
        """
        Compute statistical characteristics of each regime
        
        Parameters:
        -----------
        features : pd.DataFrame
            Original features
        states : np.ndarray
            Predicted states
            
        Returns:
        --------
        pd.DataFrame : Regime characteristics
        """
        df = features.copy()
        df['Regime'] = states
        
        regime_stats = df.groupby('Regime').agg({
            'Return_1d': ['mean', 'std', 'min', 'max'],
            'Volatility_21d': ['mean', 'std'],
            'RSI_14': ['mean'],
            'BB_Width': ['mean']
        })
        
        return regime_stats


# Example usage
if __name__ == "__main__":
    from src.data_collection.nse_data import IndianMarketData
    from src.features.technical import TechnicalFeatures
    
    # Fetch data
    collector = IndianMarketData(start_date='2015-01-01')
    nifty_data = collector.fetch_index_data('NIFTY50')
    
    # Compute features
    featured_data = TechnicalFeatures.compute_regime_features(nifty_data)
    
    # Select features for HMM
    feature_cols = ['Return_1d', 'Volatility_21d', 'RSI_14', 'ROC_14', 'BB_Width']
    X = featured_data[feature_cols]
    
    # Fit HMM
    hmm_model = HMMRegimeDetector(n_states=4)
    hmm_model.fit(X)
    
    # Predict regimes
    regimes = hmm_model.predict(X)
    
    print(f"Detected {len(np.unique(regimes))} regimes")
    print(f"Regime distribution:\n{pd.Series(regimes).value_counts()}")
    
    # Transition matrix
    trans_mat = hmm_model.get_transition_matrix()
    print(f"\nTransition Matrix:\n{trans_mat}")
    
    # Regime characteristics
    characteristics = hmm_model.get_regime_characteristics(featured_data, regimes)
    print(f"\nRegime Characteristics:\n{characteristics}")
