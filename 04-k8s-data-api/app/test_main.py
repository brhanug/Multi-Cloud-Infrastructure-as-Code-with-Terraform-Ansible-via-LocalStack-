from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """Verify healthz endpoint returns a healthy status."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "timestamp" in response.json()


def test_predict_positive():
    """Verify positive sentiment classification for text containing positive keywords."""
    response = client.post(
        "/data-api/api/v1/predict", json={"text": "FastAPI is awesome and beautiful!"}
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["sentiment"] == "positive"
    assert res_data["confidence"] > 0.5
    assert "processed_at" in res_data


def test_predict_negative():
    """Verify negative sentiment classification for text containing negative keywords."""
    response = client.post(
        "/data-api/api/v1/predict", json={"text": "Terrible slow slow slow service."}
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["sentiment"] == "negative"
    assert res_data["confidence"] > 0.5


def test_predict_neutral():
    """Verify neutral sentiment classification for neutral text."""
    response = client.post("/data-api/api/v1/predict", json={"text": "It is a table."})
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["sentiment"] == "neutral"
    assert res_data["confidence"] == 0.5


def test_predict_validation_error():
    """Verify validation error (422) is raised on empty request bodies."""
    response = client.post("/data-api/api/v1/predict", json={"text": ""})
    assert response.status_code == 422


def test_process_valid():
    """Verify statistical values and min-max normalization are correctly computed."""
    response = client.post(
        "/data-api/api/v1/process", json={"data": [10.0, 20.0, 30.0]}
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["mean"] == 20.0
    assert res_data["variance"] == 66.6667
    assert res_data["normalized_data"] == [0.0, 0.5, 1.0]
    assert res_data["count"] == 3


def test_process_division_by_zero():
    """Verify protection against division by zero when min == max in scaling."""
    response = client.post("/data-api/api/v1/process", json={"data": [5.0, 5.0, 5.0]})
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["mean"] == 5.0
    assert res_data["variance"] == 0.0
    assert res_data["normalized_data"] == [0.0, 0.0, 0.0]
    assert res_data["count"] == 3


def test_process_validation_error():
    """Verify validation error (422) on empty array processing."""
    response = client.post("/data-api/api/v1/process", json={"data": []})
    assert response.status_code == 422
