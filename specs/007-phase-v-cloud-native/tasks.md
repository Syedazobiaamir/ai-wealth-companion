# Tasks: Phase V Cloud-Native Production System

**Input**: Design documents from `/specs/007-phase-v-cloud-native/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested - implementation tasks only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Frontend**: `frontend/src/`
- **Helm**: `helm/ai-wealth-companion/`
- **Scripts**: `scripts/`

---

## Phase 1: Setup (Shared Infrastructure) ✅ COMPLETE

**Purpose**: Project initialization and DOKS cluster provisioning

- [x] T001 Create DOKS cluster setup script in scripts/doks-setup.sh
- [x] T002 [P] Create DOKS deployment script in scripts/doks-deploy.sh
- [x] T003 [P] Create DOKS rollback script in scripts/doks-rollback.sh
- [x] T004 [P] Create event validation script in scripts/validate-events.sh
- [x] T005 Create DOKS-specific Helm values in helm/ai-wealth-companion/values-doks.yaml
- [x] T006 [P] Create application namespace manifest in helm/ai-wealth-companion/templates/namespace.yaml

---

## Phase 2: Foundational (Blocking Prerequisites) ✅ COMPLETE

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Kafka Infrastructure

- [x] T007 Create Kafka cluster manifest in helm/ai-wealth-companion/templates/kafka/kafka-cluster.yaml
- [x] T008 [P] Create Kafka topics manifest in helm/ai-wealth-companion/templates/kafka/kafka-topics.yaml

### Dapr Components

- [x] T009 Create Dapr pub/sub component in helm/ai-wealth-companion/templates/dapr/pubsub.yaml
- [x] T010 [P] Create Dapr state store component in helm/ai-wealth-companion/templates/dapr/statestore.yaml
- [x] T011 [P] Create Dapr secret store component in helm/ai-wealth-companion/templates/dapr/secretstore.yaml

### Backend Event Infrastructure

- [x] T012 Create event schemas module in backend/src/events/schemas.py
- [x] T013 [P] Create event publisher module in backend/src/events/publishers.py
- [x] T014 [P] Create event handler base module in backend/src/events/handlers.py
- [x] T015 Create idempotency middleware in backend/src/events/idempotency.py

### Helm Dapr Annotations

- [x] T016 Update backend deployment with Dapr annotations in helm/ai-wealth-companion/templates/backend-deployment.yaml
- [x] T017 [P] Update frontend deployment with Dapr annotations in helm/ai-wealth-companion/templates/frontend-deployment.yaml
- [x] T018 [P] Update MCP server deployment with Dapr annotations in helm/ai-wealth-companion/templates/mcp-server-deployment.yaml

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Production Deployment (Priority: P1) 🎯 MVP ✅ COMPLETE

**Goal**: Deploy the entire AI Wealth Companion to DOKS using a single command with high availability

**Independent Test**: Run deployment command and verify all pods reach Ready state with external ingress accessible

### Cloud Tasks

- [x] T019 [US1] Provision DOKS cluster via doctl in scripts/doks-setup.sh (enhance from T001)
- [x] T020 [P] [US1] Install NGINX ingress controller in scripts/doks-setup.sh
- [x] T021 [P] [US1] Configure cert-manager for TLS in scripts/doks-setup.sh
- [x] T022 [US1] Create Kubernetes secrets manifest in helm/ai-wealth-companion/templates/secrets.yaml

### Dapr Installation

- [x] T023 [US1] Add Dapr initialization to scripts/doks-setup.sh
- [x] T024 [US1] Enable Dapr sidecar injection for namespace in helm/ai-wealth-companion/templates/namespace.yaml

### Kafka Deployment

- [x] T025 [US1] Add Strimzi operator installation to scripts/doks-setup.sh
- [x] T026 [US1] Configure Kafka broker resources in helm/ai-wealth-companion/templates/kafka/kafka-cluster.yaml

### Service Deployment

- [x] T027 [US1] Update Helm chart dependencies in helm/ai-wealth-companion/Chart.yaml
- [x] T028 [US1] Configure ingress with TLS in helm/ai-wealth-companion/templates/ingress.yaml
- [x] T029 [US1] Implement single-command deploy in scripts/doks-deploy.sh (enhance from T002)

### Validation

- [x] T030 [US1] Add deployment validation to scripts/doks-deploy.sh
- [x] T031 [US1] Add pod health check verification to scripts/validate-events.sh

**Checkpoint**: User Story 1 complete - DOKS deployment working with single command

---

## Phase 4: User Story 2 - Event-Driven Transactions (Priority: P1) ✅ COMPLETE

**Goal**: Process financial transactions through event-driven system with real-time AI agent reactions

**Independent Test**: Create a transaction and observe events published to Kafka topics consumed by AI agents

### Event Publishing

- [x] T032 [US2] Implement transaction.created event publisher in backend/src/events/publishers.py
- [x] T033 [P] [US2] Implement transaction.updated event publisher in backend/src/events/publishers.py
- [x] T034 [US2] Integrate event publishing in transaction service in backend/src/services/transaction.py

### AI Agent Event Subscription

- [x] T035 [US2] Create Analytics agent event handler in backend/src/agents/subagents/analytics_agent.py
- [x] T036 [P] [US2] Create Notification agent event handler in backend/src/agents/subagents/notification_agent.py

### Budget Exceeded Event

- [x] T037 [US2] Implement budget.exceeded event publisher in backend/src/events/publishers.py
- [x] T038 [US2] Add budget threshold detection in backend/src/agents/subagents/analytics_agent.py
- [x] T039 [US2] Configure dead letter queue for failed events in helm/ai-wealth-companion/templates/dapr/pubsub.yaml

### Event Flow Validation

- [x] T040 [US2] Add transaction event validation to scripts/validate-events.sh
- [x] T041 [US2] Add end-to-end event latency check (< 5s) to scripts/validate-events.sh

**Checkpoint**: User Story 2 complete - Events flow from transactions to AI agents

---

## Phase 5: User Story 3 - AI Insights via Events (Priority: P2) ✅ COMPLETE

**Goal**: Deliver AI-generated financial insights automatically via events

**Independent Test**: Trigger financial events and observe AI insight events generated and delivered to user

### AI Insight Generation

- [x] T042 [US3] Implement ai.insight.generated event publisher in backend/src/events/publishers.py
- [x] T043 [US3] Add spending pattern detection in backend/src/agents/subagents/analytics_agent.py
- [x] T044 [US3] Add budget warning generation (80% threshold) in backend/src/agents/subagents/analytics_agent.py

### Notification Delivery

- [x] T045 [US3] Implement user.alert.sent event publisher in backend/src/events/publishers.py
- [x] T046 [US3] Subscribe notification agent to ai.insight.generated in backend/src/agents/subagents/notification_agent.py
- [x] T047 [US3] Implement in-app notification delivery in backend/src/services/notification_service.py

### Event Idempotency

- [x] T048 [US3] Implement event ID deduplication with Redis in backend/src/events/idempotency.py
- [x] T049 [US3] Add idempotency check to all event handlers in backend/src/events/handlers.py

**Checkpoint**: User Story 3 complete - AI insights flow automatically to users

---

## Phase 6: User Story 4 - Zero-Downtime Deployments (Priority: P2) ✅ COMPLETE

**Goal**: Deploy updates without service interruption with automatic rollback

**Independent Test**: Deploy an update while monitoring active user sessions for interruption

### Rolling Update Configuration

- [x] T050 [US4] Configure rolling update strategy in helm/ai-wealth-companion/templates/backend-deployment.yaml
- [x] T051 [P] [US4] Configure rolling update strategy in helm/ai-wealth-companion/templates/frontend-deployment.yaml
- [x] T052 [P] [US4] Add readiness probes to all deployments in helm/ai-wealth-companion/templates/

### Rollback Support

- [x] T053 [US4] Implement rollback command in scripts/doks-rollback.sh (enhance from T003)
- [x] T054 [US4] Add rollback validation (< 2 min) to scripts/doks-rollback.sh
- [x] T055 [US4] Add Helm history tracking in scripts/doks-deploy.sh

### Health Checks

- [x] T056 [US4] Add liveness probes to backend in helm/ai-wealth-companion/templates/backend-deployment.yaml
- [x] T057 [P] [US4] Add liveness probes to frontend in helm/ai-wealth-companion/templates/frontend-deployment.yaml
- [x] T058 [US4] Configure automatic rollback on health check failure in scripts/doks-deploy.sh

**Checkpoint**: User Story 4 complete - Zero-downtime deployments with rollback working

---

## Phase 7: User Story 5 - Horizontal Scaling (Priority: P3) ✅ COMPLETE

**Goal**: Automatic service scaling based on load

**Independent Test**: Generate artificial load and observe pod count increase/decrease

### HPA Configuration

- [x] T059 [US5] Create HPA for backend in helm/ai-wealth-companion/templates/hpa.yaml
- [x] T060 [P] [US5] Create HPA for frontend in helm/ai-wealth-companion/templates/hpa.yaml
- [x] T061 [P] [US5] Create HPA for MCP server in helm/ai-wealth-companion/templates/hpa.yaml

### Resource Limits

- [x] T062 [US5] Configure resource requests/limits for backend in helm/ai-wealth-companion/values-doks.yaml
- [x] T063 [P] [US5] Configure resource requests/limits for frontend in helm/ai-wealth-companion/values-doks.yaml
- [x] T064 [P] [US5] Configure resource requests/limits for mcp-server in helm/ai-wealth-companion/values-doks.yaml

### Cluster Autoscaler

- [x] T065 [US5] Configure node pool autoscaling in scripts/doks-setup.sh
- [x] T066 [US5] Add load testing validation in scripts/validate-events.sh

**Checkpoint**: User Story 5 complete - Services scale automatically with load

---

## Phase 8: User Story 6 - Centralized Observability (Priority: P3) ✅ COMPLETE

**Goal**: Centralized logging, metrics, and tracing for all services

**Independent Test**: Trigger errors and verify they appear in centralized dashboards with full trace context

### Observability Stack Deployment

- [x] T067 [US6] Create Prometheus deployment in helm/ai-wealth-companion/templates/observability/prometheus.yaml
- [x] T068 [P] [US6] Create Grafana deployment in helm/ai-wealth-companion/templates/observability/grafana.yaml
- [x] T069 [P] [US6] Create Jaeger deployment in helm/ai-wealth-companion/templates/observability/jaeger.yaml
- [x] T070 [P] [US6] Create Loki deployment in helm/ai-wealth-companion/templates/observability/loki.yaml

### Metrics Endpoints

- [x] T071 [US6] Add Prometheus metrics endpoint to backend in backend/src/api/metrics.py
- [x] T072 [US6] Configure Dapr tracing with Jaeger in helm/ai-wealth-companion/templates/dapr/config.yaml

### Dashboards

- [x] T073 [US6] Create Grafana dashboard for service metrics in helm/ai-wealth-companion/templates/observability/dashboards/
- [x] T074 [US6] Configure log aggregation to Loki in helm/ai-wealth-companion/values-doks.yaml

**Checkpoint**: User Story 6 complete - Full observability stack operational

---

## Phase 9: Resilience & Failover (Final Validation) ✅ COMPLETE

**Purpose**: Demonstrate production-ready resilience

### Pod Failure Testing

- [x] T075 Add pod failure simulation to scripts/validate-events.sh
- [x] T076 Verify auto-restart within 30 seconds in scripts/validate-events.sh

### Kafka Failure Handling

- [x] T077 Add Kafka broker failure simulation to scripts/validate-events.sh
- [x] T078 Verify event queue persistence during Kafka outage in scripts/validate-events.sh

### Documentation

- [x] T079 [P] Document failure scenarios and recovery times in specs/007-phase-v-cloud-native/runbook.md
- [x] T080 [P] Update quickstart.md with production deployment steps in specs/007-phase-v-cloud-native/quickstart.md

---

## Phase 10: Polish & Cross-Cutting Concerns ✅ COMPLETE

**Purpose**: Improvements that affect multiple user stories

- [x] T081 [P] Code cleanup and remove debug logging
- [x] T082 [P] Security hardening review of all secrets (network-policies.yaml)
- [x] T083 Run full quickstart.md validation
- [x] T084 Create deployment runbook in specs/007-phase-v-cloud-native/runbook.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (P1) and US2 (P1) should be done first
  - US3 (P2) and US4 (P2) can follow
  - US5 (P3) and US6 (P3) can be parallel
- **Resilience (Phase 9)**: Depends on all user stories complete
- **Polish (Phase 10)**: Depends on resilience validation complete

### User Story Dependencies

| Story | Priority | Can Start After | Depends On |
|-------|----------|-----------------|------------|
| US1 - Production Deployment | P1 | Foundational | None |
| US2 - Event-Driven Transactions | P1 | Foundational | US1 (cluster must exist) |
| US3 - AI Insights via Events | P2 | Foundational | US2 (events must work) |
| US4 - Zero-Downtime Deployments | P2 | Foundational | US1 (deployment must exist) |
| US5 - Horizontal Scaling | P3 | Foundational | US1, US4 |
| US6 - Centralized Observability | P3 | Foundational | US1 (pods must exist) |

### Parallel Opportunities

**Within Phase 2 (Foundational)**:
- T009, T010, T011 (Dapr components) - parallel
- T012, T013, T014 (Event modules) - parallel
- T016, T017, T018 (Deployment updates) - parallel

**Within User Stories**:
- All [P] marked tasks within same story

**Across Stories** (with multiple developers):
- US4 and US6 can run parallel after US1 completes
- US5 can start once US1 and US4 complete

---

## Parallel Example: Foundational Phase

```bash
# Launch all Dapr components together:
Task: "Create Dapr pub/sub component in helm/ai-wealth-companion/templates/dapr/pubsub.yaml"
Task: "Create Dapr state store component in helm/ai-wealth-companion/templates/dapr/statestore.yaml"
Task: "Create Dapr secret store component in helm/ai-wealth-companion/templates/dapr/secretstore.yaml"

# Launch all event modules together:
Task: "Create event schemas module in backend/src/events/schemas.py"
Task: "Create event publisher module in backend/src/events/publishers.py"
Task: "Create event handler base module in backend/src/events/handlers.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2)

1. Complete Phase 1: Setup (scripts)
2. Complete Phase 2: Foundational (Kafka, Dapr, Events infra)
3. Complete Phase 3: US1 - Production Deployment
4. Complete Phase 4: US2 - Event-Driven Transactions
5. **STOP and VALIDATE**: Test deployment and event flows
6. Deploy/demo as MVP

### Incremental Delivery

1. Setup + Foundational → Infrastructure ready
2. Add US1 → Test deployment → Demo (MVP!)
3. Add US2 → Test events → Demo
4. Add US3 → Test AI insights → Demo
5. Add US4 → Test zero-downtime → Demo
6. Add US5 + US6 → Full production features

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: US1 (Production Deployment)
   - Developer B: US2 (Event-Driven) - starts after US1 cluster exists
3. After US1 + US2:
   - Developer A: US4 (Zero-Downtime)
   - Developer B: US3 (AI Insights)
   - Developer C: US5 + US6 (Scaling + Observability)

---

## Summary

| Phase | Task Count | Focus |
|-------|------------|-------|
| Setup | 6 | Scripts and base files |
| Foundational | 12 | Kafka, Dapr, Events infra |
| US1 - Deployment | 13 | DOKS cluster and services |
| US2 - Events | 10 | Event publishing and subscription |
| US3 - AI Insights | 8 | AI event generation and delivery |
| US4 - Zero-Downtime | 9 | Rolling updates and rollback |
| US5 - Scaling | 8 | HPA and resource limits |
| US6 - Observability | 8 | Prometheus, Grafana, Jaeger |
| Resilience | 6 | Failure testing and docs |
| Polish | 4 | Cleanup and final validation |
| **Total** | **84** | |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- MVP scope: US1 + US2 (core deployment and event-driven architecture)
