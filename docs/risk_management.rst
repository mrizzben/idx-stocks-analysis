Risk Management Module
=====================

The risk management module provides various risk modeling and management capabilities.

Mean-Variance Risk Model
------------------------
.. autoclass:: portfolio_optimizer.risk_management.mean_variance.MeanVarianceRiskModel
   :members:
   :undoc-members:
   :show-inheritance:

Example:
```python
from portfolio_optimizer.risk_management.mean_variance import MeanVarianceRiskModel

risk_model = MeanVarianceRiskModel()
risk_metrics = risk_model.calculate_risk_metrics(returns_data)
```

Conditional Value at Risk (CVaR)
---------------------------------
.. autoclass:: portfolio_optimizer.risk_management.cvar.CVaRRiskModel
   :members:
   :undoc-members:
   :show-inheritance:

Example:
```python
from portfolio_optimizer.risk_management.cvar import CVaRRiskModel

risk_model = CVaRRiskModel(confidence_level=0.95)
risk_metrics = risk_model.calculate_risk_metrics(returns_data)
```

Key Features
------------
- Multiple risk modeling approaches
- Risk metric calculation (volatility, VaR, CVaR, correlation)
- Risk constraint integration with optimization engine
- Confidence level configuration for CVaR
- Risk-return tradeoff analysis