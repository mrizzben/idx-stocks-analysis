import pandas as pd
import yfinance as yf
import requests
from typing import List, Optional
from portfolio_optimizer.services.utils import normalize_tickers


class GetIndexKontan:
    """Get list of stocks in index from Kontan.com"""

    INDEX_LS = ["LQ45", "KOMPAS100"]

    def __init__(self, index: str = "KOMPAS100") -> None:
        self.index = index.upper()
        self.BASE_URL = "https://www.kontan.co.id/"

    def get_url(self) -> str:
        if self.index in self.INDEX_LS:
            index_url = f"indeks-{self.index.lower()}"
            return self.BASE_URL + index_url
        else:
            raise ValueError("Index name not found: Only KOMPAS100 or LQ45")

    def get_index_list(self) -> pd.DataFrame:
        url = self.get_url()
        page = requests.get(url, timeout=10).text
        # pandas read_html returns a list of DataFrames
        df_list = pd.read_html(page)
        return df_list[0] if df_list else pd.DataFrame()


class IDXDataService:
    """
    Service for fetching and managing Indonesian Stock Market (IDX) data.
    """

    @staticmethod
    def get_index_tickers(index_name: str) -> List[str]:
        """
        Fetches tickers for a given index.
        Currently supports: LQ45, KOMPAS100, IDX30
        """
        index_name = index_name.upper()

        # Try Kontan first for LQ45 and KOMPAS100 as it's often more up-to-date
        if index_name in ["LQ45", "KOMPAS100"]:
            try:
                scraper = GetIndexKontan(index_name)
                df = scraper.get_index_list()
                if not df.empty:
                    # Assuming the first column or a column named 'Kode' contains tickers
                    ticker_col = "Kode" if "Kode" in df.columns else df.columns[0]
                    tickers = df[ticker_col].tolist()
                    return [f"{t}.JK" if not t.endswith(".JK") else t for t in tickers]
            except Exception:
                pass  # Fallback to yfinance or hardcoded

        # Mapping common Indonesian indices to Yahoo Finance symbols
        index_mapping = {
            "LQ45": "^JKLQ45",
            "KOMPAS100": "^JK100",
            "IDX30": "^JKID30",
        }

        symbol = index_mapping.get(index_name)
        if not symbol:
            symbol = "^JKSE"

        try:
            tickers = yf.Tickers(symbol).tickers
            return [t.ticker for t in tickers]
        except Exception:
            # Fallback for demo
            if index_name == "LQ45":
                return [
                    "BBCA.JK",
                    "BBRI.JK",
                    "TLKM.JK",
                    "ASII.JK",
                    "UNVR.JK",
                    "BMRI.JK",
                    "GOTO.JK",
                ]
            return ["BBCA.JK", "TLKM.JK", "ASII.JK"]

    @staticmethod
    def fetch_historical_data(
        tickers: List[str], period: str = "1y", interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetches historical price data for a list of tickers.
        """
        normalized_tickers = normalize_tickers(tickers)
        data = yf.download(
            normalized_tickers, period=period, interval=interval, group_by="ticker"
        )

        # If multiple tickers, yfinance returns multi-index columns
        # We want to extract 'Adj Close' or 'Close' for optimization
        if len(normalized_tickers) > 1:
            close_data = pd.DataFrame()
            for ticker in normalized_tickers:
                if ticker in data.columns.levels[0]:
                    close_data[ticker] = (
                        data[ticker]["Adj Close"]
                        if "Adj Close" in data[ticker]
                        else data[ticker]["Close"]
                    )
            return close_data
        else:
            ticker = normalized_tickers[0]
            return data[["Adj Close"]] if "Adj Close" in data else data[["Close"]]

    @staticmethod
    def calculate_returns(prices_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates log returns from price data.
        """
        import numpy as np

        return np.log(prices_df / prices_df.shift(1)).dropna(how="all")
