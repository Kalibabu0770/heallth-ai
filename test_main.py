import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "LifeShield AI" in response.json()["message"]

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_prediction_endpoint():
    """Test a successful prediction."""
    payload = {
        "features": {
            "age": 45,
            "gender": 1,
            "bmi": 28.5,
            "smoker": 1,
            "genhlth": 4
        }
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "risk_probability" in data
    assert "risk_level" in data
    assert "recommendation" in data

def test_prediction_missing_features():
    """Test prediction with missing features (should handle gracefully via reindex)."""
    payload = {
        "features": {
            "age": 30
            # Missing everything else
        }
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert "risk_probability" in response.json()

def test_invalid_payload():
    """Test prediction with invalid payload format."""
    payload = {"invalid_key": "data"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422  # Unprocessable Entity
