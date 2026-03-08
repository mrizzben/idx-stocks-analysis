import re
from typing import List, Union


def normalize_ticker(ticker: str) -> str:
    """
    Normalizes a ticker symbol.
    If it's a 4-letter alphanumeric string without a suffix, defaults to .JK (IDX).
    Otherwise, returns as is (upper case).
    """
    ticker = ticker.strip().upper()

    # If it's 4 letters and has no dot suffix, append .JK
    if re.match(r"^[A-Z0-9]{4}$", ticker):
        return f"{ticker}.JK"

    return ticker


def normalize_tickers(tickers: Union[List[str], str]) -> List[str]:
    """
    Normalizes a list of tickers or a comma-separated string of tickers.
    """
    if isinstance(tickers, str):
        tickers = [t.strip() for t in tickers.split(",")]

    return [normalize_ticker(t) for t in tickers if t.strip()]
