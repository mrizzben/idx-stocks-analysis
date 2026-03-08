import numpy as np
import pandas as pd
from typing import Optional


class FeatureService:
    """
    Service for extracting features from historical returns data.
    """

    @staticmethod
    def calculate_log_returns(prices_df: pd.DataFrame) -> pd.DataFrame:
        """Calculates log returns from price data."""
        return np.log(prices_df / prices_df.shift(1)).dropna(how="all")

    @staticmethod
    def calculate_daily_movement(
        open_prices: pd.Series, close_prices: pd.Series
    ) -> pd.Series:
        """Calculates daily movement as log(close/open)."""
        return np.log(close_prices / open_prices).fillna(0)

    @staticmethod
    def calculate_exponential_weighted_covariance(
        returns_df: pd.DataFrame, span: int = 300
    ) -> pd.DataFrame:
        """
        Calculates the latest exponential weighted covariance matrix.
        """
        cov = returns_df.ewm(span=span).cov()
        # Returns the latest covariance matrix
        return cov.loc[cov.index.levels[0][-1]]

    @staticmethod
    def calculate_exponential_weighted_correlation(
        returns_df: pd.DataFrame, span: int = 300
    ) -> pd.DataFrame:
        """
        Calculates the latest exponential weighted correlation matrix.
        """
        corr = returns_df.ewm(span=span).corr()
        # Returns the latest correlation matrix
        return corr.loc[corr.index.levels[0][-1]]

    @staticmethod
    def calculate_annualized_metrics(
        returns_df: pd.DataFrame, weights: pd.Series, risk_free_rate: float = 0.02
    ):
        """
        Calculates annualized expected return, volatility, and Sharpe Ratio.
        Assumes 252 trading days.
        """
        portfolio_returns = (returns_df * weights).sum(axis=1)

        avg_return = portfolio_returns.mean() * 252
        volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe_ratio = (
            (avg_return - risk_free_rate) / volatility if volatility != 0 else 0
        )

        return {
            "Expected Return": float(avg_return),
            "Volatility": float(volatility),
            "Sharpe Ratio": float(sharpe_ratio),
        }
