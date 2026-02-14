"""
Advanced Volatility Measures for Regime Detection
"""

import pandas as pd
import numpy as np
from typing import Tuple

class VolatilityFeatures:
    """
    Advanced volatility estimation methods
    """
    
    @staticmethod
    def parkinson_volatility(data: pd.DataFrame, window: int = 20) -> pd.Series:
        """
        Parkinson's volatility estimator using High-Low range
        More efficient than close-to-close volatility
        
        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame with 'High' and 'Low' columns
        window : int
            Rolling window size
            
        Returns:
        --------
        pd.Series : Annualized Parkinson volatility
        """
        hl_ratio = np.log(data['High'] / data['Low'])
        parkinson_vol = np.sqrt((1 / (4 * np.log(2))) * (hl_ratio ** 2).rolling(window).mean()) * np.sqrt(252)
        return parkinson_vol
    
    @staticmethod
    def garman_klass_volatility(data: pd.DataFrame, window: int = 20) -> pd.Series:
        """
        Garman-Klass volatility estimator
        Uses Open, High, Low, Close
        
        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame with OHLC columns
        window : int
            Rolling window size
            
        Returns:
        --------
        pd.Series : Annualized Garman-Klass volatility
        """
        log_hl = np.log(data['High'] / data['Low'])
        log_co = np.log(data['Close'] / data['Open'])
        
        gk_vol = np.sqrt(
            0.5 * (log_hl ** 2).rolling(window).mean() - 
            (2 * np.log(2) - 1) * (log_co ** 2).rolling(window).mean()
        ) * np.sqrt(252)
        
        return gk_vol
    
    @staticmethod
    def realized_volatility(data: pd.DataFrame, window: int = 20) -> pd.Series:
        """
        Realized volatility (standard deviation of log returns)
        
        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame with 'Close' column
        window : int
            Rolling window size
            
        Returns:
        --------
        pd.Series : Annualized realized volatility
        """
        log_returns = np.log(data['Close'] / data['Close'].shift(1))
        realized_vol = log_returns.rolling(window).std() * np.sqrt(252)
        return realized_vol
    
    @staticmethod
    def directional_volatility(data: pd.DataFrame, window: int = 20) -> Tuple[pd.Series, pd.Series]:
        """
        Separate upside and downside volatility
        
        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame with 'Close' column
        window : int
            Rolling window size
            
        Returns:
        --------
        Tuple[pd.Series, pd.Series] : Upside and downside volatility
        """
        returns = data['Close'].pct_change()
        
        upside_returns = returns.where(returns > 0, 0)
        downside_returns = returns.where(returns < 0, 0)
        
        upside_vol = upside_returns.rolling(window).std() * np.sqrt(252)
        downside_vol = downside_returns.rolling(window).std() * np.sqrt(252)
        
        return upside_vol, downside_vol
