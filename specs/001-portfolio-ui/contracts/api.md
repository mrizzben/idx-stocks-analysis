# API Contract: Portfolio Optimization Backend

## Base URL
`/api/v1`

## Endpoints

### POST /optimize
Runs a portfolio optimization based on provided data or tickers.

**Request Schema**:
```json
{
  "strategy": "hrp",
  "risk_free_rate": 0.02,
  "lookback_period": "1y",
  "tickers": ["BBCA.JK", "TLKM.JK", "ASII.JK"],
  "returns_data": null
}
```

**Success Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "weights": {
      "BBCA.JK": 0.33,
      "TLKM.JK": 0.33,
      "ASII.JK": 0.34
    },
    "performance": {
      "Expected Return": 0.15,
      "Volatility": 0.12,
      "Sharpe Ratio": 1.08
    },
    "success": true
  }
}
```

**Error Response (400 Bad Request)**:
```json
{
  "status": "error",
  "message": "Invalid strategy: 'random_walk'. Supported: ['hrp', 'markowitz']"
}
```

### POST /fetch-data
Fetches historical returns data for a list of tickers from yfinance.

**Request Schema**:
```json
{
  "tickers": ["AAPL", "MSFT"],
  "period": "1y",
  "interval": "1d"
}
```

**Success Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "AAPL": [0.01, -0.02, ...],
    "MSFT": [0.005, 0.01, ...]
  }
}
```
