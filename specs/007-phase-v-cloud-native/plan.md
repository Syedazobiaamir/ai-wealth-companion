# Implementation Plan: Phase V Cloud-Native Production System

**Branch**: `007-phase-v-cloud-native` | **Date**: 2026-02-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-phase-v-cloud-native/spec.md`

## Summary

Deploy the AI Wealth & Spending Companion to DigitalOcean Kubernetes (DOKS) as a distributed, event-driven system using Kafka for messaging and Dapr for service mesh abstraction. The implementation follows an 8-step execution plan: provision cluster, install Dapr, deploy Kafka, configure pub/sub, deploy services via Helm, enable autoscaling, validate event flows, and demonstrate resilience.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, Next.js 14, Dapr SDK, Strimzi Kafka Operator
**Storage**: Neon PostgreSQL (primary), Redis (Dapr state store)
**Testing**: pytest (backend), Jest (frontend), k6 (load testing)
**Target Platform**: DigitalOcean Kubernetes (DOKS) 1.28+
**Project Type**: Web application (frontend + backend + AI agents)
**Performance Goals**: 1,000 concurrent users, <5s P95 event latency
**Constraints**: 99.9% uptime, <2 min rollback, zero-downtime deployments
**Scale/Scope**: 3-node cluster, 5 event types, 4 AI agents, HPA 1-5 replicas

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| Spec-Driven Infrastructure | ✅ PASS | All manifests generated from spec via Helm |
| Event-Driven Architecture | ✅ PASS | Kafka + Dapr pub/sub, no direct SDK |
| Zero Manual kubectl in Prod | ✅ PASS | All via Helm charts, CI/CD automation |
| Observability Required | ✅ PASS | Prometheus, Grafana, Loki, Jaeger planned |
| Cloud-Portable Services | ✅ PASS | Dapr abstracts infrastructure |
| No Hardcoded Secrets | ✅ PASS | DOKS Secrets via Dapr secret store |
| No Point-to-Point Coupling | ✅ PASS | All communication via Dapr pub/sub |
| Services Communicate via Dapr | ✅ PASS | FR-006 mandates Dapr sidecars |
| Events are Idempotent | ✅ PASS | FR-008 mandates idempotent handlers |
| TLS on Ingress | ✅ PASS | NGINX + cert-manager for TLS |

**Gate Result**: ALL PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/007-phase-v-cloud-native/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (event schemas)
│   ├── events/
│   │   ├── transaction.created.json
│   │   ├── transaction.updated.json
│   │   ├── budget.exceeded.json
│   │   ├── ai.insight.generated.json
│   │   └── user.alert.sent.json
│   └── dapr/
│       ├── pubsub.yaml
│       ├── statestore.yaml
│       └── secretstore.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
# Web application structure (existing from Phase IV)
backend/
├── src/
│   ├── models/
│   ├── services/
│   ├── agents/
│   │   └── subagents/
│   ├── api/
│   └── events/           # NEW: Event publishers/handlers
│       ├── publishers.py
│       ├── handlers.py
│       └── schemas.py
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# Kubernetes/Infrastructure (existing + new)
helm/
├── ai-wealth-companion/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── values-doks.yaml      # NEW: DOKS-specific values
│   ├── templates/
│   │   ├── backend-deployment.yaml
│   │   ├── frontend-deployment.yaml
│   │   ├── mcp-server-deployment.yaml
│   │   ├── dapr/              # NEW: Dapr components
│   │   │   ├── pubsub.yaml
│   │   │   ├── statestore.yaml
│   │   │   └── secretstore.yaml
│   │   ├── kafka/             # NEW: Kafka via Strimzi
│   │   │   └── kafka-cluster.yaml
│   │   └── observability/     # NEW: Monitoring stack
│   │       ├── prometheus.yaml
│   │       ├── grafana.yaml
│   │       └── jaeger.yaml
│   └── charts/
│       └── (dependencies)

scripts/
├── doks-setup.sh             # NEW: DOKS cluster provisioning
├── doks-deploy.sh            # NEW: Production deployment
├── doks-rollback.sh          # NEW: Rollback script
└── validate-events.sh        # NEW: Event flow validation
```

**Structure Decision**: Extends existing Phase IV web application structure with new `events/` module in backend and additional Helm templates for Dapr, Kafka, and observability. DOKS-specific values file overrides local Minikube settings.

## Execution Plan

### Step 1: Provision DOKS Cluster

**Objective**: Create production-ready Kubernetes cluster on DigitalOcean

**Tasks**:
- Create DOKS cluster via doctl or Terraform (3 nodes minimum)
- Configure kubectl context for DOKS
- Install NGINX Ingress Controller
- Configure cert-manager for TLS certificates
- Verify cluster health and node readiness

**Validation**: `kubectl get nodes` shows 3 Ready nodes

### Step 2: Install Dapr on Cluster

**Objective**: Deploy Dapr control plane and enable sidecar injection

**Tasks**:
- Install Dapr CLI and initialize on DOKS
- Enable sidecar injection for application namespace
- Configure Dapr dashboard for monitoring
- Verify Dapr components are running

**Validation**: `dapr status -k` shows all components healthy

### Step 3: Deploy Kafka (via Strimzi)

**Objective**: Deploy Kafka cluster for event streaming

**Tasks**:
- Install Strimzi Kafka Operator
- Deploy Kafka cluster with 3 brokers
- Create topics for domain events
- Configure retention and partitioning
- Verify Kafka cluster health

**Validation**: `kubectl get kafka` shows cluster Ready

### Step 4: Configure Dapr Pub/Sub

**Objective**: Configure Dapr to use Kafka as pub/sub backend

**Tasks**:
- Create Dapr pub/sub component pointing to Kafka
- Create Dapr state store component for Redis
- Create Dapr secret store component for DOKS Secrets
- Configure Dapr resiliency policies (retries, timeouts)
- Verify component registration

**Validation**: `dapr components -k` shows all components

### Step 5: Deploy Services via Helm

**Objective**: Deploy all application services with Dapr sidecars

**Tasks**:
- Update Helm values for DOKS (ingress, resources, replicas)
- Add Dapr annotations to deployments
- Deploy backend with event publisher code
- Deploy frontend with Dapr sidecar
- Deploy AI agents as event consumers
- Configure ingress with TLS

**Validation**: All pods Ready, ingress accessible via HTTPS

### Step 6: Enable Autoscaling

**Objective**: Configure HPA for automatic scaling

**Tasks**:
- Define HPA for backend (CPU/memory based)
- Define HPA for frontend (request rate based)
- Define HPA for AI agents (queue depth based)
- Configure cluster autoscaler for node scaling
- Test scaling behavior under load

**Validation**: HPA shows current/desired replicas responding to load

### Step 7: Validate Event Flows

**Objective**: Verify end-to-end event processing

**Tasks**:
- Create test transaction and verify `transaction.created` event
- Verify AI agent receives and processes event
- Verify `ai.insight.generated` event is published
- Verify notification delivery
- Test idempotency with duplicate events
- Verify dead letter queue for failed events

**Validation**: Events flow through system within 5 seconds

### Step 8: Demo Resilience & Failover

**Objective**: Demonstrate production-ready resilience

**Tasks**:
- Simulate pod failure and verify auto-restart
- Simulate Kafka broker failure and verify recovery
- Test blue/green deployment with zero downtime
- Test rollback procedure
- Document failure scenarios and recovery times

**Validation**: System recovers from failures within defined SLOs

## Complexity Tracking

No constitution violations requiring justification.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| DOKS provisioning delays | High | Pre-provision cluster before implementation |
| Kafka resource consumption | Medium | Use Strimzi Kafka with modest broker config |
| Dapr learning curve | Medium | Focus on pub/sub only, defer other patterns |
| TLS certificate issues | Medium | Use Let's Encrypt with cert-manager |
| Event ordering requirements | Low | Design for eventual consistency |

## Dependencies

- **Phase IV Helm Charts**: Must be complete and working locally
- **DigitalOcean Account**: With API token configured
- **Domain Name**: For ingress TLS configuration
- **Container Registry**: Images pushed to Docker Hub or DOCR

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Execute Step 1-4 (infrastructure setup)
3. Execute Step 5-6 (service deployment)
4. Execute Step 7-8 (validation and demo)
