# API Interface for Portfolio Optimization Services

## REST API Design

### Base URL
```
/api/v1
```

### Authentication
- API Key in header: `Authorization: Api-Key <your-key>`
- OAuth2 Bearer Token (for enterprise deployments)

## Endpoints

### 1. Portfolio Optimization
**POST** `/optimize`

**Request Body:**
```json
{
  "assets": ["AAPL", "GOOG", "MSFT", "AMZN"],
  "returns": {
    "AAPL": [0.01, -0.02, 0.015, ...],
    "GOOG": [0.005, -0.01, 0.02, ...]
  },
  "covariance_matrix": {
    "AAPL": {"AAPL": 0.001, "GOOG": 0.0005},
    "GOOG": {"AAPL": 0.0005, "GOOG": 0.002}
  },
  "parameters": {
    "method": "markowitz",
    "risk_free_rate": 0.02,
    "target_return": 0.15,
    "constraints": {
      "max_volatility": 0.2,
      "min_weight": 0.05,
      "max_weight": 0.4
    }
  }
}
```

**Response:**
```json
{
  "optimal_weights": {
    "AAPL": 0.35,
    "GOOG": 0.25,
    "MSFT": 0.2,
    "AMZN": 0.2
  },
  "performance": {
    "expected_return": 0.145,
    "volatility": 0.18,
    "sharpe_ratio": 0.75
  },
  "method_specific": {
    "efficient_frontier": [
      {"return": 0.12, "volatility": 0.15},
      {"return": 0.15, "volatility": 0.18}
    ]
  }
}
```

### 2. Risk Analysis
**POST** `/risk-analysis`

**Request Body:**
```json
{
  "returns": {
    "AAPL": [0.01, -0.02, 0.015, ...],
    "GOOG": [0.005, -0.01, 0.02, ...]
  },
  "weights": {
    "AAPL": 0.35,
    "GOOG": 0.25
  },
  "parameters": {
    "confidence_level": 0.95,
    "risk_measure": "VaR"
  }
}
```

**Response:**
```json
{
  "risk_metrics": {
    "VaR": 0.05,
    "CVaR": 0.07,
    "max_drawdown": 0.15
  }
}
```

### 3. Stress Testing
**POST** `/stress-test`

**Request Body:**
```json
{
  "scenario": "market_crash",
  "intensity": 2.0,
  "portfolio": {
    "weights": {"AAPL": 0.35, "GOOG": 0.25},
    "returns": {"AAPL": [0.01, -0.02, ...]}
  }
}
```

**Response:**
```json
{
  "stress_results": {
    "scenario": "market_crash",
    "loss_estimate": 0.35,
    "recovery_period": "6 months"
  }
}
```

## Data Models

### Optimization Request
```python
class OptimizationRequest:
    def __init__(self, assets: List[str], returns: pd.DataFrame,
                 covariance_matrix: pd.DataFrame, parameters: Dict):
        self.assets = assets
        self.returns = returns
        self.covariance_matrix = covariance_matrix
        self.parameters = self._validate_parameters(parameters)
    
    def _validate_parameters(self, params: Dict) -> Dict:
        # Validation logic
```

### Optimization Response
```python
class OptimizationResponse:
    def __init__(self, weights: Dict[str, float], performance: Dict,
                 method_specific: Dict = None):
        self.weights = weights
        self.performance = performance
        self.method_specific = method_specific or {}
```

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Missing required parameters",
    "details": {
      "missing_fields": ["method", "risk_free_rate"]
    }
  }
}
```

### Common Error Codes
- `VALIDATION_ERROR` (400) - Request validation failed
- `UNSUPPORTED_METHOD` (400) - Optimization method not supported
- `DATA_ERROR` (400) - Invalid or missing market data
- `INTERNAL_ERROR` (500) - Server-side error
- `AUTH_ERROR` (401) - Authentication failed

## Service Interface
```python
class PortfolioOptimizationService:
    def optimize(self, request: OptimizationRequest) -> OptimizationResponse:
        """Process optimization request and return results"""
    
    def validate_data(self, request: OptimizationRequest) -> bool:
        """Validate input data quality and completeness"""
    
    def _select_optimizer(self, method: str) -> BaseOptimizer:
        """Factory method to select appropriate optimizer"""
```

## Integration Points
- Optimization Engine: Core optimization algorithms
- Risk Management: Risk metric calculation
- Data Pipeline: Market data validation and preprocessing
- Visualization: API response visualization

## Security Considerations
- Rate limiting (100 requests/minute for standard tier)
- API key rotation mechanism
- HTTPS enforcement
- Request validation and sanitization

## Versioning Strategy
- URL versioning: `/api/v1/optimize`
- Semantic versioning: Major versions for breaking changes
- Backward compatibility maintained for 12 months

## Asynchronous Processing
For long-running tasks (e.g., Monte Carlo simulations):
- `POST /optimize` returns 202 Accepted with task ID
- `GET /tasks/{task_id}` to check status
- Webhooks for completion notification