import os
import sqlite3
import time
import platform
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import psutil
# Setup PROCFS_PATH if running inside container with mounted host filesystem
if os.path.exists('/host/proc'):
    psutil.PROCFS_PATH = '/host/proc'
from monitor import run_collector, DB_PATH, init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database
    init_db()
    
    # Start the collector thread
    collector_thread = threading.Thread(target=run_collector, kwargs={"interval": 5}, daemon=True)
    collector_thread.start()
    
    yield
    # No cleanup required as threads are daemonized

app = FastAPI(
    title="System Health Monitor",
    description="A lightweight Linux system health dashboard and REST API.",
    version="1.0.0",
    lifespan=lifespan
)

# Template configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Helper functions for system details
def get_host_hostname():
    if os.path.exists('/host/etc/hostname'):
        try:
            with open('/host/etc/hostname', 'r') as f:
                return f.read().strip()
        except Exception:
            pass
    import socket
    return socket.gethostname()

def get_uptime():
    uptime_file = '/host/proc/uptime' if os.path.exists('/host/proc/uptime') else '/proc/uptime'
    if os.path.exists(uptime_file):
        try:
            with open(uptime_file, 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                return uptime_seconds
        except Exception:
            pass
    try:
        return time.time() - psutil.boot_time()
    except Exception:
        return 0.0

def get_cpu_model():
    cpuinfo_file = '/host/proc/cpuinfo' if os.path.exists('/host/proc/cpuinfo') else '/proc/cpuinfo'
    if os.path.exists(cpuinfo_file):
        try:
            with open(cpuinfo_file, 'r') as f:
                for line in f:
                    if 'model name' in line:
                        return line.split(':', 1)[1].strip()
        except Exception:
            pass
    return platform.processor() or "Unknown CPU Processor"

@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    """Renders the system health dashboard."""
    return templates.TemplateResponse(request, "index.html")

@app.get("/api/system/info")
async def get_system_info():
    """Returns static information about the host system."""
    disk_path = '/host' if os.path.exists('/host') else '/'
    try:
        disk_info = psutil.disk_usage(disk_path)
        disk_total = disk_info.total
    except Exception:
        disk_info = psutil.disk_usage('/')
        disk_total = disk_info.total

    mem_total = psutil.virtual_memory().total
    
    # Format Uptime
    uptime_sec = get_uptime()
    days = int(uptime_sec // (24 * 3600))
    hours = int((uptime_sec % (24 * 3600)) // 3600)
    minutes = int((uptime_sec % 3600) // 60)
    uptime_str = f"{days}d {hours}h {minutes}m"

    return {
        "hostname": get_host_hostname(),
        "os": f"{platform.system()} {platform.release()}",
        "cpu_model": get_cpu_model(),
        "cpu_cores": psutil.cpu_count(logical=True),
        "cpu_physical_cores": psutil.cpu_count(logical=False) or psutil.cpu_count(logical=True),
        "total_memory_gb": round(mem_total / (1024**3), 2),
        "total_disk_gb": round(disk_total / (1024**3), 2),
        "uptime": uptime_str,
        "uptime_seconds": uptime_sec
    }

@app.get("/api/metrics/current")
async def get_current_metrics():
    """Retrieves the single latest metrics entry from the SQLite DB."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM system_metrics 
        ORDER BY id DESC LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {"error": "No metrics available yet."}
    
    return dict(row)

@app.get("/api/metrics/history")
async def get_metrics_history(limit: int = 100):
    """Retrieves a historical list of metrics, ordered from oldest to newest."""
    # Enforce reasonable limit
    limit = min(max(1, limit), 1000)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM (
            SELECT * FROM system_metrics 
            ORDER BY id DESC LIMIT ?
        ) ORDER BY id ASC
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
