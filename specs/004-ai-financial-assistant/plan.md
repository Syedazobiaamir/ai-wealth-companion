# Implementation Plan: AI Financial Assistant

**Branch**: `004-ai-financial-assistant` | **Date**: 2026-02-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-ai-financial-assistant/spec.md`

## Summary

Transform the AI Wealth Companion from a manual financial management tool into an intelligent conversational assistant. The system uses OpenAI Agents SDK for multi-agent orchestration, MCP protocol for tool communication, ChatKit UI for the chat interface, and supports English/Urdu bilingual interaction with voice commands. The existing Phase II backend services are wrapped as MCP tools consumed by specialized agents (Budget, Spending, Investment) coordinated by a Master Orchestrator.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: OpenAI Agents SDK, Official MCP SDK, OpenAI ChatKit UI, FastAPI, Next.js 14
**Storage**: SQLite (dev) / Neon PostgreSQL (prod) — existing from Phase II
**Testing**: pytest (backend), manual integration testing (frontend)
**Target Platform**: Web application (Linux server backend, browser frontend)
**Project Type**: Web (frontend + backend)
**Performance Goals**: Chat response under 10 seconds, 50 concurrent sessions
**Constraints**: No fabricated data, no financial advice, JWT auth, browser Web Speech API for voice
**Scale/Scope**: Single-user to small team scale, 6 MCP tools, 3 subagents, 6 skills

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Constitution Reference | Status |
|------|----------------------|--------|
| OpenAI ChatKit UI required | Phase III Law #1 | PASS — ChatKit replaces existing ChatWidget |
| OpenAI Agents SDK required | Phase III Law #2 | PASS — All agents built with SDK |
| Official MCP SDK required | Phase III Law #3 | PASS — MCP server wraps financial services |
| Subagents + Skills architecture | Phase III Law #4 | PASS — Master + 3 subagents + 6 skills |
| Urdu language support | Phase III Law #5 | PASS — Urdu agent + translation skill + RTL UI |
| Voice command support | Phase III Law #6 | PASS — Web Speech API + voice skill |
| Predictive AI | Phase III Law #7 | PASS — Investment simulation + spending prediction |
| No fabricated financial data | AI Safety Law | PASS — All data from backend services via MCP |
| Structured tool calling (JSON) | Structured Tool Law | PASS — MCP protocol enforces JSON |
| Financial advice disclaimers | AI Safety Law | PASS — All predictions include disclaimers |
| Privacy-first (no data retention) | Core Principle III | PASS — Session-scoped memory with TTL |
| Spec-driven development | Core Principle I | PASS — Full spec → plan → tasks workflow |

**Post-Design Re-check**: All gates PASS. No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/004-ai-financial-assistant/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 research decisions
├── data-model.md        # Phase 1 data model
├── quickstart.md        # Phase 1 quickstart guide
├── contracts/
│   └── ai-api.md        # Phase 1 API contracts
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── agents/                    # NEW: AI agent layer
│   │   ├── __init__.py
│   │   ├── master.py              # Master orchestrator agent
│   │   ├── subagents/
│   │   │   ├── __init__.py
│   │   │   ├── budget_agent.py    # Budget management agent
│   │   │   ├── spending_agent.py  # Spending analysis agent
│   │   │   └── investment_agent.py # Investment simulation agent
│   │   └── skills/
│   │       ├── __init__.py
│   │       ├── finance_crud.py    # Finance CRUD operations skill
│   │       ├── budget_analysis.py # Budget analysis skill
│   │       ├── spending_insight.py # Spending insight skill
│   │       ├── investment_sim.py  # Investment simulation skill
│   │       ├── translation.py     # Urdu translation skill
│   │       └── voice_interpret.py # Voice interpretation skill
│   ├── mcp/                       # NEW: MCP tool server
│   │   ├── __init__.py
│   │   ├── server.py             # MCP server setup
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── financial_summary.py
│   │       ├── budget_tools.py
│   │       ├── transaction_tools.py
│   │       ├── spending_analysis.py
│   │       ├── investment_tools.py
│   │       └── dashboard_metrics.py
│   ├── models/                    # EXTEND: Add new models
│   │   ├── conversation.py        # NEW
│   │   ├── message.py             # NEW
│   │   ├── health_score.py        # NEW
│   │   └── investment_sim.py      # NEW
│   ├── services/
│   │   ├── ai.py                  # EXTEND: Connect to real agents
│   │   ├── conversation.py        # NEW: Conversation management
│   │   ├── health_score.py        # NEW: Health score calculation
│   │   └── investment_sim.py      # NEW: Investment simulation
│   ├── repositories/
│   │   ├── conversation.py        # NEW
│   │   └── health_score.py        # NEW
│   └── api/v1/endpoints/
│       └── ai.py                  # EXTEND: New endpoints
└── tests/

frontend/
├── src/
│   ├── components/
│   │   ├── chatbot/
│   │   │   └── chat-widget.tsx    # REPLACE: ChatKit UI integration
│   │   ├── ai/                    # NEW: AI-specific components
│   │   │   ├── insight-card.tsx   # Dashboard insight cards
│   │   │   ├── health-score.tsx   # Financial health score display
│   │   │   ├── voice-button.tsx   # Mic button with Web Speech API
│   │   │   └── language-toggle.tsx # EN/UR language switcher
│   │   └── ui/
│   │       └── ...                # Existing UI components
│   ├── lib/
│   │   └── api.ts                 # EXTEND: New AI endpoints
│   └── app/(app)/
│       └── dashboard/page.tsx     # EXTEND: Add insight cards
└── tests/
```

**Structure Decision**: Extends existing web application structure (Option 2). New `agents/` and `mcp/` directories added under `backend/src/`. New `ai/` component directory added under `frontend/src/components/`.

## Implementation Stages

### Stage 1 — Foundation

**Goal**: Establish the infrastructure for AI communication.

| Task | Description | Files |
|------|-------------|-------|
| 1.1 | Install OpenAI Agents SDK and MCP SDK in backend | requirements.txt |
| 1.2 | Install ChatKit UI in frontend | package.json |
| 1.3 | Build MCP server with 6 tool definitions | backend/src/mcp/ |
| 1.4 | Wire MCP tools to existing service layer | backend/src/mcp/tools/ |
| 1.5 | Secure AI endpoints with JWT authentication | backend/src/api/v1/endpoints/ai.py |
| 1.6 | Create Conversation and Message models | backend/src/models/ |
| 1.7 | Replace ChatWidget internals with ChatKit UI | frontend/src/components/chatbot/ |
| 1.8 | Connect ChatKit to /api/v1/ai/chat endpoint | frontend/src/lib/api.ts |

**Dependencies**: Phase II backend running, OpenAI API key available.

### Stage 2 — Intelligence Layer

**Goal**: Build the multi-agent orchestration system.

| Task | Description | Files |
|------|-------------|-------|
| 2.1 | Build Master Orchestrator agent | backend/src/agents/master.py |
| 2.2 | Create Budget Agent subagent | backend/src/agents/subagents/budget_agent.py |
| 2.3 | Create Spending Agent subagent | backend/src/agents/subagents/spending_agent.py |
| 2.4 | Create Investment Agent subagent | backend/src/agents/subagents/investment_agent.py |
| 2.5 | Implement Finance CRUD skill | backend/src/agents/skills/finance_crud.py |
| 2.6 | Implement Budget Analysis skill | backend/src/agents/skills/budget_analysis.py |
| 2.7 | Implement Spending Insight skill | backend/src/agents/skills/spending_insight.py |
| 2.8 | Implement Investment Simulation skill | backend/src/agents/skills/investment_sim.py |
| 2.9 | Wire master agent routing logic per constitution | backend/src/agents/master.py |
| 2.10 | Enforce constitution safety guardrails in system prompts | backend/src/agents/ |

**Dependencies**: Stage 1 complete (MCP tools available).

### Stage 3 — AI Capabilities

**Goal**: Deliver core AI financial features.

| Task | Description | Files |
|------|-------------|-------|
| 3.1 | Natural language → intent classification → API control | backend/src/agents/master.py |
| 3.2 | Financial summarization (smart spending summaries) | backend/src/agents/skills/spending_insight.py |
| 3.3 | Overspending detection and budget coaching | backend/src/agents/skills/budget_analysis.py |
| 3.4 | Financial health score calculator | backend/src/services/health_score.py |
| 3.5 | Predictive investment simulation | backend/src/services/investment_sim.py |
| 3.6 | Implement /api/v1/ai/health-score endpoint | backend/src/api/v1/endpoints/ai.py |
| 3.7 | Implement /api/v1/ai/simulate-investment endpoint | backend/src/api/v1/endpoints/ai.py |
| 3.8 | Insight generation and caching | backend/src/services/ai.py |
| 3.9 | Dashboard insight cards component | frontend/src/components/ai/insight-card.tsx |
| 3.10 | Health score display component | frontend/src/components/ai/health-score.tsx |

**Dependencies**: Stage 2 complete (agents functional).

### Stage 4 — Bonus Layer

**Goal**: Add Urdu support, voice commands, and smart suggestions.

| Task | Description | Files |
|------|-------------|-------|
| 4.1 | Implement Translation skill (Urdu) | backend/src/agents/skills/translation.py |
| 4.2 | Add language detection to master agent | backend/src/agents/master.py |
| 4.3 | Language toggle component (EN/UR) | frontend/src/components/ai/language-toggle.tsx |
| 4.4 | RTL layout support for Urdu | frontend/src/app/layout.tsx, globals.css |
| 4.5 | Voice button with Web Speech API | frontend/src/components/ai/voice-button.tsx |
| 4.6 | Voice interpretation skill | backend/src/agents/skills/voice_interpret.py |
| 4.7 | Smart suggestion engine (proactive insights) | backend/src/services/ai.py |
| 4.8 | Integrate voice button into chat widget | frontend/src/components/chatbot/chat-widget.tsx |

**Dependencies**: Stage 3 complete (core AI working).

### Stage 5 — Production Readiness

**Goal**: Finalize tool registry, memory, logging, and traceability.

| Task | Description | Files |
|------|-------------|-------|
| 5.1 | MCP tool registry with schema validation | backend/src/mcp/server.py |
| 5.2 | Agent blueprint documentation | specs/004-ai-financial-assistant/ |
| 5.3 | Conversation memory with TTL cleanup | backend/src/services/conversation.py |
| 5.4 | Event logging for all AI operations | backend/src/services/ai.py |
| 5.5 | Error handling and graceful degradation | backend/src/agents/, frontend/ |
| 5.6 | Rate limiting for AI endpoints | backend/src/api/v1/endpoints/ai.py |
| 5.7 | Integration testing for full chat flow | backend/tests/, frontend/ |

**Dependencies**: Stage 4 complete (all features functional).

## Complexity Tracking

No constitution violations requiring justification. All gates pass.

## Risks

1. **OpenAI API latency**: Chat responses may exceed 10-second target under load. Mitigation: streaming responses, response caching for common queries.
2. **Urdu accuracy**: GPT model's Urdu comprehension may vary. Mitigation: test with common financial phrases, provide English fallback.
3. **Web Speech API browser support**: Not available in all browsers. Mitigation: feature detection with graceful fallback to text-only.
