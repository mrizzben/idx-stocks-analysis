API Interface
===============

The API module provides a RESTful interface for portfolio optimization services.

Portfolio Optimization API
-------------------------
.. autoclass:: portfolio_optimizer.api.__init__.PortfolioOptimizationAPI
   :members:
   :undoc-members:
   :show-inheritance:

Example:
```python
from portfolio_optimizer.api import PortfolioOptimizationAPI

api = PortfolioOptimizationAPI()
response = api.optimize(
    assets=["AAPL", "GOOGL"],
    method="markowitz",
    constraints={"max_weight": 0.3}
)
```

Key Features
------------
- RESTful API endpoints for portfolio optimization
- Support for multiple optimization methods
- Request validation and error handling
- Configurable optimization parameters
- JSON response format with metadata
- Health check and status endpoints