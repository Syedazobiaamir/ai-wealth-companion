<!--
SYNC IMPACT REPORT
==================
Version change: 1.0.0 → 1.1.0 (MINOR - Phase I Laws added)
Modified principles: None
Added sections:
  - Phase I Laws (Core Laws, Engineering Laws, Safety Laws, Acceptance Laws)
  - Phase I Data Storage
  - Phase I Validation Rules
Removed sections: None
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ (aligned)
  - .specify/templates/spec-template.md ✅ (aligned)
  - .specify/templates/tasks-template.md ✅ (aligned)
Follow-up TODOs: None
-->

# AI Wealth & Spending Companion Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

All features MUST follow the specs → Claude Code → implementation workflow:

- Feature specifications MUST be written and approved before implementation begins
- Use Spec-Kit Plus templates for all artifacts (spec.md, plan.md, tasks.md)
- Prompt History Records (PHR) MUST be created for every development session
- Architecture Decision Records (ADR) MUST be proposed for significant decisions
- No code changes without corresponding spec or task reference

**Rationale**: Ensures traceability, reduces rework, and maintains alignment between
business requirements and technical implementation.

### II. AI-First Architecture

Subagents and Skills are first-class architectural components:

| Component | Type | Responsibility |
|-----------|------|----------------|
| Frontend Subagent | Subagent | Dashboard, forms, charts generation |
| Banking Subagent | Subagent | Account & transaction CRUD, recurring payments |
| Investment Subagent | Subagent | Stock/crypto/mutual fund tracking, ROI calculation |
| Analytics Subagent | Subagent | Predictive insights, budgeting recommendations |
| Notification Subagent | Subagent | Event-driven alerts for budget and transactions |
| Chatbot NLP Skill | Skill | Natural language & voice command processing |
| Security Subagent | Subagent | Input validation, mock encryption |

- Subagents MUST be independently deployable and testable
- Skills MUST be reusable across multiple phases
- All reusable logic MUST reside in `phase3/chatbot_agent/skills/`
- Each subagent MUST expose a well-defined API contract

**Rationale**: Enables modular development, facilitates parallel workstreams, and
maximizes code reuse across project phases.

### III. Cloud-Native Design

The system MUST be designed for containerized, orchestrated deployment:

- Phase IV: Local Kubernetes via Minikube + Helm + kagent
- Phase V: DigitalOcean Kubernetes + Kafka + Dapr
- Microservices architecture with separate agents for Banking, Analytics,
  Notifications, and Investments
- Services MUST be stateless; state persisted in external stores
- All inter-service communication MUST use defined contracts (REST/gRPC/events)
- Configuration MUST be externalized via environment variables or ConfigMaps

**Rationale**: Ensures scalability, resilience, and portability across local
development and cloud production environments.

### IV. Multi-Modal Interface

The application MUST support multiple interaction modes:

- CLI interface with emoji + color-coded feedback
- Web dashboard (Next.js + Tailwind)
- Voice command support (+200 bonus points)
- Multi-language support: English and Urdu (+100 bonus points)
- AI chatbot with personality and predictive investment assistant

Interface requirements:
- All interfaces MUST provide consistent data and behavior
- Error messages MUST be user-friendly and actionable
- Response times MUST meet defined performance constraints

**Rationale**: Maximizes accessibility and user engagement across different
user preferences and contexts.

### V. Test-First Development (NON-NEGOTIABLE)

TDD is mandatory for all implementation work:

- Tests MUST be written before implementation code
- Tests MUST fail (Red) before implementation begins
- Implementation MUST make tests pass (Green)
- Code MUST be refactored only after tests pass (Refactor)
- Contract tests MUST exist for all API endpoints
- Integration tests MUST cover critical user journeys

**Rationale**: Ensures code correctness, prevents regressions, and maintains
confidence during refactoring.

### VI. Observability & Security

All components MUST be observable and secure:

Observability requirements:
- Structured logging in JSON format
- Metrics exposed for monitoring (latency, throughput, errors)
- Distributed tracing for cross-service requests
- Alerting thresholds defined for critical paths

Security requirements:
- Input validation on all external interfaces
- Mock encryption for sensitive data in development
- No hardcoded secrets; use environment variables or secret stores
- Audit logging for security-relevant events
- Authentication/authorization framework for all protected resources

**Rationale**: Enables rapid debugging, ensures compliance, and protects user
financial data.

## Phase I Laws – CLI Financial Core

Phase I establishes a stable, testable, in-memory financial core that will be
reused by the web app and AI agents in subsequent phases.

### Core Laws (NON-NEGOTIABLE)

- All behavior MUST come from specifications
- No AI features in Phase I
- No databases; in-memory storage ONLY
- CLI is the ONLY interface in Phase I
- Clean separation MUST exist between CLI, logic, and storage layers

**Rationale**: Creates a solid foundation that can be extended without refactoring
the core domain logic.

### Engineering Laws

- Domain logic MUST be framework-independent
- Storage layer MUST be swappable (in-memory now, database later)
- Commands MUST be deterministic (same input → same output)
- Every command MUST be independently testable

**Rationale**: Ensures the CLI core can be lifted into web/AI phases without
modification to business logic.

### Safety Laws

- No real banking connections permitted
- No real financial advice permitted
- Sample/mock data ONLY

**Rationale**: Protects users and developers from accidental financial operations
during development.

### Acceptance Laws

- Every feature MUST work via CLI
- All commands MUST show user confirmations
- Data resets on application restart (no persistence)

**Rationale**: Simplifies testing and ensures predictable behavior during Phase I.

### Phase I Data Storage

| Data Type | Storage Structure |
|-----------|-------------------|
| Accounts | Dictionary (key: account_id) |
| Transactions | List of dictionaries |
| Recurring Payments | Boolean flag on transaction |

### Phase I Validation Rules

| Field | Validation Rule |
|-------|-----------------|
| Account Name | MUST be unique |
| Transaction Amount | MUST be > 0 |
| Transaction Date | MUST be valid YYYY-MM-DD format |
| Transaction Type | MUST be one of: Income, Expense, Transfer |
| Recurring Flag | MUST be Yes or No |

### Phase I UI Guidelines

- Emoji & color coding: 💚 Income, ❤️ Expense, 💛 Recurring
- Menu numbers for clear navigation
- Tabular output for transactions (use `tabulate` library)

## Technology Stack

**Backend**:
- Language: Python 3.x
- Framework: FastAPI + SQLModel
- Database: PostgreSQL (production), SQLite (development)

**Frontend**:
- Framework: Next.js
- Styling: Tailwind CSS
- Charts: TBD (Recharts or Chart.js recommended)

**AI/ML**:
- Claude Code for development assistance
- Natural language processing for chatbot
- Voice recognition integration

**DevOps**:
- Containerization: Docker
- Orchestration: Kubernetes (Minikube → DigitalOcean)
- Event streaming: Kafka
- Service mesh: Dapr

## AI Subagents & Skills Architecture

### Subagent Deployment Model

```
┌─────────────────────────────────────────────────────────┐
│                    API Gateway                          │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ Banking  │  │Investment│  │Analytics │  │Notifica-│ │
│  │ Subagent │  │ Subagent │  │ Subagent │  │  tion   │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
├─────────────────────────────────────────────────────────┤
│              Shared Skills Layer                        │
│  ┌──────────────────┐  ┌──────────────────────────────┐ │
│  │ Chatbot NLP Skill│  │    Security Validation       │ │
│  └──────────────────┘  └──────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│                    Data Layer                           │
│         (PostgreSQL / Event Store / Cache)              │
└─────────────────────────────────────────────────────────┘
```

### Skill Reuse Policy

- Skills MUST be defined once in `phase3/chatbot_agent/skills/`
- Skills MUST NOT contain business logic; delegate to subagents
- Skills MUST be versioned alongside the main application

## UI/UX Standards

### Color Coding for Transaction Types

| Type | Color | Emoji |
|------|-------|-------|
| Income | Green | 💚 |
| Expense | Red | ❤️ |
| Recurring | Yellow | 💛 |

### Category Icons

| Category | Emoji |
|----------|-------|
| Food | 🍔 |
| Rent | 🏠 |
| Utilities | 💡 |
| Salary | 💵 |
| Investment | 💎 |

### Interface Guidelines

- CLI menus MUST use consistent formatting and navigation
- Web dashboard MUST be responsive (mobile-first)
- Voice commands MUST provide audio feedback
- Multi-language strings MUST be externalized for i18n

## Deployment Phases

### Phase I: CLI Application

- Platform: Local Python CLI
- Storage: In-memory only
- Interface: Command-line only
- Purpose: Core domain logic validation

### Phase IV: Local Kubernetes

- Platform: Minikube
- Packaging: Helm charts
- Agent orchestration: kagent
- Purpose: Development and integration testing

### Phase V: Cloud Production

- Platform: DigitalOcean Kubernetes
- Event streaming: Kafka
- Service mesh: Dapr
- Microservices: Banking, Analytics, Notifications, Investments
- Purpose: Production deployment with scalability

## Governance

### Amendment Process

1. Propose amendment via PR with justification
2. Review by project leads (minimum 1 approval)
3. Update constitution version per semantic versioning:
   - MAJOR: Backward-incompatible principle changes
   - MINOR: New principles or significant expansions
   - PATCH: Clarifications and typo fixes
4. Update dependent templates if affected
5. Document in ADR if architecturally significant

### Compliance Requirements

- All PRs MUST verify compliance with Core Principles
- Code reviews MUST check for constitution violations
- Complexity beyond constitution guidelines MUST be justified in ADR
- Quarterly compliance reviews recommended

### Authoritative Hierarchy

1. This Constitution (highest authority)
2. Architecture Decision Records (ADRs)
3. Feature Specifications (spec.md)
4. Implementation Plans (plan.md)
5. Task Lists (tasks.md)

**Version**: 1.1.0 | **Ratified**: 2026-01-18 | **Last Amended**: 2026-01-18
