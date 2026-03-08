import requests
import os
from typing import List, Dict, Any, Optional


class APIClient:
    BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000") + "/api/v1"

    @staticmethod
    def fetch_market_data(
        tickers: List[str], period: str = "1y"
    ) -> Dict[str, List[float]]:
        response = requests.post(
            f"{APIClient.BASE_URL}/fetch-data",
            json={"tickers": tickers, "period": period},
        )
        response.raise_for_status()
        return response.json()["data"]

    @staticmethod
    def optimize(
        strategy: str,
        returns_data: Optional[Dict[str, List[float]]] = None,
        tickers: Optional[List[str]] = None,
        risk_free_rate: float = 0.02,
    ) -> Dict[str, Any]:
        payload = {
            "strategy": strategy,
            "risk_free_rate": risk_free_rate,
            "returns_data": returns_data,
            "tickers": tickers,
        }
        response = requests.post(f"{APIClient.BASE_URL}/optimize", json=payload)
        response.raise_for_status()
        return response.json()
