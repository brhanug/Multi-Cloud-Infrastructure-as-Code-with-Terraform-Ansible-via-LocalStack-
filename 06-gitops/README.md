# GitOps Continuous Delivery with ArgoCD & Sealed Secrets

This directory contains the declarative GitOps configuration for our Kubernetes applications. It configures **ArgoCD** to automatically reconcile the state of the cluster with our GitLab repository, and integrates **Bitnami Sealed Secrets** to encrypt sensitive credentials safely inside Git.

---

## 📂 Directory Structure

*   [`apps/`](file:///Users/brhanu/Documents/Projects/06-gitops/apps)
    *   [`fastapi-app.yaml`](file:///Users/brhanu/Documents/Projects/06-gitops/apps/fastapi-app.yaml): Declarative ArgoCD Application for the Project 1 FastAPI application.
    *   [`data-api.yaml`](file:///Users/brhanu/Documents/Projects/06-gitops/apps/data-api.yaml): Declarative ArgoCD Application for the Project 4 Mock ML/Data API.
*   [`secrets/`](file:///Users/brhanu/Documents/Projects/06-gitops/secrets)
    *   [`gitlab-registry-credentials-sealed.yaml`](file:///Users/brhanu/Documents/Projects/06-gitops/secrets/gitlab-registry-credentials-sealed.yaml): A kubeseal-encrypted SealedSecret. The Sealed Secrets controller inside the cluster automatically decrypts this to create the standard `gitlab-registry-credentials` secret, allowing pods to authenticate with the local registry.

---

## ⚙️ How It Works

### 1. Controllers Deployment
The ArgoCD and Sealed Secrets controllers are running inside the k3d cluster:
*   **ArgoCD namespace**: `argocd`
*   **Sealed Secrets namespace**: `kube-system`

### 2. Sealed Secret Generation
To recreate or generate new sealed secrets, use the local `kubeseal` binary installed in `bin/`:
```bash
# 1. Create a dry-run standard secret
kubectl create secret docker-registry gitlab-registry-credentials \
  --docker-server=localhost:5005 \
  --docker-username=root \
  --docker-password='YOUR_PASSWORD' \
  --dry-run=client -o yaml > temp-secret.yaml

# 2. Seal the secret using the controller key
bin/kubeseal --controller-name=sealed-secrets-controller --controller-namespace=kube-system < temp-secret.yaml > gitlab-registry-credentials-sealed.yaml

# 3. Safely delete the plain-text secret
rm temp-secret.yaml
```

---

## 🛠️ Verification & Demo

### 1. Access the ArgoCD Dashboard
To view the ArgoCD visual UI, port forward the service to host port `8082`:
```bash
kubectl port-forward svc/argocd-server -n argocd 8082:443
```
👉 Access: **[https://localhost:8082](https://localhost:8082)**
*   **Username**: `admin`
*   **Password**: Retrieve the auto-generated password by running:
    ```bash
    kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
    ```

### 2. Test GitOps Reconciliation (Scale Pods)
1. Edit `/helm/fastapi-app/values.yaml` and change `replicaCount` from `1` to `2`.
2. Commit and push the changes to GitLab.
3. ArgoCD will instantly detect the change, synchronize, and spawn a second pod in the cluster!
