"""
Unit Tests for Markowitz Optimizer

This module contains test cases for the MarkowitzOptimizer class,
covering various optimization scenarios and edge cases.
"""

import pytest
import numpy as np
import pandas as pd
from portfolio_optimizer.core.markowitz import MarkowitzOptimizer

def test_markowitz_initialization():
    """Test initialization of MarkowitzOptimizer with default and custom parameters."""
    # Test default initialization
    optimizer = MarkowitzOptimizer()
    assert optimizer.config['solver'] == 'SLSQP'
    assert optimizer.config['risk_aversion'] == 1.0
    
    # Test custom initialization
    custom_config = {'solver': 'Nelder-Mead', 'risk_aversion': 2.5}
    optimizer = MarkowitzOptimizer(config=custom_config)
    assert optimizer.config['solver'] == 'Nelder-Mead'
    assert optimizer.config['risk_aversion'] == 2.5

def test_mean_variance_optimization(sample_assets, sample_expected_returns, sample_covariance_matrix):
    """Test basic mean-variance optimization with expected returns and covariance matrix."""
    optimizer = MarkowitzOptimizer()
    
    # Test minimum variance portfolio
    weights = optimizer.optimize(
        expected_returns=None,  # Should use minimum variance
        covariance_matrix=sample_covariance_matrix,
        assets=sample_assets
    )
    
    # Check weights sum to 1 and are non-negative
    assert abs(sum(weights.values()) - 1.0) < 1e-6
    assert all(weight >= 0 for weight in weights.values())

def test_mean_variance_optimization_with_expected_returns(sample_assets, sample_expected_returns, sample_covariance_matrix):
    """Test mean-variance optimization with expected returns."""
    optimizer = MarkowitzOptimizer()
    
    # Test with expected returns
    weights = optimizer.optimize(
        expected_returns=sample_expected_returns,
        covariance_matrix=sample_covariance_matrix,
        assets=sample_assets
    )
    
    # Check weights sum to 1 and are non-negative
    assert abs(sum(weights.values()) - 1.0) < 1e-6
    assert all(weight >= 0 for weight in weights.values())

def test_optimization_with_constraints(sample_assets, sample_expected_returns, sample_covariance_matrix):
    """Test optimization with various constraints."""
    optimizer = MarkowitzOptimizer()
    
    # Test long-only constraint
    weights = optimizer.optimize(
        expected_returns=sample_expected_returns,
        covariance_matrix=sample_covariance_matrix,
        assets=sample_assets,
        constraints={'long_only': True}
    )
    
    # Test max weight constraint
    weights = optimizer.optimize(
        expected_returns=sample_expected_returns,
        covariance_matrix=sample_covariance_matrix,
        assets=sample_assets,
        constraints={'max_weight': 0.5}
    )
    
    # Check that no weight exceeds max_weight
    max_weight = 0.5
    assert all(weight <= max_weight + 1e-6 for weight in weights.values())

def test_invalid_inputs(sample_assets, sample_expected_returns, sample_covariance_matrix):
    """Test optimizer behavior with invalid inputs."""
    optimizer = MarkowitzOptimizer()
    
    # Test with no assets
    with pytest.raises(ValueError):
        optimizer.optimize(
            expected_returns=sample_expected_returns,
            covariance_matrix=sample_covariance_matrix,
            assets=None
        )
    
    # Test with mismatched expected returns and assets
    mismatched_returns = {**sample_expected_returns, 'NEW_ASSET': 0.1}
    with pytest.raises(ValueError):
        optimizer.optimize(
            expected_returns=mismatched_returns,
            covariance_matrix=sample_covariance_matrix,
            assets=sample_assets
        )

def test_risk_parity_optimization(sample_assets, sample_covariance_matrix):
    """Test risk parity optimization."""
    optimizer = MarkowitzOptimizer()
    
    weights = optimizer.optimize(
        expected_returns=None,
        covariance_matrix=sample_covariance_matrix,
        assets=sample_assets,
        optimization_type='risk_parity'
    )
    
    # Check weights sum to 1 and are non-negative
    assert abs(sum(weights.values()) - 1.0) < 1e-6
    assert all(weight >= 0 for weight in weights.values())

def test_efficient_frontier_generation(sample_assets, sample_expected_returns, sample_covariance_matrix):
    """Test generation of efficient frontier."""
    optimizer = MarkowitzOptimizer()
    
    # Test efficient frontier calculation
    frontier_points = optimizer.get_efficient_frontier(
        expected_returns=sample_expected_returns,
        covariance_matrix=sample_covariance_matrix,
        assets=sample_assets,
        num_points=10
    )
    
    # Check that we get the requested number of points
    assert len(frontier_points) == 10
    
    # Check that each point has expected return, risk, and weights
    for point in frontier_points:
        assert 'expected_return' in point
        assert 'risk' in point
        assert 'weights' in point
        assert len(point['weights']) == len(sample_assets)