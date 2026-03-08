import pytest
import numpy as np
import pandas as pd
from portfolio_optimizer.services.portfolio_service import PortfolioService
from portfolio_optimizer.services.feature_service import FeatureService

def generate_market_data(num_assets=10, num_periods=100, seed=None):
    """Generate synthetic market data with controllable parameters"""
    if seed:
        np.random.seed(seed)
    
    # Create correlated returns
    mu = np.random.uniform(0.0005, 0.0015, num_assets)
    cov = np.random.randn(num_assets, num_assets)
    cov = np.dot(cov, cov.T)
    cov = cov * 0.0001  # Scale down covariance
    
    returns = np.random.multivariate_normal(mu, cov, num_periods)
    dates = pd.date_range('2023-01-01', periods=num_periods)
    assets = [f'Asset_{i}' for i in range(num_assets)]
    
    return pd.DataFrame(returns, index=dates, columns=assets)

@pytest.mark.benchmark(group="optimizer-performance")
def test_markowitz_benchmark(benchmark):
    """Benchmark Markowitz optimizer with different data sizes"""
    data = generate_market_data(num_assets=20, num_periods=200, seed=42)
    
    @benchmark
    def optimize():
        return PortfolioService.optimize(data, method="markowitz", strategy="min_variance")
    
    result = optimize()
    assert result.success is True
    assert abs(sum(result.weights.values()) - 1.0) < 1e-6

@pytest.mark.benchmark(group="optimizer-performance")
def test_hrp_benchmark(benchmark):
    """Benchmark HRP optimizer with different data sizes"""
    data = generate_market_data(num_assets=20, num_periods=200, seed=42)
    
    @benchmark
    def optimize():
        return PortfolioService.optimize(data, method="hrp")
    
    result = optimize()
    assert result.success is True
    assert abs(sum(result.weights.values()) - 1.0) < 1e-6

@pytest.mark.benchmark(group="optimizer-performance")
def test_monte_carlo_benchmark(benchmark):
    """Benchmark Monte Carlo optimizer with different data sizes"""
    data = generate_market_data(num_assets=20, num_periods=200, seed=42)
    
    @benchmark
    def optimize():
        return PortfolioService.optimize(data, method="monte_carlo", n_simulations=1000)
    
    result = optimize()
    assert result.success is True
    assert abs(sum(result.weights.values()) - 1.0) < 1e-6

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
