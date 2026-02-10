---
id: "0001"
title: "Phase IV Kubernetes Laws Added"
stage: constitution
date: 2026-02-09
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: ibek34578921
command: /sp.constitution
labels: ["kubernetes", "phase-iv", "infrastructure", "helm", "minikube"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

Deploy the AI-powered Wealth & Spending Companion as a locally orchestrated, cloud-native system using Kubernetes, governed by specs and operated via AI tooling.

Core Principles:
- Spec-Driven Infrastructure: No manual kubectl YAML writing; Claude Code generates infra from specs
- Container First: Every service is containerized with no local runtime dependencies
- AI-Operated Kubernetes: kubectl-ai used for cluster operations; kagent used for AI-managed workloads
- Local Cloud Parity: Minikube simulates real cloud; Helm charts are cloud-ready

Forbidden Practices:
- Manual kubectl apply without spec
- Single-container monolith
- Hardcoded secrets
- Non-reproducible clusters

Kubernetes Governance Rules:
- Each service runs in its own Pod
- Communication via Services only
- Secrets injected via env vars
- MCP must be stateless
- Agents must scale independently
- Helm is the single source of truth
- kubectl-ai controls operations
- kagent governs AI workloads

## Response snapshot

Updated constitution from v2.0.0 to v3.0.0 (MAJOR version bump) with comprehensive Phase IV Kubernetes Laws:

1. Added "Phase IV Laws – Local Kubernetes Deployment" section with:
   - Core Principles (Spec-Driven Infrastructure, Container First, AI-Operated Kubernetes, Local Cloud Parity)
   - Forbidden Practices table with severity levels
   - Kubernetes Governance Rules table
   - AI-Operated Kubernetes Laws (kubectl-ai and kagent requirements)
   - Helm Chart Standards with directory structure
   - Container Requirements with Dockerfile patterns
   - Service Mesh Readiness for Phase V
   - Phase IV Deployment Architecture diagram
   - Acceptance Criteria table

2. Updated Cloud-Native Design principle (IV) to include kubectl-ai, kagent, and Helm governance

3. Updated Technology Stack DevOps section with kubectl-ai and kagent

4. Updated Deployment Phases to mark Phase III as complete and Phase IV as in progress

## Outcome

- ✅ Impact: Constitution v3.0.0 with Phase IV Kubernetes governance laws
- 🧪 Tests: N/A (governance document)
- 📁 Files: 1 file updated (.specify/memory/constitution.md)
- 🔁 Next prompts: Create Phase IV spec, plan, and tasks for Kubernetes implementation
- 🧠 Reflection: Major version bump appropriate due to new phase-level governance rules

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
