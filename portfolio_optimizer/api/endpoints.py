from fastapi import APIRouter, HTTPException
from portfolio_optimizer.api.models import (
    MarketDataRequest,
    MarketDataResponse,
    OptimizationRequest,
    OptimizationResponse,
    OptimizationResultData,
)
from portfolio_optimizer.services.data_service import IDXDataService
from portfolio_optimizer.services.portfolio_service import PortfolioService
import pandas as pd

router = APIRouter(prefix="/api/v1")


@router.post("/fetch-data", response_model=MarketDataResponse)
async def fetch_data(request: MarketDataRequest):
    try:
        prices_df = IDXDataService.fetch_historical_data(
            request.tickers, period=request.period, interval=request.interval
        )
        returns_df = IDXDataService.calculate_returns(prices_df)

        # Convert to dictionary for response
        data_dict = returns_df.to_dict(orient="list")

        return MarketDataResponse(status="success", data=data_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_portfolio(request: OptimizationRequest):
    try:
        if request.returns_data:
            returns_df = pd.DataFrame(request.returns_data)
        elif request.tickers:
            prices_df = IDXDataService.fetch_historical_data(
                request.tickers, period=request.lookback_period
            )
            returns_df = IDXDataService.calculate_returns(prices_df)
        else:
            raise HTTPException(
                status_code=400,
                detail="Either tickers or returns_data must be provided",
            )

        result = PortfolioService.optimize(
            returns_df, method=request.strategy, risk_free_rate=request.risk_free_rate
        )

        result_data = OptimizationResultData(
            weights=result.weights,
            performance=result.performance,
            success=result.success,
            message=result.message,
            dendrogram_data=result.method_specific.get("linkage_matrix")
            if result.success
            else None,
        )

        return OptimizationResponse(status="success", data=result_data)
    except Exception as e:
        return OptimizationResponse(status="error", message=str(e))
