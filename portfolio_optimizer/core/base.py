# Base classes for portfolio optimization algorithms
"""
This module contains the base classes and core data structures for portfolio optimization algorithms.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class OptimizationResult:
    """
    Data class to store portfolio optimization results.

    Attributes:
        weights (Dict[str, float]): Portfolio weights for each asset
        performance (Dict[str, float]): Performance metrics (return, volatility, Sharpe ratio)
        method_specific (Dict[str, Any]): Method-specific output (e.g., efficient frontier)
        success (bool): Optimization success status
        message (str): Description of optimization outcome
    """

    weights: dict[str, float]
    performance: dict[str, float]
    method_specific: dict[str, Any] | None = None
    success: bool = True
    message: str = "Optimization completed successfully"


class BaseOptimizer(ABC):
    """
    Abstract base class for portfolio optimization algorithms.

    This class defines the common interface and core functionality
    for all portfolio optimization methods.
    """

    def __init__(self, returns: pd.DataFrame, covariance_matrix: pd.DataFrame):
        """
        Initialize the optimizer with basic portfolio data.

        Args:
            returns: Historical returns for assets (n_assets × n_periods)
            covariance_matrix: Asset covariance matrix (n_assets × n_assets)
        """
        self.returns = returns
        self.covariance_matrix = covariance_matrix
        self.n_assets = len(returns.columns)
        self._validate_inputs()

    def _validate_inputs(self):
        """Validate input data consistency and quality."""
        # Check covariance matrix dimensions match the returns columns
        if self.covariance_matrix.shape != (self.n_assets, self.n_assets):
            raise ValueError(
                f"Covariance matrix shape {self.covariance_matrix.shape} does not match "
                f"number of assets ({self.n_assets})"
            )

        # Check for missing values
        if self.returns.isnull().values.any():
            raise ValueError("Returns data contains missing values")

        # Check for valid covariance matrix
        if not self._is_valid_covariance_matrix(self.covariance_matrix):
            raise ValueError(
                "Invalid covariance matrix: must be symmetric and positive semi-definite"
            )

    def _is_valid_covariance_matrix(self, matrix: pd.DataFrame) -> bool:
        """Check if matrix is symmetric and positive semi-definite."""
        # Check symmetry
        if not np.allclose(matrix, matrix.T):
            return False

        # Check positive semi-definiteness
        try:
            np.linalg.cholesky(matrix + 1e-10 * np.eye(matrix.shape[0]))
            return True
        except np.linalg.LinAlgError:
            return False

    def _validate_weights(self, weights: np.ndarray) -> bool:
        """Validate portfolio weights meet constraints."""
        # Check weights sum to 1 (within tolerance)
        if not np.isclose(np.sum(weights), 1.0, atol=1e-6):
            return False

        # Check weights are within [0, 1] range (with solver tolerance)
        if np.any(weights < -1e-8) or np.any(weights > 1 + 1e-8):
            return False

        return True

    def _calculate_performance_metrics(self, weights: np.ndarray) -> dict[str, float]:
        """Calculate portfolio performance metrics.

        Contract: ``returns`` holds per-period (daily) returns, while
        ``covariance_matrix`` is ANNUALIZED. Expected return is therefore
        annualized here (x252) so return, volatility and Sharpe share one scale.
        """
        # Annualized expected return (daily mean x 252 trading days)
        expected_return = float(np.sum(self.returns.mean() * weights)) * 252

        # Calculate portfolio volatility (already annualized via covariance_matrix)
        volatility = np.sqrt(np.dot(weights.T, np.dot(self.covariance_matrix, weights)))

        # Calculate Sharpe ratio (assuming risk-free rate of 0.02)
        sharpe_ratio = (expected_return - 0.02) / volatility if volatility > 0 else 0

        return {
            "expected_return": float(expected_return),
            "volatility": float(volatility),
            "sharpe_ratio": float(sharpe_ratio),
        }

    @abstractmethod
    def optimize(self, **kwargs) -> OptimizationResult:
        """
        Run the optimization algorithm.

        Returns:
            OptimizationResult: Results of the portfolio optimization
        """
