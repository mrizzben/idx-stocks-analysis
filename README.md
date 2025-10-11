# IDX Stocks Portfolio Optimization using Hierarchical Clustering

## Study Overview
This repository implements the findings of a quantitative study on portfolio optimization using data science techniques. The research focused on creating optimal portfolios through clustering analysis (k-means and agglomerative hierarchical clustering) combined with modern portfolio optimization methods (mean-variance and hierarchical risk parity). The study utilized intraday data from KOMPAS100 stocks and bond yields (2010-2021) to develop and validate its approach.

## Key Features
- **Clustering Analysis**:
  - K-means clustering for stock portfolio segmentation
  - Agglomerative hierarchical clustering for market structure analysis
- **Portfolio Optimization**:
  - Mean-variance optimization (Markowitz, 1952)
  - Hierarchical risk parity (Lopez de Prado, 2016)
- **Risk Assessment**:
  - Sharpe ratio calculation (0.676-0.678 in validation)
  - Return analysis (58.38-63.19% holding returns in validation)
- **Data Pipeline**:
  - Intraday stock market data processing
  - Bond yield integration for risk-free rate calculation

## Project Structure
```
portfolio_optimizer/
├── core/               # Optimization algorithms
├── data_pipeline/      # Market data processing
├── risk_management/    # Risk assessment modules
├── visualization/      # Portfolio performance analysis
notebooks/              # EDA and clustering implementation
docs/                   # Technical documentation
data/                   # Raw/processed financial data
tests/                  # Validation tests
```

## Methodology
The study implemented two-stage portfolio construction:
1. **Clustering Stage**:
   - Applied k-means and agglomerative clustering to group stocks
   - Identified optimal cluster configurations for market conditions
2. **Optimization Stage**:
   - Applied mean-variance and HRP optimization within clusters
   - Validated results against market benchmarks and random portfolios

## Usage Example
```python
# Clustering implementation
from portfolio_optimizer.data_pipeline import MarketDataSource
from portfolio_optimizer.core import PortfolioOptimizer

# Load and preprocess data
market_data = MarketDataSource.load_kompas100('data/stocks-data.pkl')

# Apply clustering and optimization
optimizer = PortfolioOptimizer(clustering='kmeans', optimization='hrp')
portfolio = optimizer.create_portfolio(market_data)
```

## Validation Results
- **K-means + HRP**: 63.19% holding return (Sharpe 0.676)
- **Agglomerative + HRP**: 58.38% holding return (Sharpe 0.678)
- Outperformed market benchmarks and random portfolios

## Documentation
Detailed implementation documentation and research methodology are available in the `docs/` directory, including:
- API reference for optimization modules
- Data pipeline architecture
- Clustering algorithm specifications