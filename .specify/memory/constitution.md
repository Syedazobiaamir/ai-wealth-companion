<!--
SYNC IMPACT REPORT
==================
Version change: 1.3.0 → 2.0.0 (MAJOR - Phase III AI Agent Laws added)
Modified principles:
  - AI-First Architecture: Expanded with MCP, OpenAI SDK requirements
  - Multi-Modal Interface: Enhanced with voice and Urdu requirements
  - Technology Stack: Added OpenAI ChatKit, Agents SDK, MCP SDK
Added sections:
  - Phase III Laws – AI Financial Assistant (complete new section)
  - AI Safety & Governance Laws
  - MCP Communication Contract
  - Voice Pipeline Governance
  - Bilingual Output Requirements (Urdu + English)
  - Agent Routing Rules
Removed sections: None
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ (aligned)
  - .specify/templates/spec-template.md ✅ (aligned)
  - .specify/templates/tasks-template.md ✅ (aligned)
Follow-up TODOs: None
-->

# AI Wealth & Spending Companion Constitution

## Mission Statement

Build a governed AI financial assistant that can understand natural language, manage financial data, assist budgeting, analyze spending, predict investments, support Urdu language, accept voice commands, and operate using reusable intelligence through Claude Code.

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

All features MUST follow the specs → Claude Code → implementation workflow:

- Feature specifications MUST be written and approved before implementation begins
- All AI behavior MUST be controlled through specifications
- Use Spec-Kit Plus templates for all artifacts (spec.md, plan.md, tasks.md)
- Prompt History Records (PHR) MUST be created for every development session
- Architecture Decision Records (ADR) MUST be proposed for significant decisions
- No code changes without corresponding spec or task reference
- No manual coding outside spec-driven workflow

**Rationale**: Ensures traceability, reduces rework, and maintains alignment between
business requirements and technical implementation.

### II. AI-First Architecture (NON-NEGOTIABLE)

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
| Voice Skill | Skill | Speech-to-text and text-to-speech processing |
| Urdu Language Skill | Skill | Bilingual translation and RTL support |

- All intelligence MUST be reusable via Skills & Subagents
- Subagents MUST be independently deployable and testable
- Skills MUST be reusable across multiple phases
- All reusable logic MUST reside in `phase3/chatbot_agent/skills/`
- Each subagent MUST expose a well-defined API contract
- Multi-agent orchestration MUST be supported

**Rationale**: Enables modular development, facilitates parallel workstreams, and
maximizes code reuse across project phases.

### III. Privacy-First Finance Assistant (NON-NEGOTIABLE)

User financial data MUST be protected at all times:

- Financial data MUST NOT be shared with external services without explicit consent
- AI models MUST NOT retain user financial data after session ends
- All PII MUST be encrypted at rest and in transit
- Audit logs MUST track all data access
- Users MUST be able to delete all their data on request
- No third-party analytics on financial transactions

**Rationale**: Financial data is highly sensitive; privacy violations destroy user trust
and may violate regulations.

### IV. Cloud-Native Design

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

### V. Multi-Modal Interface (NON-NEGOTIABLE)

The application MUST support multiple interaction modes:

- CLI interface with emoji + color-coded feedback
- Web dashboard (Next.js + Tailwind)
- Voice command support (MANDATORY - bonus feature)
- Multi-language support: English and Urdu (MANDATORY - bonus feature)
- AI chatbot with personality and predictive investment assistant
- OpenAI ChatKit UI for conversational interface

Interface requirements:
- All interfaces MUST provide consistent data and behavior
- Error messages MUST be user-friendly and actionable
- Response times MUST meet defined performance constraints
- Voice responses MUST provide audio feedback
- Urdu text MUST render correctly with RTL support

**Rationale**: Maximizes accessibility and user engagement across different
user preferences and contexts. Bonus features are mandatory per project requirements.

### VI. Test-First Development (NON-NEGOTIABLE)

TDD is mandatory for all implementation work:

- Tests MUST be written before implementation code
- Tests MUST fail (Red) before implementation begins
- Implementation MUST make tests pass (Green)
- Code MUST be refactored only after tests pass (Refactor)
- Contract tests MUST exist for all API endpoints
- Integration tests MUST cover critical user journeys

**Rationale**: Ensures code correctness, prevents regressions, and maintains
confidence during refactoring.

### VII. Observability & Security

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

## Phase III Laws – AI Financial Assistant (NON-NEGOTIABLE)

Phase III transforms the application into an intelligent AI-powered financial
assistant with natural language understanding, voice commands, and predictive analytics.

### Core Laws (NON-NEGOTIABLE)

The following requirements are MANDATORY for Phase III:

1. **OpenAI ChatKit UI**: All conversational interfaces MUST use OpenAI ChatKit UI
2. **OpenAI Agents SDK**: All AI agents MUST be built using OpenAI Agents SDK
3. **Official MCP SDK**: All tool communication MUST use the Official MCP SDK
4. **Subagents + Skills Architecture**: All intelligence MUST be organized into Subagents and Skills
5. **Urdu Language Support**: Full bilingual support (English + Urdu) MUST be implemented
6. **Voice Command Support**: Voice input and output MUST be supported
7. **Predictive AI**: Investment predictions and spending forecasts MUST be included

**Rationale**: Ensures standardized AI integration, maximum reusability, and
delivery of all bonus features.

### AI Safety Laws (NON-NEGOTIABLE)

All AI components MUST adhere to these safety requirements:

**Financial Advice Safety Layer**:
- AI MUST NOT provide specific investment recommendations
- AI MUST include disclaimers on all financial suggestions
- AI MUST clearly state it is not a licensed financial advisor
- AI MUST recommend consulting professionals for major decisions
- All predictions MUST include confidence intervals and disclaimers

**Explainable AI Responses**:
- AI MUST explain the reasoning behind recommendations
- AI MUST cite data sources for any claims
- AI MUST show calculation methodology when presenting numbers
- Users MUST be able to ask "why" and get explanations

**No Hallucinated Financial Data**:
- AI MUST NEVER fabricate transaction data
- AI MUST NEVER invent account balances
- AI MUST NEVER create fake investment returns
- All data presented MUST come from verified backend sources
- If data is unavailable, AI MUST say "I don't have that information"

**Rationale**: Financial AI errors can cause real monetary harm; safety is paramount.

### Structured Tool Calling Laws (NON-NEGOTIABLE)

All AI-to-tool communication MUST follow these rules:

**JSON Tool Calling**:
```json
{
  "tool": "tool_name",
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  },
  "context": {
    "user_id": "string",
    "session_id": "string",
    "language": "en|ur"
  }
}
```

- All tool calls MUST use structured JSON format
- All tool responses MUST be JSON with status codes
- Error responses MUST include machine-readable error codes
- Tool calls MUST be logged for audit purposes

**Rationale**: Structured communication ensures reliability and debuggability.

### MCP Communication Contract (NON-NEGOTIABLE)

All MCP (Model Context Protocol) communication MUST follow these rules:

**Request Format**:
```json
{
  "jsonrpc": "2.0",
  "method": "tool/call",
  "params": {
    "name": "tool_name",
    "arguments": {}
  },
  "id": "unique_request_id"
}
```

**Response Format**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [],
    "isError": false
  },
  "id": "unique_request_id"
}
```

- All MCP servers MUST implement the official MCP SDK
- All tools MUST be registered with proper schemas
- All tools MUST handle errors gracefully
- Timeout handling MUST be implemented (30s default)

**Rationale**: Standardized MCP communication enables tool reuse and debugging.

### Agent Routing Rules (NON-NEGOTIABLE)

AI requests MUST be routed to appropriate agents:

| Intent Category | Target Agent | Priority |
|-----------------|--------------|----------|
| Account queries | Banking Subagent | High |
| Transaction CRUD | Banking Subagent | High |
| Budget analysis | Analytics Subagent | Medium |
| Spending insights | Analytics Subagent | Medium |
| Investment predictions | Investment Subagent | Medium |
| Alerts and notifications | Notification Subagent | Low |
| Voice commands | Voice Skill → Router | High |
| Urdu queries | Urdu Skill → Router | High |

**Routing Logic**:
1. Parse user intent from natural language
2. Identify language (English/Urdu)
3. Route to appropriate skill/subagent
4. Return response in user's preferred language

**Rationale**: Proper routing ensures efficient processing and accurate responses.

### Bilingual Output Requirements (NON-NEGOTIABLE)

All user-facing AI responses MUST support English and Urdu:

**Language Detection**:
- System MUST auto-detect user's language preference
- Users MUST be able to switch languages mid-conversation
- Mixed-language input MUST be handled gracefully

**Urdu-Specific Requirements**:
- All Urdu text MUST render right-to-left (RTL)
- Numbers MUST be displayed in user's preferred format
- Currency MUST support Pakistani Rupee (PKR) formatting
- Date formats MUST support local conventions
- UI MUST adapt layout for RTL when Urdu is selected

**Translation Quality**:
- Financial terms MUST be accurately translated
- Technical terms MAY remain in English with Urdu explanation
- Translations MUST be culturally appropriate

**Example Response Structure**:
```json
{
  "response": {
    "en": "Your balance is $1,000",
    "ur": "آپ کا بیلنس $1,000 ہے"
  },
  "preferred_language": "ur",
  "display": "آپ کا بیلنس $1,000 ہے"
}
```

**Rationale**: Urdu support is mandatory per project requirements and expands accessibility.

### Voice Pipeline Governance (NON-NEGOTIABLE)

Voice commands MUST follow this pipeline:

```
┌─────────────────────────────────────────────────────────┐
│                    Voice Input                          │
│              (Microphone / Audio File)                  │
├─────────────────────────────────────────────────────────┤
│                Speech-to-Text (STT)                     │
│         (Whisper API / Browser Web Speech)              │
├─────────────────────────────────────────────────────────┤
│                Language Detection                        │
│               (English / Urdu / Mixed)                  │
├─────────────────────────────────────────────────────────┤
│                Intent Recognition                        │
│              (NLP Processing via Agent)                 │
├─────────────────────────────────────────────────────────┤
│                 Agent Routing                            │
│        (Banking / Analytics / Investment)               │
├─────────────────────────────────────────────────────────┤
│                Tool Execution                            │
│              (MCP Tool Calls)                           │
├─────────────────────────────────────────────────────────┤
│              Response Generation                         │
│           (Bilingual if required)                       │
├─────────────────────────────────────────────────────────┤
│                Text-to-Speech (TTS)                     │
│          (Browser TTS / Cloud TTS API)                  │
├─────────────────────────────────────────────────────────┤
│                   Audio Output                          │
│                (Speaker / Headphones)                   │
└─────────────────────────────────────────────────────────┘
```

**Voice Requirements**:
- Voice input MUST be transcribed within 3 seconds
- Voice responses MUST be generated within 5 seconds total
- Users MUST be able to interrupt voice output
- Voice MUST work in both English and Urdu
- Fallback to text MUST be available if voice fails

**Rationale**: Voice support is mandatory per project requirements and enables hands-free usage.

### Skill Reusability Rules (NON-NEGOTIABLE)

All Skills MUST be designed for maximum reusability:

**Skill Definition Requirements**:
- Each Skill MUST have a single, well-defined purpose
- Skills MUST NOT contain business logic; delegate to subagents
- Skills MUST be versioned alongside the main application
- Skills MUST be documented with examples
- Skills MUST be testable in isolation

**Skill Organization**:
```
phase3/chatbot_agent/skills/
├── __init__.py
├── voice_skill.py          # Voice processing
├── urdu_skill.py           # Urdu translation
├── nlp_skill.py            # Natural language processing
├── prediction_skill.py     # Investment predictions
└── formatting_skill.py     # Response formatting
```

**Skill Interface**:
```python
class Skill:
    name: str
    description: str
    version: str

    async def execute(self, input: dict, context: dict) -> dict:
        """Execute skill with input and context, return result"""
        pass
```

**Rationale**: Reusable skills reduce code duplication and enable rapid feature development.

### Predictive AI Requirements (NON-NEGOTIABLE)

The system MUST include predictive analytics:

**Spending Predictions**:
- Predict next month's spending by category
- Identify spending trends and anomalies
- Alert users to unusual spending patterns
- Suggest budget adjustments based on trends

**Investment Predictions** (with disclaimers):
- Show historical ROI calculations
- Project future values based on historical data
- Compare investment options
- All predictions MUST include confidence levels
- All predictions MUST include "past performance" disclaimers

**Budget Forecasting**:
- Predict budget overruns before they happen
- Suggest optimal budget allocations
- Track progress toward financial goals

**Rationale**: Predictive AI is mandatory per project requirements and adds significant user value.

### Phase III API Structure

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/ai/chat` | POST | Send message to AI chatbot |
| `/api/v1/ai/voice` | POST | Process voice command |
| `/api/v1/ai/predict/spending` | GET | Get spending predictions |
| `/api/v1/ai/predict/investment` | GET | Get investment projections |
| `/api/v1/ai/insights` | GET | Get AI-generated insights |
| `/api/v1/ai/language` | POST | Set preferred language |

### Phase III UI Components

| Component | Description |
|-----------|-------------|
| ChatKitUI | OpenAI ChatKit conversational interface |
| VoiceButton | Push-to-talk voice input |
| LanguageToggle | English/Urdu switcher |
| PredictionCard | AI prediction display with disclaimers |
| InsightPanel | AI-generated insights feed |
| VoiceWaveform | Visual feedback during voice input |

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
- i18n: next-intl (English + Urdu)
- Chat UI: OpenAI ChatKit UI

**AI/ML (Phase III)**:
- AI Framework: OpenAI Agents SDK
- Tool Protocol: Official MCP SDK
- Voice STT: Whisper API / Web Speech API
- Voice TTS: Browser TTS / Cloud TTS
- NLP: Claude Code / OpenAI GPT
- Predictions: Statistical models + ML

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
│                  OpenAI ChatKit UI                      │
├─────────────────────────────────────────────────────────┤
│              OpenAI Agents SDK Router                   │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ Banking  │  │Investment│  │Analytics │  │Notifica-│ │
│  │ Subagent │  │ Subagent │  │ Subagent │  │  tion   │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
├─────────────────────────────────────────────────────────┤
│              Shared Skills Layer (MCP)                  │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────────────┐│
│  │ Voice  │  │  Urdu  │  │  NLP   │  │   Prediction   ││
│  │ Skill  │  │ Skill  │  │ Skill  │  │     Skill      ││
│  └────────┘  └────────┘  └────────┘  └────────────────┘│
├─────────────────────────────────────────────────────────┤
│                    Data Layer                           │
│         (PostgreSQL / Event Store / Cache)              │
└─────────────────────────────────────────────────────────┘
```

### Skill Reuse Policy

- Skills MUST be defined once in `phase3/chatbot_agent/skills/`
- Skills MUST NOT contain business logic; delegate to subagents
- Skills MUST be versioned alongside the main application
- Skills MUST communicate via MCP protocol

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
- RTL layout MUST be supported for Urdu

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

### Phase II: Full-Stack Web Application ✅ COMPLETE

- Backend: FastAPI on Python
- Frontend: Next.js 14 on Vercel/Node
- Database: Neon PostgreSQL (serverless)
- Authentication: JWT-based
- Purpose: Web-based financial management with modern UI

### Phase III: AI Financial Assistant 🔄 IN PROGRESS

- AI Framework: OpenAI Agents SDK
- Chat UI: OpenAI ChatKit UI
- Tool Protocol: Official MCP SDK
- Voice: STT/TTS integration
- Language: English + Urdu bilingual
- Predictions: Spending and investment forecasts
- Purpose: Intelligent conversational financial assistant

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
- AI components MUST pass safety review before deployment

### Authoritative Hierarchy

1. This Constitution (highest authority)
2. Architecture Decision Records (ADRs)
3. Feature Specifications (spec.md)
4. Implementation Plans (plan.md)
5. Task Lists (tasks.md)

**Version**: 2.0.0 | **Ratified**: 2026-01-18 | **Last Amended**: 2026-01-28
