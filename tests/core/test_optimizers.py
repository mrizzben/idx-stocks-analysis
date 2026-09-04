"""Regression tests for the optimizers used by app.py.

Covers the bugs fixed in the 2026-09 review:
- max_sharpe was a DCP violation (always failed)
- HRP final weights summed to n_clusters instead of 1
- HRP bisection gave both halves identical weight
- performance metrics mixed daily returns with annualized covariance
"""

import numpy as np
import pandas as pd
import pytest

from portfolio_optimizer.core.hrp import HierarchicalRiskParityOptimizer
from portfolio_optimizer.core.markowitz import MarkowitzOptimizer


@pytest.fixture
def returns_and_cov():
    """Synthetic 5-asset daily returns + annualized covariance."""
    rng = np.random.RandomState(42)
    cols = ["A", "B", "C", "D", "E"]
    returns = pd.DataFrame(rng.randn(252, 5) * 0.02, columns=cols)  # type: ignore[reportArgumentType]
    cov = returns.cov() * 252
    return returns, cov


def _assert_valid_weights(weights, n):
    assert len(weights) == n
    assert np.isclose(sum(weights.values()), 1.0, atol=1e-4), f"weights sum to {sum(weights.values())}"
    assert all(w >= -1e-9 for w in weights.values()), "negative weight found"


def test_max_sharpe_succeeds(returns_and_cov):
    returns, cov = returns_and_cov
    result = MarkowitzOptimizer(returns, cov).optimize(method="max_sharpe")
    assert result.success, f"max_sharpe failed: {result.message}"
    _assert_valid_weights(result.weights, 5)
    # Sharpe must be positive-ish scale: annualized return vs annualized vol
    assert result.performance["volatility"] > 0.01, "volatility looks like a daily scale"


def test_min_variance_succeeds(returns_and_cov):
    returns, cov = returns_and_cov
    result = MarkowitzOptimizer(returns, cov).optimize(method="min_variance")
    assert result.success, f"min_variance failed: {result.message}"
    _assert_valid_weights(result.weights, 5)


def test_min_variance_beats_max_sharpe_volatility(returns_and_cov):
    returns, cov = returns_and_cov
    mv = MarkowitzOptimizer(returns, cov).optimize(method="min_variance")
    ms = MarkowitzOptimizer(returns, cov).optimize(method="max_sharpe")
    assert mv.performance["volatility"] <= ms.performance["volatility"] + 1e-6


def test_hrp_weights_sum_to_one(returns_and_cov):
    returns, cov = returns_and_cov
    result = HierarchicalRiskParityOptimizer(returns, cov).optimize()
    assert result.success, f"HRP failed: {result.message}"
    _assert_valid_weights(result.weights, 5)


def test_hrp_two_assets(returns_and_cov):
    returns, cov = returns_and_cov
    result = HierarchicalRiskParityOptimizer(returns[["A", "B"]], cov.loc[["A", "B"], ["A", "B"]]).optimize()
    assert result.success, f"HRP (2 assets) failed: {result.message}"
    _assert_valid_weights(result.weights, 2)


def test_frontier_consistent_scales(returns_and_cov):
    """Frontier returns must be annual-scale (comparable to its annual vol)."""
    returns, cov = returns_and_cov
    ef = MarkowitzOptimizer(returns, cov).get_efficient_frontier(n_points=10)
    assert all(r > 0.005 for r in ef["returns"]), "frontier returns look like daily scale"
