# Research: AI Financial Assistant (Phase III)

**Branch**: `004-ai-financial-assistant` | **Date**: 2026-02-01

## R-001: OpenAI Agents SDK Integration Pattern

**Decision**: Use OpenAI Agents SDK as the orchestration layer for all AI agents.

**Rationale**: Constitution mandates OpenAI Agents SDK (Phase III Law #2). The SDK provides built-in agent routing, tool calling, and memory management that aligns with the multi-agent architecture specified.

**Alternatives considered**:
- LangChain/LangGraph: More flexible but adds unnecessary abstraction; constitution requires OpenAI Agents SDK specifically.
- Custom agent framework: Higher maintenance burden; no benefit over SDK.

**Integration approach**:
- Install `openai-agents` Python package in backend
- Define agents as Python classes inheriting from SDK base
- Master agent uses SDK's built-in routing to delegate to subagents
- Each subagent registers MCP tools it can call

## R-002: MCP Server Architecture

**Decision**: Build a single MCP server in the backend that exposes financial tools, consumed by agents via the Official MCP SDK.

**Rationale**: Constitution mandates Official MCP SDK (Phase III Law #3). A single server keeps deployment simple while exposing all 6 required tools.

**Alternatives considered**:
- Multiple MCP servers per domain (budget, spending, etc.): Over-engineered for current scale; can split later.
- Direct function calls without MCP: Violates constitution; loses tool schema validation and audit logging.

**Implementation**:
- MCP server runs as part of the FastAPI application (same process)
- Tools wrap existing service layer methods (TransactionService, BudgetService, etc.)
- Each tool has JSON Schema validation for inputs/outputs
- Tool calls logged to EventLog table

## R-003: ChatKit UI Integration

**Decision**: Replace the existing mock ChatWidget with OpenAI ChatKit UI components on the frontend.

**Rationale**: Constitution mandates OpenAI ChatKit UI (Phase III Law #1). The existing ChatWidget (`frontend/src/components/chatbot/chat-widget.tsx`) provides the UX pattern but uses mock responses.

**Alternatives considered**:
- Keep existing ChatWidget and add AI backend: Loses ChatKit features (streaming, tool visualization).
- Build custom chat UI from scratch: Unnecessary duplication; constitution requires ChatKit.

**Implementation**:
- Install `@openai/chatkit` npm package in frontend
- Replace `chat-widget.tsx` internals with ChatKit components
- Connect to `/api/v1/ai/chat` endpoint (already stubbed)
- Preserve existing positioning (bottom-right collapsible widget)

## R-004: Voice Command Pipeline

**Decision**: Use browser Web Speech API for speech-to-text (client-side) with server-side intent processing.

**Rationale**: Web Speech API is free, requires no API keys, and runs client-side reducing latency. Constitution's voice pipeline shows STT happening before server processing.

**Alternatives considered**:
- Whisper API (server-side): Higher accuracy but adds latency, API cost, and requires audio upload. Reserved as fallback.
- Third-party STT services: Unnecessary vendor dependency.

**Implementation**:
- Frontend mic button activates `webkitSpeechRecognition` / `SpeechRecognition`
- Supports `lang: 'en-US'` and `lang: 'ur-PK'` based on user preference
- Transcribed text sent to chat as normal text message
- Graceful fallback message if Web Speech API is unsupported

## R-005: Urdu Language Support Strategy

**Decision**: Use OpenAI GPT model's native Urdu capabilities for understanding and response generation. Roman Urdu (Latin script) is the primary input method.

**Rationale**: GPT-4 has strong Urdu comprehension. Roman Urdu is how most Pakistani users actually type on standard keyboards. Nastaliq rendering requires RTL CSS support which Tailwind provides via `dir="rtl"`.

**Alternatives considered**:
- Dedicated translation service (Google Translate API): Adds latency and cost; model already handles Urdu.
- Custom Urdu NLP models: Overkill for this use case; GPT handles it natively.

**Implementation**:
- Language detection via prompt engineering (model detects language in system prompt)
- User language preference stored in localStorage and user settings
- UI toggle switches `dir` attribute for RTL support
- Response formatting adapts currency/date to locale

## R-006: Financial Health Score Algorithm

**Decision**: Score based on weighted formula: budget adherence (40%), savings rate (30%), spending consistency (20%), goal progress (10%).

**Rationale**: These four factors capture the key dimensions of financial health that can be measured from existing data. Weights prioritize budget discipline.

**Alternatives considered**:
- Simple budget adherence only: Too narrow; misses savings behavior.
- ML-based scoring: Requires training data we don't have; over-engineered.

**Implementation**:
- Budget adherence: Average (spending / budget limit) across categories, inverted (100 = perfect adherence)
- Savings rate: (income - expenses) / income * 100
- Spending consistency: Standard deviation of daily spending, normalized
- Goal progress: Average completion percentage across active goals
- Score = 0.4 * adherence + 0.3 * savings + 0.2 * consistency + 0.1 * goals

## R-007: Investment Simulation Approach

**Decision**: Simple compound interest projection with Monte Carlo variance, not real market data.

**Rationale**: Constitution prohibits real financial advice. Educational simulation based on user's current savings rate and standard return assumptions provides value without legal risk.

**Alternatives considered**:
- Real market data integration: Legal liability; constitution forbids investment recommendations.
- Fixed return projections only: Too simplistic; doesn't show range of outcomes.

**Implementation**:
- User provides: investment amount, time period
- System calculates: projected value at conservative (5%), moderate (8%), aggressive (12%) returns
- Monte Carlo: 1000 simulations with random variance to show confidence intervals
- All outputs include mandatory disclaimer per constitution

## R-008: Conversation Memory Architecture

**Decision**: Session-scoped memory stored in AgentMemory table (already exists), with short-term context window for the current conversation.

**Rationale**: AgentMemory model already exists with importance scoring, TTL, and access counting. Session scope prevents cross-session data leakage per privacy requirements.

**Alternatives considered**:
- In-memory only: Loses context if user refreshes page.
- Long-term cross-session memory: Privacy concern; constitution requires no data retention after session.

**Implementation**:
- Each chat session gets a unique conversation_id
- Last N messages (context window = 20) sent with each API call
- Agent memory stores extracted preferences and referenced entities
- Memory expires after session ends (TTL-based cleanup)

## R-009: Existing Code Reuse Assessment

**Decision**: Maximize reuse of existing backend services, models, and frontend components.

**What exists and will be reused**:
- Backend AI endpoints (stubs at `/api/v1/ai/`) → Flesh out with real logic
- AIService context gathering → Already functional, needs LLM connection
- InsightCache model → Ready for insight storage
- AgentMemory model → Ready for conversation memory
- EventLog model → Ready for audit trail
- ChatWidget positioning/UX → Replace internals with ChatKit
- All financial services → Wrapped as MCP tools

**What must be built new**:
- MCP server with tool definitions
- Agent classes (Master, Budget, Spending, Investment)
- Skill implementations (NLP, Translation, Voice, Prediction)
- ChatKit UI integration
- Voice input component
- Language toggle component
- Insight card components
- Financial health score calculator
