import sys
import os

# Add the project root to sys.path to allow running as a script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from portfolio_optimizer.api.models import OptimizationResponse, MarketDataResponse
from portfolio_optimizer.api.endpoints import router as api_router

app = FastAPI(title="Portfolio Optimization API", version="1.0.0")

app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "Portfolio Optimization API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
