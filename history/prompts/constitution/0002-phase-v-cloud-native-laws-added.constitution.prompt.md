---
id: "0002"
title: Phase V Cloud-Native Laws Added
stage: constitution
date: 2026-02-10
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: 006-k8s-local-deployment
user: ibek34578921
command: /sp.constitution
labels: ["phase-v", "cloud-native", "doks", "kafka", "dapr", "event-driven"]
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

Phase V — Cloud-Native Constitution

Purpose:
Operate the AI Wealth & Spending Companion as a distributed, event-driven, production-ready cloud system on DigitalOcean Kubernetes (DOKS).

Core Laws

Spec-Driven Infra only (Claude Code generates manifests)

Event-Driven Architecture via Kafka + Dapr

Zero manual kubectl edits in prod

Observability & resilience required

All services cloud-portable

Forbidden

Local-only configs

Hardcoded secrets

Point-to-point service coupling

Direct Kafka SDK usage (must go through Dapr)

📘 specs/sp.constitution.md
Distributed Systems Governance

Reliability Rules

Services communicate via Dapr pub/sub

Events are idempotent

Services restart safely

Security Rules

Secrets via DOKS Secrets

TLS on ingress

Principle of least privilege

AI Rules

AI agents consume events

AI insights published as events

MCP tools accessible via service mesh

Ops Rules

Kubernetes is source of truth

Blue/Green deployments

Rollbacks supported

## Response snapshot

Updated constitution from v3.0.0 to v4.0.0 (MAJOR version bump) with Phase V Cloud-Native laws:

- Added Phase V Laws section with 5 core laws (Spec-Driven Infra, Event-Driven Architecture, Zero Manual kubectl, Observability Required, Cloud-Portable Services)
- Added Forbidden Practices table (Local-only configs, Hardcoded secrets, Point-to-point coupling, Direct Kafka SDK)
- Added Event-Driven Architecture Laws (Dapr pub/sub, event schemas, topic naming)
- Added Distributed Systems Governance (Reliability, Security, AI Event, Operations rules)
- Added Phase V Architecture diagram with DOKS, Dapr, Kafka, Observability stack
- Updated Technology Stack with Cloud-Native section
- Updated Deployment Phases with Phase V details

## Outcome

- ✅ Impact: Constitution v4.0.0 now governs Phase V cloud-native production deployment
- 🧪 Tests: N/A (governance document)
- 📁 Files: 1 file modified (.specify/memory/constitution.md)
- 🔁 Next prompts: /sp.spec for Phase V feature specs, /sp.plan for implementation planning
- 🧠 Reflection: Phase V laws establish clear governance for distributed, event-driven architecture

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Create Phase V spec with event schemas
