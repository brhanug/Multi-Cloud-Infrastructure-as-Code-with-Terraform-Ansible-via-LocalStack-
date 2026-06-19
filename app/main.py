import logging
import os
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import httpx

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.propagate import inject

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fastapi-app")

app = FastAPI(
    title="DevOps Demo FastAPI App",
    description="A simple API for showcasing CI/CD, Docker, and Kubernetes deployment.",
    version="1.0.0",
)

# Initialize OpenTelemetry Tracing
otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger-collector.istio-system.svc.cluster.local:4317")
resource = Resource(attributes={SERVICE_NAME: "fastapi-app"})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

FastAPIInstrumentor.instrument_app(app)


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

@app.get("/items/sentiment", tags=["Items"])
def get_items_sentiment(text: str):
    logger.info(f"Querying sentiment prediction for text: {text}")
    data_api_url = os.getenv("DATA_API_URL", "http://data-api/data-api/api/v1/predict")
    
    headers = {}
    inject(headers)
    
    try:
        response = httpx.post(
            data_api_url,
            json={"text": text},
            headers=headers,
            timeout=5.0
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Downstream service returned error: {response.text}"
            )
        return response.json()
    except Exception as e:
        logger.error(f"Error querying data-api: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query downstream data-api: {str(e)}"
        )


@app.get("/items/{item_id}", response_model=ItemResponse, tags=["Items"])
def get_item(item_id: int):
    logger.info(f"Fetching item with ID: {item_id}")
    if item_id not in ITEMS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found"
        )
    return ITEMS_DB[item_id]

@app.post(
    "/items",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Items"],
)
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

