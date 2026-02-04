# Quickstart: AI Financial Assistant (Phase III)

**Branch**: `004-ai-financial-assistant` | **Date**: 2026-02-01

## Prerequisites

- Phase II running (backend on :8000, frontend on :3000)
- OpenAI API key with GPT-4 access
- Python 3.11+ with venv
- Node.js 18+

## Setup Steps

### 1. Backend Dependencies

```bash
cd backend
source venv/bin/activate
pip install openai-agents mcp aiosqlite
```

### 2. Environment Variables

Add to `backend/.env`:
```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4
```

### 3. Frontend Dependencies

```bash
cd frontend
npm install @openai/chatkit
```

### 4. Run Development Servers

```bash
# Terminal 1: Backend
cd backend && source venv/bin/activate && uvicorn src.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

### 5. Test the Chat

1. Open http://localhost:3000/dashboard
2. Click the chat widget (bottom-right)
3. Type: "Show my expenses this month"
4. Verify AI responds with actual data from your account

## Development Workflow

1. **Stage 1 (Foundation)**: MCP server + ChatKit UI + JWT pipeline
2. **Stage 2 (Intelligence)**: Master agent + subagents + skills
3. **Stage 3 (Capabilities)**: NLP control + summaries + coaching + predictions
4. **Stage 4 (Bonus)**: Urdu agent + voice pipeline + smart suggestions
5. **Stage 5 (Production)**: Tool registry + memory + logging

## Key File Locations

| Component | Path |
|-----------|------|
| MCP Server | `backend/src/mcp/server.py` |
| MCP Tools | `backend/src/mcp/tools/` |
| Master Agent | `backend/src/agents/master.py` |
| Subagents | `backend/src/agents/subagents/` |
| Skills | `backend/src/agents/skills/` |
| Chat Widget | `frontend/src/components/chatbot/chat-widget.tsx` |
| AI API Client | `frontend/src/lib/api.ts` (aiApi section) |
| AI Endpoints | `backend/src/api/v1/endpoints/ai.py` |
