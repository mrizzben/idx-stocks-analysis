# IDX Stocks Portfolio Optimization using Hierarchical Clustering

## Study Overview
This repository implements a quantitative study on portfolio optimization using data science techniques. The research focuses on creating optimal portfolios through clustering analysis (k-means, agglomerative hierarchical clustering, and PCA-based clustering) combined with modern portfolio optimization methods (mean-variance, hierarchical risk parity, and Monte Carlo optimization). The study utilizes intraday data from KOMPAS100 stocks and bond yields (2010-2021) to develop and validate its approach, including extensive backtesting of different portfolio strategies.

## Key Features
- **Data Analysis & Preprocessing**:
  - Data cleaning with Z-score outlier detection
  - Feature engineering (correlation scores, risk metrics)
  - Multiple scaling methods (MinMax, Standard, Robust)
  - Time-series analysis of stock returns and volatility
- **Clustering Analysis**:
  - K-means clustering with elbow method for optimal cluster selection
  - Agglomerative hierarchical clustering with dendrogram analysis
  - PCA-based clustering for dimensionality reduction
- **Portfolio Optimization**:
  - Mean-variance optimization (Markowitz, 1952)
  - Hierarchical risk parity (Lopez de Prado, 2016) with quasi-diagonalization
  - Monte Carlo simulation with 500,000+ portfolio combinations
  - Equal-weighted benchmark portfolios
- **Risk Assessment**:
  - Sharpe ratio calculation (0.676-0.678 in validation)
  - Sortino ratio for downside risk analysis
  - Value-at-Risk (parametric and historical methods)
  - Maximum drawdown analysis
- **Backtesting Framework**:
  - Rolling window validation (2010-2021)
  - Performance comparison against market benchmarks
  - Stress-testing across different market conditions
- **Data Pipeline**:
  - Intraday stock market data processing (2010-2021)
  - Bond yield integration for risk-free rate calculation
  - Financial statement analysis for fundamental metrics
  - Volume and liquidity analysis

## Project Structure
```
portfolio_optimizer/
├── core/               # Core optimization algorithms
│   ├── base.py         # Base optimization models
│   ├── hrp.py          # Hierarchical Risk Parity
│   ├── markowitz.py    # Mean-variance optimization
│   └── monte_carlo.py # Simulation framework
├── data_pipeline/      # Market data processing
│   ├── base.py         # Base data pipeline
│   ├── api_data_source.py # External API integration
│   └── csv_data_source.py # Local data loading
├── risk_management/    # Risk assessment modules
│   ├── base.py         # Base risk models
│   ├── cvar.py         # Conditional Value at Risk
│   └── mean_variance.py # Variance analysis
├── visualization/      # Portfolio performance analysis
│   ├── base.py         # Base visualization
│   └── portfolio_performance.py # Backtest visualization
notebooks/              # EDA and implementation
├── data/               # Raw/processed financial data
│   ├── raw/            # Original datasets
│   ├── interim/        # Intermediate processing
│   └── processed/      # Final processed data
docs/                   # Technical documentation
src/                    # Supporting scripts
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
