import pytest
import numpy as np
import pandas as pd
from portfolio_optimizer.core.markowitz import MarkowitzOptimizer
from portfolio_optimizer.core.hrp import HRP
from portfolio_optimizer.core.monte_carlo import MonteCarloOptimizer
from portfolio_optimizer.risk_management.mean_variance import MeanVarianceRiskModel
from portfolio_optimizer.risk_management.cvar import CVaRRiskModel

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
    risk_model = MeanVarianceRiskModel()
    optimizer = MarkowitzOptimizer(risk_model=risk_model)
    
    @benchmark
    def optimize():
        data = generate_market_data(num_assets=20, num_periods=200)
        return optimizer.optimize(data)
    
    weights = optimize()
    assert sum(weights.values()) == pytest.approx(1.0)

@pytest.mark.benchmark(group="optimizer-performance")
def test_hrp_benchmark(benchmark):
    """Benchmark HRP optimizer with different data sizes"""
    optimizer = HRP()
    
    @benchmark
    def optimize():
        data = generate_market_data(num_assets=20, num_periods=200)
        return optimizer.optimize(data)
    
    weights = optimize()
    assert sum(weights.values()) == pytest.approx(1.0)

@pytest.mark.benchmark(group="optimizer-performance")
def test_monte_carlo_benchmark(benchmark):
    """Benchmark Monte Carlo optimizer with different data sizes"""
    optimizer = MonteCarloOptimizer(num_simulations=1000)
    
    @benchmark
    def optimize():
        data = generate_market_data(num_assets=20, num_periods=200)
        return optimizer.optimize(data)
    
    weights = optimize()
    assert sum(weights.values()) == pytest.approx(1.0)

@pytest.mark.benchmark(group="risk-model-scalability")
def test_risk_model_scalability(benchmark):
    """Test risk model performance with increasing assets"""
    risk_model = MeanVarianceRiskModel()
    optimizer = MarkowitzOptimizer(risk_model=risk_model)
    
    @benchmark
    def optimize_large():
        data = generate_market_data(num_assets=50, num_periods=100)
        return optimizer.optimize(data)
    
    weights = optimize_large()
    assert len(weights) == 50

@pytest.mark.benchmark(group="constrained-optimization")
def test_constrained_optimization(benchmark):
    """Benchmark performance with different constraint sets"""
    risk_model = MeanVarianceRiskModel()
    optimizer = MarkowitzOptimizer(
        risk_model=risk_model,
        constraints=[{'type': 'ineq', 'fun': lambda x: 1 - sum(x)}]
    )
    
    @benchmark
    def optimize_with_constraints():
        data = generate_market_data(num_assets=20, num_periods=200)
        return optimizer.optimize(data)
    
    weights = optimize_with_constraints()
    assert all(w >= 0 for w in weights.values())

if __name__ == "__main__":
    pytest.main([__file__, "-v"])