import logging
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fastapi-app")

app = FastAPI(
    title="DevOps Demo FastAPI App",
    description="A simple API for showcasing CI/CD, Docker, and Kubernetes deployment.",
    version="1.0.0",
)

# Mock database
ITEMS_DB: Dict[int, Dict] = {
    1: {"id": 1, "name": "Kubernetes Book", "price": 29.99, "category": "DevOps"},
    2: {"id": 2, "name": "Docker Mug", "price": 14.99, "category": "Merchandise"},
    3: {"id": 3, "name": "Prometheus Sticker", "price": 1.99, "category": "Observability"},
}

class Item(BaseModel):
    name: str
    price: float
    category: str

class ItemResponse(Item):
    id: int

@app.get("/", tags=["General"])
def read_root():
    return {
        "message": "Welcome to the DevOps Demo FastAPI Application!",
        "status": "Running",
        "documentation": "/docs"
    }

@app.get("/health", tags=["Health"])
def health_check():
    # Simple dependency health check mock
    logger.info("Performing health check...")
    return {
        "status": "healthy",
        "database": "connected",
        "items_count": len(ITEMS_DB)
    }

@app.get("/items", response_model=List[ItemResponse], tags=["Items"])
def get_items(category: Optional[str] = None):
    logger.info(f"Fetching items (category filter: {category})")
    if category:
        return [item for item in ITEMS_DB.values() if item["category"].lower() == category.lower()]
    return list(ITEMS_DB.values())

@app.get("/items/{item_id}", response_model=ItemResponse, tags=["Items"])
def get_item(item_id: int):
    logger.info(f"Fetching item with ID: {item_id}")
    if item_id not in ITEMS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    return ITEMS_DB[item_id]

@app.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED, tags=["Items"])
def create_item(item: Item):
    logger.info(f"Creating new item: {item.name}")
    new_id = max(ITEMS_DB.keys()) + 1 if ITEMS_DB else 1
    new_item = {
        "id": new_id,
        "name": item.name,
        "price": item.price,
        "category": item.category
    }
    ITEMS_DB[new_id] = new_item
    return new_item
