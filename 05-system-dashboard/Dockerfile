# Stage 1: Build dependencies
FROM python:3.11-alpine AS builder

WORKDIR /build

COPY requirements.txt .

# Install compile tools needed for psutil build
RUN apk add --no-cache gcc musl-dev linux-headers python3-dev

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Hardened Runtime
FROM python:3.11-alpine AS runner

WORKDIR /app

# Copy virtualenv and application components
COPY --from=builder /opt/venv /opt/venv
COPY monitor.py .
COPY app.py .
COPY templates/ templates/

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non-privileged user and group
RUN addgroup -g 1000 -S dashgroup && adduser -u 1000 -S -G dashgroup dashuser

# Ensure writing permissions for SQLite database file
RUN chown -R dashuser:dashgroup /app

USER dashuser

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
