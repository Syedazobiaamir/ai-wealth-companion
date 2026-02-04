# Research: AI-Powered Todo Chatbot

**Feature**: 005-ai-todo-chatbot
**Date**: 2026-02-03

## Research Tasks

### 1. OpenAI ChatKit Integration

**Decision**: Use `@openai/chatkit-react` v1.4.3

**Rationale**:
- Official OpenAI React SDK for chat interfaces
- Provides `<ChatKit>` component and `useChatKit` hook
- Handles message streaming, typing indicators, and UI state
- Requires domain allowlisting in OpenAI dashboard

**Alternatives Considered**:
- Custom chat UI: More work, less standardized
- Vercel AI SDK: Good but ChatKit is required by constitution

**Integration Pattern**:
```tsx
import { ChatKit, useChatKit } from '@openai/chatkit-react';

function ChatPage() {
  const { messages, sendMessage, isLoading } = useChatKit({
    endpoint: '/api/v1/ai/chat',
  });

  return <ChatKit messages={messages} onSend={sendMessage} />;
}
```

**Key Requirement**: Domain must be allowlisted at platform.openai.com → Settings → Allowed Domains

---

### 2. OpenAI Agents SDK

**Decision**: Use `openai-agents` v0.7.0

**Rationale**:
- Official OpenAI SDK for building AI agents
- Native tool/function calling support
- Handles conversation context management
- Supports streaming responses

**Alternatives Considered**:
- LangChain: More complex, not required
- Custom agent loop: Reinventing the wheel

**Integration Pattern**:
```python
from agents import Agent, Tool

# Define tools
create_task_tool = Tool(
    name="create_task",
    description="Create a new task for the user",
    parameters={...},
    handler=create_task_handler
)

# Create agent
agent = Agent(
    name="TaskAgent",
    instructions="You help users manage their tasks...",
    tools=[create_task_tool, list_tasks_tool, ...]
)

# Run agent
response = await agent.run(user_message)
```

---

### 3. Official MCP SDK (FastMCP)

**Decision**: Use `mcp` v1.26.0 with FastMCP

**Rationale**:
- Official Model Context Protocol SDK
- FastMCP provides decorator-based tool registration
- Standardized JSON-RPC 2.0 communication
- Easy integration with OpenAI Agents SDK

**Alternatives Considered**:
- Custom tool registry: Already exists but not standard MCP
- Direct function calling: Loses MCP benefits

**Integration Pattern**:
```python
from mcp.server import FastMCP

mcp = FastMCP("task-tools")

@mcp.tool()
async def create_task(title: str, priority: str = "medium") -> dict:
    """Create a new task."""
    # Implementation
    return {"status": "created", "task_id": "..."}

# Export for OpenAI Agents SDK
tools = mcp.get_tools()
```

---

### 4. Voice Input (Web Speech API)

**Decision**: Use browser's Web Speech API with ur-PK locale

**Rationale**:
- No additional service needed
- Supports both en-US and ur-PK
- Real-time transcription
- Free, privacy-preserving (browser-side)

**Alternatives Considered**:
- Whisper API: Better accuracy but adds latency and cost
- Google Cloud Speech: Overkill for this use case

**Integration Pattern**:
```typescript
const recognition = new webkitSpeechRecognition();
recognition.lang = language === 'ur' ? 'ur-PK' : 'en-US';
recognition.continuous = false;
recognition.interimResults = true;

recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  // Show for confirmation before sending
};
```

**Browser Support**: Chrome, Edge, Safari (not Firefox)

---

### 5. Date Parsing for Natural Language

**Decision**: Use `dateparser` Python library

**Rationale**:
- Handles relative dates: "tomorrow", "next Friday", "in 3 days"
- Multi-language support including Urdu
- Well-maintained, widely used
- Returns Python datetime objects

**Alternatives Considered**:
- parsedatetime: Less language support
- Custom regex: Error-prone, limited
- spaCy NER: Overkill for dates only

**Integration Pattern**:
```python
import dateparser
from datetime import date

def parse_due_date(text: str, language: str = "en") -> Optional[date]:
    """Parse natural language date expression."""
    settings = {
        'PREFER_DATES_FROM': 'future',
        'RELATIVE_BASE': datetime.now(),
    }

    parsed = dateparser.parse(
        text,
        languages=[language, 'en'],
        settings=settings
    )

    return parsed.date() if parsed else None

# Examples:
# "tomorrow" → 2026-02-04
# "next Friday" → 2026-02-07
# "in 3 days" → 2026-02-06
# "کل" (kal/tomorrow in Urdu) → 2026-02-04
```

---

## Technology Summary

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Chat UI | @openai/chatkit-react | 1.4.3 | Frontend chat component |
| Agent Framework | openai-agents | 0.7.0 | Backend agent orchestration |
| Tool Protocol | mcp (FastMCP) | 1.26.0 | Standardized tool communication |
| Voice STT | Web Speech API | Browser | Speech-to-text |
| Voice TTS | SpeechSynthesis API | Browser | Text-to-speech |
| Date Parsing | dateparser | Latest | Natural language dates |

## Dependencies to Add

### Backend (requirements.txt)
```
dateparser>=1.2.0
```
Note: `openai-agents` and `mcp` already installed.

### Frontend (package.json)
```json
{
  "@openai/chatkit-react": "^1.4.3"
}
```
Note: Already installed.

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| How to handle ChatKit domain allowlist? | Document in quickstart.md |
| What if voice recognition fails? | Fallback to text input |
| How to handle Urdu date expressions? | dateparser supports multiple languages |
| What about offline mode? | Out of scope per spec |
