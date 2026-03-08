import pytest
import pandas as pd
import numpy as np
from portfolio_optimizer.services.utils import normalize_ticker, normalize_tickers
from portfolio_optimizer.services.data_service import IDXDataService
from portfolio_optimizer.services.feature_service import FeatureService
from portfolio_optimizer.services.portfolio_service import PortfolioService


def test_ticker_normalization():
    assert normalize_ticker("BBCA") == "BBCA.JK"
    assert normalize_ticker("AAPL") == "AAPL.JK"  # 4 letters, defaults to .JK
    assert normalize_ticker("GOOGL") == "GOOGL"  # 5 letters, no .JK
    assert normalize_ticker("BBCA.JK") == "BBCA.JK"
    assert normalize_tickers("BBCA, TLKM") == ["BBCA.JK", "TLKM.JK"]


def test_data_service_calculate_returns():
    df = pd.DataFrame({"A": [100, 101, 102], "B": [200, 198, 202]})
    returns = IDXDataService.calculate_returns(df)
    assert len(returns) == 2
    assert "A" in returns.columns
    assert "B" in returns.columns


def test_feature_service_annualized_metrics():
    # Create some dummy returns
    dates = pd.date_range("2023-01-01", periods=10)
    returns_df = pd.DataFrame(
        {
            "AAPL": np.random.normal(0.001, 0.01, 10),
            "MSFT": np.random.normal(0.001, 0.01, 10),
        },
        index=dates,
    )

    weights = pd.Series({"AAPL": 0.5, "MSFT": 0.5})
    metrics = FeatureService.calculate_annualized_metrics(returns_df, weights)

    assert "Expected Return" in metrics
    assert "Volatility" in metrics
    assert "Sharpe Ratio" in metrics
    assert isinstance(metrics["Sharpe Ratio"], float)


def test_portfolio_service_equal_weight():
    dates = pd.date_range("2023-01-01", periods=10)
    returns_df = pd.DataFrame(
        {
            "A": np.random.normal(0.001, 0.01, 10),
            "B": np.random.normal(0.001, 0.01, 10),
        },
        index=dates,
    )

    result = PortfolioService.optimize(returns_df, method="equal_weight")
    assert result.success
    assert result.weights["A"] == 0.5
    assert result.weights["B"] == 0.5
