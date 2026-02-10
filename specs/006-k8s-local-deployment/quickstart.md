# Phase IV Quickstart: Local Kubernetes Deployment

**Feature**: 006-k8s-local-deployment
**Date**: 2026-02-09

## Prerequisites

Before starting, ensure you have the following installed:

| Tool | Version | Installation |
|------|---------|--------------|
| Docker | 20.10+ | [docker.com](https://docs.docker.com/get-docker/) |
| Minikube | 1.30+ | `brew install minikube` or [minikube.sigs.k8s.io](https://minikube.sigs.k8s.io/docs/start/) |
| Helm | 3.x | `brew install helm` or [helm.sh](https://helm.sh/docs/intro/install/) |
| kubectl | 1.28+ | `brew install kubectl` or [kubernetes.io](https://kubernetes.io/docs/tasks/tools/) |
| kubectl-ai | latest | `kubectl krew install ai` |

## Quick Deploy (5 Minutes)

### Step 1: Start Minikube

```bash
# Start Minikube with required resources
minikube start --driver=docker --cpus=2 --memory=4096

# Enable ingress addon
minikube addons enable ingress

# Verify cluster is running
kubectl cluster-info
```

### Step 2: Build Docker Images

```bash
# Point Docker to Minikube's registry
eval $(minikube docker-env)

# Build backend image
cd backend
docker build -t ai-wealth-companion/backend:dev .

# Build frontend image
cd ../frontend
docker build -t ai-wealth-companion/frontend:dev .
```

### Step 3: Create Secrets

```bash
# Create namespace
kubectl create namespace ai-wealth

# Create secrets (replace with your values)
kubectl create secret generic db-credentials \
  --namespace=ai-wealth \
  --from-literal=DATABASE_URL='postgresql+asyncpg://user:pass@host/db'

kubectl create secret generic jwt-secret \
  --namespace=ai-wealth \
  --from-literal=JWT_SECRET_KEY='your-super-secret-key'

kubectl create secret generic ai-credentials \
  --namespace=ai-wealth \
  --from-literal=GEMINI_API_KEY='your-gemini-api-key' \
  --from-literal=OPENAI_API_KEY='optional-openai-key'

kubectl create secret generic oauth-credentials \
  --namespace=ai-wealth \
  --from-literal=GOOGLE_CLIENT_ID='your-google-client-id' \
  --from-literal=GOOGLE_CLIENT_SECRET='your-google-secret' \
  --from-literal=GITHUB_CLIENT_ID='your-github-client-id' \
  --from-literal=GITHUB_CLIENT_SECRET='your-github-secret'
```

### Step 4: Deploy with Helm

```bash
# Navigate to project root
cd /path/to/hackathone2

# Install the Helm chart
helm install ai-wealth ./helm/ai-wealth-companion \
  --namespace ai-wealth \
  --values ./helm/ai-wealth-companion/values-dev.yaml

# Wait for pods to be ready
kubectl wait --for=condition=ready pod \
  --all \
  --namespace=ai-wealth \
  --timeout=300s
```

### Step 5: Access the Application

```bash
# Get Minikube IP
minikube ip

# Add to /etc/hosts
echo "$(minikube ip) ai-wealth.local" | sudo tee -a /etc/hosts

# Open in browser
open http://ai-wealth.local
```

---

## Verify Deployment

### Check Pod Status

```bash
kubectl get pods -n ai-wealth
```

Expected output:
```
NAME                          READY   STATUS    RESTARTS   AGE
backend-xxx-yyy               1/1     Running   0          2m
frontend-xxx-yyy              1/1     Running   0          2m
mcp-server-xxx-yyy            1/1     Running   0          2m
```

### Check Services

```bash
kubectl get svc -n ai-wealth
```

Expected output:
```
NAME         TYPE        CLUSTER-IP      PORT(S)    AGE
backend      ClusterIP   10.96.xxx.xxx   8000/TCP   2m
frontend     ClusterIP   10.96.xxx.xxx   3000/TCP   2m
mcp-server   ClusterIP   10.96.xxx.xxx   8080/TCP   2m
```

### Test Backend Health

```bash
kubectl port-forward svc/backend 8000:8000 -n ai-wealth &
curl http://localhost:8000/health
```

---

## AI-Operated Commands (kubectl-ai)

kubectl-ai enables natural language interaction with your Kubernetes cluster.

### Installation

```bash
# Install krew plugin manager (if not installed)
# See: https://krew.sigs.k8s.io/docs/user-guide/setup/install/

# Install kubectl-ai
kubectl krew install ai

# Verify installation
kubectl ai --help
```

### kubectl-ai Cheat Sheet

| Task | Command |
|------|---------|
| Cluster health | `kubectl ai "what is the cluster health in ai-wealth namespace?"` |
| Pod status | `kubectl ai "show all pods in ai-wealth namespace"` |
| Debug failure | `kubectl ai "why is the backend pod failing?"` |
| View logs | `kubectl ai "show me the last 50 logs from backend"` |
| Restart service | `kubectl ai "restart the frontend deployment in ai-wealth"` |
| Scale deployment | `kubectl ai "scale backend to 3 replicas in ai-wealth"` |
| Resource usage | `kubectl ai "what are the resource limits for backend?"` |
| Check secrets | `kubectl ai "list all secrets in ai-wealth namespace"` |
| Ingress status | `kubectl ai "describe the ingress in ai-wealth"` |
| Events | `kubectl ai "show recent events in ai-wealth namespace"` |

### Common Queries

```bash
# Cluster Health Check
kubectl ai "what is the cluster health in ai-wealth namespace?"

# Debug Failing Pod
kubectl ai "why is the backend pod failing?"

# Restart Service
kubectl ai "restart the frontend deployment in ai-wealth"

# View Logs
kubectl ai "show me the last 50 logs from backend"

# Check Resource Usage
kubectl ai "which pods are using the most memory in ai-wealth?"

# Network Troubleshooting
kubectl ai "can frontend reach backend service?"
```

---

## kagent AI Workload Management

kagent provides intelligent AI agent workload governance with automatic scaling and recovery.

### Features

- **Health Monitoring**: Continuous monitoring of AI agent pods
- **Auto-Restart**: Failed pods restart within 30 seconds (SC-005)
- **Intelligent Scaling**: Scale based on workload patterns
- **Policy-Based Governance**: Define scaling and recovery policies

### Installation (Optional)

```bash
# Install kagent operator (if available)
kubectl apply -f https://github.com/kagent-dev/kagent/releases/latest/download/kagent.yaml

# Or via the setup script
./scripts/k8s-setup.sh
```

### Scaling Configuration

The Helm chart includes HPA (Horizontal Pod Autoscaler) for automatic scaling:

```yaml
# Enable in values.yaml or values-dev.yaml
autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 3
  targetCPUUtilization: 70
```

### Manual Scaling

```bash
# Scale backend to 3 replicas
kubectl scale deployment/backend --replicas=3 -n ai-wealth

# Enable HPA
helm upgrade ai-wealth ./helm/ai-wealth-companion \
  --namespace ai-wealth \
  --set autoscaling.enabled=true
```

### Health Probes

All services have liveness and readiness probes configured:

| Service | Liveness | Readiness | Restart Threshold |
|---------|----------|-----------|-------------------|
| Backend | `/health` | `/health/ready` | 3 failures |
| Frontend | `/` | `/` | 3 failures |
| MCP Server | `/health` | `/health` | 3 failures |

Expected restart time for failed pods: **< 30 seconds**

---

## Common Operations

### Update Deployment

```bash
# Rebuild image
docker build -t ai-wealth-companion/backend:dev ./backend

# Rollout restart
kubectl rollout restart deployment/backend -n ai-wealth
```

### Scale Deployment

```bash
# Scale to 3 replicas
kubectl scale deployment/backend --replicas=3 -n ai-wealth
```

### View Logs

```bash
# Backend logs
kubectl logs -f deployment/backend -n ai-wealth

# Frontend logs
kubectl logs -f deployment/frontend -n ai-wealth
```

### Uninstall

```bash
# Remove Helm release
helm uninstall ai-wealth -n ai-wealth

# Delete namespace
kubectl delete namespace ai-wealth

# Stop Minikube
minikube stop
```

---

## Troubleshooting

### Pod CrashLoopBackOff

```bash
# Check pod events
kubectl describe pod <pod-name> -n ai-wealth

# Check logs
kubectl logs <pod-name> -n ai-wealth --previous
```

### ImagePullBackOff

```bash
# Ensure Minikube docker env is set
eval $(minikube docker-env)

# Verify image exists
docker images | grep ai-wealth-companion
```

### Ingress Not Working

```bash
# Check ingress status
kubectl get ingress -n ai-wealth

# Verify ingress controller
kubectl get pods -n ingress-nginx
```

### Database Connection Failed

```bash
# Verify secret exists
kubectl get secret db-credentials -n ai-wealth -o yaml

# Check DATABASE_URL format
kubectl get secret db-credentials -n ai-wealth -o jsonpath='{.data.DATABASE_URL}' | base64 -d
```

---

## Resource Monitoring

```bash
# View resource usage
kubectl top pods -n ai-wealth

# View node resources
kubectl top nodes
```

---

## Service Communication Architecture

All inter-service communication uses Kubernetes Services (ClusterIP) for service mesh readiness.

### Service DNS Names

| Service | DNS Name | Port |
|---------|----------|------|
| Backend | `backend.ai-wealth.svc.cluster.local` | 8000 |
| Frontend | `frontend.ai-wealth.svc.cluster.local` | 3000 |
| MCP Server | `mcp-server.ai-wealth.svc.cluster.local` | 8080 |

### Communication Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      Ingress (ai-wealth.local)               │
│                    ┌─────────┬─────────┐                     │
│                    │  /api   │   /     │                     │
│                    └────┬────┴────┬────┘                     │
│                         │         │                          │
│                         ▼         ▼                          │
│ ┌───────────────────────────┐  ┌───────────────────────────┐│
│ │   Backend Service         │  │   Frontend Service        ││
│ │   (backend:8000)          │  │   (frontend:3000)         ││
│ └───────────┬───────────────┘  └───────────────────────────┘│
│             │                                                │
│             ▼                                                │
│ ┌───────────────────────────┐                                │
│ │   MCP Server Service      │                                │
│ │   (mcp-server:8080)       │                                │
│ └───────────────────────────┘                                │
│                                                              │
│         All communication via K8s Service DNS                │
└─────────────────────────────────────────────────────────────┘
```

### Environment Configuration

Services discover each other via ConfigMap:

```yaml
# Set in helm/ai-wealth-companion/values.yaml
config:
  backendUrl: "http://backend:8000"
  mcpServerUrl: "http://mcp-server:8080"
```

---

## Using Helper Scripts

The `scripts/` directory contains helper scripts for common operations:

| Script | Purpose | Usage |
|--------|---------|-------|
| `k8s-setup.sh` | Initialize Minikube cluster | `./scripts/k8s-setup.sh` |
| `k8s-secrets.sh` | Create/manage secrets | `./scripts/k8s-secrets.sh --all` |
| `k8s-deploy.sh` | Deploy with Helm | `./scripts/k8s-deploy.sh --build` |
| `k8s-teardown.sh` | Remove deployment | `./scripts/k8s-teardown.sh` |

### Full Deployment Workflow

```bash
# 1. Setup cluster
./scripts/k8s-setup.sh

# 2. Create secrets (interactive)
./scripts/k8s-secrets.sh --all

# 3. Build and deploy
./scripts/k8s-deploy.sh --build

# 4. Access application
echo "$(minikube ip) ai-wealth.local" | sudo tee -a /etc/hosts
open http://ai-wealth.local
```

---

## Next Steps

1. Test the full application workflow
2. Enable HPA for auto-scaling: `--set autoscaling.enabled=true`
3. Configure custom domains for production
4. Prepare for Phase V cloud deployment (DigitalOcean Kubernetes)
