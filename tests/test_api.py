"""
Tests for American Computers Albania — Supply Chain API
Run with: pytest tests/ -v
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)


# ─── Health ───────────────────────────────────────────────────────────────────

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "online"

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ─── Delay Prediction ─────────────────────────────────────────────────────────

def test_delay_predict_low_risk():
    """Short route, good supplier, low risk factors → LOW risk."""
    mock_result = {
        "risk_class": "LOW",
        "risk_probability": 18.5,
        "confidence": 93.2,
        "top_factors": {
            "Customs risk": 3.0,
            "Distance": 2.1,
            "Weather": 2.0,
            "Supplier rating": 0.8,
            "Lead time": 2.1,
        },
        "model_info": {
            "name": "Random Forest Classifier",
            "n_estimators": 200,
            "accuracy": 89.7,
            "precision": 87.3,
            "recall": 88.1,
        },
    }
    with patch.object(app.state if hasattr(app, 'state') else MagicMock(),
                      'ml_service', create=True):
        with patch("app.ml.inference.ml_service.predict_delay", return_value=mock_result):
            r = client.post("/api/v1/ml/delay/predict", json={
                "route": "Greece → Tirana (road)",
                "distance_km": 490,
                "weather_score": 2.0,
                "customs_risk": 2.0,
                "supplier_rating": 4.9,
                "lead_time_days": 4,
            })
    assert r.status_code == 200
    data = r.json()
    assert "risk_class" in data
    assert "risk_probability" in data
    assert "top_factors" in data


def test_delay_predict_high_risk():
    """Long route, bad weather, high customs → HIGH risk."""
    mock_result = {
        "risk_class": "HIGH",
        "risk_probability": 78.4,
        "confidence": 88.1,
        "top_factors": {
            "Customs risk": 24.0,
            "Distance": 20.3,
            "Weather": 18.0,
            "Supplier rating": 12.5,
            "Lead time": 9.3,
        },
        "model_info": {
            "name": "Random Forest Classifier",
            "n_estimators": 200,
            "accuracy": 89.7,
            "precision": 87.3,
            "recall": 88.1,
        },
    }
    with patch("app.ml.inference.ml_service.predict_delay", return_value=mock_result):
        r = client.post("/api/v1/ml/delay/predict", json={
            "route": "China → Tirana (air)",
            "distance_km": 7500,
            "weather_score": 9.0,
            "customs_risk": 8.5,
            "supplier_rating": 2.8,
            "lead_time_days": 14,
        })
    assert r.status_code == 200
    data = r.json()
    assert data["risk_class"] in ["LOW", "MEDIUM", "HIGH"]


def test_delay_predict_validation():
    """Invalid input — weather_score > 10 — should return 422."""
    r = client.post("/api/v1/ml/delay/predict", json={
        "route": "Italy → Durrës (sea)",
        "distance_km": 860,
        "weather_score": 99,       # invalid
        "customs_risk": 4.0,
        "supplier_rating": 4.1,
        "lead_time_days": 6,
    })
    assert r.status_code == 422


# ─── Demand Forecast ──────────────────────────────────────────────────────────

def test_forecast_request():
    mock_result = {
        "category": "Laptops",
        "horizon_days": 30,
        "rmse": 4.1,
        "mae": 2.9,
        "r2": 0.881,
        "model_name": "ARIMA(2,1,2)",
        "forecast": [
            {"date": "2024-04-10", "actual": 82.0, "predicted": 84.5,
             "lower_bound": 72.1, "upper_bound": 96.9}
        ],
    }
    with patch("app.ml.inference.ml_service.predict_demand", return_value=mock_result):
        r = client.post("/api/v1/ml/forecast", json={
            "product_category": "Laptops",
            "horizon_days": 30,
        })
    assert r.status_code == 200
    data = r.json()
    assert data["category"] == "Laptops"
    assert "forecast" in data
    assert isinstance(data["forecast"], list)


def test_forecast_invalid_horizon():
    """Horizon > 90 days should fail validation."""
    r = client.post("/api/v1/ml/forecast", json={
        "product_category": "Laptops",
        "horizon_days": 200,   # too long
    })
    assert r.status_code == 422


# ─── Route Optimizer ──────────────────────────────────────────────────────────

def test_route_optimize_default():
    r = client.post("/api/v1/ml/routes/optimize")
    assert r.status_code == 200
    data = r.json()
    assert "routes" in data
    assert "total_saving_eur" in data
    assert len(data["routes"]) > 0

def test_route_optimize_by_cost():
    r = client.post("/api/v1/ml/routes/optimize?objective=cost&max_vehicles=5")
    assert r.status_code == 200
    data = r.json()
    assert data["objective"] == "cost"
    assert len(data["routes"]) == 5

def test_route_optimize_invalid_objective():
    r = client.post("/api/v1/ml/routes/optimize?objective=invalid")
    assert r.status_code == 422


# ─── ETL Pipeline ─────────────────────────────────────────────────────────────

def test_etl_run_empty_db():
    """ETL with empty DB should return warning, not crash."""
    mock_db = MagicMock()
    mock_db.query.return_value.all.return_value = []

    with patch("app.api.v1.endpoints.ml.get_db", return_value=iter([mock_db])):
        with patch("app.api.v1.endpoints.ml.run_etl", return_value={
            "status": "warning",
            "records_processed": 0,
            "null_rate": 0.0,
            "duration_seconds": 0.01,
            "train_size": 0,
            "test_size": 0,
            "log": ["[INF] No orders found — seed the database first."],
        }):
            r = client.post("/api/v1/ml/etl/run")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert "log" in data
