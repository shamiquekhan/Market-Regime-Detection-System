"""
Gaussian Mixture Model for Market Regime Detection
"""

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from typing import Tuple

class GMMRegimeDetector:
    """
    Gaussian Mixture Model for regime clustering
    """
    
    def __init__(self, n_components: int = 4, covariance_type: str = 'full', 
                 random_state: int = 42, max_iter: int = 200):
        """
        Initialize GMM
        
        Parameters:
        -----------
        n_components : int
            Number of mixture components (regimes)
        covariance_type : str
            Type of covariance ('full', 'tied', 'diag', 'spherical')
        random_state : int
            Random seed
        max_iter : int
            Maximum EM iterations
        """
        self.n_components = n_components
        self.covariance_type = covariance_type
        self.random_state = random_state
        self.max_iter = max_iter
        
        self.model = None
        self.scaler = StandardScaler()
        
    def fit(self, features: pd.DataFrame) -> 'GMMRegimeDetector':
        """
        Fit GMM to features
        
        Parameters:
        -----------
        features : pd.DataFrame
            Feature matrix
            
        Returns:
        --------
        self : GMMRegimeDetector
        """
        # Scale features
        X_scaled = self.scaler.fit_transform(features.values)
        
        # Fit GMM
        self.model = GaussianMixture(
            n_components=self.n_components,
            covariance_type=self.covariance_type,
            max_iter=self.max_iter,
            random_state=self.random_state
        )
        
        self.model.fit(X_scaled)
        
        return self
    
    def predict(self, features: pd.DataFrame) -> np.ndarray:
        """
        Predict cluster assignments
        
        Parameters:
        -----------
        features : pd.DataFrame
            Feature matrix
            
        Returns:
        --------
        np.ndarray : Cluster labels
        """
        if self.model is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        X_scaled = self.scaler.transform(features.values)
        clusters = self.model.predict(X_scaled)
        
        return clusters
    
    def predict_proba(self, features: pd.DataFrame) -> np.ndarray:
        """
        Predict cluster probabilities
        
        Parameters:
        -----------
        features : pd.DataFrame
            Feature matrix
            
        Returns:
        --------
        np.ndarray : Probability matrix (n_samples, n_components)
        """
        if self.model is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        X_scaled = self.scaler.transform(features.values)
        probs = self.model.predict_proba(X_scaled)
        
        return probs
    
    def get_bic_aic(self, features: pd.DataFrame) -> Tuple[float, float]:
        """
        Get BIC and AIC scores for model selection
        
        Parameters:
        -----------
        features : pd.DataFrame
            Feature matrix
            
        Returns:
        --------
        Tuple[float, float] : BIC and AIC scores
        """
        if self.model is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        X_scaled = self.scaler.transform(features.values)
        
        bic = self.model.bic(X_scaled)
        aic = self.model.aic(X_scaled)
        
        return bic, aic
    
    @staticmethod
    def find_optimal_components(features: pd.DataFrame, 
                               max_components: int = 10) -> pd.DataFrame:
        """
        Find optimal number of components using BIC/AIC
        
        Parameters:
        -----------
        features : pd.DataFrame
            Feature matrix
        max_components : int
            Maximum number of components to test
            
        Returns:
        --------
        pd.DataFrame : BIC/AIC scores for each n_components
        """
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(features.values)
        
        results = []
        
        for n in range(2, max_components + 1):
            gmm = GaussianMixture(n_components=n, random_state=42)
            gmm.fit(X_scaled)
            
            results.append({
                'n_components': n,
                'BIC': gmm.bic(X_scaled),
                'AIC': gmm.aic(X_scaled)
            })
        
        results_df = pd.DataFrame(results)
        
        return results_df


# Example usage
if __name__ == "__main__":
    from src.data_collection.nse_data import IndianMarketData
    from src.features.technical import TechnicalFeatures
    
    # Fetch and prepare data
    collector = IndianMarketData(start_date='2015-01-01')
    nifty_data = collector.fetch_index_data('NIFTY50')
    featured_data = TechnicalFeatures.compute_regime_features(nifty_data)
    
    # Select features
    feature_cols = ['Return_1d', 'Volatility_21d', 'RSI_14', 'ROC_14', 'BB_Width']
    X = featured_data[feature_cols]
    
    # Find optimal components
    print("Finding optimal number of components...")
    opt_results = GMMRegimeDetector.find_optimal_components(X, max_components=8)
    print(opt_results)
    
    optimal_n = opt_results.loc[opt_results['BIC'].idxmin(), 'n_components']
    print(f"\nOptimal number of components: {optimal_n}")
    
    # Fit GMM
    gmm_model = GMMRegimeDetector(n_components=int(optimal_n))
    gmm_model.fit(X)
    
    # Predict regimes
    regimes = gmm_model.predict(X)
    probs = gmm_model.predict_proba(X)
    
    print(f"\nRegime distribution:\n{pd.Series(regimes).value_counts()}")
    print(f"\nAverage regime confidence: {probs.max(axis=1).mean():.2%}")
