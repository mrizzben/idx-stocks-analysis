import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from portfolio_optimizer.core.hrp import HierarchicalRiskParityOptimizer
from portfolio_optimizer.core.markowitz import MarkowitzOptimizer
from portfolio_optimizer.core.monte_carlo import MonteCarloOptimizer
from portfolio_optimizer.core.base import OptimizationResult
from portfolio_optimizer.services.feature_service import FeatureService


class PortfolioService:
    """
    Unified service for portfolio optimization.
    """

    @staticmethod
    def optimize(
        returns_df: pd.DataFrame,
        method: str = "hrp",
        risk_free_rate: float = 0.02,
        **kwargs,
    ) -> OptimizationResult:
        """
        Main entry point for portfolio optimization.
        """
        method = method.lower().replace(" ", "_")
        if method == "hrp":
            return PortfolioService._optimize_hrp(returns_df, risk_free_rate, **kwargs)
        elif method == "markowitz":
            return PortfolioService._optimize_markowitz(
                returns_df, risk_free_rate, **kwargs
            )
        elif method == "monte_carlo":
            return PortfolioService._optimize_monte_carlo(
                returns_df, risk_free_rate, **kwargs
            )
        elif method == "equal_weight":
            return PortfolioService._optimize_equal_weight(returns_df, risk_free_rate)
        else:
            raise ValueError(f"Unsupported optimization method: {method}")

    @staticmethod
    def _optimize_hrp(
        returns_df: pd.DataFrame, risk_free_rate: float, **kwargs
    ) -> OptimizationResult:
        """Runs HRP optimization."""
        cov_matrix = FeatureService.calculate_exponential_weighted_covariance(
            returns_df
        )
        optimizer = HierarchicalRiskParityOptimizer(returns_df, cov_matrix)
        result = optimizer.optimize(**kwargs)
        return PortfolioService._post_process_result(result, returns_df, risk_free_rate)

    @staticmethod
    def _optimize_markowitz(
        returns_df: pd.DataFrame, risk_free_rate: float, **kwargs
    ) -> OptimizationResult:
        """Runs Markowitz optimization."""
        cov_matrix = FeatureService.calculate_exponential_weighted_covariance(
            returns_df
        )
        optimizer = MarkowitzOptimizer(returns_df, cov_matrix)
        result = optimizer.optimize(**kwargs)
        return PortfolioService._post_process_result(result, returns_df, risk_free_rate)

    @staticmethod
    def _optimize_monte_carlo(
        returns_df: pd.DataFrame, risk_free_rate: float, **kwargs
    ) -> OptimizationResult:
        """Runs Monte Carlo optimization."""
        cov_matrix = FeatureService.calculate_exponential_weighted_covariance(
            returns_df
        )
        optimizer = MonteCarloOptimizer(returns_df, cov_matrix)
        result = optimizer.optimize(**kwargs)
        return PortfolioService._post_process_result(result, returns_df, risk_free_rate)

    @staticmethod
    def _optimize_equal_weight(
        returns_df: pd.DataFrame, risk_free_rate: float
    ) -> OptimizationResult:
        """Runs Equal Weight optimization."""
        n_assets = len(returns_df.columns)
        weights = {ticker: 1.0 / n_assets for ticker in returns_df.columns}
        result = OptimizationResult(
            weights=weights,
            performance={},
            method_specific={"method": "equal_weight"},
            success=True,
        )
        return PortfolioService._post_process_result(result, returns_df, risk_free_rate)

    @staticmethod
    def _post_process_result(
        result: OptimizationResult, returns_df: pd.DataFrame, risk_free_rate: float
    ) -> OptimizationResult:
        """Recalculates performance metrics for consistency."""
        if result.success:
            weights_series = pd.Series(result.weights)
            performance = FeatureService.calculate_annualized_metrics(
                returns_df, weights_series, risk_free_rate
            )
            result.performance = performance
        return result
