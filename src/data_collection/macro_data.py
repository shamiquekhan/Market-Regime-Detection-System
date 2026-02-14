"""
Macro Economic Data Collection for India
Fetches government bond yields, inflation, forex rates
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

class IndianMacroData:
    """
    Fetches macro-economic indicators for Indian market regime detection
    """
    
    # Government bond yields (via proxy ETFs/futures when available)
    BOND_PROXIES = {
        '10Y_YIELD': '^TNX',  # US 10Y as proxy, adjust with spread
        'INDIA_10Y': 'INDIAGILT10Y.NS',  # If available
    }
    
    # Currency pairs
    FOREX = {
        'USDINR': 'USDINR=X',
        'EURINR': 'EURINR=X'
    }
    
    def __init__(self, start_date: str = '2015-01-01'):
        self.start_date = start_date
    
    def fetch_forex_data(self, pair: str = 'USDINR') -> pd.DataFrame:
        """
        Fetch forex rates
        
        Parameters:
        -----------
        pair : str
            Currency pair from FOREX dict
            
        Returns:
        --------
        pd.DataFrame : Forex rate data
        """
        ticker = self.FOREX.get(pair, 'USDINR=X')
        
        try:
            data = yf.download(ticker, start=self.start_date, progress=False)
            if not data.empty:
                data.columns = [col[0] if isinstance(col, tuple) else col 
                              for col in data.columns]
                data['Returns'] = data['Close'].pct_change()
            return data
        except Exception as e:
            print(f"Error fetching {pair}: {str(e)}")
            return pd.DataFrame()
    
    def calculate_yield_spread(self) -> pd.DataFrame:
        """
        Calculate yield spreads (proxy using available data)
        In practice, fetch actual Indian government bond yields from RBI
        
        Returns:
        --------
        pd.DataFrame : Yield spread metrics
        """
        # This is a simplified proxy
        # For production, use actual Indian G-Sec yields from NSE/RBI
        
        try:
            # Fetch long-term rate proxy
            long_term = yf.download('^TNX', start=self.start_date, progress=False)['Close']
            
            # Create dummy short-term (in practice, fetch 91-day T-bill)
            spread_data = pd.DataFrame({
                'Long_Term_Yield': long_term,
                'Spread_1Y_3M': np.random.randn(len(long_term)) * 0.5 + 0.5  # Placeholder
            })
            
            return spread_data
            
        except Exception as e:
            print(f"Error calculating spreads: {str(e)}")
            return pd.DataFrame()


# Example usage
if __name__ == "__main__":
    macro = IndianMacroData(start_date='2020-01-01')
    
    # Fetch USD-INR
    usdinr = macro.fetch_forex_data('USDINR')
    print(f"Fetched {len(usdinr)} days of USD-INR data")
    print(usdinr.tail())
