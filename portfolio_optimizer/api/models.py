from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class MarketDataRequest(BaseModel):
    tickers: List[str]
    period: str = "1y"
    interval: str = "1d"


class OptimizationRequest(BaseModel):
    strategy: str = Field(
        ..., description="Strategy name, e.g., 'hrp' or 'equal_weight'"
    )
    risk_free_rate: float = 0.02
    lookback_period: str = "1y"
    tickers: Optional[List[str]] = None
    returns_data: Optional[Dict[str, List[float]]] = None


class OptimizationPerformance(BaseModel):
    expected_return: float = Field(..., alias="Expected Return")
    volatility: float = Field(..., alias="Volatility")
    sharpe_ratio: float = Field(..., alias="Sharpe Ratio")

    class Config:
        populate_by_name = True


class OptimizationResultData(BaseModel):
    weights: Dict[str, float]
    performance: Dict[str, float]
    success: bool
    message: Optional[str] = None
    dendrogram_data: Optional[List[Any]] = None


class OptimizationResponse(BaseModel):
    status: str
    data: Optional[OptimizationResultData] = None
    message: Optional[str] = None


class MarketDataResponse(BaseModel):
    status: str
    data: Dict[str, List[float]]
    message: Optional[str] = None
