# Markowitz Mean-Variance Optimization
"""
This module implements the Markowitz mean-variance optimization algorithm.
"""

import cvxpy as cp
import numpy as np
import pandas as pd

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
        target_return: float | None = None,
        risk_aversion: float = 1.0,
        **kwargs,
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

            if not self._validate_weights(weights):
                raise ValueError(
                    "Computed weights violate the sum-to-one / long-only constraints"
                )

            # Create method-specific output (frontier only if already computed —
            # computing it here would add 50 QP solves to every optimize() call)
            method_specific = {
                "efficient_frontier": self.efficient_frontier_points,
                "method": method,
            }

            return OptimizationResult(
                weights=dict(zip(self.returns.columns, weights, strict=True)),
                performance=performance,
                method_specific=method_specific,
                success=True,
            )

        except Exception as e:
            return OptimizationResult(
                weights=dict.fromkeys(self.returns.columns, 0.0),
                performance={},
                method_specific={"error": str(e)},
                success=False,
                message=f"Optimization failed: {str(e)}",
            )

    def _optimize_max_sharpe(self) -> np.ndarray:
        """Optimize portfolio for maximum Sharpe ratio.

        Direct maximization of ret/risk is not DCP, so use the standard
        Cornuejols-Tütüncü reformulation: minimize y'Σy s.t.
        (mu - rf)'y = 1, y >= 0, then normalize w = y / sum(y).
        """
        n_assets = self.n_assets
        Sigma = self.covariance_matrix.values
        mu = np.asarray(self.returns.mean())
        # Risk-free rate per period (0.02 annual / 252 daily periods)
        rf = 0.02 / 252

        y = cp.Variable(n_assets)
        excess = (mu - rf) @ y

        constraints = [excess == 1, y >= 0]
        problem = cp.Problem(cp.Minimize(cp.quad_form(y, Sigma)), constraints)
        problem.solve()

        if problem.status != cp.OPTIMAL or y.value is None:
            raise RuntimeError(f"Optimization failed to converge: {problem.status}")

        # Clip solver-tolerance negatives before normalizing
        y_val = np.clip(y.value, 0.0, None)
        return y_val / np.sum(y_val)

    def _optimize_min_variance(self) -> np.ndarray:
        """Optimize portfolio for minimum variance."""
        n_assets = self.n_assets
        Sigma = self.covariance_matrix.values

        # Define optimization variables
        weights = cp.Variable(n_assets)

        # Define optimization problem
        risk = cp.quad_form(weights, Sigma)

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

        if problem.status != cp.OPTIMAL or weights.value is None:
            raise RuntimeError(f"Optimization failed to converge: {problem.status}")

        return weights.value

    def _optimize_target_return(
        self, target_return: float, risk_aversion: float = 1.0
    ) -> np.ndarray:
        """Optimize portfolio for a target return with risk aversion."""
        n_assets = self.n_assets
        Sigma = self.covariance_matrix.values
        mu = np.asarray(self.returns.mean())

        # Define optimization variables
        weights = cp.Variable(n_assets)

        # Define optimization problem
        risk = cp.quad_form(weights, Sigma)
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

        if problem.status != cp.OPTIMAL or weights.value is None:
            raise RuntimeError(f"Optimization failed to converge: {problem.status}")

        return weights.value

    def get_efficient_frontier(self, n_points: int = 50) -> dict[str, list[float]]:
        """Calculate the efficient frontier (public API)."""
        if self.efficient_frontier_points is not None:
            return self.efficient_frontier_points

        mu = np.asarray(self.returns.mean())
        min_return = mu.min()
        max_return = mu.max()
        span = max_return - min_return

        # Degenerate case: all assets share (nearly) the same expected return, so
        # the whole feasible set sits on one return level — the frontier is a point.
        if span < 1e-12:
            perf = self._calculate_performance_metrics(self._optimize_min_variance())
            self.efficient_frontier_points = {
                "returns": [perf["expected_return"]],
                "risk": [perf["volatility"]],
                "sharpe_ratios": [perf["sharpe_ratio"]],
            }
            return self.efficient_frontier_points

        # With long-only weights the max portfolio return equals max(mu) exactly;
        # a `ret >= target` constraint pinned at that boundary leaves a measure-zero
        # feasible set, which QP solvers flag infeasible. Back off a hair instead.
        max_target = max_return - 1e-4 * span

        risk_levels = []
        returns_levels = []
        sharpe_ratios = []

        for target_return in np.linspace(min_return, max_target, n_points):
            try:
                weights = self._optimize_target_return(target_return)
            except RuntimeError:
                break  # past the feasible boundary — every later target fails too
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
