import os
import sys
import time
import sqlite3
from datetime import datetime

try:
    import psutil
    if os.path.exists('/host/proc'):
        psutil.PROCFS_PATH = '/host/proc'
except ImportError:
    print("Error: psutil not installed. Install with 'pip install psutil'")
    sys.exit(1)

DB_PATH = os.environ.get("DB_PATH", "system_health.db")

def init_db():
    """Initializes the SQLite database and creates the metrics table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            cpu_percent REAL NOT NULL,
            memory_percent REAL NOT NULL,
            disk_percent REAL NOT NULL,
            net_sent_bytes INTEGER NOT NULL,
            net_recv_bytes INTEGER NOT NULL,
            net_sent_rate REAL NOT NULL,
            net_recv_rate REAL NOT NULL,
            docker_status INTEGER NOT NULL,
            gitlab_status INTEGER NOT NULL,
            k3s_status INTEGER NOT NULL,
            prometheus_status INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def check_process_running(keywords):
    """
    Checks if any running process matches any of the given keywords
    in its name or command line arguments.
    """
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            info = proc.info
            name = info.get('name') or ''
            cmdline = info.get('cmdline') or []
            cmd_str = ' '.join(cmdline)
            
            for keyword in keywords:
                if keyword.lower() in name.lower() or keyword.lower() in cmd_str.lower():
                    return 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return 0

def collect_metrics(prev_net_sent=None, prev_net_recv=None, prev_time=None):
    """
    Collects current system metrics and calculates network rates.
    Returns:
        tuple: (metrics_dict, current_net_sent, current_net_recv, current_time)
    """
    # CPU percent (interval=None is non-blocking, returns since last call)
    # The first call to cpu_percent(interval=None) will return 0.0, which is normal.
    cpu_percent = psutil.cpu_percent(interval=None)
    
    # Virtual Memory
    memory_percent = psutil.virtual_memory().percent
    
    # Disk (use /host if mounted, else /)
    disk_path = '/host' if os.path.exists('/host') else '/'
    try:
        disk_percent = psutil.disk_usage(disk_path).percent
    except Exception:
        disk_percent = psutil.disk_usage('/').percent
        
    # Network interface counters (all interfaces aggregated)
    net_io = psutil.net_io_counters()
    net_sent = net_io.bytes_sent
    net_recv = net_io.bytes_recv
    
    now = time.time()
    
    # Calculate transfer rates (bytes/sec)
    net_sent_rate = 0.0
    net_recv_rate = 0.0
    if prev_net_sent is not None and prev_net_recv is not None and prev_time is not None:
        time_delta = now - prev_time
        if time_delta > 0:
            net_sent_rate = max(0.0, (net_sent - prev_net_sent) / time_delta)
            net_recv_rate = max(0.0, (net_recv - prev_net_recv) / time_delta)
            
    # Process Statuses
    docker_status = check_process_running(['dockerd', 'docker-proxy', 'containerd-shim'])
    gitlab_status = check_process_running(['gitlab', 'gitaly', 'sidekiq', 'unicorn', 'puma', 'runsvdir'])
    k3s_status = check_process_running(['k3s', 'k3d', 'kubelet'])
    prometheus_status = check_process_running(['prometheus'])
    
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": cpu_percent,
        "memory_percent": memory_percent,
        "disk_percent": disk_percent,
        "net_sent_bytes": net_sent,
        "net_recv_bytes": net_recv,
        "net_sent_rate": net_sent_rate,
        "net_recv_rate": net_recv_rate,
        "docker_status": docker_status,
        "gitlab_status": gitlab_status,
        "k3s_status": k3s_status,
        "prometheus_status": prometheus_status
    }
    
    return metrics, net_sent, net_recv, now

def save_metrics(metrics):
    """Saves a dictionary of metrics into the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO system_metrics (
            timestamp, cpu_percent, memory_percent, disk_percent,
            net_sent_bytes, net_recv_bytes, net_sent_rate, net_recv_rate,
            docker_status, gitlab_status, k3s_status, prometheus_status
        ) VALUES (
            :timestamp, :cpu_percent, :memory_percent, :disk_percent,
            :net_sent_bytes, :net_recv_bytes, :net_sent_rate, :net_recv_rate,
            :docker_status, :gitlab_status, :k3s_status, :prometheus_status
        )
    """, metrics)
    conn.commit()
    conn.close()

def run_collector(interval=5):
    """Runs the metrics collection loop indefinitely."""
    print(f"Starting metrics collector. Logging to {DB_PATH} every {interval} seconds...")
    init_db()
    
    # Initialize previous values for rates calculation
    _, prev_net_sent, prev_net_recv, prev_time = collect_metrics()
    
    # Wait a small moment to let CPU counter initialize
    time.sleep(0.5)
    
    while True:
        try:
            metrics, prev_net_sent, prev_net_recv, prev_time = collect_metrics(
                prev_net_sent, prev_net_recv, prev_time
            )
            save_metrics(metrics)
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\nCollector stopped by user.")
            break
        except Exception as e:
            print(f"Error in collection loop: {e}", file=sys.stderr)
            time.sleep(interval)

if __name__ == "__main__":
    run_collector()
