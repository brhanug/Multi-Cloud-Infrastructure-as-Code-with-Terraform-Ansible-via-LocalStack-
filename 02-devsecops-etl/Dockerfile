# Stage 1: Build dependencies
FROM python:3.11-alpine AS builder

WORKDIR /build

COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Hardened Runtime
FROM python:3.11-alpine AS runner

WORKDIR /app

# Copy virtual environment and etl script
COPY --from=builder /opt/venv /opt/venv
COPY etl.py .

# Ensure we use the virtual environment
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Application configurations via Env variables
ENV ETL_DB_PATH="/app/data/weather_data.db"
ENV ETL_API_URL="https://api.open-meteo.com/v1/forecast"

# Create a non-privileged user and directory for database file persistence
RUN addgroup -S etlgroup && adduser -S -G etlgroup etluser
RUN mkdir -p /app/data && chown -R etluser:etlgroup /app

# Run as non-root user (security hardening)
USER etluser

CMD ["python", "etl.py"]
