# Tasks: AI Wealth Companion Chatbot

**Input**: Design documents from `/specs/005-ai-todo-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, etc.)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Frontend**: `frontend/src/`

---

## Phase 1: Setup (SDK Integration)

**Purpose**: Install and verify OpenAI SDKs (Agents SDK, MCP SDK, ChatKit)

- [x] T001 Verify OpenAI Agents SDK import works: `python -c "from agents import Agent; print('OK')"`
- [x] T002 [P] Verify Official MCP SDK import works: `python -c "from mcp.server import FastMCP; print('OK')"`
- [x] T003 [P] Verify ChatKit React SDK is installed: `npm list @openai/chatkit-react`
- [x] T004 [P] Add OPENAI_API_KEY to backend/.env.example with documentation comment

---

## Phase 2: Foundational (OpenAI SDK Integration)

**Purpose**: Replace custom implementations with official OpenAI SDKs - this MUST be complete before user stories

**⚠️ CRITICAL**: All user stories depend on this phase

- [x] T005 Create OpenAI Agents SDK wrapper in backend/src/agents/openai_wrapper.py with tool registration
- [x] T006 Create Official MCP SDK server in backend/src/mcp/official_server.py using FastMCP
- [x] T007 Register existing MCP tools with FastMCP in backend/src/mcp/official_server.py (create_budget, add_transaction, etc.)
- [x] T008 Update backend/src/services/ai.py to use OpenAI Agents SDK for process_chat()
- [x] T009 [P] Create ChatKit configuration in frontend/src/lib/chatkit-config.ts
- [x] T010 [P] Create ChatKit wrapper component in frontend/src/components/chatbot/chatkit-wrapper.tsx
- [x] T011 Update backend/src/api/v1/endpoints/ai.py to integrate with OpenAI agent pipeline

**Checkpoint**: Foundation ready - OpenAI SDKs integrated with existing agents ✅ COMPLETE

---

## Phase 3: User Story 1 - Record Transactions via Chat (Priority: P1) 🎯 MVP

**Goal**: Users can record income/expenses by typing "spent 500 on groceries" or "received salary 85000"

**Independent Test**: Send "spent 2000 on food" → transaction created with correct amount and category

### Implementation for User Story 1

- [x] T012 [US1] Verify SpendingAgent handles "spent X on Y" patterns in backend/src/agents/subagents/spending_agent.py
- [x] T013 [US1] Verify add_transaction MCP tool works via OpenAI agent in backend/src/mcp/tools/transaction_tools.py
- [x] T014 [US1] Add amount extraction for Urdu formats ("15 hazar", "500 rupay") in backend/src/agents/skills/finance_crud.py
- [x] T015 [US1] Update ChatKit wrapper to show transaction confirmation in frontend/src/components/chatbot/chatkit-wrapper.tsx
- [x] T016 [US1] Add voice input integration with ChatKit in frontend/src/components/ai/voice-button.tsx

**Checkpoint**: User Story 1 complete - users can record transactions via chat ✅

---

## Phase 4: User Story 2 - Query Spending & Financial Summary (Priority: P1)

**Goal**: Users can ask "show my spending this month" and see financial breakdown

**Independent Test**: Ask "where did my money go?" → chatbot shows category breakdown

### Implementation for User Story 2

- [x] T017 [US2] Verify SpendingAgent handles "show spending" queries in backend/src/agents/subagents/spending_agent.py
- [x] T018 [US2] Verify get_financial_summary MCP tool returns correct data in backend/src/mcp/tools/financial_summary.py
- [x] T019 [US2] Verify analyze_spending MCP tool provides trends in backend/src/mcp/tools/spending_analysis.py
- [x] T020 [US2] Add spending summary formatting for chat response in backend/src/agents/skills/spending_insight.py
- [x] T021 [US2] Style ChatKit messages for financial data display in frontend/src/app/globals.css

**Checkpoint**: User Story 2 complete - users can query spending via chat ✅

---

## Phase 5: User Story 3 - Budget Management via Chat (Priority: P1)

**Goal**: Users can say "set food budget to 15000" and ask "how's my food budget?"

**Independent Test**: Say "set food budget to 15000" → budget created; ask "how's my food budget?" → status shown

### Implementation for User Story 3

- [x] T022 [US3] Verify BudgetAgent handles "set X budget to Y" patterns in backend/src/agents/subagents/budget_agent.py
- [x] T023 [US3] Verify create_budget MCP tool works via OpenAI agent in backend/src/mcp/tools/budget_tools.py
- [x] T024 [US3] Add budget status query handling ("how's my X budget?") in backend/src/agents/subagents/budget_agent.py
- [x] T025 [US3] Add budget status formatting (on-track, warning, exceeded) in backend/src/agents/skills/budget_analysis.py
- [x] T026 [US3] Add budget coaching messages in backend/src/agents/skills/budget_analysis.py

**Checkpoint**: User Stories 1-3 complete - Core MVP (transactions, spending, budgets via chat) ✅

---

## Phase 6: User Story 4 - Investment Simulation (Priority: P2)

**Goal**: Users can ask "what if I invest 50000 for 12 months?" and get projections

**Independent Test**: Ask "can I invest 50000?" → projections at 3 risk levels shown

### Implementation for User Story 4

- [x] T027 [US4] Verify InvestmentAgent handles investment queries in backend/src/agents/subagents/investment_agent.py
- [x] T028 [US4] Verify simulate_investment MCP tool returns projections in backend/src/mcp/tools/investment_tools.py
- [x] T029 [US4] Add feasibility analysis based on user finances in backend/src/agents/skills/investment_sim.py
- [x] T030 [US4] Ensure financial disclaimer is included in responses in backend/src/agents/master.py

**Checkpoint**: User Story 4 complete - investment simulation via chat ✅

---

## Phase 7: User Story 5 - Task & Reminder Management (Priority: P2)

**Goal**: Users can say "remind me to pay rent on the 5th" and manage tasks via chat

**Independent Test**: Say "remind me to pay electricity bill next Friday" → task created

### Implementation for User Story 5

- [x] T031 [US5] Verify TaskAgent handles "remind me" and "task" patterns in backend/src/agents/subagents/task_agent.py
- [x] T032 [US5] Verify create_task MCP tool with date parsing in backend/src/mcp/tools/task_tools.py
- [x] T033 [US5] Verify list_tasks MCP tool with filtering in backend/src/mcp/tools/task_tools.py
- [x] T034 [US5] Add task completion handling ("mark X as done") in backend/src/agents/subagents/task_agent.py
- [x] T035 [US5] Add task list formatting for chat response in backend/src/agents/subagents/task_agent.py

**Checkpoint**: User Story 5 complete - task management via chat ✅

---

## Phase 8: User Story 6 - Financial Health Check (Priority: P2)

**Goal**: Users can ask "what's my financial health?" and get score with recommendations

**Independent Test**: Ask "how am I doing financially?" → health score and recommendations shown

### Implementation for User Story 6

- [x] T036 [US6] Add health score query handling in backend/src/agents/master.py
- [x] T037 [US6] Expose get_health_score via MCP tool in backend/src/mcp/official_server.py
- [x] T038 [US6] Add health score formatting with grade and breakdown in backend/src/services/ai.py
- [x] T039 [US6] Add personalized recommendations based on score in backend/src/services/ai.py

**Checkpoint**: User Story 6 complete - financial health via chat ✅

---

## Phase 9: User Story 7 - Bilingual Urdu Support (Priority: P3)

**Goal**: Users can interact in Urdu with responses in Urdu when preferred

**Independent Test**: Set language to Urdu, type "میرے اخراجات دکھاؤ" → response in Urdu

### Implementation for User Story 7

- [x] T040 [US7] Verify Urdu/Roman Urdu detection in backend/src/agents/skills/translation.py
- [x] T041 [US7] Add Urdu response templates for all agents in backend/src/agents/skills/translation.py
- [x] T042 [US7] Add Roman Urdu keyword support (kharcha, kamai, bajat) in backend/src/agents/skills/finance_crud.py
- [x] T043 [US7] Add Urdu voice recognition (ur-PK) in frontend/src/components/ai/voice-button.tsx
- [x] T044 [US7] Add RTL text support in ChatKit wrapper in frontend/src/components/chatbot/chatkit-wrapper.tsx

**Checkpoint**: User Story 7 complete - full bilingual English/Urdu support ✅

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting all user stories

- [x] T045 [P] Add error handling for OpenAI API failures in backend/src/agents/openai_wrapper.py
- [x] T046 [P] Add retry with exponential backoff for rate limits in backend/src/agents/openai_wrapper.py
- [x] T047 [P] Add tool call logging for audit in backend/src/mcp/official_server.py
- [x] T048 Add typing indicator while AI processes in frontend/src/components/chatbot/chatkit-wrapper.tsx
- [x] T049 [P] Style ChatKit to match app theme in frontend/src/app/globals.css
- [x] T050 Update quickstart.md with ChatKit domain allowlist instructions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phases 3-9)**: All depend on Foundational completion
  - US1-US3 are P1 (Core MVP) - implement first
  - US4-US6 are P2 - implement after MVP validated
  - US7 is P3 - implement last
- **Polish (Phase 10)**: Depends on desired user stories being complete

### User Story Dependencies

| Story | Priority | Depends On | Focus Area |
|-------|----------|------------|------------|
| US1 - Transactions | P1 | Foundational | Record income/expenses |
| US2 - Spending Query | P1 | Foundational | View spending data |
| US3 - Budgets | P1 | Foundational | Create/monitor budgets |
| US4 - Investments | P2 | Foundational | Investment simulations |
| US5 - Tasks | P2 | Foundational | Task management |
| US6 - Health Score | P2 | Foundational | Financial wellness |
| US7 - Bilingual | P3 | Foundational | Urdu language support |

**Note**: All user stories can start in parallel after Foundational, but recommended order is P1 → P2 → P3.

### Within Each User Story

1. Backend agent verification first
2. MCP tool verification second
3. Skills/formatting third
4. Frontend integration last
5. Checkpoint validation before next story

---

## Implementation Strategy

### MVP First (User Stories 1-3)

1. Complete Phase 1: Setup (4 tasks)
2. Complete Phase 2: Foundational (7 tasks) - CRITICAL
3. Complete Phase 3: US1 - Transactions (5 tasks)
4. Complete Phase 4: US2 - Spending Query (5 tasks)
5. Complete Phase 5: US3 - Budgets (5 tasks)
6. **STOP and VALIDATE**: Test recording transactions, viewing spending, managing budgets via chat
7. Deploy/demo as MVP

### Incremental Delivery

| Milestone | User Stories | Total Tasks | Cumulative |
|-----------|--------------|-------------|------------|
| Foundation | Setup + Foundational | 11 | 11 |
| MVP | + US1 + US2 + US3 | 15 | 26 |
| Enhanced | + US4 + US5 + US6 | 13 | 39 |
| Full Feature | + US7 | 5 | 44 |
| Polish | Final phase | 6 | 50 |

---

## Summary

| Metric | Count |
|--------|-------|
| **Total Tasks** | 50 |
| Phase 1 (Setup) | 4 |
| Phase 2 (Foundational) | 7 |
| Phase 3 (US1 - Transactions) | 5 |
| Phase 4 (US2 - Spending) | 5 |
| Phase 5 (US3 - Budgets) | 5 |
| Phase 6 (US4 - Investments) | 4 |
| Phase 7 (US5 - Tasks) | 5 |
| Phase 8 (US6 - Health) | 4 |
| Phase 9 (US7 - Bilingual) | 5 |
| Phase 10 (Polish) | 6 |
| **MVP Tasks (US1-US3)** | 26 |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Existing agents (Spending, Budget, Investment, Task) are REUSED, not rebuilt
- Focus is on OpenAI SDK integration, not rebuilding functionality
- Each user story is independently testable after Foundational
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
