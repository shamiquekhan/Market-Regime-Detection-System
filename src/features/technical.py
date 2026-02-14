"""
Technical Indicators for Regime Detection
Computes returns, volatility, momentum, and other features
"""

import pandas as pd
import numpy as np
from typing import List, Tuple
import warnings
warnings.filterwarnings('ignore')

class TechnicalFeatures:
    """
    Compute technical indicators for regime detection
    """
    
    @staticmethod
    def compute_returns(data: pd.DataFrame, periods: List[int] = [1, 5, 21, 63]) -> pd.DataFrame:
        """
        Compute multi-period returns
        
        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame with 'Close' column
        periods : List[int]
            List of lookback periods (default: daily, weekly, monthly, quarterly)
            
        Returns:
        --------
        pd.DataFrame : DataFrame with return columns
        """
        df = data.copy()
        
        for period in periods:
            df[f'Return_{period}d'] = df['Close'].pct_change(period)
            df[f'Log_Return_{period}d'] = np.log(df['Close'] / df['Close'].shift(period))
        
        return df
    
    @staticmethod
    def compute_volatility(data: pd.DataFrame, windows: List[int] = [5, 21, 63]) -> pd.DataFrame:
        """
        Compute rolling volatility measures
        
        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame with return columns
        windows : List[int]
            Rolling window sizes
            
        Returns:
        --------
        pd.DataFrame : DataFrame with volatility columns
        """
        df = data.copy()
        
        if 'Log_Returns' not in df.columns:
            df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        for window in windows:
            # Standard deviation of log returns
            df[f'Volatility_{window}d'] = df['Log_Returns'].rolling(window).std() * np.sqrt(252)
            
            # Parkinson volatility (uses High-Low range)
            if 'High' in df.columns and 'Low' in df.columns:
                df[f'Parkinson_Vol_{window}d'] = np.sqrt(
                    (1 / (4 * np.log(2))) * 
                    ((np.log(df['High'] / df['Low'])) ** 2).rolling(window).mean()
                ) * np.sqrt(252)
        
        return df
    
    @staticmethod
    def compute_momentum(data: pd.DataFrame, periods: List[int] = [14, 28, 50]) -> pd.DataFrame:
        """
        Compute momentum indicators
        
        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame with 'Close' column
        periods : List[int]
            Lookback periods for momentum
            
        Returns:
        --------
        pd.DataFrame : DataFrame with momentum columns
        """
        df = data.copy()
        
        for period in periods:
            # Rate of Change (ROC)
            df[f'ROC_{period}'] = ((df['Close'] - df['Close'].shift(period)) / 
                                   df['Close'].shift(period)) * 100
            
            # Relative Strength Index (RSI)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            df[f'RSI_{period}'] = 100 - (100 / (1 + rs))
        
        return df
    
    @staticmethod
    def compute_moving_averages(data: pd.DataFrame, windows: List[int] = [20, 50, 200]) -> pd.DataFrame:
        """
        Compute moving averages and crossovers
        
        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame with 'Close' column
        windows : List[int]
            Moving average window sizes
            
        Returns:
        --------
        pd.DataFrame : DataFrame with MA columns
        """
        df = data.copy()
        
        for window in windows:
            df[f'SMA_{window}'] = df['Close'].rolling(window).mean()
            df[f'EMA_{window}'] = df['Close'].ewm(span=window, adjust=False).mean()
        
        # MA crossover signals
        if len(windows) >= 2:
            df['MA_Crossover_Short_Long'] = (df[f'SMA_{windows[0]}'] > df[f'SMA_{windows[1]}']).astype(int)
        
        return df
    
    @staticmethod
    def compute_bollinger_bands(data: pd.DataFrame, window: int = 20, num_std: float = 2.0) -> pd.DataFrame:
        """
        Compute Bollinger Bands
        
        Parameters:
        -----------
        data : pd.DataFrame
            DataFrame with 'Close' column
        window : int
            Rolling window size
        num_std : float
            Number of standard deviations
            
        Returns:
        --------
        pd.DataFrame : DataFrame with Bollinger Band columns
        """
        df = data.copy()
        
        df['BB_Middle'] = df['Close'].rolling(window).mean()
        rolling_std = df['Close'].rolling(window).std()
        df['BB_Upper'] = df['BB_Middle'] + (rolling_std * num_std)
        df['BB_Lower'] = df['BB_Middle'] - (rolling_std * num_std)
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        return df
    
    @staticmethod
    def compute_regime_features(data: pd.DataFrame) -> pd.DataFrame:
        """
        Compute comprehensive feature set for regime detection
        
        Parameters:
        -----------
        data : pd.DataFrame
            Raw OHLCV data
            
        Returns:
        --------
        pd.DataFrame : Fully featured dataset
        """
        df = data.copy()
        
        # Returns
        df = TechnicalFeatures.compute_returns(df, periods=[1, 5, 21, 63])
        
        # Volatility
        df = TechnicalFeatures.compute_volatility(df, windows=[5, 21, 63])
        
        # Momentum
        df = TechnicalFeatures.compute_momentum(df, periods=[14, 28])
        
        # Moving averages
        df = TechnicalFeatures.compute_moving_averages(df, windows=[20, 50, 200])
        
        # Bollinger Bands
        df = TechnicalFeatures.compute_bollinger_bands(df)
        
        # Volume features
        if 'Volume' in df.columns:
            df['Volume_MA_20'] = df['Volume'].rolling(20).mean()
            df['Volume_Ratio'] = df['Volume'] / df['Volume_MA_20']
        
        # Trend strength
        if 'Close' in df.columns:
            df['Trend_Strength'] = (df['Close'] - df['Close'].rolling(50).min()) / \
                                   (df['Close'].rolling(50).max() - df['Close'].rolling(50).min())
        
        # Dropna for training
        df = df.dropna()
        
        return df


# Example usage
if __name__ == "__main__":
    # Test with sample data
    from src.data_collection.nse_data import IndianMarketData
    
    collector = IndianMarketData(start_date='2020-01-01')
    nifty_data = collector.fetch_index_data('NIFTY50')
    
    # Compute features
    featured_data = TechnicalFeatures.compute_regime_features(nifty_data)
    
    print(f"Original columns: {len(nifty_data.columns)}")
    print(f"Featured columns: {len(featured_data.columns)}")
    print(f"\nFeature columns:\n{featured_data.columns.tolist()}")
    print(f"\nSample data:\n{featured_data.tail()}")
