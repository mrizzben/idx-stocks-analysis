# Markowitz Mean-Variance Optimization
"""
This module implements the Markowitz mean-variance optimization algorithm.
"""

import numpy as np
import pandas as pd
import cvxpy as cp
from typing import Dict, List, Optional, Union, Any
from .base import BaseOptimizer, OptimizationResult


class MarkowitzOptimizer(BaseOptimizer):
    """
    Implementation of the Markowitz Mean-Variance Optimization algorithm.

    This class provides methods to find optimal portfolio weights using the
    mean-variance framework, including minimum variance, maximum Sharpe ratio,
    and target return optimization.
    """

    def __init__(self, returns: pd.DataFrame, covariance_matrix: pd.DataFrame):
        """
        Initialize the Markowitz optimizer.

        Args:
            returns: Historical returns for assets (n_assets × n_periods)
            covariance_matrix: Asset covariance matrix (n_assets × n_assets)
        """
        super().__init__(returns, covariance_matrix)
        self.efficient_frontier_points = None

    def optimize(
        self,
        method: str = "max_sharpe",
        target_return: Optional[float] = None,
        risk_aversion: float = 1.0,
    ) -> OptimizationResult:
        """
        Run Markowitz optimization using the specified method.

        Args:
            method: Optimization method ('max_sharpe', 'min_variance', 'target_return')
            target_return: Target return for 'target_return' optimization
            risk_aversion: Risk aversion parameter for mean-variance optimization

        Returns:
            OptimizationResult: Results of the portfolio optimization
        """
        try:
            if method == "max_sharpe":
                weights = self._optimize_max_sharpe()
            elif method == "min_variance":
                weights = self._optimize_min_variance()
            elif method == "target_return":
                if target_return is None:
                    raise ValueError(
                        "target_return must be provided for target return optimization"
                    )
                weights = self._optimize_target_return(target_return, risk_aversion)
            else:
                raise ValueError(f"Unknown optimization method: {method}")

            # Calculate performance metrics
            performance = self._calculate_performance_metrics(weights)

            # Create method-specific output
            method_specific = {
                "efficient_frontier": self._calculate_efficient_frontier()
                if method != "efficient_frontier"
                else self.efficient_frontier_points,
                "method": method,
            }

            return OptimizationResult(
                weights=dict(zip(self.returns.columns, weights)),
                performance=performance,
                method_specific=method_specific,
                success=True,
            )

        except Exception as e:
            return OptimizationResult(
                weights={asset: 0.0 for asset in self.returns.columns},
                performance={},
                method_specific={"error": str(e)},
                success=False,
                message=f"Optimization failed: {str(e)}",
            )

    def _optimize_max_sharpe(self) -> np.ndarray:
        """Optimize portfolio for maximum Sharpe ratio."""
        n_assets = self.n_assets

        # Define optimization variables
        weights = cp.Variable(n_assets)
        mu = cp.Parameter(n_assets)
        Sigma = cp.Parameter((n_assets, n_assets))

        # Set parameter values
        mu.value = self.returns.mean().values
        # Ensure symmetry for CVXPY
        sigma_val = self.covariance_matrix.values
        Sigma.value = (sigma_val + sigma_val.T) / 2

        # Define optimization problem
        risk = cp.quad_form(weights, cp.psd_wrap(Sigma))
        ret = mu @ weights

        # Mean-variance optimization: Minimize (risk - return)
        # This is a common DCP-compliant proxy for Sharpe maximization
        objective = cp.Minimize(risk - ret)

        # Constraints: fully invested portfolio
        constraints = [
            cp.sum(weights) == 1,
            weights >= 0,  # Long-only positions
        ]

        problem = cp.Problem(objective, constraints)

        # Solve optimization problem
        problem.solve()

        if problem.status != cp.OPTIMAL:
            raise RuntimeError(f"Optimization failed to converge: {problem.status}")

        return weights.value

    def _optimize_min_variance(self) -> np.ndarray:
        """Optimize portfolio for minimum variance."""
        n_assets = self.n_assets

        # Define optimization variables
        weights = cp.Variable(n_assets)
        Sigma = cp.Parameter((n_assets, n_assets))

        # Set parameter values
        sigma_val = self.covariance_matrix.values
        Sigma.value = (sigma_val + sigma_val.T) / 2

        # Define optimization problem
        risk = cp.quad_form(weights, cp.psd_wrap(Sigma))

        # Objective: minimize portfolio variance
        objective = cp.Minimize(risk)

        # Constraints: fully invested portfolio
        constraints = [
            cp.sum(weights) == 1,
            weights >= 0,  # Long-only positions
        ]

        problem = cp.Problem(objective, constraints)

        # Solve optimization problem
        problem.solve()

        if problem.status != cp.OPTIMAL:
            raise RuntimeError(f"Optimization failed to converge: {problem.status}")

        return weights.value

    def _optimize_target_return(
        self, target_return: float, risk_aversion: float = 1.0
    ) -> np.ndarray:
        """Optimize portfolio for a target return with risk aversion."""
        n_assets = self.n_assets

        # Define optimization variables
        weights = cp.Variable(n_assets)
        mu = cp.Parameter(n_assets)
        Sigma = cp.Parameter((n_assets, n_assets))

        # Set parameter values
        mu.value = self.returns.mean().values
        # Ensure symmetry for CVXPY
        sigma_val = self.covariance_matrix.values
        Sigma.value = (sigma_val + sigma_val.T) / 2

        # Define optimization problem
        risk = cp.quad_form(weights, cp.psd_wrap(Sigma))
        ret = mu @ weights

        # Objective: balance between risk and return
        objective = cp.Minimize(risk_aversion * risk - ret)

        # Constraints: target return and fully invested portfolio
        constraints = [
            cp.sum(weights) == 1,
            ret >= target_return,
            weights >= 0,  # Long-only positions
        ]

        problem = cp.Problem(objective, constraints)

        # Solve optimization problem
        problem.solve()

        if problem.status != cp.OPTIMAL:
            raise RuntimeError(f"Optimization failed to converge: {problem.status}")

        return weights.value

    def _calculate_efficient_frontier(
        self, n_points: int = 50
    ) -> Dict[str, List[float]]:
        """Calculate the efficient frontier."""
        if self.efficient_frontier_points is not None:
            return self.efficient_frontier_points

        min_return = self.returns.mean().min()
        max_return = self.returns.mean().max()

        risk_levels = []
        returns_levels = []
        sharpe_ratios = []

        for target_return in np.linspace(min_return, max_return, n_points):
            weights = self._optimize_target_return(target_return)
            perf = self._calculate_performance_metrics(weights)

            risk_levels.append(perf["volatility"])
            returns_levels.append(perf["expected_return"])
            sharpe_ratios.append(perf["sharpe_ratio"])

        self.efficient_frontier_points = {
            "returns": returns_levels,
            "risk": risk_levels,
            "sharpe_ratios": sharpe_ratios,
        }

        return self.efficient_frontier_points
