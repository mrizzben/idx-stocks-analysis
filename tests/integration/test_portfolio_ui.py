import pytest
import pandas as pd
import numpy as np
from api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_fetch_data_endpoint():
    payload = {"tickers": ["BBCA.JK", "TLKM.JK"], "period": "1mo", "interval": "1d"}
    response = client.post("/api/v1/fetch-data", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "BBCA.JK" in data["data"]
    assert len(data["data"]["BBCA.JK"]) > 0


def test_optimize_endpoint_hrp():
    # Create dummy returns
    returns_data = {
        "ASII.JK": [0.01, -0.01, 0.02, 0.005, -0.005] * 5,
        "BBCA.JK": [0.005, 0.01, -0.005, 0.01, 0.01] * 5,
    }
    payload = {"strategy": "hrp", "risk_free_rate": 0.06, "returns_data": returns_data}
    response = client.post("/api/v1/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["success"] is True


def test_optimize_endpoint_markowitz():
    returns_data = {
        "ASII.JK": [0.01, -0.01, 0.02, 0.005, -0.005] * 5,
        "BBCA.JK": [0.005, 0.01, -0.005, 0.01, 0.01] * 5,
    }
    payload = {
        "strategy": "markowitz",
        "method": "min_variance",
        "risk_free_rate": 0.02,
        "returns_data": returns_data,
    }
    response = client.post("/api/v1/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["success"] is True
    assert abs(sum(data["data"]["weights"].values()) - 1.0) < 1e-6


def test_optimize_endpoint_monte_carlo():
    returns_data = {
        "ASII.JK": [0.01, -0.01, 0.02, 0.005, -0.005] * 5,
        "BBCA.JK": [0.005, 0.01, -0.005, 0.01, 0.01] * 5,
    }
    payload = {
        "strategy": "monte_carlo",
        "risk_free_rate": 0.06,
        "returns_data": returns_data,
    }
    response = client.post("/api/v1/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["success"] is True
    assert abs(sum(data["data"]["weights"].values()) - 1.0) < 1e-6
    # T029: Validate performance with 100 tickers
    tickers = [f"TICKER_{i}" for i in range(100)]
    returns_data = {t: np.random.normal(0, 0.01, 50).tolist() for t in tickers}

    payload = {"strategy": "hrp", "returns_data": returns_data}
    import time

    start_time = time.time()
    response = client.post("/api/v1/optimize", json=payload)
    end_time = time.time()

    assert response.status_code == 200
    assert (end_time - start_time) < 30.0  # Should be well under 30s
