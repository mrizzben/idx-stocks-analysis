from requests import get
import pandas as pd
import yfinance

INDEX_LS = ["LQ45", "KOMPAS100"]


class GetIndexKontan:
    def __init__(self, index: str = "KOMPAS100") -> None:
        self.index = index
        self.BASE_URL = "https://www.kontan.co.id/"

    def get_url(self) -> str:
        if self.index in INDEX_LS:
            index_url = f"indeks-{self.index.lower()}"
            return self.BASE_URL + index_url
        else:
            raise ValueError("Index name not found: Only KOMPAS100 or LQ45")

    def get_index_list(self) -> pd.DataFrame:
        url = self.get_url()
        page = get(url)
        df = pd.read_html(page)[0]
        return df
    
class GetStocks: 
    
