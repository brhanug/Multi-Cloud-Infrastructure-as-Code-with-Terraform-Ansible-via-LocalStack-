from fastapi.testclient import TestClient

try:
    from app.main import app
except ModuleNotFoundError:
    from main import app


client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "Running"
    assert "documentation" in response.json()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "database": "connected",
        "items_count": 3
    }

def test_get_items():
    response = client.get("/items")
    assert response.status_code == 200
    assert len(response.json()) == 3
    assert response.json()[0]["name"] == "Kubernetes Book"

def test_get_items_filter():
    response = client.get("/items?category=Observability")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Prometheus Sticker"

def test_get_item_not_found():
    response = client.get("/items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item with ID 999 not found"

def test_create_item():
    new_item = {
        "name": "Helm Mug",
        "price": 12.50,
        "category": "Merchandise"
    }
    response = client.post("/items", json=new_item)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Helm Mug"
    assert data["price"] == 12.50
    assert "id" in data

    # Verify it was added
    get_response = client.get(f"/items/{data['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Helm Mug"
