# Quickstart: Phase V Cloud-Native Deployment

**Branch**: `007-phase-v-cloud-native`
**Version**: 5.0.0
**Prerequisites**: DigitalOcean account, doctl CLI, kubectl, Helm 3, Dapr CLI

## Overview

This guide walks through deploying the AI Wealth & Spending Companion to DigitalOcean Kubernetes (DOKS) with event-driven architecture using Kafka and Dapr. For production operations, see the [Production Runbook](./runbook.md).

## Prerequisites Checklist

- [ ] DigitalOcean account with API token
- [ ] `doctl` CLI installed and authenticated
- [ ] `kubectl` installed (v1.28+)
- [ ] `helm` installed (v3.x)
- [ ] `dapr` CLI installed
- [ ] Domain name configured (optional, for TLS)
- [ ] Docker images pushed to registry
- [ ] Environment file (`.env.doks`) with required secrets

## Quick Start (Automated)

The fastest way to deploy is using the provided automation scripts:

```bash
# 1. Setup cluster and infrastructure (one-time)
./scripts/doks-setup.sh

# 2. Deploy application
./scripts/doks-deploy.sh

# 3. Validate event flow
./scripts/validate-events.sh
```

## Environment Setup

Create `.env.doks` with your credentials:

```bash
# Required
export DO_API_TOKEN="your-digitalocean-api-token"
export DATABASE_URL="postgresql+asyncpg://user:pass@host/db"
export GEMINI_API_KEY="your-gemini-key"
export JWT_SECRET_KEY="your-jwt-secret"
export REDIS_PASSWORD="your-redis-password"

# Optional
export OPENAI_API_KEY="your-openai-key"
export DOMAIN="your-domain.com"
export EMAIL="your-email@example.com"
```

---

## Manual Deployment Steps

### Step 1: Provision DOKS Cluster

```bash
# Create DOKS cluster (3 nodes, s-4vcpu-8gb)
doctl kubernetes cluster create ai-wealth-prod \
  --region nyc1 \
  --version 1.28.2-do.0 \
  --node-pool "name=default;size=s-4vcpu-8gb;count=3;auto-scale=true;min-nodes=3;max-nodes=5"

# Configure kubectl
doctl kubernetes cluster kubeconfig save ai-wealth-prod

# Verify cluster
kubectl get nodes
# Expected: 3 nodes in Ready state
```

### Step 2: Install NGINX Ingress Controller

```bash
# Add ingress-nginx repo
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Install ingress controller
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.publishService.enabled=true

# Get external IP (wait ~2 minutes)
kubectl get svc -n ingress-nginx ingress-nginx-controller
```

### Step 3: Install Dapr

```bash
# Initialize Dapr on Kubernetes
dapr init -k --wait

# Verify Dapr components
dapr status -k
# Expected: dapr-operator, dapr-sidecar-injector, dapr-placement, dapr-dashboard all Running
```

### Step 4: Deploy Kafka (Strimzi)

```bash
# Install Strimzi operator
kubectl create namespace kafka
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Wait for operator
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s

# Deploy Kafka cluster (using Helm chart)
helm upgrade --install ai-wealth ./helm/ai-wealth-companion \
  --namespace ai-wealth \
  --create-namespace \
  --values helm/ai-wealth-companion/values-doks.yaml \
  --set kafka.enabled=true

# Or deploy standalone Kafka cluster
kubectl apply -f helm/ai-wealth-companion/templates/kafka/kafka-cluster.yaml -n ai-wealth

# Wait for Kafka
kubectl wait kafka/ai-wealth-kafka -n ai-wealth --for=condition=Ready --timeout=600s
```

### Step 5: Create Kafka Topics

```bash
# Topics are automatically created by Helm chart
# To manually create topics:
kubectl apply -f helm/ai-wealth-companion/templates/kafka/kafka-topics.yaml -n ai-wealth

# Verify topics
kubectl get kafkatopics -n ai-wealth
```

### Step 6: Deploy Application Namespace and Secrets

```bash
# Create namespace (if not already created by Helm)
kubectl create namespace ai-wealth

# Enable Dapr sidecar injection
kubectl label namespace ai-wealth dapr.io/enabled=true

# Create secrets from environment
source .env.doks
kubectl create secret generic ai-wealth-secrets -n ai-wealth \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=GEMINI_API_KEY="$GEMINI_API_KEY" \
  --from-literal=JWT_SECRET_KEY="$JWT_SECRET_KEY" \
  --from-literal=REDIS_PASSWORD="$REDIS_PASSWORD" \
  --from-literal=OPENAI_API_KEY="${OPENAI_API_KEY:-}"
```

### Step 7: Deploy Dapr Components

```bash
# Apply Dapr components from Helm chart
helm upgrade --install ai-wealth ./helm/ai-wealth-companion \
  --namespace ai-wealth \
  --values helm/ai-wealth-companion/values-doks.yaml \
  --set dapr.enabled=true

# Verify components
dapr components -k -n ai-wealth
# Expected: pubsub-kafka, statestore-redis, secretstore-kubernetes
```

### Step 8: Deploy Application via Helm

```bash
# Full deployment with all components
helm upgrade --install ai-wealth ./helm/ai-wealth-companion \
  --namespace ai-wealth \
  --values helm/ai-wealth-companion/values-doks.yaml \
  --set global.domain="${DOMAIN:-localhost}" \
  --set ingress.enabled=true \
  --set ingress.tls.enabled=true \
  --wait --timeout 10m

# Verify pods
kubectl get pods -n ai-wealth
# Expected: All pods Running with 2/2 (app + Dapr sidecar)
```

### Step 9: Configure TLS (Optional)

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create Let's Encrypt ClusterIssuer
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: ${EMAIL:-your-email@example.com}
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - http01:
          ingress:
            class: nginx
EOF

# Update ingress with TLS (via Helm values or kubectl patch)
```

### Step 10: Validate Deployment

```bash
# Use the automated validation script
./scripts/validate-events.sh

# Or manually validate:

# Check all pods ready
kubectl get pods -n ai-wealth -w

# Check Dapr sidecars
kubectl get pods -n ai-wealth -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}'

# Test event flow
curl -X POST https://your-domain.com/api/v1/transactions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100, "type": "expense", "category": "food"}'

# Check Kafka topics for event
kubectl exec -n ai-wealth ai-wealth-kafka-kafka-0 -- bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic transactions \
  --from-beginning --max-messages 1
```

---

## Observability Access

### Grafana Dashboard

```bash
# Port forward to access Grafana
kubectl port-forward svc/grafana 3000:3000 -n ai-wealth

# Access at http://localhost:3000
# Default credentials: admin / admin (change on first login)
# Main dashboard: AI Wealth Companion Overview
```

### Prometheus Metrics

```bash
# Port forward to access Prometheus
kubectl port-forward svc/prometheus-server 9090:80 -n ai-wealth

# Access at http://localhost:9090
# Key metrics:
#   - http_requests_total
#   - http_request_duration_seconds
#   - events_published_total
#   - events_processed_total
```

### Jaeger Tracing

```bash
# Port forward to access Jaeger UI
kubectl port-forward svc/jaeger-query 16686:16686 -n ai-wealth

# Access at http://localhost:16686
# Select service: backend, frontend, or mcp-server
```

### Loki Logs

```bash
# Logs are accessible via Grafana's Explore feature
# Use the "Loki" datasource and LogQL queries:
#   {app="backend"} |= "error"
#   {namespace="ai-wealth"} | json | level="error"
```

---

## Production Operations

### Deployment

```bash
# Standard deployment with auto-rollback
./scripts/doks-deploy.sh

# Dry-run deployment (shows what would happen)
DRY_RUN=true ./scripts/doks-deploy.sh

# Skip certain components
SKIP_OBSERVABILITY=true ./scripts/doks-deploy.sh
```

### Rollback

```bash
# Quick rollback to previous version (< 2 minutes)
./scripts/doks-rollback.sh

# Rollback to specific revision
./scripts/doks-rollback.sh --revision 3

# List available revisions
./scripts/doks-rollback.sh --list

# Emergency rollback (force restart all pods)
./scripts/doks-rollback.sh --emergency
```

### Scaling

```bash
# Manual scaling
kubectl scale deployment/backend --replicas=5 -n ai-wealth

# Check HPA status
kubectl get hpa -n ai-wealth

# Node pool scaling
doctl kubernetes cluster node-pool update ai-wealth-doks default \
  --auto-scale --min-nodes 2 --max-nodes 10
```

### Event Validation

```bash
# Full event flow validation
./scripts/validate-events.sh

# Test with pod failure simulation
./scripts/validate-events.sh --test-pod-failure

# Test with Kafka failure simulation
./scripts/validate-events.sh --test-kafka-failure
```

---

## Troubleshooting

### Pods stuck in Pending
```bash
kubectl describe pod <pod-name> -n ai-wealth
# Check for resource constraints or node affinity issues

# Check node resources
kubectl describe nodes | grep -A5 "Allocated resources"
```

### Dapr sidecar not injecting
```bash
kubectl get namespace ai-wealth --show-labels
# Ensure dapr.io/enabled=true label exists

# Check Dapr operator logs
kubectl logs -l app=dapr-operator -n dapr-system
```

### Kafka connection issues
```bash
kubectl logs <pod-name> -c daprd -n ai-wealth
# Check for pub/sub component errors

# Check Kafka cluster health
kubectl get kafka -n ai-wealth
kubectl describe kafka ai-wealth-kafka -n ai-wealth
```

### Event not being published
```bash
# Check application logs
kubectl logs <pod-name> -c backend -n ai-wealth

# Check Dapr sidecar logs
kubectl logs <pod-name> -c daprd -n ai-wealth

# Verify Dapr pub/sub component
dapr components -k -n ai-wealth
kubectl describe component pubsub-kafka -n ai-wealth
```

### High Latency Issues
```bash
# Check HPA metrics
kubectl get hpa -n ai-wealth

# View Prometheus metrics
kubectl port-forward svc/prometheus-server 9090:80 -n ai-wealth &
# Query: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{namespace="ai-wealth"}[5m])) by (le))

# Check resource utilization
kubectl top pods -n ai-wealth
```

### Database Connection Issues
```bash
# Verify secret exists
kubectl get secret ai-wealth-secrets -n ai-wealth -o yaml

# Test connection from pod
kubectl exec -it deployment/backend -n ai-wealth -- \
  python -c "from src.db.session import get_db; print('Connected')"

# Check Neon status at https://console.neon.tech
```

---

## Health Checks

| Endpoint | Description |
|----------|-------------|
| `/health` | Basic health check |
| `/health/ready` | Readiness probe |
| `/health/live` | Liveness probe |
| `/metrics` | Prometheus metrics |

---

## SLOs (Service Level Objectives)

| Metric | Target | Critical |
|--------|--------|----------|
| Availability | 99.9% | < 99% |
| API p95 Latency | < 200ms | > 500ms |
| Event Latency | < 5s | > 10s |
| Error Rate | < 0.1% | > 1% |
| Pod Recovery | < 30s | > 60s |
| Rollback Time | < 2min | > 5min |

---

## Next Steps

- [ ] Review [Production Runbook](./runbook.md) for incident response
- [ ] Configure alerting in Grafana for SLO violations
- [ ] Run load tests to validate auto-scaling
- [ ] Set up backup procedures for secrets
- [ ] Configure log retention policies in Loki
