Core Optimization Engine
=======================

The core optimization engine provides multiple portfolio optimization approaches:

Markowitz Mean-Variance Optimization
-------------------------------------
.. autoclass:: portfolio_optimizer.core.markowitz.MarkowitzOptimizer
   :members:
   :undoc-members:
   :show-inheritance:

Example:
```python
from portfolio_optimizer.core.markowitz import MarkowitzOptimizer
from portfolio_optimizer.risk_management.mean_variance import MeanVarianceRiskModel

risk_model = MeanVarianceRiskModel()
optimizer = MarkowitzOptimizer(risk_model=risk_model)
weights = optimizer.optimize(returns_data)
```

Hierarchical Risk Parity (HRP)
---------------------------------
.. autoclass:: portfolio_optimizer.core.hrp.HRP
   :members:
   :undoc-members:
   :show-inheritance:

Example:
```python
from portfolio_optimizer.core.hrp import HRP
optimizer = HRP()
weights = optimizer.optimize(returns_data)
```

Monte Carlo Optimization
------------------------
.. autoclass:: portfolio_optimizer.core.monte_carlo.MonteCarloOptimizer
   :members:
   :undoc-members:
   :show-inheritance:

Example:
```python
from portfolio_optimizer.core.monte_carlo import MonteCarloOptimizer

optimizer = MonteCarloOptimizer(num_simulations=1000)
weights = optimizer.optimize(returns_data)
```

Key Features
-------------
- Strategy pattern for different optimization approaches
- Constraint handling for portfolio weights
- Risk model integration
- Performance metrics calculation