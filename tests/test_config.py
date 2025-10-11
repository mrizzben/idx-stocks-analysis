"""
Test Configuration for Portfolio Optimization System

This module provides configuration and fixtures for testing the portfolio optimization system.
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from portfolio_optimizer.core.markowitz import MarkowitzOptimizer
from portfolio_optimizer.data_pipeline.csv_data_source import CSVDataSource
from portfolio_optimizer.risk_management.mean_variance import MeanVarianceRiskModel
from portfolio_optimizer.api import PortfolioOptimizationAPI

# Sample test data
@pytest.fixture
def sample_assets():
    """Sample asset list for testing."""
    return ['AAPL', 'GOOGL', 'MSFT', 'AMZN']

@pytest.fixture
def sample_returns(sample_assets):
    """Sample returns data for testing."""
    np.random.seed(42)
    dates = pd.date_range(start='2020-01-01', periods=100, freq='D')
    returns = pd.DataFrame(np.random.randn(100, 4) * 0.01, 
                          index=dates, 
                          columns=sample_assets)
    return returns

@pytest.fixture
def sample_covariance_matrix(sample_returns):
    """Sample covariance matrix for testing."""
    return sample_returns.cov().values

@pytest.fixture
def sample_expected_returns(sample_assets):
    """Sample expected returns for testing."""
    return {asset: 0.05 + i*0.01 for i, asset in enumerate(sample_assets)}

@pytest.fixture
def sample_optimization_config(sample_assets):
    """Sample optimization configuration for testing."""
    return {
        'type': 'mean_variance',
        'assets': sample_assets,
        'expected_returns': {asset: 0.05 + i*0.01 for i, asset in enumerate(sample_assets)},
        'covariance': np.random.rand(len(sample_assets), len(sample_assets)) * 0.01,
        'constraints': {
            'long_only': True,
            'max_weight': 0.5
        },
        'risk_free_rate': 0.02
    }

@pytest.fixture
def markowitz_optimizer():
    """Fixture for Markowitz optimizer."""
    return MarkowitzOptimizer(config={'solver': 'SLSQP'})

@pytest.fixture
def csv_data_source(tmp_path):
    """Fixture for CSV data source with temporary data."""
    # Create temporary CSV file
    test_data = pd.DataFrame({
        'date': pd.date_range(start='2020-01-01', periods=50, freq='D'),
        'AAPL': np.random.rand(50) * 100,
        'GOOGL': np.random.rand(50) * 100
    })
    
    csv_path = tmp_path / "test_data.csv"
    test_data.to_csv(csv_path, index=False)
    
    return CSVDataSource(config={'file_path': str(csv_path)})

@pytest.fixture
def mean_variance_risk_model():
    """Fixture for mean variance risk model."""
    return MeanVarianceRiskModel(config={'window': 20})

@pytest.fixture
def test_api_client():
    """Fixture for testing the API interface."""
    # Create a test optimizer engine (mock)
    class MockOptimizerEngine:
        def optimize(self, **kwargs):
            return {
                'weights': {asset: 1.0/len(kwargs['assets']) for asset in kwargs['assets']},
                'expected_return': 0.08,
                'risk': 0.12,
                'sharpe_ratio': 0.5
            }
        
        def backtest(self, **kwargs):
            return {
                'cumulative_return': 1.25,
                'annualized_return': 0.20,
                'max_drawdown': 0.15,
                'sharpe_ratio': 0.6
            }
    
    # Create API instance with mock optimizer
    api = PortfolioOptimizationAPI(MockOptimizerEngine())
    
    # Create test client
    with api.app.test_client() as client:
        yield client