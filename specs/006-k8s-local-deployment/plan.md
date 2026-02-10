# Implementation Plan: Phase IV Local Kubernetes Deployment

**Branch**: `006-k8s-local-deployment` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-k8s-local-deployment/spec.md`

## Summary

Deploy the AI Wealth & Spending Companion as a locally orchestrated, cloud-native system using Kubernetes. The implementation follows 5 stages: Containerization, Minikube Cluster Setup, Helm Deployment, AI Operations Layer, and Validation. All infrastructure is spec-driven with Helm as the single source of truth.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend), YAML (Kubernetes manifests)
**Primary Dependencies**: FastAPI, Next.js 14, Helm 3.x, Minikube 1.30+, kubectl-ai, kagent
**Storage**: Neon PostgreSQL (external cloud database)
**Testing**: kubectl wait, curl health checks, kubectl-ai queries
**Target Platform**: Linux/macOS/Windows WSL2 with Docker
**Project Type**: Web application (frontend + backend + MCP server)
**Performance Goals**: All pods ready within 5 minutes, kubectl-ai response < 5s
**Constraints**: Minikube default resources (2 CPU, 4GB RAM), no hardcoded secrets
**Scale/Scope**: Single-node local cluster, 3-5 services, 1-3 replicas per service

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| Spec-Driven Infrastructure | ✅ PASS | All manifests generated from specs via Helm templates |
| Container First | ✅ PASS | Existing Dockerfiles for backend/frontend, multi-stage builds |
| AI-Operated Kubernetes | ✅ PASS | kubectl-ai and kagent integrated per constitution |
| Local Cloud Parity | ✅ PASS | Minikube + Helm charts are cloud-ready |
| No Manual kubectl YAML | ✅ PASS | Helm templates only, no raw kubectl apply |
| Secrets via K8s Secrets | ✅ PASS | All secrets injected via environment variables |
| Service Communication | ✅ PASS | ClusterIP services for inter-service calls |
| Agent Scaling | ✅ PASS | HPA configuration for AI agents |

## Project Structure

### Documentation (this feature)

```text
specs/006-k8s-local-deployment/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 research output
├── data-model.md        # Kubernetes entity definitions
├── quickstart.md        # Deployment guide
├── contracts/           # Helm values schema
│   └── helm-values-schema.json
├── checklists/
│   └── requirements.md  # Quality validation
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
# Existing structure (no changes to application code)
backend/
├── Dockerfile           # Existing, update for K8s
├── src/
│   ├── main.py
│   ├── agents/          # AI agents (existing)
│   ├── mcp/             # MCP server (existing)
│   └── ...

frontend/
├── Dockerfile           # Existing, update for K8s
├── src/
│   └── ...

# New Kubernetes infrastructure
helm/
├── ai-wealth-companion/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── values-dev.yaml
│   ├── templates/
│   │   ├── _helpers.tpl
│   │   ├── namespace.yaml
│   │   ├── configmap.yaml
│   │   ├── secrets.yaml
│   │   ├── backend-deployment.yaml
│   │   ├── backend-service.yaml
│   │   ├── frontend-deployment.yaml
│   │   ├── frontend-service.yaml
│   │   ├── mcp-server-deployment.yaml
│   │   ├── mcp-server-service.yaml
│   │   ├── ingress.yaml
│   │   └── hpa.yaml
│   └── charts/

scripts/
├── k8s-setup.sh         # Minikube and kubectl-ai setup
├── k8s-deploy.sh        # Helm deployment script
├── k8s-secrets.sh       # Secret creation helper
└── k8s-teardown.sh      # Cleanup script
```

**Structure Decision**: Web application with existing frontend/backend structure. New `helm/` directory for Kubernetes infrastructure following umbrella chart pattern.

## Implementation Stages

### Stage 1: Containerization

**Goal**: Update existing Dockerfiles for Kubernetes compatibility.

| Task | Description | Files |
|------|-------------|-------|
| 1.1 | Update backend Dockerfile for port 8000 | `backend/Dockerfile` |
| 1.2 | Add health endpoint if missing | `backend/src/api/v1/endpoints/health.py` |
| 1.3 | Verify frontend Dockerfile standalone output | `frontend/Dockerfile` |
| 1.4 | Create .dockerignore files | `backend/.dockerignore`, `frontend/.dockerignore` |
| 1.5 | Test local Docker builds | Manual verification |

**Validation**: `docker build` succeeds for both services, health endpoints respond.

### Stage 2: Minikube Cluster Setup

**Goal**: Configure local Kubernetes environment with required addons.

| Task | Description | Files |
|------|-------------|-------|
| 2.1 | Create Minikube setup script | `scripts/k8s-setup.sh` |
| 2.2 | Enable ingress addon | Part of setup script |
| 2.3 | Configure kubectl-ai plugin | Part of setup script |
| 2.4 | Create namespace | `helm/.../templates/namespace.yaml` |
| 2.5 | Verify cluster health | `kubectl cluster-info` |

**Validation**: `minikube status` shows Running, ingress controller pod is Ready.

### Stage 3: Helm Deployment

**Goal**: Create complete Helm chart with all service manifests.

| Task | Description | Files |
|------|-------------|-------|
| 3.1 | Create Chart.yaml and values.yaml | `helm/ai-wealth-companion/Chart.yaml`, `values.yaml` |
| 3.2 | Create _helpers.tpl with template functions | `helm/.../templates/_helpers.tpl` |
| 3.3 | Create ConfigMap template | `helm/.../templates/configmap.yaml` |
| 3.4 | Create Secret templates | `helm/.../templates/secrets.yaml` |
| 3.5 | Create backend deployment | `helm/.../templates/backend-deployment.yaml` |
| 3.6 | Create backend service | `helm/.../templates/backend-service.yaml` |
| 3.7 | Create frontend deployment | `helm/.../templates/frontend-deployment.yaml` |
| 3.8 | Create frontend service | `helm/.../templates/frontend-service.yaml` |
| 3.9 | Create MCP server deployment | `helm/.../templates/mcp-server-deployment.yaml` |
| 3.10 | Create MCP server service | `helm/.../templates/mcp-server-service.yaml` |
| 3.11 | Create Ingress | `helm/.../templates/ingress.yaml` |
| 3.12 | Create HPA for scaling | `helm/.../templates/hpa.yaml` |
| 3.13 | Create values-dev.yaml override | `helm/ai-wealth-companion/values-dev.yaml` |
| 3.14 | Create secret creation script | `scripts/k8s-secrets.sh` |
| 3.15 | Create deployment script | `scripts/k8s-deploy.sh` |

**Validation**: `helm lint` passes, `helm template` generates valid YAML.

### Stage 4: AI Operations Layer

**Goal**: Configure kubectl-ai and kagent for AI-operated Kubernetes.

| Task | Description | Files |
|------|-------------|-------|
| 4.1 | Document kubectl-ai commands | `specs/006-k8s-local-deployment/quickstart.md` |
| 4.2 | Create kagent CRD (if available) | `helm/.../templates/kagent-policy.yaml` |
| 4.3 | Configure agent health monitoring | HPA and probes |
| 4.4 | Test AI-driven cluster queries | Manual verification |

**Validation**: `kubectl ai "cluster health"` returns meaningful response.

### Stage 5: Validation

**Goal**: Verify complete deployment meets all acceptance criteria.

| Task | Description | Validation |
|------|-------------|------------|
| 5.1 | Deploy to fresh cluster | `helm install` succeeds |
| 5.2 | All pods reach Ready | `kubectl wait --for=condition=ready` |
| 5.3 | Frontend accessible via Ingress | `curl http://ai-wealth.local` |
| 5.4 | Backend health check | `curl http://ai-wealth.local/api/health` |
| 5.5 | Chatbot responds | Frontend → Backend → AI test |
| 5.6 | Agents scale on load | HPA observation |
| 5.7 | No secrets in source | `grep` scan |
| 5.8 | Reproducible deployment | Fresh cluster test |

**Validation**: All SC-001 through SC-010 criteria met.

## Files Summary

| # | File | Action | Stage |
|---|------|--------|-------|
| 1 | `backend/Dockerfile` | MODIFY | 1 |
| 2 | `backend/.dockerignore` | CREATE | 1 |
| 3 | `frontend/.dockerignore` | CREATE | 1 |
| 4 | `scripts/k8s-setup.sh` | CREATE | 2 |
| 5 | `scripts/k8s-secrets.sh` | CREATE | 3 |
| 6 | `scripts/k8s-deploy.sh` | CREATE | 3 |
| 7 | `scripts/k8s-teardown.sh` | CREATE | 3 |
| 8 | `helm/ai-wealth-companion/Chart.yaml` | CREATE | 3 |
| 9 | `helm/ai-wealth-companion/values.yaml` | CREATE | 3 |
| 10 | `helm/ai-wealth-companion/values-dev.yaml` | CREATE | 3 |
| 11 | `helm/ai-wealth-companion/templates/_helpers.tpl` | CREATE | 3 |
| 12 | `helm/ai-wealth-companion/templates/namespace.yaml` | CREATE | 3 |
| 13 | `helm/ai-wealth-companion/templates/configmap.yaml` | CREATE | 3 |
| 14 | `helm/ai-wealth-companion/templates/secrets.yaml` | CREATE | 3 |
| 15 | `helm/ai-wealth-companion/templates/backend-deployment.yaml` | CREATE | 3 |
| 16 | `helm/ai-wealth-companion/templates/backend-service.yaml` | CREATE | 3 |
| 17 | `helm/ai-wealth-companion/templates/frontend-deployment.yaml` | CREATE | 3 |
| 18 | `helm/ai-wealth-companion/templates/frontend-service.yaml` | CREATE | 3 |
| 19 | `helm/ai-wealth-companion/templates/mcp-server-deployment.yaml` | CREATE | 3 |
| 20 | `helm/ai-wealth-companion/templates/mcp-server-service.yaml` | CREATE | 3 |
| 21 | `helm/ai-wealth-companion/templates/ingress.yaml` | CREATE | 3 |
| 22 | `helm/ai-wealth-companion/templates/hpa.yaml` | CREATE | 3 |

**Total**: 22 files (3 MODIFY, 19 CREATE)

## Complexity Tracking

No constitution violations requiring justification. All complexity is within guidelines:
- Single Helm chart (not multiple)
- Standard Kubernetes resources (Deployment, Service, Ingress, ConfigMap, Secret, HPA)
- No custom operators or CRDs beyond kagent

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Minikube | 1.30+ | Local Kubernetes cluster |
| Helm | 3.x | Package management |
| kubectl | 1.28+ | Cluster CLI |
| kubectl-ai | latest | AI-operated commands |
| Docker | 20.10+ | Container runtime |

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Minikube resource limits | High | Document minimum requirements, provide tuning guide |
| kubectl-ai plugin availability | Medium | Fallback to standard kubectl commands |
| Neon DB latency | Medium | Document expected latency, connection pooling |

## Success Criteria Mapping

| SC ID | Criterion | Implementation |
|-------|-----------|----------------|
| SC-001 | Deploy < 10 minutes | Optimized Docker builds, Helm chart |
| SC-002 | Pods ready < 5 minutes | Proper resource limits, health probes |
| SC-003 | 100% reproducible | Helm values, no state dependencies |
| SC-004 | kubectl-ai < 5s | Plugin optimization |
| SC-005 | kagent restart < 30s | HPA + liveness probes |
| SC-006 | No plaintext secrets | K8s Secrets only |
| SC-007 | Frontend accessible | Ingress configuration |
| SC-008 | Backend healthy < 60s | Health endpoint + readiness probe |
| SC-009 | 2 CPU, 4GB RAM | Conservative resource limits |
| SC-010 | Service DNS names | ClusterIP services |

## Next Steps

1. Run `/sp.tasks` to generate detailed task list
2. Execute Stage 1: Containerization
3. Execute Stage 2: Minikube Cluster Setup
4. Execute Stage 3: Helm Deployment
5. Execute Stage 4: AI Operations Layer
6. Execute Stage 5: Validation
