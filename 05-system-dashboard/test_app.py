import os
import pytest
from fastapi.testclient import TestClient

# Set environment variable to use a test database
os.environ["DB_PATH"] = "test_system_health.db"

from app import app
from monitor import init_db, collect_metrics, save_metrics

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    # Initialize the test database
    init_db()
    
    # Save a couple of dummy metrics
    dummy_metrics_1 = {
        "timestamp": "2026-06-17T12:00:00.000000",
        "cpu_percent": 12.5,
        "memory_percent": 45.2,
        "disk_percent": 60.1,
        "net_sent_bytes": 1000,
        "net_recv_bytes": 2000,
        "net_sent_rate": 10.0,
        "net_recv_rate": 20.0,
        "docker_status": 1,
        "gitlab_status": 0,
        "k3s_status": 1,
        "prometheus_status": 0
    }
    
    dummy_metrics_2 = {
        "timestamp": "2026-06-17T12:00:05.000000",
        "cpu_percent": 18.2,
        "memory_percent": 45.8,
        "disk_percent": 60.1,
        "net_sent_bytes": 1500,
        "net_recv_bytes": 3000,
        "net_sent_rate": 100.0,
        "net_recv_rate": 200.0,
        "docker_status": 1,
        "gitlab_status": 1,
        "k3s_status": 1,
        "prometheus_status": 1
    }
    
    save_metrics(dummy_metrics_1)
    save_metrics(dummy_metrics_2)
    
    yield
    
    # Clean up the test database file
    if os.path.exists("test_system_health.db"):
        os.remove("test_system_health.db")

def test_read_dashboard():
    """Verify that root page HTML renders successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "System Health Dashboard" in response.text

def test_api_system_info():
    """Verify system info returns valid keys and values."""
    response = client.get("/api/system/info")
    assert response.status_code == 200
    data = response.json()
    assert "hostname" in data
    assert "os" in data
    assert "cpu_model" in data
    assert "cpu_cores" in data
    assert "total_memory_gb" in data
    assert "total_disk_gb" in data
    assert "uptime" in data
    assert data["cpu_cores"] > 0

def test_api_metrics_current():
    """Verify current metrics returns the latest record inserted."""
    response = client.get("/api/metrics/current")
    assert response.status_code == 200
    data = response.json()
    assert "timestamp" in data
    assert data["cpu_percent"] == 18.2
    assert data["memory_percent"] == 45.8
    assert data["disk_percent"] == 60.1
    assert data["net_sent_bytes"] == 1500
    assert data["docker_status"] == 1
    assert data["gitlab_status"] == 1

def test_api_metrics_history():
    """Verify metrics history returns ordered list of metric records."""
    response = client.get("/api/metrics/history?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    # Check that they are returned in ascending order (older first)
    assert data[0]["cpu_percent"] == 12.5
    assert data[1]["cpu_percent"] == 18.2

def test_collect_metrics():
    """Verify the metrics collection function collects reasonable data types."""
    metrics, net_sent, net_recv, now = collect_metrics()
    assert isinstance(metrics["cpu_percent"], float)
    assert isinstance(metrics["memory_percent"], float)
    assert isinstance(metrics["disk_percent"], float)
    assert isinstance(net_sent, int)
    assert isinstance(net_recv, int)
    assert isinstance(now, float)
