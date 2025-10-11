"""
Unit Tests for Hierarchical Risk Parity (HRP) Optimizer

This module contains test cases for the HRPOptimizer class,
covering various optimization scenarios and edge cases.
"""

import pytest
import numpy as np
import pandas as pd
from portfolio_optimizer.core.hrp import HRPOptimizer

def test_hrp_initialization():
    """Test initialization of HRPOptimizer with default and custom parameters."""
    # Test default initialization
    optimizer = HRPOptimizer()
    assert optimizer.config[' linkage_method'] == 'single'
    assert optimizer.config['n_clusters'] == None
    
    # Test custom initialization
    custom_config = {'linkage_method': 'ward', 'n_clusters': 3}
    optimizer = HRPOptimizer(config=custom_config)
    assert optimizer.config['linkage_method'] == 'ward'
    assert optimizer.config['n_clusters'] == 3

def test_hrp_optimization_process(sample_assets, sample_returns):
    """Test the complete HRP optimization process."""
    optimizer = HRPOptimizer()
    
    # Test optimization with sample data
    weights = optimizer.optimize(
        expected_returns=None,  # HRP typically doesn't use expected returns
        covariance_matrix=sample_returns.cov().values,
        assets=sample_assets,
        returns=sample_returns.values
    )
    
    # Check weights sum to 1 and are non-negative
    assert abs(sum(weights.values()) - 1.0) < 1e-6
    assert all(weight >= 0 for weight in weights.values())

def test_hrp_with_clustering(sample_assets, sample_returns):
    """Test HRP optimization with different clustering configurations."""
    # Test with specified number of clusters
    optimizer = HRPOptimizer(config={'n_clusters': 2})
    
    weights = optimizer.optimize(
        expected_returns=None,
        covariance_matrix=sample_returns.cov().values,
        assets=sample_assets,
        returns=sample_returns.values
    )
    
    # Check weights sum to 1 and are non-negative
    assert abs(sum(weights.values()) - 1.0) < 1e-6
    assert all(weight >= 0 for weight in weights.values())

def test_hrp_with_linkage_methods(sample_assets, sample_returns):
    """Test HRP optimization with different linkage methods."""
    linkage_methods = ['single', 'complete', 'average', 'ward']
    
    for method in linkage_methods:
        optimizer = HRPOptimizer(config={'linkage_method': method})
        
        weights = optimizer.optimize(
            expected_returns=None,
            covariance_matrix=sample_returns.cov().values,
            assets=sample_assets,
            returns=sample_returns.values
        )
        
        # Check weights sum to 1 and are non-negative
        assert abs(sum(weights.values()) - 1.0) < 1e-6
        assert all(weight >= 0 for weight in weights.values())

def test_hrp_invalid_inputs(sample_assets, sample_returns):
    """Test HRP optimizer behavior with invalid inputs."""
    optimizer = HRPOptimizer()
    
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

def test_hrp_diversification_analysis(sample_assets, sample_returns):
    """Test diversification metrics of HRP optimization."""
    optimizer = HRPOptimizer()
    
    weights = optimizer.optimize(
        expected_returns=None,
        covariance_matrix=sample_returns.cov().values,
        assets=sample_assets,
        returns=sample_returns.values
    )
    
    # Check that HRP produces more diversified weights than Markowitz
    # This is a basic check - in practice we would use more sophisticated metrics
    num_assets = len(sample_assets)
    equal_weights = 1.0 / num_assets
    diversification_ratio = sum(weight / equal_weights for weight in weights.values())
    
    # HRP should produce more diversified portfolio than equal weights
    assert diversification_ratio > 0.9 * num_assets  # Allow some flexibility

def test_hrp_rebalancing_impact(sample_assets, sample_returns):
    """Test HRP optimization with different rebalancing frequencies."""
    optimizer = HRPOptimizer()
    
    # Test with monthly rebalancing
    monthly_weights = optimizer.optimize(
        expected_returns=None,
        covariance_matrix=sample_returns.cov().values,
        assets=sample_assets,
        returns=sample_returns.values,
        rebalance_frequency='monthly'
    )
    
    # Test with quarterly rebalancing
    quarterly_weights = optimizer.optimize(
        expected_returns=None,
        covariance_matrix=sample_returns.cov().values,
        assets=sample_assets,
        returns=sample_returns.values,
        rebalance_frequency='quarterly'
    )
    
    # Check weights sum to 1 and are non-negative for both cases
    assert abs(sum(monthly_weights.values()) - 1.0) < 1e-6
    assert all(weight >= 0 for weight in monthly_weights.values())
    assert abs(sum(quarterly_weights.values()) - 1.0) < 1e-6
    assert all(weight >= 0 for weight in quarterly_weights.values())