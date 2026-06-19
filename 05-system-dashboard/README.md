# Linux System Health Dashboard & Monitoring Daemon

A lightweight, premium, containerized system health monitoring dashboard. This repository contains a background monitoring daemon that gathers system metrics (CPU load, memory load, disk utilization, and network throughput rates) and monitors daemon service activities, exposing them through a FastAPI REST API and displaying them on a modern, real-time glassmorphic dashboard.

---

## 🚀 Key Features

*   **Background Collector**: A lightweight Python monitoring daemon using `psutil` that records time-series resource stats to a local SQLite database every 5 seconds.
*   **Host Namespace Inspection**: Safely reads `/proc` and `/sys` of the host system programmatically from within an isolated container environment.
*   **Daemon Service Status Check**: Scans active processes to report the health of critical system services (`docker`, `gitlab`, `k3s/k3d`, `prometheus`).
*   **Glassmorphic Frontend**: A frosted-glass visual UI featuring:
    *   Dynamic, live-updating line charts powered by **Chart.js**.
    *   Pulsating service status badges (Active/Inactive).
    *   Manual refresh button with micro-animations.
    *   Adjustable auto-refresh intervals.
*   **Hardened Containerization**: A secure multi-stage Alpine Dockerfile executing under a non-root system user (`dashuser`, UID 1000).

---

## 🛠️ Prerequisites

*   **Python**: Python 3.9 or higher (if running locally without containers).
*   **Docker**: For running containerized system monitoring.

---

## 📦 Quick Start Guide

### Option A: Running with Docker (Recommended)

To allow the containerized application to monitor host metrics, mount the host's `/proc` and `/sys` filesystems:

```bash
# 1. Build the Docker image
docker build -t system-dashboard .

# 2. Run the container with host filesystem mounts
docker run -d \
  --name system-monitor \
  -p 8085:8000 \
  -v /proc:/host/proc:ro \
  -v /sys:/host/sys:ro \
  system-dashboard
```

Once running, access the dashboard at:
👉 **[http://localhost:8085](http://localhost:8085)**

---

### Option B: Local Python Development

If you prefer to run the daemon directly on your host machine:

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the FastAPI server (starts the background collector automatically)
python app.py
```

Access the dashboard at:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 📊 REST API Endpoints

The FastAPI server exposes the following endpoints:

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Renders the HTML templates dashboard UI. |
| `/api/system/info` | `GET` | Returns static host details (OS, logical cores, memory/disk size, uptime). |
| `/api/metrics/current` | `GET` | Returns the single latest metrics entry from the database. |
| `/api/metrics/history` | `GET` | Returns time-series history records (up to last 100 entries). |

### Example Metrics JSON Response:
```json
{
  "id": 142,
  "timestamp": "2026-06-17T19:10:17.739364",
  "cpu_percent": 3.4,
  "memory_percent": 65.8,
  "disk_percent": 1.4,
  "net_sent_bytes": 126480,
  "net_recv_bytes": 1172901,
  "net_sent_rate": 25.40,
  "net_recv_rate": 114.25,
  "docker_status": 1,
  "gitlab_status": 1,
  "k3s_status": 1,
  "prometheus_status": 1
}
```

---

## 🧪 Running Unit Tests

Unit tests are included to verify database schema initialization, metrics collection metrics, and FastAPI routing:

```bash
# Run pytest test suite locally
pytest test_app.py
```
