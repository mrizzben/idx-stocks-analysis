# Quickstart: Portfolio Optimization UI

## 1. Prerequisites
- Python 3.12 (Required for Streamlit/PyArrow compatibility)
- `uv` installed (`pip install uv`)

## 2. Environment Setup
```bash
# Recommended: Using uv with Python 3.12
uv sync
source .venv/bin/activate
```

## 3. Launch the Backend (FastAPI)
```bash
# From the root directory
export PYTHONPATH=.
python api/main.py
```

## 4. Launch the Frontend (Streamlit)
```bash
# In a new terminal tab
export PYTHONPATH=.
streamlit run ui/app.py
```

## 3. Launch the Backend (FastAPI)
```bash
# From the root directory
uvicorn api.main:app --reload --port 8000
```

## 4. Launch the Frontend (Streamlit)
```bash
# In a new terminal tab
streamlit run ui/app.py
```

## 5. Launch with Docker
```bash
docker-compose -f docker/docker-compose.yml up --build
```

## 6. Usage
1. Open the Streamlit URL (default: `http://localhost:8501`).
2. **Data Source**: Choose between CSV upload or API fetching.
3. **Tickers**: Enter IDX or global tickers (e.g., "BBCA, TLKM" or "AAPL, MSFT").
4. **Optimize**: Adjust the risk-free rate and click "Generate Portfolio".
5. **Analyze**: Explore the interactive Plotly charts and risk breakdown.
