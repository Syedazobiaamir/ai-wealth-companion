# Tasks: Phase IV Local Kubernetes Deployment

**Input**: Design documents from `/specs/006-k8s-local-deployment/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No tests explicitly requested in spec. Validation tasks included in final phase.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## User Stories from Spec

| ID | Story | Priority |
|----|-------|----------|
| US1 | Developer Deploys Full Stack Locally | P1 |
| US2 | AI-Operated Cluster Health Check | P2 |
| US3 | AI Agent Scaling via kagent | P2 |
| US4 | Secret Management via Kubernetes Secrets | P3 |
| US5 | Service Communication via Kubernetes Services | P3 |

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Kubernetes infrastructure directory structure

- [x] T001 Create helm chart directory structure in helm/ai-wealth-companion/
- [x] T002 Create scripts directory structure in scripts/
- [x] T003 [P] Create backend/.dockerignore with Python exclusions
- [x] T004 [P] Create frontend/.dockerignore with Node.js exclusions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core containerization and Helm base configuration that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Docker Updates

- [x] T005 Update backend Dockerfile for K8s port 8000 in backend/Dockerfile
- [x] T006 [P] Verify and add health endpoint for readiness probe in backend/src/api/v1/endpoints/health.py
- [x] T007 [P] Verify frontend Dockerfile standalone output configuration in frontend/Dockerfile

### Helm Chart Base

- [x] T008 Create Chart.yaml with metadata and version in helm/ai-wealth-companion/Chart.yaml
- [x] T009 Create values.yaml with all configurable parameters in helm/ai-wealth-companion/values.yaml
- [x] T010 [P] Create _helpers.tpl with template helper functions in helm/ai-wealth-companion/templates/_helpers.tpl
- [x] T011 [P] Create namespace.yaml template in helm/ai-wealth-companion/templates/namespace.yaml

### Cluster Setup

- [x] T012 Create k8s-setup.sh for Minikube and addons in scripts/k8s-setup.sh

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Developer Deploys Full Stack Locally (Priority: P1) 🎯 MVP

**Goal**: Deploy the entire AI Wealth Companion stack to local Kubernetes with a single Helm command

**Independent Test**: Run `helm install ai-wealth ./helm/ai-wealth-companion -n ai-wealth` and verify all pods reach Ready state within 5 minutes

**Acceptance Criteria**:
- SC-001: Deploy in under 10 minutes
- SC-002: All pods ready within 5 minutes
- SC-003: 100% reproducible deployment
- SC-007: Frontend accessible via Ingress
- SC-008: Backend healthy within 60 seconds

### Implementation for User Story 1

**ConfigMaps & Secrets Templates**:
- [x] T013 [P] [US1] Create configmap.yaml template in helm/ai-wealth-companion/templates/configmap.yaml

**Backend Deployment**:
- [x] T014 [P] [US1] Create backend-deployment.yaml with resource limits, probes, and env in helm/ai-wealth-companion/templates/backend-deployment.yaml
- [x] T015 [P] [US1] Create backend-service.yaml as ClusterIP in helm/ai-wealth-companion/templates/backend-service.yaml

**Frontend Deployment**:
- [x] T016 [P] [US1] Create frontend-deployment.yaml with resource limits and probes in helm/ai-wealth-companion/templates/frontend-deployment.yaml
- [x] T017 [P] [US1] Create frontend-service.yaml as ClusterIP in helm/ai-wealth-companion/templates/frontend-service.yaml

**MCP Server Deployment**:
- [x] T018 [P] [US1] Create mcp-server-deployment.yaml (stateless) in helm/ai-wealth-companion/templates/mcp-server-deployment.yaml
- [x] T019 [P] [US1] Create mcp-server-service.yaml as ClusterIP in helm/ai-wealth-companion/templates/mcp-server-service.yaml

**Ingress Configuration**:
- [x] T020 [US1] Create ingress.yaml with path-based routing in helm/ai-wealth-companion/templates/ingress.yaml

**Deployment Scripts**:
- [x] T021 [US1] Create k8s-deploy.sh for Helm install/upgrade in scripts/k8s-deploy.sh
- [x] T022 [P] [US1] Create k8s-teardown.sh for cleanup in scripts/k8s-teardown.sh

**Environment Overrides**:
- [x] T023 [US1] Create values-dev.yaml for local development in helm/ai-wealth-companion/values-dev.yaml

**Checkpoint**: At this point, User Story 1 should be fully functional - `helm install` deploys all services

---

## Phase 4: User Story 4 - Secret Management via Kubernetes Secrets (Priority: P3)

**Goal**: Inject all secrets (JWT, Gemini API key, database credentials) via Kubernetes Secrets with no hardcoded values

**Independent Test**: Deploy without secrets in source code, verify services authenticate using injected K8s Secrets

**Acceptance Criteria**:
- SC-006: No plaintext secrets in source-controlled files
- FR-014: Secrets stored in K8s Secrets
- FR-015: Secrets injected as environment variables
- FR-017: No secrets in Helm charts or Dockerfiles

**Note**: US4 is placed before US2/US3 because secrets are required for full deployment

### Implementation for User Story 4

- [x] T024 [US4] Create secrets.yaml template with external secret refs in helm/ai-wealth-companion/templates/secrets.yaml
- [x] T025 [US4] Create k8s-secrets.sh helper script for secret creation in scripts/k8s-secrets.sh
- [x] T026 [US4] Update backend-deployment.yaml to reference secrets via envFrom in helm/ai-wealth-companion/templates/backend-deployment.yaml
- [x] T027 [P] [US4] Update mcp-server-deployment.yaml to reference secrets in helm/ai-wealth-companion/templates/mcp-server-deployment.yaml
- [x] T028 [US4] Document secret creation process in specs/006-k8s-local-deployment/quickstart.md

**Checkpoint**: Secrets management complete - services authenticate via K8s Secrets

---

## Phase 5: User Story 5 - Service Communication via Kubernetes Services (Priority: P3)

**Goal**: All inter-service communication goes through Kubernetes Services (ClusterIP) for service mesh readiness

**Independent Test**: Verify frontend-to-backend and backend-to-MCP communication uses Service DNS names, not pod IPs

**Acceptance Criteria**:
- SC-010: All inter-service calls use K8s Service DNS names
- FR-012: Inter-service communication via K8s Services
- FR-013: Backend not directly exposed externally

**Note**: US5 validates services created in US1 and ensures proper networking

### Implementation for User Story 5

- [x] T029 [US5] Update configmap.yaml with internal service URLs (backend:8000, mcp-server:8080) in helm/ai-wealth-companion/templates/configmap.yaml
- [x] T030 [US5] Verify frontend environment points to backend service URL in values.yaml
- [x] T031 [US5] Verify backend environment points to MCP service URL in values.yaml
- [x] T032 [US5] Document service communication architecture in specs/006-k8s-local-deployment/quickstart.md

**Checkpoint**: Service networking complete - all communication uses K8s Services

---

## Phase 6: User Story 2 - AI-Operated Cluster Health Check (Priority: P2)

**Goal**: Use kubectl-ai to query cluster health in natural language

**Independent Test**: Run `kubectl ai "what is the cluster health in ai-wealth namespace?"` and receive accurate summary

**Acceptance Criteria**:
- SC-004: kubectl-ai responds within 5 seconds
- FR-018: kubectl-ai describes cluster health
- FR-019: kubectl-ai can restart services
- FR-020: kubectl-ai explains failures from logs

### Implementation for User Story 2

- [x] T033 [US2] Add kubectl-ai installation to k8s-setup.sh in scripts/k8s-setup.sh
- [x] T034 [US2] Document kubectl-ai commands and examples in specs/006-k8s-local-deployment/quickstart.md
- [x] T035 [P] [US2] Create kubectl-ai cheat sheet section in specs/006-k8s-local-deployment/quickstart.md
- [x] T036 [US2] Test and document common kubectl-ai queries in specs/006-k8s-local-deployment/quickstart.md

**Checkpoint**: AI-operated cluster health check functional

---

## Phase 7: User Story 3 - AI Agent Scaling via kagent (Priority: P2)

**Goal**: kagent monitors and manages AI agent workloads with auto-scaling and failure recovery

**Independent Test**: Simulate pod failure, observe kagent restart within 30 seconds; simulate load, observe HPA scale up

**Acceptance Criteria**:
- SC-005: kagent restarts failed pods within 30 seconds
- FR-021: kagent monitors AI agent health
- FR-022: kagent auto-restarts failed pods
- FR-023: kagent scales based on policies

### Implementation for User Story 3

- [x] T037 [US3] Create hpa.yaml for backend/AI agent scaling in helm/ai-wealth-companion/templates/hpa.yaml
- [x] T038 [US3] Add kagent installation to k8s-setup.sh (if available) in scripts/k8s-setup.sh
- [x] T039 [P] [US3] Create kagent-policy.yaml for AI workload governance in helm/ai-wealth-companion/templates/kagent-policy.yaml
- [x] T040 [US3] Configure liveness probes for agent health in backend-deployment.yaml
- [x] T041 [US3] Document kagent commands and scaling behavior in specs/006-k8s-local-deployment/quickstart.md

**Checkpoint**: AI agent scaling and recovery operational

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Validation, documentation, and final verification

### Validation Tasks

- [x] T042 Run helm lint on chart in helm/ai-wealth-companion/
- [x] T043 Run helm template to verify YAML generation
- [x] T044 Deploy to fresh Minikube cluster and verify all pods ready
- [x] T045 Verify frontend accessible via port-forward (Ingress optional)
- [x] T046 Verify backend health endpoint responds
- [x] T047 [P] Grep scan for plaintext secrets in source files
- [x] T048 [P] Verify chatbot responds (frontend → backend → AI flow)
- [x] T049 Test reproducibility with fresh cluster deployment

### Documentation Updates

- [x] T050 [P] Finalize quickstart.md with complete deployment guide in specs/006-k8s-local-deployment/quickstart.md
- [x] T051 [P] Add troubleshooting section to quickstart.md
- [x] T052 Update README with Phase IV deployment instructions (includes Docker Hub support)

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup ✅
    ↓
Phase 2: Foundational (BLOCKS all user stories) ✅
    ↓
Phase 3: US1 - Full Stack Deployment (P1) 🎯 MVP ✅
    ↓
Phase 4: US4 - Secret Management (P3) ✅
    ↓
Phase 5: US5 - Service Communication (P3) ✅
    ↓ ↘
Phase 6: US2 - kubectl-ai Health (P2) ✅   Phase 7: US3 - kagent Scaling (P2) ✅
    ↓ ↙
Phase 8: Polish & Validation 🔄
```

### User Story Dependencies

| Story | Depends On | Can Parallelize With |
|-------|------------|---------------------|
| US1 (P1) | Foundational | - |
| US4 (P3) | US1 | - |
| US5 (P3) | US1 | US4 |
| US2 (P2) | US1, US4, US5 | US3 |
| US3 (P2) | US1, US4, US5 | US2 |

---

## Summary

| Phase | Tasks | Completed | Status |
|-------|-------|-----------|--------|
| Setup | 4 | 4 | ✅ Done |
| Foundational | 8 | 8 | ✅ Done |
| US1 (P1) | 11 | 11 | ✅ Done |
| US4 (P3) | 5 | 5 | ✅ Done |
| US5 (P3) | 4 | 4 | ✅ Done |
| US2 (P2) | 4 | 4 | ✅ Done |
| US3 (P2) | 5 | 5 | ✅ Done |
| Polish | 11 | 11 | ✅ Done |

**Total**: 52 tasks (52 completed)

**Phase IV Complete**: All tasks finished including runtime validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- All runtime validation tasks completed on Minikube cluster
- All infrastructure code complete and deployed successfully
- Docker Hub support added: `values-dockerhub.yaml` and `--dockerhub` flag in deploy script
- Auto-install scripts: `install-and-deploy.sh` (Linux/WSL) and `install-and-deploy.ps1` (Windows)
- Backend connected to Neon PostgreSQL database for production data persistence
