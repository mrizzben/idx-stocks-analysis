# Core Optimization Engine Implementation Plan

## Module Structure
```
optimization/
├── __init__.py
├── markowitz.py      # Markowitz mean-variance optimization
├── hrp.py            # Hierarchical Risk Parity implementation
├── monte_carlo.py    # Monte Carlo simulation framework
├── utils.py           # Shared utility functions
└── models.py          # Data models and type definitions
```

## Markowitz Optimization Module
```python
class MarkowitzOptimizer:
    def __init__(self, returns: pd.DataFrame, cov_matrix: pd.DataFrame):
        """Initialize with returns and covariance matrix"""
        self.returns = returns
        self.cov_matrix = cov_matrix
    
    def efficient_frontier(self, num_portfolios: int = 100) -> pd.DataFrame:
        """Calculate efficient frontier portfolios"""
    
    def optimal_weights(self, risk_free_rate: float = 0.02) -> Dict[str, float]:
        """Calculate optimal weights using Sharpe ratio"""
    
    def _minimize_volatility(self, weights) -> float:
        """Internal optimization objective function"""
```

## Hierarchical Risk Parity (HRP) Module
```python
class HRPOptimizer:
    def __init__(self, cov_matrix: pd.DataFrame):
        self.cov_matrix = cov_matrix
        self.linkage_matrix = self._compute_linkage()
    
    def _compute_linkage(self) -> np.ndarray:
        """Compute hierarchical clustering linkage matrix"""
    
    def optimize(self) -> Dict[str, float]:
        """Main optimization workflow using recursive bisection"""
    
    def _get_quasi_diag(self, indices) -> List:
        """Reorder assets to form quasi-diagonal matrix"""
```

## Monte Carlo Simulation Module
```python
class MonteCarloSimulator:
    def __init__(self, returns: pd.DataFrame, cov_matrix: pd.DataFrame):
        self.returns = returns
        self.cov_matrix = cov_matrix
    
    def run_simulations(self, num_simulations: int = 10000) -> pd.DataFrame:
        """Run Monte Carlo simulations to find optimal portfolios"""
    
    def _calculate_portfolio_stats(self, weights) -> Tuple[float, float]:
        """Calculate return and volatility for given weights"""
    
    def find_optimal(self, simulations: pd.DataFrame) -> Dict[str, float]:
        """Find optimal portfolio based on Sharpe ratio"""
```

## Shared Utilities
- Portfolio metrics calculation
- Weight validation and normalization
- Covariance matrix processing
- Risk-return space sampling

## Integration Points
- Data Service: Market data ingestion
- Risk Management Service: Risk constraint application
- Clustering Service: Cluster-based optimization
- Backtesting Service: Performance validation

## Error Handling Strategy
- Input validation for all public methods
- Graceful degradation for singular covariance matrices
- Bounds checking for optimization constraints
- Comprehensive exception hierarchy