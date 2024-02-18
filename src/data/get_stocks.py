from requests import get
import pandas as pd
import yfinance as yf 
import requests
from datetime import datetime
from bs4 import BeautifulSoup


INDEX_LS = ["LQ45", "KOMPAS100"]
DATE_FORMAT = "%d/%m/%Y"


class GetIndexKontan:
    """Get list of stocks in index from Kontan.com"""
    def __init__(self, index: str = "KOMPAS100") -> None:
        self.index = index
        self.BASE_URL = "https://www.kontan.co.id/"

    def get_url(self) -> str:
        """Get URL of the lists of stocks from the index.

        Raises:
            ValueError: Stock index is not valid.

        Returns:
            str: URL of the stocks list in the index.
        """
        if self.index in INDEX_LS:
            index_url = f"indeks-{self.index.lower()}"
            return self.BASE_URL + index_url
        else:
            raise ValueError("Index name not found: Only KOMPAS100 or LQ45")

    def get_index_list(self) -> pd.DataFrame:
        """Get the list from the URL and return it as DataFrame

        Returns:
            pd.DataFrame: List of stocks
        """
        url = self.get_url()
        page = get(url, timeout=10)
        df = pd.read_html(page)[0]
        return df

def get_stock_tickers():
    # Get all stock tickers from IDX
    idx_tickers = yf.Tickers('JKSE').tickers

    # Extract the ticker symbols
    stock_tickers = [ticker.ticker for ticker in idx_tickers]

    return stock_tickers

def get_kompas100_tickers():
    # Get the components of Kompas 100 Index
    kompas100 = yf.Tickers('^KOMPAS100').tickers[0]

    # Extract the ticker symbols
    stock_tickers = kompas100.symbols

    return stock_tickers

def get_all_stock_prices(start_date, end_date):
    # Get all stock tickers from IDX
    idx_tickers = yf.Tickers('JKSE').tickers

    stock_prices = pd.DataFrame()

    # Retrieve OHLC prices for each stock ticker
    for ticker in idx_tickers:
        try:
            # Download stock data using yfinance
            stock_data = yf.download(ticker.ticker, start=start_date, end=end_date)

            # Extract OHLC prices
            ohlc_data = stock_data[['Open', 'High', 'Low', 'Close']]

            # Add OHLC data to the DataFrame
            ohlc_data['Ticker'] = ticker.ticker
            stock_prices = stock_prices.append(ohlc_data)
        except:
            # Skip ticker if prices cannot be retrieved
            continue

    return stock_prices

def get_exchange_symbols(exchange):
    # Get all tickers for the specified exchange
    tickers = yf.Tickers(f"{exchange}")

    # Get the symbols from the tickers
    symbols = tickers.tickers

    return [symbol for symbol in symbols]

if __name__ == "__main__":
    # Get all stock symbols from IDX
    idx_symbols = get_exchange_symbols("^JKSE")

    # Print the symbols
    print(idx_symbols)