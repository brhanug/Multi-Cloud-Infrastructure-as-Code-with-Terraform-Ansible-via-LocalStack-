# DevOps, Cloud-Native, & DevSecOps Portfolio

Welcome to the **DevOps & Cloud-Native Portfolio** repository! This monorepo contains five integrated engineering projects demonstrating modern practices in containerization, local Kubernetes orchestration, automated ETL pipelines, infrastructure monitoring, and security integration.

---

## 🛠️ Portfolio Overview

Below is the directory mapping and technical stack for the 5 projects contained within this workspace:

| Project | Folder | Description | Tech Stack |
| :--- | :--- | :--- | :--- |
| **Project 1** | [`/app`](file:///Users/brhanu/Documents/Projects/app) | **Kubernetes-Deployed API** (FastAPI app containerized and running under non-privileged configurations inside k3d). | FastAPI, Docker, Kubernetes (`k3d`), Helm |
| **Project 2** | [`/02-devsecops-etl`](file:///Users/brhanu/Documents/Projects/02-devsecops-etl) | **DevSecOps Ingestion Pipeline** (Automated weather data extraction, transformed/validated using Pydantic, and ingested into SQLite). | Python, Pydantic, SQLite, Bandit, Ruff |
| **Project 3** | [`/03-monitoring`](file:///Users/brhanu/Documents/Projects/03-monitoring) | **IaC Monitoring Stack** (Telemetry ingestion for ETL scripts using Pushgateway, Prometheus scraping, and Grafana visualization). | Docker Compose, Prometheus, Grafana |
| **Project 4** | [`/04-k8s-data-api`](file:///Users/brhanu/Documents/Projects/04-k8s-data-api) | **Kubernetes ML/Data API** (FastAPI mock ML sentiment inference and normalizer deployed via a customized Helm chart with liveness/readiness probes). | FastAPI, Helm Charts, Traefik Ingress |
| **Project 5** | [`/05-system-dashboard`](file:///Users/brhanu/Documents/Projects/05-system-dashboard) | **Linux System Health Dashboard** (Background monitoring collector that writes system metrics and service daemons to SQLite, serving a real-time glassmorphic UI). | FastAPI, psutil, SQLite, Chart.js |
| **Project 6** | [`/06-gitops`](file:///Users/brhanu/Documents/Projects/06-gitops) | **Declarative GitOps CD** (ArgoCD gitops-based continuous delivery and automated sync/self-healing, using Sealed Secrets for encryption). | ArgoCD, Sealed Secrets (`kubeseal`), Kubernetes |
| **Project 7** | [`/07-multi-cloud-iac`](file:///Users/brhanu/Documents/Projects/07-multi-cloud-iac) | **Multi-Cloud IaC & Configuration** (Terraform infrastructure provisioning in LocalStack and server hardening & configuration using Ansible). | Terraform, Ansible, LocalStack, Docker |
| **Project 8** | [`/08-mesh-tracing`](file:///Users/brhanu/Documents/Projects/08-mesh-tracing) | **Cloud-Native Microservices Mesh & Distributed Tracing** (Istio mesh integration with OpenTelemetry and Jaeger trace visualizer). | Istio, OpenTelemetry, Jaeger, FastAPI, Kubernetes |
| **Project 9** | [`/09-chaos-engineering`](file:///Users/brhanu/Documents/Projects/09-chaos-engineering) | **SRE Chaos Engineering Pipeline** (Chaos Mesh deployment executing Pod failure recovery and Network latency injection experiments). | Chaos Mesh, Kubernetes, Helm |

---

## ⚙️ Base Infrastructure & Environment

To support local pipelines and deployments, this project runs a suite of infrastructure containers:
1. **Local GitLab CE Server & Runner**: Running at [http://localhost:8989](http://localhost:8989) (credentials: `root` / `xY9$kL2#mP5*qT1!`) mapping to container registry `localhost:5005`.
2. **Local k3d Kubernetes Cluster**: Active on host port `8081` mapping internal ingress to Traefik.
3. **Local Monitoring Network**: Bridged network containing the Prometheus and Grafana instances.

---

## 🚀 Interactive Demo & Verification Guide

Follow these instructions to verify and run each of the 5 projects:

### 1️⃣ Project 1: FastAPI Application on Kubernetes
* **Deployment**: Deployed via Helm to k3d.
* **Test Endpoints**:
  * API Health Status: [http://localhost:8081/health](http://localhost:8081/health)
  * Preloaded Mock DB Items: [http://localhost:8081/items](http://localhost:8081/items)
* **Verify**:
  ```bash
  curl -s http://localhost:8081/health
  curl -s http://localhost:8081/items
  ```

### 2️⃣ Project 2 & 3: Weather ETL & Prometheus Telemetry Ingestion
* **Deployment**: Python script with Docker Compose monitoring stack.
* **Launch Monitoring Stack**:
  ```bash
  cd 03-monitoring
  docker-compose up -d
  ```
* **Trigger ETL Pipeline Ingestion**:
  ```bash
  # Execute the ETL pipeline and push statistics to Prometheus Pushgateway
  export ETL_PUSHGATEWAY_URL=http://localhost:9091
  python3 02-devsecops-etl/etl.py
  ```
* **Verify Dashboards**:
  * **Grafana**: Visit [http://localhost:3000](http://localhost:3000) (Credentials: `admin` / `admin`) to view the Weather ETL execution statistics.
  * **Prometheus targets**: Visit [http://localhost:9090](http://localhost:9090).
  * **Pushgateway metrics**: Visit [http://localhost:9091](http://localhost:9091).

### 3️⃣ Project 4: Kubernetes Mock ML/Data API
* **Deployment**: Deployed using the customized Helm chart at `/04-k8s-data-api/helm/data-api`.
* **Verify Endpoints**:
  * Health status check: [http://localhost:8081/data-api/healthz](http://localhost:8081/data-api/healthz)
  * ML Sentiment Inference:
    ```bash
    curl -X POST http://localhost:8081/data-api/api/v1/predict \
      -H "Content-Type: application/json" \
      -d '{"text": "Advanced Agentic Coding is extremely fast!"}'
    ```
  * Min-Max Normalization Processing:
    ```bash
    curl -X POST http://localhost:8081/data-api/api/v1/process \
      -H "Content-Type: application/json" \
      -d '{"data": [10.0, 25.0, 50.0, 100.0]}'
    ```

### 4️⃣ Project 5: Linux System Health Dashboard
* **Deployment**: Containerized daemon running as non-root user `dashuser` with read-only host proc mounts.
* **Launch locally**:
  ```bash
  docker run -d \
    --name system-monitor \
    -p 8085:8000 \
    -v /proc:/host/proc:ro \
    -v /sys:/host/sys:ro \
    system-dashboard
  ```
* **Verify**:
  * **Web Dashboard**: Access the interactive glassmorphic dark-theme dashboard UI at [http://localhost:8085](http://localhost:8085).
  * **Current stats JSON**: Visit [http://localhost:8085/api/metrics/current](http://localhost:8085/api/metrics/current) to see realtime metrics and host daemon status flags.

### 5️⃣ Project 6: Declarative GitOps CD with ArgoCD
* **Deployment**: ArgoCD controller manages deployments inside k3d.
* **Verify**:
  * Access the ArgoCD dashboard at [http://localhost:8080](http://localhost:8080) (using credentials set up during installation).
  * Inspect the sync status and self-healing status of `fastapi-app` and `data-api` applications.
  * Check the sealed secret configuration mapping under `06-gitops/secrets/gitlab-registry-credentials-sealed.yaml`.

### 6️⃣ Project 7: Multi-Cloud Infrastructure as Code with Terraform & Ansible (via LocalStack)
* **Deployment**: Local AWS Emulation (LocalStack) and Ubuntu target host container.
* **Execution & Demo**:
  * Execute the full demo run (starting containers, applying Terraform, running Ansible playbooks):
    ```bash
    ./07-multi-cloud-iac/demo.sh
    ```
  * Verify mock S3 bucket creation inside LocalStack:
    ```bash
    aws --endpoint-url=http://localhost:4566 s3 ls
    ```

### 7️⃣ Project 8: Cloud-Native Microservices Mesh & Distributed Tracing
* **Deployment**: Istio Service Mesh, OpenTelemetry tracing SDK, and Jaeger collector in k3d.
* **Verify**:
  * Trigger outbound multi-hop sentiment query from `fastapi-app` to `data-api`:
    ```bash
    curl -s "http://localhost:8081/items/sentiment?text=Advanced%20Agentic%20Coding%20is%20extremely%20fast!"
    ```
  * Forward the Jaeger UI dashboard to host port `16686`:
    ```bash
    kubectl port-forward -n istio-system service/tracing 16686:80
    ```
  * Access Jaeger at [http://localhost:16686/jaeger](http://localhost:16686/jaeger) and trace telemetry flow across `fastapi-app` and `data-api`.

### 8️⃣ Project 9: SRE Chaos Engineering Pipeline (Chaos Mesh)
* **Deployment**: Chaos Mesh operator engine targeting the k3d nodes containerd socket.
* **Verify**:
  * Execute the automated chaos suite:
    ```bash
    ./09-chaos-engineering/demo.sh
    ```
  * Verify ReplicaSet healing by watching Kubernetes replace pods in real-time.
  * Verify Network Latency injection triggers and that response time spikes by 250ms+.

---

## 🔒 Automated CI/CD & Security Pipelines

All modifications pushed to the `main` branch trigger a comprehensive pipeline in our local GitLab CE runner:
1. **Lint Stage (`ruff`, `terraform validate`, `ansible-lint`)**: Checks Python style, Terraform syntax, and Ansible playbook configurations.
2. **SAST Scan Stage (`bandit`)**: Identifies potential security issues in Python scripts.
3. **Test Stage (`pytest`, `terraform plan`)**: Runs python unit testing suites and generates infrastructure plan outputs using local LocalStack mock environments.
4. **Build Stage (`docker build`)**: Packages each application using hardened Alpine base structures.
5. **Vulnerability Scan Stage (`trivy`)**: Scans built images for **CRITICAL** CVE vulnerabilities, breaking the build if security issues are identified.
6. **Release Stage (`docker push`)**: Deploys the secure containers to our local registry.
7. **Deploy Stage (`helm upgrade`)**: Applies Helm charts dynamically into our k3d Kubernetes cluster.

