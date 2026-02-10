# Feature Specification: Phase IV Local Kubernetes Deployment

**Feature Branch**: `006-k8s-local-deployment`
**Created**: 2026-02-09
**Status**: Draft
**Input**: User description: "Phase IV Local Kubernetes Deployment with Minikube, Helm, kubectl-ai and kagent for AI-powered Wealth & Spending Companion"

## Overview

Deploy the AI-powered Wealth & Spending Companion as a locally orchestrated, cloud-native system using Kubernetes. The system will be governed by specs and operated via AI tooling (kubectl-ai and kagent). This enables developers to run the complete production-like environment locally for development and integration testing.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Deploys Full Stack Locally (Priority: P1)

As a developer, I want to deploy the entire AI Wealth Companion stack to my local Kubernetes cluster with a single command, so that I can develop and test against a production-like environment.

**Why this priority**: This is the foundational capability - without local deployment, no other Phase IV features can be developed or tested.

**Independent Test**: Can be fully tested by running `helm install` and verifying all pods reach Ready state, delivering a working local environment.

**Acceptance Scenarios**:

1. **Given** Minikube is running and Helm is installed, **When** developer runs the Helm install command, **Then** all services (Frontend, Backend, MCP Server, AI Agents) are deployed and reach Ready state within 5 minutes
2. **Given** all services are deployed, **When** developer accesses the ingress URL, **Then** the frontend loads and connects to the backend successfully
3. **Given** a fresh Minikube cluster, **When** developer runs the deployment, **Then** the same configuration produces identical results every time

---

### User Story 2 - AI-Operated Cluster Health Check (Priority: P2)

As a developer, I want to use kubectl-ai to query cluster health in natural language, so that I can quickly understand the state of my local deployment without memorizing kubectl commands.

**Why this priority**: AI-operated Kubernetes is a key differentiator and constitution requirement; enables faster debugging and operations.

**Independent Test**: Can be tested by asking kubectl-ai "describe cluster health" and receiving an accurate, human-readable summary of all service statuses.

**Acceptance Scenarios**:

1. **Given** the cluster is running with all services, **When** developer asks kubectl-ai "what is the cluster health?", **Then** kubectl-ai returns a summary of pod statuses, resource usage, and any warnings
2. **Given** a service is in CrashLoopBackOff, **When** developer asks kubectl-ai "why is backend failing?", **Then** kubectl-ai explains the failure reason from logs
3. **Given** services are running normally, **When** developer asks kubectl-ai to "restart the backend", **Then** the backend pod is gracefully restarted

---

### User Story 3 - AI Agent Scaling via kagent (Priority: P2)

As a developer, I want kagent to monitor and manage AI agent workloads, so that agents can scale based on load and recover from failures automatically.

**Why this priority**: AI workload management is essential for production-readiness and constitution compliance.

**Independent Test**: Can be tested by simulating load on an agent and observing kagent scale up replicas, then scale down when load decreases.

**Acceptance Scenarios**:

1. **Given** an AI agent pod fails, **When** kagent detects the failure, **Then** kagent automatically restarts the agent within 30 seconds
2. **Given** an AI agent is under high load, **When** kagent policies trigger, **Then** additional agent replicas are spawned
3. **Given** load decreases on AI agents, **When** kagent policies evaluate, **Then** excess replicas are terminated gracefully

---

### User Story 4 - Secret Management via Kubernetes Secrets (Priority: P3)

As a developer, I want all secrets (JWT, Gemini API key, database credentials) injected via Kubernetes Secrets, so that no sensitive data is hardcoded in configuration files.

**Why this priority**: Security is non-negotiable per constitution; secrets management enables safe credential handling.

**Independent Test**: Can be tested by deploying without any secrets in source code and verifying services authenticate successfully using injected secrets.

**Acceptance Scenarios**:

1. **Given** Kubernetes Secrets are created with required credentials, **When** pods start, **Then** secrets are injected as environment variables
2. **Given** a developer inspects deployment manifests, **When** searching for credentials, **Then** no plaintext secrets are found in any YAML files
3. **Given** a secret value changes, **When** the Secret is updated and pods restarted, **Then** services use the new credentials

---

### User Story 5 - Service Communication via Kubernetes Services (Priority: P3)

As a developer, I want all inter-service communication to go through Kubernetes Services, so that the architecture is ready for service mesh integration in Phase V.

**Why this priority**: Proper service networking is required for Dapr integration in Phase V.

**Independent Test**: Can be tested by verifying frontend-to-backend and backend-to-MCP communication works only through Service DNS names.

**Acceptance Scenarios**:

1. **Given** Frontend and Backend are deployed, **When** Frontend makes an API call, **Then** the request routes through the Backend Service (not direct pod IP)
2. **Given** Backend needs to call MCP Server, **When** making the call, **Then** communication uses the MCP Service endpoint
3. **Given** a pod is replaced, **When** a new pod starts with a different IP, **Then** services continue to function without configuration changes

---

### Edge Cases

- What happens when Minikube runs out of resources (memory/CPU)?
  - System should report clear resource exhaustion errors via kubectl-ai
- How does system handle pod eviction due to resource pressure?
  - Pods should be rescheduled; kagent should monitor and report
- What happens when Ingress controller is not available?
  - Helm install should fail fast with clear error message
- How does the system handle network partitions between services?
  - Services should timeout gracefully and log errors; no silent failures
- What happens when Neon DB (external) is unreachable?
  - Backend should return appropriate error responses; health checks should fail

## Requirements *(mandatory)*

### Functional Requirements

**Infrastructure & Deployment**:
- **FR-001**: System MUST deploy all services to Minikube via a single Helm chart
- **FR-002**: System MUST support environment-specific configuration via values.yaml overrides
- **FR-003**: All services MUST be containerized with no local runtime dependencies
- **FR-004**: Helm MUST be the single source of truth for all Kubernetes resources
- **FR-005**: System MUST generate all infrastructure from specs (no manual kubectl YAML)

**Services**:
- **FR-006**: Frontend service MUST deploy as a containerized Next.js application
- **FR-007**: Backend service MUST deploy as a containerized FastAPI application
- **FR-008**: MCP Server MUST deploy as a stateless containerized service
- **FR-009**: AI Agent services MUST deploy independently and scale separately
- **FR-010**: All services MUST connect to Neon DB (external cloud database)

**Networking**:
- **FR-011**: System MUST expose Frontend via Kubernetes Ingress
- **FR-012**: All inter-service communication MUST use Kubernetes Services
- **FR-013**: Backend MUST NOT be directly exposed externally (only through Ingress)

**Secrets & Configuration**:
- **FR-014**: System MUST store all secrets in Kubernetes Secrets
- **FR-015**: System MUST inject secrets as environment variables to pods
- **FR-016**: System MUST use ConfigMaps for non-sensitive configuration
- **FR-017**: No secrets MUST appear in Helm charts, Dockerfiles, or source code

**AI Operations**:
- **FR-018**: kubectl-ai MUST be able to describe cluster health in natural language
- **FR-019**: kubectl-ai MUST be able to restart services on command
- **FR-020**: kubectl-ai MUST be able to explain service failures from logs
- **FR-021**: kagent MUST monitor all AI agent pod health
- **FR-022**: kagent MUST automatically restart failed AI agent pods
- **FR-023**: kagent MUST scale AI agents based on defined policies

**Observability**:
- **FR-024**: All services MUST expose health check endpoints
- **FR-025**: All pods MUST have liveness and readiness probes configured
- **FR-026**: System MUST support distributed tracing header propagation

### Key Entities

- **Helm Chart**: Package containing all Kubernetes manifests, values, and templates for the complete system deployment
- **Service**: Kubernetes abstraction for stable networking endpoints (Frontend, Backend, MCP Server, each Agent)
- **Pod**: Running container instance for each service component
- **ConfigMap**: Non-sensitive configuration data (environment settings, feature flags)
- **Secret**: Sensitive credentials (JWT secret, Gemini API key, database URL)
- **Ingress**: External access point routing traffic to Frontend service
- **HPA (Horizontal Pod Autoscaler)**: Scaling configuration for AI agent workloads

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developer can deploy the complete stack from zero to running in under 10 minutes
- **SC-002**: All pods reach Ready state within 5 minutes of Helm install
- **SC-003**: Redeployment from clean cluster produces identical configuration 100% of the time
- **SC-004**: kubectl-ai responds to natural language queries within 5 seconds
- **SC-005**: kagent detects and restarts failed AI agent pods within 30 seconds
- **SC-006**: No plaintext secrets exist in any source-controlled files
- **SC-007**: Frontend is accessible via Ingress URL immediately after deployment
- **SC-008**: Backend health check returns healthy within 60 seconds of pod start
- **SC-009**: System operates correctly with Minikube's default resource allocation (2 CPU, 4GB RAM)
- **SC-010**: All inter-service calls use Kubernetes Service DNS names (verified by network policy)

## Assumptions

1. Developer has Minikube installed and running (minimum version 1.30)
2. Developer has Helm 3.x installed
3. kubectl-ai and kagent are available as kubectl plugins
4. Neon PostgreSQL database is already provisioned and accessible
5. Docker images will be built locally or pulled from a container registry
6. Local machine has at least 8GB RAM and 4 CPU cores available
7. Developer has basic familiarity with Kubernetes concepts

## Out of Scope

- Production cloud deployment (Phase V)
- Kafka event streaming integration (Phase V)
- Dapr service mesh integration (Phase V)
- CI/CD pipeline automation
- Container image registry setup
- SSL/TLS certificate management for Ingress
- Multi-node cluster configuration
- Persistent volume claims (Neon DB is external)

## Dependencies

- Phase III AI Financial Assistant (complete) - AI agents to deploy
- Existing Backend and Frontend Dockerfiles
- Neon PostgreSQL database credentials
- Gemini API key for AI services
- JWT secret for authentication

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Minikube resource constraints | High | Document minimum requirements; provide resource tuning guide |
| kubectl-ai/kagent learning curve | Medium | Include example queries and troubleshooting guide |
| Network latency to Neon DB | Medium | Document expected latency; consider connection pooling |
| Docker image build time | Low | Provide pre-built images for common scenarios |
