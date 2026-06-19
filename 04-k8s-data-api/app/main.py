import logging
import os
import sys
from datetime import datetime
from typing import List

from fastapi import FastAPI, status
from pydantic import BaseModel, Field

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("data-api")

# Define the main application (for root endpoints like healthz)
app = FastAPI(
    title="Data/ML Processing API Root",
    description="Root application hosting liveness probes.",
    version="1.0.0",
)

# Initialize OpenTelemetry Tracing
otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger-collector.istio-system.svc.cluster.local:4317")
resource = Resource(attributes={SERVICE_NAME: "data-api"})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

FastAPIInstrumentor.instrument_app(app)

# Define the sub-application (to mount under /data-api prefix)
sub_app = FastAPI(
    title="Data/ML Processing API",
    description="A microservice for text sentiment prediction and numerical data processing.",
    version="1.0.0",
)


# Input/Output schemas
class PredictRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        description="Input text to perform mock sentiment prediction on.",
    )


class PredictResponse(BaseModel):
    sentiment: str = Field(
        ..., description="Predicted sentiment class (positive, negative, or neutral)."
    )
    confidence: float = Field(
        ..., description="Model confidence score between 0.0 and 1.0."
    )
    processed_at: str = Field(
        ..., description="ISO timestamp of when request was processed."
    )


class ProcessRequest(BaseModel):
    data: List[float] = Field(
        ...,
        min_length=1,
        description="List of numerical values to analyze and normalize.",
    )


class ProcessResponse(BaseModel):
    mean: float = Field(..., description="Mean of the numerical list.")
    variance: float = Field(..., description="Variance of the numerical list.")
    normalized_data: List[float] = Field(
        ..., description="Min-Max scaled list between 0.0 and 1.0."
    )
    count: int = Field(..., description="Total count of processed elements.")


@app.get("/healthz", status_code=status.HTTP_200_OK)
def health_check():
    """Liveness and readiness probe endpoint for Kubernetes."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@sub_app.post(
    "/api/v1/predict", response_model=PredictResponse, status_code=status.HTTP_200_OK
)
def predict(request: PredictRequest):
    """Predicts text sentiment using keyword-matching logic to simulate ML inference."""
    logger.info(f"Received prediction request for text of length: {len(request.text)}")
    text_lower = request.text.lower()

    # Simple deterministic heuristic mapping to simulate ML model inference
    positive_words = [
        "love",
        "like",
        "great",
        "awesome",
        "excellent",
        "beautiful",
        "good",
        "fast",
        "easy",
    ]
    negative_words = [
        "hate",
        "dislike",
        "bad",
        "terrible",
        "worst",
        "ugly",
        "slow",
        "hard",
        "error",
    ]

    pos_count = sum(word in text_lower for word in positive_words)
    neg_count = sum(word in text_lower for word in negative_words)

    if pos_count > neg_count:
        sentiment = "positive"
        confidence = min(0.5 + (pos_count - neg_count) * 0.1, 0.99)
    elif neg_count > pos_count:
        sentiment = "negative"
        confidence = min(0.5 + (neg_count - pos_count) * 0.1, 0.99)
    else:
        sentiment = "neutral"
        confidence = 0.5

    return PredictResponse(
        sentiment=sentiment,
        confidence=round(confidence, 4),
        processed_at=datetime.utcnow().isoformat(),
    )


@sub_app.post(
    "/api/v1/process", response_model=ProcessResponse, status_code=status.HTTP_200_OK
)
def process(request: ProcessRequest):
    """Calculates summary statistics and performs Min-Max scaling normalization on numerical arrays."""
    logger.info(
        f"Received processing request for data list of size: {len(request.data)}"
    )
    data = request.data
    n = len(data)

    # Calculate stats
    mean = sum(data) / n
    variance = sum((x - mean) ** 2 for x in data) / n

    # Min-Max normalization
    data_min = min(data)
    data_max = max(data)
    span = data_max - data_min

    if span > 0:
        normalized = [(x - data_min) / span for x in data]
    else:
        normalized = [0.0] * n  # Avoid division by zero if all values are equal

    return ProcessResponse(
        mean=round(mean, 4),
        variance=round(variance, 4),
        normalized_data=[round(x, 4) for x in normalized],
        count=n,
    )


# Mount the sub-application under the /data-api path
app.mount("/data-api", sub_app)
