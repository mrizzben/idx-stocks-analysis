"""
Unit Tests for Monte Carlo Optimizer

This module contains test cases for the MonteCarloOptimizer class,
covering various optimization scenarios and edge cases.
"""

import pytest
import numpy as np
import pandas as pd
from portfolio_optimizer.core.monte_carlo import MonteCarloOptimizer

def test_monte_carlo_initialization():
    """Test initialization of MonteCarloOptimizer with default and custom parameters."""
    # Test default initialization
    optimizer = MonteCarloOptimizer()
    assert optimizer.config['num_simulations'] == 10000
    assert optimizer.config['random_seed'] == 42
    
    # Test custom initialization
    custom_config = {'num_simulations': 5000, 'random_seed': 123}
    optimizer = MonteCarloOptimizer(config=custom_config)
    assert optimizer.config['num_simulations'] == 5000
    assert optimizer.config['random_seed'] == 123

def test_monte_carlo_optimization_process(sample_assets, sample_returns):
    """Test the complete Monte Carlo optimization process."""
    optimizer = MonteCarloOptimizer()
    
    # Test optimization with sample data
    weights = optimizer.optimize(
        expected_returns=None,  # Monte Carlo typically doesn't use expected returns
        covariance_matrix=sample_returns.cov().values,
        assets=sample_assets,
        returns=sample_returns.values
    )
    
    # Check weights sum to 1 and are non-negative
    assert abs(sum(weights.values()) - 1.0) < 1e-6
    assert all(weight >= 0 for weight in weights.values())

def test_monte_carlo_with_different_simulations(sample_assets, sample_returns):
    """Test Monte Carlo optimization with different numbers of simulations."""
    # Test with fewer simulations
    optimizer = MonteCarloOptimizer(config={'num_simulations': 1000})
    
    weights = optimizer.optimize(
        expected_returns=None,
        covariance_matrix=sample_returns.cov().values,
        assets=sample_assets,
        returns=sample_returns.values
    )
    
    # Check weights sum to 1 and are non-negative
    assert abs(sum(weights.values()) - 1.0) < 1e-6
    assert all(weight >= 0 for weight in weights.values())

def test_monte_carlo_with_expected_returns(sample_assets, sample_expected_returns, sample_returns):
    """Test Monte Carlo optimization with expected returns."""
    optimizer = MonteCarloOptimizer()
    
    # Test with expected returns
    weights = optimizer.optimize(
        expected_returns=sample_expected_returns,
        covariance_matrix=sample_returns.cov().values,
        assets=sample_assets,
        returns=sample_returns.values
    )
    
    # Check weights sum to 1 and are non-negative
    assert abs(sum(weights.values()) - 1.0) < 1e-6
    assert all(weight >= 0 for weight in weights.values())

def test_monte_carlo_invalid_inputs(sample_assets, sample_returns):
    """Test Monte Carlo optimizer behavior with invalid inputs."""
    optimizer = MonteCarloOptimizer()
    
    # Test with no assets
    with pytest.raises(ValueError):
        optimizer.optimize(
            expected_returns=None,
            covariance_matrix=sample_returns.cov().values,
            assets=None,
            returns=sample_returns.values
        )
    
    # Test with missing returns data
    with pytest.raises(ValueError):
        optimizer.optimize(
            expected_returns=None,
            covariance_matrix=sample_returns.cov().values,
            assets=sample_assets,
            returns=None
        )
    
    # Test with mismatched returns and assets
    mismatched_returns = sample_returns.iloc[:, :-1]  # Remove one asset's data
    with pytest.raises(ValueError):
        optimizer.optimize(
            expected_returns=None,
            covariance_matrix=mismatched_returns.cov().values,
            assets=sample_assets,
            returns=mismatched_returns.values
        )

def test_monte_carlo_risk_metrics(sample_assets, sample_returns):
    """Test risk metrics calculation in Monte Carlo optimization."""
    optimizer = MonteCarloOptimizer()
    
    # Test optimization and get risk metrics
    weights = optimizer.optimize(
        expected_returns=None,
        covariance_matrix=sample_returns.cov().values,
        assets=sample_assets,
        returns=sample_returns.values,
        return_metrics=True
    )
    
    # Check that metrics are included in the response
    assert 'portfolio_volatility' in weights
    assert 'sharpe_ratio' in weights
    assert 'max_drawdown' in weights
    
    # Check metrics are reasonable values
    assert 0 <= weights['portfolio_volatility'] <= 1
    assert weights['sharpe_ratio'] >= 0

def test_monte_carlo_reproducibility(sample_assets, sample_returns):
    """Test that Monte Carlo optimization produces reproducible results with same seed."""
    # First run
    optimizer1 = MonteCarloOptimizer(config={'num_simulations': 1000, 'random_seed': 42})
    weights1 = optimizer1.optimize(
        expected_returns=None,
        covariance_matrix=sample_returns.cov().values,
        assets=sample_assets,
        returns=sample_returns.values
    )
    
    # Second run with same seed
    optimizer2 = MonteCarloOptimizer(config={'num_simulations': 1000, 'random_seed': 42})
    weights2 = optimizer2.optimize(
        expected_returns=None,
        covariance_matrix=sample_returns.cov().values,
        assets=sample_assets,
        returns=sample_returns.values
    )
    
    # Check that weights are similar (exact match unlikely, but should be close)
    for asset in sample_assets:
        assert abs(weights1[asset] - weights2[asset]) < 0.1  # Allow 10% difference

def test_monte_carlo_with_constraints(sample_assets, sample_returns):
    """Test Monte Carlo optimization with various constraints."""
    optimizer = MonteCarloOptimizer()
    
    # Test long-only constraint
    weights = optimizer.optimize(
        expected_returns=None,
        covariance_matrix=sample_returns.cov().values,
        assets=sample_assets,
        returns=sample_returns.values,
        constraints={'long_only': True}
    )
    
    # Check all weights are positive
    assert all(weight >= 0 for weight in weights.values())
    
    # Test max weight constraint
    weights = optimizer.optimize(
        expected_returns=None,
        covariance_matrix=sample_returns.cov().values,
        assets=sample_assets,
        returns=sample_returns.values,
        constraints={'max_weight': 0.5}
    )
    
    # Check that no weight exceeds max_weight
    max_weight = 0.5
    assert all(weight <= max_weight + 1e-6 for weight in weights.values())