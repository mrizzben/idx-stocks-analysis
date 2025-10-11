Visualization Components
=========================

The visualization module provides tools for portfolio composition and performance visualization.

Portfolio Weights Visualizer
----------------------------
.. autoclass:: portfolio_optimizer.visualization.portfolio_weights.PortfolioWeightsVisualizer
   :members:
   :undoc-members:
   :show-inheritance:

Example:
```python
from portfolio_optimizer.visualization.portfolio_weights import PortfolioWeightsVisualizer

visualizer = PortfolioWeightsVisualizer()
fig = visualizer.visualize(portfolio_weights)
fig.show()
```

Portfolio Performance Visualizer
-------------------------------
.. autoclass:: portfolio_optimizer.visualization.portfolio_performance.PortfolioPerformanceVisualizer
   :members:
   :undoc-members:
   :show-inheritance:

Example:
```python
from portfolio_optimizer.visualization.portfolio_performance import PortfolioPerformanceVisualizer

visualizer = PortfolioPerformanceVisualizer()
fig = visualizer.visualize(portfolio_returns)
fig.show()
```

Key Features
------------
- Interactive visualization with Plotly
- Customizable color schemes and layouts
- Support for both static and dynamic portfolio visualization
- Performance metrics overlay (Sharpe ratio, drawdowns)
- Export to multiple formats (PNG, HTML, PDF)