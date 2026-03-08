"""
Test Configuration for Portfolio Optimization System

This module provides configuration and fixtures for testing the portfolio optimization system.
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from portfolio_optimizer.core.markowitz import MarkowitzOptimizer
from portfolio_optimizer.core.hrp import HRPOptimizer

# Sample test data
@pytest.fixture
def sample_assets():
    """Sample asset list for testing."""
    return ["AAPL", "GOOGL", "MSFT", "AMZN"]


@pytest.fixture
def sample_returns(sample_assets):
    """Sample returns data for testing."""
    np.random.seed(42)
    dates = pd.date_range(start="2020-01-01", periods=100, freq="D")
    returns = pd.DataFrame(
        np.random.randn(100, 4) * 0.01, index=dates, columns=sample_assets
    )
    return returns


@pytest.fixture
def sample_covariance_matrix(sample_returns):
    """Sample covariance matrix for testing."""
    return sample_returns.cov()


@pytest.fixture
def sample_expected_returns(sample_assets):
    """Sample expected returns for testing."""
    return {asset: 0.05 + i * 0.01 for i, asset in enumerate(sample_assets)}


@pytest.fixture
def markowitz_optimizer(sample_returns):
    """Fixture for Markowitz optimizer."""
    return MarkowitzOptimizer(sample_returns, sample_returns.cov())


@pytest.fixture
def hrp_optimizer(sample_returns):
    """Fixture for HRP optimizer."""
    return HRPOptimizer(sample_returns, sample_returns.cov())

