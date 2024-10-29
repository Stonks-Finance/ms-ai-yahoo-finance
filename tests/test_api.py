import pytest
from fastapi.testclient import TestClient
from api.api import api

client = TestClient(api)

def test_predict_default_case():
    response = client.get("/predict?stock_name=AAPL")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "prices" in response.json()["data"]
    assert "timestamps" in response.json()["data"]

def test_predict_valid_request():
    response = client.get("/predict?stock_name=AAPL&interval=1h&duration=5")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "prices" in response.json()["data"]
    assert "timestamps" in response.json()["data"]

def test_predict_invalid_duration_high():
    response = client.get("/predict?stock_name=AAPL&interval=1h&duration=15")
    assert response.json()["status"] == 400
    assert "Duration" in response.json()["message"]

def test_predict_invalid_duration_low():
    response = client.get("/predict?stock_name=AAPL&interval=1h&duration=0")
    assert response.json()["status"] == 400
    assert "Duration" in response.json()["message"]

def test_predict_invalid_duration_not_integer():
    response = client.get("/predict?stock_name=AAPL&interval=1h&duration=abc")
    assert response.json()["status"] == 400
    assert "The 'duration' parameter must be an integer." in response.json()["message"]

def test_predict_invalid_interval():
    response = client.get("/predict?stock_name=AAPL&interval=invalid_interval&duration=5")
    assert response.json()["status"] == 400
    assert "Unsupported interval" in response.json()["message"]

def test_predict_no_data_found():
    response = client.get("/predict?stock_name=INVALID_STOCK&interval=1h&duration=5")
    assert response.json()["status"] == 404
    assert "No data found for the specified stock." in response.json()["message"]

if __name__ == "__main__":
    pytest.main()
