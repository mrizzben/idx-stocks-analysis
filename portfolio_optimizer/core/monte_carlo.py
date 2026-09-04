# Monte Carlo Portfolio Optimization
"""
This module implements the Monte Carlo simulation-based portfolio optimization algorithm.
"""


import numpy as np
import pandas as pd

from .base import BaseOptimizer, OptimizationResult


class MonteCarloOptimizer(BaseOptimizer):
    """
    Implementation of Monte Carlo simulation-based portfolio optimization.

    This class generates random portfolio weights and evaluates their performance
    to find near-optimal solutions based on different criteria.
    """

    def __init__(self, returns: pd.DataFrame, covariance_matrix: pd.DataFrame):
        """
        Initialize the Monte Carlo optimizer.

        Args:
            returns: Historical returns for assets (n_assets × n_periods)
            covariance_matrix: Asset covariance matrix (n_assets × n_assets)
        """
        super().__init__(returns, covariance_matrix)
        self.simulation_results = None

    def optimize(self, n_simulations: int = 10000,
                optimization_criterion: str = 'sharpe_ratio',
                target_return: float | None = None,
                target_volatility: float | None = None, **kwargs) -> OptimizationResult:
        """
        Run Monte Carlo optimization.

        Args:
            n_simulations: Number of random portfolios to simulate
            optimization_criterion: Criterion to select optimal portfolio
                                   ('sharpe_ratio', 'return', 'risk', 'target_return', 'target_volatility')
            target_return: Target return for optimization (if applicable)
            target_volatility: Target volatility for optimization (if applicable)

        Returns:
            OptimizationResult: Results of the portfolio optimization
        """
        try:
            # Generate random portfolios
            portfolio_weights, portfolio_metrics = self._generate_portfolios(n_simulations)

            # Find optimal portfolio based on selected criterion
            optimal_idx = self._find_optimal_portfolio(
                portfolio_metrics,
                optimization_criterion,
                target_return,
                target_volatility
            )

            # Store simulation results
            self.simulation_results = {
                'weights': portfolio_weights,
                'metrics': portfolio_metrics,
                'optimal_idx': optimal_idx
            }

            # Get optimal weights and metrics
            optimal_weights = portfolio_weights[optimal_idx]
            optimal_metrics = portfolio_metrics[optimal_idx]

            # Create method-specific output
            method_specific = {
                'efficient_frontier': self._extract_efficient_frontier(portfolio_metrics),
                'optimization_criterion': optimization_criterion,
                'n_simulations': n_simulations,
                'all_metrics': portfolio_metrics.tolist()
            }

            return OptimizationResult(
                weights=dict(zip(self.returns.columns, optimal_weights)),
                performance=optimal_metrics,
                method_specific=method_specific,
                success=True
            )

        except Exception as e:
            return OptimizationResult(
                weights=dict.fromkeys(self.returns.columns, 0.0),
                performance={},
                method_specific={'error': str(e)},
                success=False,
                message=f"Optimization failed: {str(e)}"
            )

    def _generate_portfolios(self, n_simulations: int) -> tuple:
        """Generate random portfolios and calculate their performance metrics."""
        n_assets = self.n_assets

        # Initialize arrays to store results
        portfolio_weights = np.zeros((n_simulations, n_assets))
        portfolio_metrics = np.zeros(n_simulations, dtype=[
            ('return', float),
            ('volatility', float),
            ('sharpe_ratio', float)
        ])

        # Generate random portfolios
        for i in range(n_simulations):
            # Generate random weights and normalize to sum to 1
            weights = np.random.random(n_assets)
            weights /= np.sum(weights)

            # Store weights
            portfolio_weights[i] = weights

            # Calculate performance metrics
            expected_return = np.sum(self.returns.mean() * weights)
            volatility = np.sqrt(np.dot(weights.T, np.dot(self.covariance_matrix, weights)))
            sharpe_ratio = (expected_return - 0.02) / volatility if volatility > 0 else 0

            # Store metrics
            portfolio_metrics[i] = (expected_return, volatility, sharpe_ratio)

        return portfolio_weights, portfolio_metrics

    def _find_optimal_portfolio(self, metrics, criterion, target_return, target_volatility):
        """Find the optimal portfolio based on the selected criterion."""
        if criterion == 'sharpe_ratio':
            # Find portfolio with highest Sharpe ratio
            return np.argmax(metrics['sharpe_ratio'])
        elif criterion == 'return':
            # Find portfolio with highest return
            return np.argmax(metrics['return'])
        elif criterion == 'risk':
            # Find portfolio with lowest volatility
            return np.argmin(metrics['volatility'])
        elif criterion == 'target_return':
            if target_return is None:
                raise ValueError("target_return must be provided for target return optimization")
            # Find portfolio with closest return to target (with penalty for underperformance)
            return np.argmin(np.abs(metrics['return'] - target_return) +
                            0.1 * (metrics['return'] < target_return))
        elif criterion == 'target_volatility':
            if target_volatility is None:
                raise ValueError("target_volatility must be provided for target volatility optimization")
            # Find portfolio with closest volatility to target
            return np.argmin(np.abs(metrics['volatility'] - target_volatility))
        else:
            raise ValueError(f"Unknown optimization criterion: {criterion}")

    def _extract_efficient_frontier(self, metrics):
        """Extract the efficient frontier from simulated portfolios."""
        # Sort portfolios by Sharpe ratio
        sorted_indices = np.argsort(metrics['sharpe_ratio'])[::-1]

        # Initialize efficient frontier
        efficient_frontier = []

        # Find the maximum return for each level of volatility
        min_volatility = float('inf')
        for idx in sorted_indices:
            if metrics['volatility'][idx] < min_volatility:
                efficient_frontier.append({
                    'return': float(metrics['return'][idx]),
                    'volatility': float(metrics['volatility'][idx]),
                    'sharpe_ratio': float(metrics['sharpe_ratio'][idx])
                })
                min_volatility = metrics['volatility'][idx]

        return efficient_frontier

