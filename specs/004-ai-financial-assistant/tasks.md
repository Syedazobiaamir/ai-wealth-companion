# Tasks: AI Financial Assistant

**Input**: Design documents from `/specs/004-ai-financial-assistant/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/ai-api.md, quickstart.md

**Tests**: Not explicitly requested in spec. Test tasks omitted. Manual integration testing per quickstart.md.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Frontend**: `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies and create directory structure for Phase III AI layer.

- [x] T001 Install OpenAI Agents SDK and MCP SDK in backend: add `openai-agents`, `mcp`, `aiosqlite` to `backend/requirements.txt` and install
- [x] T002 Install ChatKit UI in frontend: add `@openai/chatkit` to `frontend/package.json` and install
- [x] T003 [P] Create backend agent directory structure: `backend/src/agents/__init__.py`, `backend/src/agents/subagents/__init__.py`, `backend/src/agents/skills/__init__.py`
- [x] T004 [P] Create backend MCP directory structure: `backend/src/mcp/__init__.py`, `backend/src/mcp/tools/__init__.py`
- [x] T005 [P] Create frontend AI component directory: `frontend/src/components/ai/`
- [x] T006 [P] Add OPENAI_API_KEY and OPENAI_MODEL to `backend/.env.example` and load in `backend/src/core/config.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: MCP tool server, data models, and ChatKit UI — infrastructure ALL user stories depend on.

**CRITICAL**: No user story work can begin until this phase is complete.

### Data Models

- [x] T007 [P] Create Conversation model with fields (id, user_id, title, language, is_active, message_count, timestamps) in `backend/src/models/conversation.py`
- [x] T008 [P] Create Message model with fields (id, conversation_id, role, content, content_ur, intent, entities, tool_calls, confidence, input_method, processing_time_ms, timestamps) in `backend/src/models/message.py`
- [x] T009 Register Conversation and Message models in `backend/src/models/__init__.py` and create Alembic migration

### Data Access & Service Layer

- [x] T010 Create ConversationRepository with CRUD + list-by-user + mark-inactive in `backend/src/repositories/conversation.py`
- [x] T011 Create ConversationService with create, get, list, add-message, close logic in `backend/src/services/conversation.py`

### MCP Server & Tools

- [x] T012 Build MCP server setup with tool registration and JSON schema validation in `backend/src/mcp/server.py`
- [x] T013 [P] Implement `get_financial_summary` MCP tool wrapping DashboardService in `backend/src/mcp/tools/financial_summary.py`
- [x] T014 [P] Implement `create_budget` MCP tool wrapping BudgetService in `backend/src/mcp/tools/budget_tools.py`
- [x] T015 [P] Implement `add_transaction` MCP tool wrapping TransactionService in `backend/src/mcp/tools/transaction_tools.py`
- [x] T016 [P] Implement `analyze_spending` MCP tool wrapping SummaryService in `backend/src/mcp/tools/spending_analysis.py`
- [x] T017 [P] Implement `simulate_investment` MCP tool (placeholder logic, fleshed out in US2) in `backend/src/mcp/tools/investment_tools.py`
- [x] T018 [P] Implement `generate_dashboard_metrics` MCP tool wrapping DashboardService in `backend/src/mcp/tools/dashboard_metrics.py`
- [x] T019 Register all 6 MCP tools in `backend/src/mcp/server.py` and export from `backend/src/mcp/tools/__init__.py`

### API Endpoints (Foundation)

- [x] T020 Implement POST `/api/v1/ai/chat` endpoint with conversation creation, message storage, and placeholder agent call in `backend/src/api/v1/endpoints/ai.py`
- [x] T021 [P] Implement GET `/api/v1/ai/conversations` endpoint with pagination and active filter in `backend/src/api/v1/endpoints/ai.py`
- [x] T022 [P] Implement GET `/api/v1/ai/conversations/{id}/messages` endpoint with pagination in `backend/src/api/v1/endpoints/ai.py`
- [x] T023 Verify all new AI endpoints are registered in `backend/src/api/v1/router.py` with JWT auth dependency

### ChatKit UI Integration

- [x] T024 Replace ChatWidget internals with ChatKit UI components in `frontend/src/components/chatbot/chat-widget.tsx`
- [x] T025 Add AI chat API functions (sendMessage, getConversations, getMessages) to `frontend/src/lib/api.ts`
- [x] T026 Connect ChatKit widget to POST `/api/v1/ai/chat` endpoint with JWT token in `frontend/src/components/chatbot/chat-widget.tsx`

**Checkpoint**: MCP server running, models migrated, ChatKit UI sending messages to backend, placeholder responses returned. Foundation ready.

---

## Phase 3: User Story 1 — Conversational Financial Commands (Priority: P1) MVP

**Goal**: Users type natural language commands (e.g., "Add grocery budget 15,000", "Show my expenses this month") and the AI assistant understands intent, executes the action via MCP tools, and confirms.

**Independent Test**: Send text commands through the chat widget. Verify the assistant classifies intent, calls the right MCP tool, and returns a confirmation with details.

### Agent Architecture

- [x] T027 Build Master Orchestrator agent with system prompt, intent routing, and MCP tool access in `backend/src/agents/master.py`
- [x] T028 [P] [US1] Create Budget Agent subagent with budget-specific system prompt and tool bindings in `backend/src/agents/subagents/budget_agent.py`
- [x] T029 [P] [US1] Create Spending Agent subagent with spending-specific system prompt and tool bindings in `backend/src/agents/subagents/spending_agent.py`
- [x] T030 [US1] Export subagents from `backend/src/agents/subagents/__init__.py`

### Skills

- [x] T031 [US1] Implement Finance CRUD skill: parse natural language into create/read/update/delete operations, validate extracted entities (amounts, categories, dates) in `backend/src/agents/skills/finance_crud.py`
- [x] T032 [US1] Export skill from `backend/src/agents/skills/__init__.py`

### Agent Routing & Safety

- [x] T033 [US1] Implement intent classification routing in master agent: map intents (query, create, update) to Budget or Spending subagent in `backend/src/agents/master.py`
- [x] T034 [US1] Add safety guardrails to all agent system prompts: no fabricated data, financial disclaimer, redirect off-topic queries in `backend/src/agents/master.py`
- [x] T035 [US1] Implement clarification handling: when intent is ambiguous (confidence < 0.7), ask follow-up question instead of guessing in `backend/src/agents/master.py`

### Chat Pipeline Integration

- [x] T036 [US1] Wire POST `/api/v1/ai/chat` to invoke Master Orchestrator: receive message → create/resume conversation → run agent → store messages → return response in `backend/src/api/v1/endpoints/ai.py`
- [x] T037 [US1] Implement session context: send last 20 messages as conversation history to agent on each request in `backend/src/services/conversation.py`
- [x] T038 [US1] Update AIService to connect to real agent pipeline instead of stubs in `backend/src/services/ai.py`
- [x] T039 [US1] Log all tool calls and agent responses to EventLog in `backend/src/services/event.py`

**Checkpoint**: User can type "Add grocery budget 15,000" in ChatKit widget → AI creates budget via MCP tool → confirms with details. User can type "Show my expenses" → AI retrieves and summarizes. Ambiguous input gets clarification. Off-topic gets redirect. US1 is independently functional. MVP COMPLETE.

---

## Phase 4: User Story 2 — AI Financial Insights & Coaching (Priority: P2)

**Goal**: Users ask "Why is my spending high?" or "How is my financial health?" and receive data-driven analysis, health scores, overspending alerts, and investment feasibility assessments.

**Independent Test**: Query the assistant for spending analysis and health score. Verify response contains accurate data with specific actionable recommendations.

### New Models

- [x] T040 [P] [US2] Create FinancialHealthScore model with fields (id, user_id, month, year, overall_score, budget_adherence, savings_rate, spending_consistency, goal_progress, factors, recommendations, timestamps) and unique constraint on (user_id, month, year) in `backend/src/models/health_score.py`
- [x] T041 [P] [US2] Create InvestmentSimulation model with fields (id, user_id, conversation_id, investment_amount, time_horizon_months, projections, feasibility_score, monthly_savings_needed, assumptions, timestamps) in `backend/src/models/investment_sim.py`
- [x] T042 [US2] Register new models in `backend/src/models/__init__.py` and create Alembic migration

### Repositories & Services

- [x] T043 [P] [US2] Create HealthScoreRepository with CRUD + get-by-month + get-trend in `backend/src/repositories/health_score.py`
- [x] T044 [P] [US2] Create HealthScoreService implementing weighted formula (budget adherence 40%, savings rate 30%, spending consistency 20%, goal progress 10%) with grade assignment in `backend/src/services/health_score.py`
- [x] T045 [US2] Create InvestmentSimulationService with compound interest projections at 3 risk levels (5%, 8%, 12%), feasibility scoring based on current finances, and mandatory disclaimer in `backend/src/services/investment_sim.py`

### Skills & Agents

- [x] T046 [P] [US2] Implement Budget Analysis skill: compare spending vs budgets, detect overspending (>80% threshold), generate coaching recommendations in `backend/src/agents/skills/budget_analysis.py`
- [x] T047 [P] [US2] Implement Spending Insight skill: smart spending summaries with category breakdown, period comparison, anomaly detection in `backend/src/agents/skills/spending_insight.py`
- [x] T048 [P] [US2] Implement Investment Simulation skill: parse investment queries, run projections, format results with disclaimers in `backend/src/agents/skills/investment_sim.py`
- [x] T049 [US2] Create Investment Agent subagent with investment-specific system prompt and tool bindings in `backend/src/agents/subagents/investment_agent.py`
- [x] T050 [US2] Register Investment Agent in master orchestrator routing (intent: analyze, predict → Investment Agent) in `backend/src/agents/master.py`
- [x] T051 [US2] Export new skills from `backend/src/agents/skills/__init__.py` and subagent from `backend/src/agents/subagents/__init__.py`

### API Endpoints

- [x] T052 [US2] Implement GET `/api/v1/ai/health-score` endpoint with month/year params, compute-on-demand, and cache result in `backend/src/api/v1/endpoints/ai.py`
- [x] T053 [US2] Implement POST `/api/v1/ai/simulate-investment` endpoint with amount/horizon params and structured response with disclaimer in `backend/src/api/v1/endpoints/ai.py`
- [x] T054 [US2] Refine GET `/api/v1/ai/insights` endpoint: generate real insights from spending/budget data, filter by type/severity, store in InsightCache in `backend/src/api/v1/endpoints/ai.py`

### MCP Tool Enhancement

- [x] T055 [US2] Flesh out `simulate_investment` MCP tool with real InvestmentSimulationService logic in `backend/src/mcp/tools/investment_tools.py`
- [x] T056 [US2] Update `analyze_spending` MCP tool to use Spending Insight skill for richer analysis in `backend/src/mcp/tools/spending_analysis.py`

**Checkpoint**: User asks "How is my financial health?" → gets score with breakdown. User asks "Predict if I can invest 10k" → gets projections with disclaimer. Overspending detection and coaching work. US2 independently functional.

---

## Phase 5: User Story 3 — Urdu Language Support (Priority: P3)

**Goal**: Users type in Urdu (Roman or Nastaliq) and the assistant detects the language, processes the request, and responds in Urdu. A language toggle allows explicit switching.

**Independent Test**: Send Urdu commands through the chat widget. Verify intent classification, action execution, and Urdu response with proper formatting.

- [x] T057 [US3] Implement Translation skill: detect language (en/ur/mixed), translate responses to Urdu, format currency (PKR ₨) and dates for Urdu locale in `backend/src/agents/skills/translation.py`
- [x] T058 [US3] Add language detection to Master Orchestrator system prompt: auto-detect input language, respond in same language, respect user preference override in `backend/src/agents/master.py`
- [x] T059 [US3] Store content_ur field in Message model responses when language is Urdu or bilingual mode is active in `backend/src/services/conversation.py`
- [x] T060 [US3] Implement POST `/api/v1/ai/language` endpoint for setting user language preference in `backend/src/api/v1/endpoints/ai.py`
- [x] T061 [P] [US3] Create LanguageToggle component (EN/UR switcher) with localStorage persistence in `frontend/src/components/ai/language-toggle.tsx`
- [x] T062 [P] [US3] Add RTL layout support: conditional `dir="rtl"` attribute, Tailwind RTL utilities, Urdu font stack in `frontend/src/app/layout.tsx` and `frontend/src/app/globals.css`
- [x] T063 [US3] Integrate LanguageToggle into ChatKit widget header and pass language preference to POST `/api/v1/ai/chat` in `frontend/src/components/chatbot/chat-widget.tsx`
- [x] T064 [US3] Export Translation skill from `backend/src/agents/skills/__init__.py`

**Checkpoint**: User types "Mera balance kya hai?" → assistant responds in Urdu with formatted amount. Language toggle switches all AI responses. RTL layout renders correctly. US3 independently functional.

---

## Phase 6: User Story 4 — Voice Command Input (Priority: P4)

**Goal**: Users tap a mic button, speak a command (English or Urdu), and the system transcribes, displays, and processes it through the conversational engine.

**Independent Test**: Press mic button, speak "Show my expenses", verify transcription appears in chat and assistant processes it correctly.

- [x] T065 [P] [US4] Create VoiceButton component with Web Speech API integration (`SpeechRecognition`), language support (en-US, ur-PK), recording state, and graceful fallback for unsupported browsers in `frontend/src/components/ai/voice-button.tsx`
- [x] T066 [US4] Implement Voice Interpretation skill: process transcribed text, handle low-confidence transcriptions, provide confirm/re-record prompt in `backend/src/agents/skills/voice_interpret.py`
- [x] T067 [US4] Integrate VoiceButton into ChatKit widget: position mic button in input area, send transcribed text as message with `input_method: "voice"` in `frontend/src/components/chatbot/chat-widget.tsx`
- [x] T068 [US4] Display transcription preview in chat input before sending: show transcribed text with confirm/edit/re-record options in `frontend/src/components/chatbot/chat-widget.tsx`
- [x] T069 [US4] Export Voice Interpretation skill from `backend/src/agents/skills/__init__.py`

**Checkpoint**: User taps mic → speaks "Show my expenses" → transcription appears → processed as normal command. Urdu speech recognized with ur-PK locale. Unsupported browsers show text-only fallback. US4 independently functional.

---

## Phase 7: User Story 5 — Dashboard AI Integration (Priority: P5)

**Goal**: Dashboard displays AI insight cards (spending alerts, budget warnings, savings tips) alongside financial widgets. Chat widget persists across pages.

**Independent Test**: Log into dashboard, verify AI insight cards appear with real data, chat widget is accessible, and health score displays correctly.

- [x] T070 [P] [US5] Create InsightCard component displaying insight type, severity badge, title, content, action suggestion, and dismiss button in `frontend/src/components/ai/insight-card.tsx`
- [x] T071 [P] [US5] Create HealthScoreDisplay component with radial score visualization, component breakdown, grade label, and trend indicator in `frontend/src/components/ai/health-score.tsx`
- [x] T072 [US5] Add AI insights API functions (getInsights, getHealthScore, dismissInsight) to `frontend/src/lib/api.ts`
- [x] T073 [US5] Integrate InsightCard list and HealthScoreDisplay into dashboard page, fetching from GET `/api/v1/ai/insights` and GET `/api/v1/ai/health-score` in `frontend/src/app/(app)/dashboard/page.tsx`
- [x] T074 [US5] Ensure chat widget persists across all app pages by rendering in app layout in `frontend/src/app/(app)/layout.tsx`
- [x] T075 [US5] Update `generate_dashboard_metrics` MCP tool to include insight cards data and health score in `backend/src/mcp/tools/dashboard_metrics.py`

**Checkpoint**: Dashboard loads with AI insight cards (overspending alerts, savings tips). Health score ring displays with breakdown. Chat widget accessible from all pages. US5 independently functional.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Production hardening, memory management, and operational readiness.

- [x] T076 [P] Add JSON schema validation for all MCP tool inputs/outputs in `backend/src/mcp/server.py`
- [x] T077 [P] Implement conversation memory TTL cleanup: auto-close conversations after 30 min idle, purge agent memory per privacy requirements in `backend/src/services/conversation.py`
- [x] T078 [P] Add structured event logging for all AI operations (chat, tool calls, insights, scores) in `backend/src/services/event.py`
- [x] T079 Implement error handling and graceful degradation: AI unavailable fallback message, partial response handling, timeout management in `backend/src/agents/master.py` and `frontend/src/components/chatbot/chat-widget.tsx`
- [x] T080 Configure rate limiting for AI endpoints (30 messages/minute per user) in `backend/src/api/v1/endpoints/ai.py`
- [x] T081 [P] Create agent blueprint documentation with system prompts, tool mappings, and routing rules in `specs/004-ai-financial-assistant/agent-blueprint.md`
- [x] T082 Run quickstart.md validation: verify full chat flow end-to-end per `specs/004-ai-financial-assistant/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 — MVP target
- **US2 (Phase 4)**: Depends on Phase 2; uses agents from US1 but independently testable
- **US3 (Phase 5)**: Depends on Phase 2; extends master agent from US1 but independently testable
- **US4 (Phase 6)**: Depends on Phase 2; benefits from US3 (Urdu) but independently testable with English
- **US5 (Phase 7)**: Depends on Phase 2; benefits from US2 (insights) but independently testable with basic data
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 — no other story dependencies. **This is the MVP.**
- **US2 (P2)**: Can start after Phase 2 — benefits from US1 agents but has own agent/skill implementations
- **US3 (P3)**: Can start after Phase 2 — extends master agent routing, independent translation layer
- **US4 (P4)**: Can start after Phase 2 — pure frontend + one backend skill, benefits from US3 for Urdu voice
- **US5 (P5)**: Can start after Phase 2 — frontend components + API integration, benefits from US2 for insight data

### Within Each User Story

- Models before repositories
- Repositories before services
- Services before endpoints
- Skills before agents that use them
- Backend before frontend integration
- Core implementation before integration

### Parallel Opportunities

- All Phase 1 tasks marked [P] can run in parallel
- All Phase 2 MCP tools (T013-T018) can run in parallel
- Phase 2 models (T007, T008) can run in parallel
- Once Phase 2 completes, US1-US5 can start in parallel (if team capacity allows)
- Within US2: all three skills (T046-T048) can run in parallel
- Within US2: both models (T040-T041) can run in parallel
- Within US3: LanguageToggle and RTL layout (T061-T062) can run in parallel
- Within US5: InsightCard and HealthScoreDisplay (T070-T071) can run in parallel
- All Phase 8 tasks marked [P] can run in parallel

---

## Parallel Example: Phase 2 — MCP Tools

```bash
# Launch all 6 MCP tools in parallel (different files, no dependencies):
Task T013: "Implement get_financial_summary in backend/src/mcp/tools/financial_summary.py"
Task T014: "Implement create_budget in backend/src/mcp/tools/budget_tools.py"
Task T015: "Implement add_transaction in backend/src/mcp/tools/transaction_tools.py"
Task T016: "Implement analyze_spending in backend/src/mcp/tools/spending_analysis.py"
Task T017: "Implement simulate_investment in backend/src/mcp/tools/investment_tools.py"
Task T018: "Implement generate_dashboard_metrics in backend/src/mcp/tools/dashboard_metrics.py"
```

## Parallel Example: US2 — Skills

```bash
# Launch all 3 analysis skills in parallel:
Task T046: "Budget Analysis skill in backend/src/agents/skills/budget_analysis.py"
Task T047: "Spending Insight skill in backend/src/agents/skills/spending_insight.py"
Task T048: "Investment Simulation skill in backend/src/agents/skills/investment_sim.py"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: US1 — Conversational Financial Commands
4. **STOP and VALIDATE**: Test US1 independently via quickstart.md
5. Deploy/demo if ready — users can chat with the AI assistant

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 → Test independently → Deploy/Demo (**MVP!**)
3. Add US2 → Test independently → Deploy/Demo (insights + coaching)
4. Add US3 → Test independently → Deploy/Demo (Urdu support)
5. Add US4 → Test independently → Deploy/Demo (voice commands)
6. Add US5 → Test independently → Deploy/Demo (dashboard integration)
7. Polish → Full production readiness

### Recommended Execution Order (Single Developer)

Phase 1 → Phase 2 → Phase 3 (US1/MVP) → Phase 4 (US2) → Phase 7 (US5) → Phase 5 (US3) → Phase 6 (US4) → Phase 8

*Note: US5 moved before US3/US4 because dashboard integration delivers high user-visible value once insights (US2) exist.*

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All agent system prompts must include safety guardrails per constitution
- All investment outputs must include mandatory disclaimer
- All Urdu responses must use proper locale formatting (PKR ₨, Urdu dates)
