# Phase IV Research: Local Kubernetes Deployment

**Feature**: 006-k8s-local-deployment
**Date**: 2026-02-09
**Status**: Complete

## Research Summary

This document resolves all technical unknowns for Phase IV Local Kubernetes Deployment.

---

## 1. Minikube Configuration

### Decision
Use Minikube with Docker driver and NGINX ingress controller.

### Rationale
- Docker driver is most portable across Linux, macOS, and Windows WSL2
- NGINX ingress is the default and most documented option
- Minikube addons system simplifies ingress setup

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| VirtualBox driver | Slower startup, more resource overhead |
| K3s | Less Minikube-compatible tooling |
| Kind (Kubernetes in Docker) | Less production-like, fewer addons |

### Configuration
```bash
minikube start --driver=docker --cpus=2 --memory=4096 --addons=ingress
```

---

## 2. Helm Chart Structure

### Decision
Single umbrella chart with subcharts for each service.

### Rationale
- Constitution requires Helm as single source of truth
- Umbrella pattern allows independent service upgrades
- Values override per environment (dev, prod)

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| Multiple independent charts | Harder to manage dependencies |
| Kustomize | Not Helm-based, violates constitution |
| Raw kubectl manifests | Violates spec-driven infrastructure principle |

### Structure
```
helm/ai-wealth-companion/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
└── templates/
    ├── backend/
    ├── frontend/
    ├── mcp-server/
    └── agents/
```

---

## 3. kubectl-ai Integration

### Decision
Use kubectl-ai plugin for natural language cluster operations.

### Rationale
- Constitution mandates AI-operated Kubernetes
- kubectl-ai provides LLM-powered kubectl commands
- Enables natural language troubleshooting

### Installation
```bash
kubectl krew install ai
```

### Usage Patterns
```bash
kubectl ai "show all pods in ai-wealth namespace"
kubectl ai "why is backend pod failing"
kubectl ai "restart the frontend deployment"
```

---

## 4. kagent for AI Workloads

### Decision
Use kagent CRD for managing AI agent pod lifecycle.

### Rationale
- Constitution requires kagent for AI workload governance
- Enables policy-based scaling of AI agents
- Provides autonomous health monitoring

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| Standard HPA | Doesn't understand AI workload patterns |
| KEDA | More complex, overkill for local dev |
| Manual scaling | Not AI-operated |

### Configuration
```yaml
apiVersion: kagent.io/v1
kind: AgentPolicy
metadata:
  name: ai-agents-policy
spec:
  selector:
    matchLabels:
      app.kubernetes.io/component: ai-agent
  scaling:
    minReplicas: 1
    maxReplicas: 3
  health:
    restartPolicy: OnFailure
    maxRestarts: 3
```

---

## 5. Secret Management

### Decision
Use Kubernetes Secrets with values injected at deploy time.

### Rationale
- Constitution forbids hardcoded secrets
- K8s Secrets integrate with pod environment injection
- Simple for local development

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| HashiCorp Vault | Overkill for local dev |
| Sealed Secrets | Adds complexity |
| External Secrets Operator | Requires cloud provider |

### Required Secrets
| Secret Name | Keys |
|-------------|------|
| `db-credentials` | DATABASE_URL |
| `jwt-secret` | JWT_SECRET_KEY |
| `ai-credentials` | GEMINI_API_KEY, OPENAI_API_KEY |
| `oauth-credentials` | GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET |

---

## 6. Container Images

### Decision
Build multi-stage Docker images, tag with git SHA and semantic version.

### Rationale
- Constitution requires multi-stage builds
- Git SHA provides traceability
- Semantic versions for release tracking

### Image Tags
```
ai-wealth-companion/backend:v4.0.0
ai-wealth-companion/backend:abc1234  # git SHA
ai-wealth-companion/frontend:v4.0.0
ai-wealth-companion/mcp-server:v4.0.0
```

### Registry
Local Minikube registry for development:
```bash
eval $(minikube docker-env)
docker build -t ai-wealth-companion/backend:dev .
```

---

## 7. Service Communication

### Decision
All inter-service communication via ClusterIP Services.

### Rationale
- Constitution requires Service-based communication
- Prepares for Phase V service mesh (Dapr)
- No direct pod-to-pod communication

### Service DNS
| Service | DNS Name | Port |
|---------|----------|------|
| Backend | `backend.ai-wealth.svc.cluster.local` | 8000 |
| Frontend | `frontend.ai-wealth.svc.cluster.local` | 3000 |
| MCP Server | `mcp-server.ai-wealth.svc.cluster.local` | 8080 |

---

## 8. Health Probes

### Decision
Liveness and readiness probes for all services.

### Rationale
- Constitution requires health check endpoints
- Kubernetes self-healing depends on probes
- Enables rolling updates

### Probe Configuration
| Service | Liveness | Readiness |
|---------|----------|-----------|
| Backend | `/health` (HTTP 200) | `/health/ready` (HTTP 200) |
| Frontend | `/` (HTTP 200) | `/` (HTTP 200) |
| MCP Server | `/health` (HTTP 200) | `/health` (HTTP 200) |

---

## 9. Resource Limits

### Decision
Conservative resource limits for local development (2 CPU, 4GB RAM total).

### Rationale
- SC-009 requires operation within Minikube defaults
- Prevents resource exhaustion on developer machines
- Can be overridden for production

### Resource Allocation
| Service | CPU Request | CPU Limit | Memory Request | Memory Limit |
|---------|-------------|-----------|----------------|--------------|
| Backend | 100m | 500m | 256Mi | 512Mi |
| Frontend | 100m | 300m | 128Mi | 256Mi |
| MCP Server | 50m | 200m | 64Mi | 128Mi |
| AI Agent (each) | 100m | 500m | 256Mi | 512Mi |

---

## 10. Ingress Configuration

### Decision
NGINX Ingress with path-based routing.

### Rationale
- Single entry point for all services
- Path routing: `/` → Frontend, `/api` → Backend
- Ready for TLS in production

### Ingress Routes
| Path | Service | Port |
|------|---------|------|
| `/` | frontend | 3000 |
| `/api/*` | backend | 8000 |
| `/mcp/*` | mcp-server | 8080 |

---

## Unknowns Resolution Status

| Unknown | Status | Resolution |
|---------|--------|------------|
| Minikube driver | ✅ Resolved | Docker driver |
| Helm structure | ✅ Resolved | Umbrella chart |
| kubectl-ai setup | ✅ Resolved | krew plugin |
| kagent configuration | ✅ Resolved | CRD-based policies |
| Secret management | ✅ Resolved | K8s Secrets |
| Container registry | ✅ Resolved | Minikube local |
| Service mesh prep | ✅ Resolved | ClusterIP Services |
| Resource limits | ✅ Resolved | Conservative allocation |

---

## Next Steps

1. Create `data-model.md` with Kubernetes entity definitions
2. Create `/contracts/` with Helm values schema
3. Write `quickstart.md` with deployment guide
4. Generate full implementation plan
