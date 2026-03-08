"""
Unit Tests for Hierarchical Risk Parity (HRP) Optimizer
"""

import pytest
import numpy as np
import pandas as pd
from portfolio_optimizer.core.hrp import HRPOptimizer


def test_hrp_initialization(sample_returns):
    """Test initialization of HRPOptimizer."""
    cov_matrix = sample_returns.cov()
    optimizer = HRPOptimizer(sample_returns, cov_matrix)
    assert optimizer.returns.equals(sample_returns)
    assert optimizer.covariance_matrix.equals(cov_matrix)
    assert optimizer.n_assets == len(sample_returns.columns)


def test_hrp_optimization(sample_returns):
    """Test HRP optimization process."""
    cov_matrix = sample_returns.cov()
    optimizer = HRPOptimizer(sample_returns, cov_matrix)
    result = optimizer.optimize()

    assert result.success is True
    assert isinstance(result.weights, dict)
    assert len(result.weights) == len(sample_returns.columns)
    assert np.isclose(sum(result.weights.values()), 1.0)
    assert all(w >= 0 for w in result.weights.values())


def test_hrp_with_custom_parameters(sample_returns):
    """Test HRP with custom clustering parameters."""
    cov_matrix = sample_returns.cov()
    optimizer = HRPOptimizer(sample_returns, cov_matrix)
    result = optimizer.optimize(n_clusters=2, linkage_method="single")

    assert result.success is True
    assert result.method_specific["n_clusters"] == 2
    assert result.method_specific["linkage_method"] == "single"


def test_hrp_invalid_inputs():
    """Test HRP with invalid inputs."""
    returns = pd.DataFrame(np.random.randn(10, 3))
    # Mismatched covariance matrix
    cov_matrix = pd.DataFrame(np.random.randn(4, 4))

    with pytest.raises(ValueError):
        HRPOptimizer(returns, cov_matrix)
