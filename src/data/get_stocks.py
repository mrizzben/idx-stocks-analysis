from requests import get
import pandas as pd
import yfinance as yf 

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
        # Use page.text or page.content for read_html
        df = pd.read_html(page.text)[0]
        return df

def get_stock_tickers():
    # Get all stock tickers from IDX
    # Note: This is an approximation/placeholder as yfinance does not scrape all IDX tickers via ^JKSE
    idx_tickers = yf.Tickers("^JKSE").tickers

    # Extract the ticker symbols
    # yfinance returns a dict of tickers
    stock_tickers = list(idx_tickers.keys())

    return stock_tickers

def get_kompas100_tickers():
    # Get the components of Kompas 100 Index
    # Note: yfinance does not provide components of ^KOMPAS100 directly.
    # This function is retained for structure but may not return components.
    # It attempts to return the index ticker itself as a fallback.
    kompas100_tickers = yf.Tickers("^KOMPAS100").tickers

    # Returning keys (tickers) as list
    stock_tickers = list(kompas100_tickers.keys())

    return stock_tickers

def get_all_stock_prices(start_date, end_date):
    # Get all stock tickers from IDX
    # This uses the same logic as get_stock_tickers, so it only gets ^JKSE in practice with current yfinance behavior
    idx_tickers = yf.Tickers("^JKSE").tickers

    stock_prices_list = []

    # Retrieve OHLC prices for each stock ticker
    for ticker_symbol, ticker_obj in idx_tickers.items():
        try:
            # Download stock data using yfinance
            stock_data = yf.download(ticker_symbol, start=start_date, end=end_date)

            # Extract OHLC prices
            ohlc_data = stock_data[['Open', 'High', 'Low', 'Close']].copy()

            # Add OHLC data to the DataFrame
            ohlc_data['Ticker'] = ticker_symbol
            stock_prices_list.append(ohlc_data)
        except:
            # Skip ticker if prices cannot be retrieved
            continue

    if stock_prices_list:
        stock_prices = pd.concat(stock_prices_list)
    else:
        stock_prices = pd.DataFrame()

    return stock_prices

def get_exchange_symbols(exchange):
    # Get all tickers for the specified exchange
    tickers = yf.Tickers(f"{exchange}")

    # Get the symbols from the tickers
    # yfinance returns a dict
    symbols = list(tickers.tickers.keys())

    return symbols

if __name__ == "__main__":
    # Get all stock symbols from IDX
    idx_symbols = get_exchange_symbols("^JKSE")

    # Print the symbols
    print(idx_symbols)
