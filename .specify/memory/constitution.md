<!--
SYNC IMPACT REPORT
==================
Version change: 1.2.0 → 1.3.0 (MINOR - Phase II Laws strengthened)
Modified principles:
  - Phase II Core Laws: Enhanced with 8 explicit non-negotiables
  - Phase II Engineering Laws: Added JWT auth, event-driven architecture
  - Phase II Security Laws: Added JWT authentication requirement
Added sections:
  - Phase II Data Laws (new subsection)
  - Phase II Future-Proofing Laws (new subsection)
Removed sections: None
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ (aligned - no changes needed)
  - .specify/templates/spec-template.md ✅ (aligned - no changes needed)
  - .specify/templates/tasks-template.md ✅ (aligned - no changes needed)
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

## Phase II Laws – Full-Stack Financial Platform

Phase II builds a modern full-stack web application that exposes the financial
core via APIs and presents it with a professional, animated UI.

### Core Laws (NON-NEGOTIABLE)

The following 8 laws are absolute requirements for Phase II development:

1. **Spec-Driven Development**: All functionality MUST trace to specifications
2. **Backend is Single Source of Truth**: The backend API is the ONLY authoritative source for all data; frontend MUST NOT maintain independent data state
3. **Backend-First Rule**: Backend API endpoints MUST be implemented and tested BEFORE any frontend component that consumes them
4. **No Hard-Coded UI Data**: Frontend MUST NOT contain hard-coded data, mock data, or static values; ALL displayed data MUST come from backend API calls
5. **All Data from Neon DB**: Every piece of persistent data MUST be stored in and retrieved from Neon PostgreSQL; no local storage, no frontend state persistence
6. **JWT Authentication Required**: All authenticated endpoints MUST use JWT tokens; no session-based auth, no cookies for auth state
7. **AI Expansion Mandatory**: Architecture MUST support future AI agent integration; APIs MUST be designed for both human and AI consumers
8. **Event-Driven Readiness**: System MUST be structured to emit and consume events for future Kafka/Dapr integration

**Rationale**: Ensures clean separation of concerns, maintainability, data integrity,
and future scalability across the full stack.

### Engineering Laws

- Backend: FastAPI + SQLModel for API and ORM
- Frontend: Next.js 14 App Router for server/client rendering
- Styling: Tailwind CSS + Framer Motion for animations
- Database: Neon PostgreSQL (serverless, scalable)
- API versioning: `/api/v1/` prefix for all endpoints
- All API responses MUST follow consistent JSON schema
- Backend MUST be developed and deployed independently of frontend
- API contracts MUST be defined before frontend development begins

**Rationale**: Modern, production-ready stack that enables rapid development
with excellent developer experience and performance.

### Data Laws (NON-NEGOTIABLE)

Data flow MUST follow this strict hierarchy:

```
Neon PostgreSQL (Source of Truth)
        ↓
    FastAPI Backend (Data Access Layer)
        ↓
    REST API (JSON Responses)
        ↓
    Next.js Frontend (Display Only)
```

- Frontend components MUST NOT store business data in React state beyond the current render cycle
- All CRUD operations MUST go through backend API endpoints
- Frontend MUST refetch data after mutations; no optimistic updates without backend confirmation
- Local storage MUST NOT be used for business data; only for UI preferences (theme, language)

**Rationale**: Guarantees data consistency, prevents stale data bugs, and ensures
audit trail through backend logging.

### UI/UX Laws

- Glassmorphism aesthetic: Frosted glass effects with backdrop blur
- Gradient identity: Consistent brand gradients across UI elements
- Card-based layout: Information organized in reusable card components
- Motion-first microinteractions: Subtle animations on all user interactions
- Chart-driven insights: Visual data representation using Recharts/Chart.js
- Integrated chatbot shell: Persistent chat interface for AI assistant

**Rationale**: Creates a modern, visually appealing, and intuitive user experience
that differentiates the product and delights users.

### Security Laws (NON-NEGOTIABLE)

- JWT tokens MUST be used for all authenticated API requests
- Tokens MUST be stored securely (httpOnly cookies or secure memory, NOT localStorage)
- Token refresh mechanism MUST be implemented for session continuity
- Input validation MUST occur on both frontend AND backend
- Rate limiting MUST be applied to all API endpoints
- CORS protection MUST be configured for allowed origins only
- All secrets MUST be stored in environment variables (never in code)
- Password hashing MUST use bcrypt or argon2

**Rationale**: Defense in depth approach protects against common web vulnerabilities
and ensures data security.

### Future-Proofing Laws (NON-NEGOTIABLE)

Architecture MUST be prepared for future expansion:

**AI Integration Readiness**:
- API endpoints MUST return structured, parseable responses suitable for AI consumption
- Error responses MUST include machine-readable error codes
- API MUST support batch operations for AI agent efficiency
- Webhook endpoints MUST be planned for AI-triggered actions

**Event-Driven Readiness**:
- Domain events MUST be defined for all state changes (TransactionCreated, BudgetExceeded, etc.)
- Service layer MUST emit events even if not yet consumed
- Event schemas MUST be documented in contracts/
- Code MUST NOT assume synchronous processing; design for eventual consistency

**Urdu & Voice Future-Proofing**:
- All user-facing strings MUST be externalized in i18n files
- Text content MUST NOT be hard-coded in components
- UI components MUST support RTL (right-to-left) layout switching
- Input fields MUST support Unicode text entry
- API MUST accept and return UTF-8 encoded strings
- Voice command integration points MUST be identified in UI

**Rationale**: Prevents costly rewrites when AI agents, event streaming, multi-language,
and voice features are implemented in later phases.

### Acceptance Laws

- All CLI features MUST be available via web interface
- Dashboard MUST load in under 2 seconds (LCP)
- UI MUST be consistent across devices (mobile, tablet, desktop)
- All forms MUST provide real-time validation feedback
- Error states MUST be clearly communicated to users
- All data displayed MUST be fetched from backend API

**Rationale**: Ensures feature parity, performance standards, and excellent
user experience across all platforms.

### Phase II API Structure

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/auth/register` | POST | User registration |
| `/api/v1/auth/login` | POST | User login, returns JWT |
| `/api/v1/auth/refresh` | POST | Refresh JWT token |
| `/api/v1/transactions` | GET, POST | List and create transactions |
| `/api/v1/transactions/{id}` | GET, PUT, DELETE | Single transaction CRUD |
| `/api/v1/categories` | GET | List categories |
| `/api/v1/budgets` | GET, POST | List and set budgets |
| `/api/v1/budgets/{category}` | GET | Budget status for category |
| `/api/v1/summary` | GET | Financial summary |

### Phase II UI Components

| Component | Description |
|-----------|-------------|
| Dashboard | Overview with charts, recent transactions, budget status |
| TransactionList | Filterable, sortable table of transactions |
| TransactionForm | Add/edit transaction with category picker |
| BudgetCard | Visual budget progress with alerts |
| CategoryPicker | Emoji-enhanced category selector |
| ChatbotShell | Floating AI assistant interface |
| AuthGuard | HOC/wrapper for protected routes |

## Technology Stack

**Backend**:
- Language: Python 3.11+
- Framework: FastAPI + SQLModel
- Database: Neon PostgreSQL (Phase II+), In-memory (Phase I)
- Authentication: JWT (python-jose + passlib)

**Frontend**:
- Framework: Next.js 14 (App Router)
- Styling: Tailwind CSS + Framer Motion
- Charts: Recharts or Chart.js
- State: React Server Components + Client hooks
- i18n: next-intl or similar (prepared for Urdu)

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

### Phase II Design System

| Element | Specification |
|---------|---------------|
| Primary Gradient | `from-purple-600 to-blue-500` |
| Glass Effect | `bg-white/10 backdrop-blur-lg` |
| Border Radius | `rounded-2xl` for cards |
| Shadow | `shadow-xl shadow-purple-500/10` |
| Animation Duration | 200-300ms for microinteractions |

## Deployment Phases

### Phase I: CLI Application ✅ COMPLETE

- Platform: Local Python CLI
- Storage: In-memory only
- Interface: Command-line only
- Purpose: Core domain logic validation

### Phase II: Full-Stack Web Application

- Backend: FastAPI on Python
- Frontend: Next.js 14 on Vercel/Node
- Database: Neon PostgreSQL (serverless)
- Authentication: JWT-based
- Purpose: Web-based financial management with modern UI

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

**Version**: 1.3.0 | **Ratified**: 2026-01-18 | **Last Amended**: 2026-01-25
