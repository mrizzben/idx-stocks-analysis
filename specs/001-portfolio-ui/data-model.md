# Data Model: Portfolio Optimization UI

## Entity: MarketDataRequest
Represents the request to fetch historical stock data.
- `tickers`: List[str] (e.g., ["ASII", "BBCA"])
- `period`: str (Default: "1y", Options: "1mo", "3mo", "6mo", "1y", "2y", "5y")
- `interval`: str (Default: "1d")

## Entity: OptimizationInput
Input passed to the optimization services.
- `returns`: pd.DataFrame (Rows: dates, Columns: assets, Values: float returns)
- `method`: str (Enum: "hrp", "markowitz")
- `risk_free_rate`: float (e.g., 0.06 for 6%)

## Entity: OptimizationResult
Output from the portfolio engine to be visualized.
- `weights`: Dict[str, float] (Key: Ticker, Value: Weight [0-1])
- `metrics`: Dict[str, float] (Key: "Sharpe Ratio", "Volatility", "Expected Return")
- `dendrogram_data`: Optional[Dict] (JSON representation of hierarchical clusters for HRP)

## Validation Rules
- `weights`: sum(values) MUST equal 1.0 (with tolerance 1e-6).
- `tickers`: If no suffix, default to `.JK`.
- `data`: Minimum 2 valid assets required for correlation calculation.
