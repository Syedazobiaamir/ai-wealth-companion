# Implementation Plan: AI Wealth Companion Chatbot

**Branch**: `005-ai-todo-chatbot` | **Date**: 2026-02-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-ai-todo-chatbot/spec.md`

## Summary

Build an AI-powered chatbot that serves as the primary interface for the AI Wealth Companion platform. Users can manage their entire financial life through natural language conversation - tracking expenses, creating budgets, analyzing spending patterns, simulating investments, managing tasks/reminders, and checking their financial health. The chatbot uses **OpenAI ChatKit** for the frontend UI, **OpenAI Agents SDK** for backend agent orchestration, and the **Official MCP SDK** for tool integration. Supports text and voice commands in English or Urdu.

**Key Integration**: Leverages ALL existing subagents (SpendingAgent, BudgetAgent, InvestmentAgent, TaskAgent) and MCP tools (9+ existing tools) - not replacing, but integrating with official OpenAI SDKs.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, OpenAI Agents SDK (`openai-agents`), Official MCP SDK (`mcp`), OpenAI SDK (`openai`)
- Frontend: Next.js 14, React 18, OpenAI ChatKit React (`@openai/chatkit-react`), Framer Motion
**Storage**: Neon PostgreSQL (existing from Phase II) - Task, Conversation, Message models already exist
**Testing**: pytest (backend), Jest (frontend)
**Target Platform**: Web application (responsive)
**Project Type**: Web (backend + frontend)
**Performance Goals**: <5s task creation, <3s interface load, 100 concurrent sessions
**Constraints**: <200ms p95 API response, WebSocket for real-time chat, browser Web Speech API for voice
**Scale/Scope**: Multi-user, existing auth system, bilingual (English + Urdu)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| **OpenAI ChatKit UI** (NON-NEGOTIABLE) | ✅ PASS | FR-001: System MUST use ChatKit component |
| **OpenAI Agents SDK** (NON-NEGOTIABLE) | ✅ PASS | FR-018: System MUST use Agents SDK |
| **Official MCP SDK** (NON-NEGOTIABLE) | ✅ PASS | FR-019: System MUST use MCP SDK |
| **Urdu Language Support** (NON-NEGOTIABLE) | ✅ PASS | FR-021-023: Bilingual support |
| **Voice Command Support** (NON-NEGOTIABLE) | ✅ PASS | FR-002: Voice input support |
| **AI Safety Laws** | ✅ PASS | Tasks are user data, not financial advice |
| **Structured Tool Calling** | ✅ PASS | MCP tools already follow JSON format |
| **Backend is Single Source of Truth** | ✅ PASS | All data from Neon PostgreSQL |
| **JWT Authentication** | ✅ PASS | Existing auth system reused |

**Gate Result**: ✅ ALL PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/005-ai-todo-chatbot/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── ai-chat-api.md   # Chat API contract
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── agents/
│   │   ├── base.py              # Existing BaseAgent
│   │   ├── registry.py          # Existing AgentRegistry
│   │   ├── master.py            # Existing MasterOrchestrator
│   │   ├── openai_agent.py      # NEW: OpenAI Agents SDK integration
│   │   └── subagents/
│   │       └── task_agent.py    # Existing TaskAgent (to be enhanced)
│   ├── mcp/
│   │   ├── server.py            # Existing MCP tool registry
│   │   ├── official_server.py   # NEW: Official MCP SDK server
│   │   └── tools/
│   │       ├── task_tools.py    # Existing (to add complete_task, update_task)
│   │       └── ...
│   ├── models/
│   │   ├── task.py              # Existing Task model
│   │   ├── conversation.py      # Existing Conversation model
│   │   └── message.py           # Existing Message model
│   ├── services/
│   │   ├── task.py              # Existing TaskService
│   │   ├── conversation.py      # Existing ConversationService
│   │   └── ai.py                # Existing AIService (to be enhanced)
│   └── api/v1/endpoints/
│       └── ai.py                # Existing AI endpoints (to be enhanced)
└── tests/
    ├── unit/
    │   └── test_task_agent.py   # NEW
    └── integration/
        └── test_ai_chat.py      # NEW

frontend/
├── src/
│   ├── app/(app)/
│   │   └── chat/
│   │       └── page.tsx         # Existing (to use ChatKit)
│   ├── components/
│   │   ├── ai/
│   │   │   ├── language-toggle.tsx  # Existing
│   │   │   └── voice-button.tsx     # Existing
│   │   └── chatbot/
│   │       ├── chat-widget.tsx      # Existing (to use ChatKit)
│   │       └── chatkit-wrapper.tsx  # NEW: ChatKit integration
│   └── lib/
│       └── chatkit-config.ts    # NEW: ChatKit configuration
└── tests/
    └── components/
        └── chat.test.tsx        # NEW
```

**Structure Decision**: Web application structure with backend (FastAPI + agents) and frontend (Next.js + ChatKit). Builds on existing Phase II code.

## Complexity Tracking

> No constitution violations - no complexity justification needed.

## Phase 0: Research Summary

### Research Tasks

1. **OpenAI ChatKit Integration**: How to integrate `@openai/chatkit-react` with Next.js 14
2. **OpenAI Agents SDK**: How to use `openai-agents` for agent orchestration with tools
3. **Official MCP SDK**: How to create an MCP server with `FastMCP` and register tools
4. **Voice Input**: Browser Web Speech API for Urdu (ur-PK) support
5. **Date Parsing**: NLP approaches for relative date extraction from natural language

### Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Chat UI | OpenAI ChatKit | Required by constitution; production-ready |
| Agent Framework | OpenAI Agents SDK | Required by constitution; official SDK |
| Tool Protocol | Official MCP SDK (FastMCP) | Required by constitution; standardized |
| Voice STT | Web Speech API | Browser-native, supports ur-PK |
| Voice TTS | Browser TTS | No additional service needed |
| Date Parsing | dateparser library | Handles "tomorrow", "next Friday", etc. |

## Phase 1: Design Artifacts

### 1.1 Data Model

**Existing models are sufficient** - Task, Conversation, Message already exist with all required fields:
- `Task`: title, due_date, priority, category, is_completed
- `Conversation`: user_id, language, is_active
- `Message`: role, content, content_ur, intent, tool_calls, input_method

**No new models required.**

### 1.2 API Contracts

**Existing endpoints** (`/api/v1/ai/*`) will be enhanced:

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/api/v1/ai/chat` | POST | Send chat message | EXISTS - enhance for ChatKit |
| `/api/v1/ai/conversations` | GET | List conversations | EXISTS |
| `/api/v1/ai/conversations/{id}/messages` | GET | Get messages | EXISTS |
| `/api/v1/ai/language` | POST | Set language | EXISTS |

**MCP Tools to add/enhance**:

| Tool | Purpose | Status |
|------|---------|--------|
| `create_task` | Create task from chat | EXISTS |
| `list_tasks` | List tasks by status | EXISTS |
| `get_task_summary` | Task counts | EXISTS |
| `complete_task` | Mark task done | NEW |
| `update_task` | Update task fields | NEW |

### 1.3 Integration Points

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            OpenAI ChatKit Component                   │    │
│  │  - Text input                                         │    │
│  │  - Voice button (Web Speech API)                      │    │
│  │  - Language toggle (EN/UR)                            │    │
│  └─────────────────────────────────────────────────────┘    │
│                          │                                   │
│                    POST /api/v1/ai/chat                      │
└──────────────────────────┼──────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────────┐
│                     Backend (FastAPI)                        │
│                          ▼                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              OpenAI Agents SDK Agent                  │    │
│  │  - Process natural language                           │    │
│  │  - Route to tools via MCP                             │    │
│  │  - Generate response                                  │    │
│  └─────────────────────────────────────────────────────┘    │
│                          │                                   │
│                  MCP Tool Calls                              │
│                          ▼                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            Official MCP SDK Server                    │    │
│  │  - create_task                                        │    │
│  │  - list_tasks                                         │    │
│  │  - complete_task                                      │    │
│  │  - update_task                                        │    │
│  │  - get_task_summary                                   │    │
│  └─────────────────────────────────────────────────────┘    │
│                          │                                   │
│                     TaskService                              │
│                          ▼                                   │
│                    Neon PostgreSQL                           │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Phases

### Phase A: Backend - OpenAI Agents SDK Integration
1. Create `openai_agent.py` using Agents SDK with tool registration
2. Add MCP tools: `complete_task`, `update_task`
3. Integrate date parsing for relative dates
4. Enhance `/api/v1/ai/chat` endpoint
5. Add Urdu response generation

### Phase B: Backend - Official MCP SDK Server
1. Create `official_mcp_server.py` using FastMCP
2. Register all task tools with proper schemas
3. Connect to TaskService for database operations
4. Add tool call logging for audit

### Phase C: Frontend - ChatKit Integration
1. Create ChatKit wrapper component
2. Configure ChatKit with backend endpoint
3. Integrate voice input button
4. Add language toggle
5. Style to match app theme

### Phase D: Testing & Polish
1. Unit tests for task agent
2. Integration tests for chat flow
3. E2E test for task creation via chat
4. Performance optimization

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| ChatKit domain allowlist requirement | Document setup steps in quickstart.md |
| OpenAI API rate limits | Implement retry with exponential backoff |
| Urdu voice recognition accuracy | Show transcription for confirmation |
| Date parsing ambiguity | Ask for clarification when confidence low |

## Next Steps

Run `/sp.tasks` to generate detailed task breakdown with test cases.
