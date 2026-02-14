"""
NSE/BSE Data Collection Module
Fetches stock data, indices, and market information
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')

class IndianMarketData:
    """
    Comprehensive data fetcher for Indian stock market (NSE/BSE)
    """
    
    # Major Indian indices
    INDICES = {
        'NIFTY50': '^NSEI',
        'SENSEX': '^BSESN',
        'NIFTY_BANK': '^NSEBANK',
        'NIFTY_IT': '^CNXIT',
        'NIFTY_PHARMA': '^CNXPHARMA',
        'NIFTY_AUTO': '^CNXAUTO',
        'NIFTY_FMCG': '^CNXFMCG',
        'NIFTY_MIDCAP': '^NSEMDCP50',
        'NIFTY_SMALLCAP': 'NIFTY_SMLCAP_100.NS'
    }
    
    # Top NSE stocks by market cap
    TOP_STOCKS = [
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 
        'HINDUNILVR.NS', 'ICICIBANK.NS', 'KOTAKBANK.NS', 'SBIN.NS',
        'BHARTIARTL.NS', 'ITC.NS', 'BAJFINANCE.NS', 'ASIANPAINT.NS',
        'LT.NS', 'AXISBANK.NS', 'MARUTI.NS', 'TITAN.NS', 
        'SUNPHARMA.NS', 'WIPRO.NS', 'ULTRACEMCO.NS', 'NESTLEIND.NS'
    ]
    
    def __init__(self, start_date: str = '2015-01-01', end_date: str = None):
        """
        Initialize data collector
        
        Parameters:
        -----------
        start_date : str
            Start date in 'YYYY-MM-DD' format
        end_date : str, optional
            End date in 'YYYY-MM-DD' format (defaults to today)
        """
        self.start_date = start_date
        self.end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        
    def fetch_index_data(self, index_name: str = 'NIFTY50') -> pd.DataFrame:
        """
        Fetch historical data for an Indian index
        
        Parameters:
        -----------
        index_name : str
            Name of the index from INDICES dict
            
        Returns:
        --------
        pd.DataFrame : OHLCV data with datetime index
        """
        ticker = self.INDICES.get(index_name, '^NSEI')
        
        try:
            data = yf.download(
                ticker, 
                start=self.start_date, 
                end=self.end_date,
                progress=False
            )
            
            if data.empty:
                raise ValueError(f"No data found for {index_name}")
            
            # Clean column names
            data.columns = [col[0] if isinstance(col, tuple) else col 
                           for col in data.columns]
            
            # Add useful columns
            data['Returns'] = data['Close'].pct_change()
            data['Log_Returns'] = np.log(data['Close'] / data['Close'].shift(1))
            
            return data
            
        except Exception as e:
            print(f"Error fetching {index_name}: {str(e)}")
            return pd.DataFrame()
    
    def fetch_multiple_stocks(self, tickers: List[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple stocks
        
        Parameters:
        -----------
        tickers : List[str], optional
            List of stock tickers (defaults to TOP_STOCKS)
            
        Returns:
        --------
        Dict[str, pd.DataFrame] : Dictionary of stock data
        """
        tickers = tickers or self.TOP_STOCKS
        
        data_dict = {}
        for ticker in tickers:
            try:
                data = yf.download(
                    ticker,
                    start=self.start_date,
                    end=self.end_date,
                    progress=False
                )
                
                if not data.empty:
                    data.columns = [col[0] if isinstance(col, tuple) else col 
                                  for col in data.columns]
                    data_dict[ticker] = data
                    
            except Exception as e:
                print(f"Failed to fetch {ticker}: {str(e)}")
                continue
        
        return data_dict
    
    def fetch_sector_indices(self) -> pd.DataFrame:
        """
        Fetch all sector indices and combine into single DataFrame
        
        Returns:
        --------
        pd.DataFrame : Combined sector index closing prices
        """
        sector_data = {}
        
        for sector_name, ticker in self.INDICES.items():
            try:
                data = yf.download(
                    ticker,
                    start=self.start_date,
                    end=self.end_date,
                    progress=False
                )['Close']
                
                sector_data[sector_name] = data
                
            except Exception as e:
                print(f"Failed to fetch {sector_name}: {str(e)}")
                continue
        
        return pd.DataFrame(sector_data)
    
    def fetch_intraday_data(self, ticker: str, interval: str = '5m') -> pd.DataFrame:
        """
        Fetch intraday data for real-time regime detection
        
        Parameters:
        -----------
        ticker : str
            Stock ticker
        interval : str
            Data interval ('1m', '5m', '15m', '1h', '1d')
            
        Returns:
        --------
        pd.DataFrame : Intraday OHLCV data
        """
        try:
            # yfinance allows max 7 days for minute data
            data = yf.download(
                ticker,
                period='7d',
                interval=interval,
                progress=False
            )
            
            if not data.empty:
                data.columns = [col[0] if isinstance(col, tuple) else col 
                              for col in data.columns]
            
            return data
            
        except Exception as e:
            print(f"Error fetching intraday data: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def get_india_vix() -> pd.DataFrame:
        """
        Fetch India VIX (Volatility Index)
        
        Returns:
        --------
        pd.DataFrame : India VIX historical data
        """
        try:
            vix = yf.download('^INDIAVIX', period='max', progress=False)
            vix.columns = [col[0] if isinstance(col, tuple) else col 
                          for col in vix.columns]
            return vix
        except:
            return pd.DataFrame()


# Example usage and testing
if __name__ == "__main__":
    # Initialize data collector
    collector = IndianMarketData(start_date='2020-01-01')
    
    # Fetch NIFTY 50 data
    nifty_data = collector.fetch_index_data('NIFTY50')
    print(f"Fetched {len(nifty_data)} days of NIFTY data")
    print(nifty_data.tail())
    
    # Fetch sector indices
    sector_data = collector.fetch_sector_indices()
    print(f"\nFetched {len(sector_data.columns)} sector indices")
    print(sector_data.tail())
    
    # Fetch India VIX
    vix_data = IndianMarketData.get_india_vix()
    print(f"\nFetched {len(vix_data)} days of India VIX data")
