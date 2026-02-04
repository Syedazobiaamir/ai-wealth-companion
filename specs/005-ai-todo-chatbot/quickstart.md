# Quickstart: AI Wealth Companion Chatbot

**Feature**: 005-ai-todo-chatbot
**Date**: 2026-02-03
**Status**: Implementation Complete

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+ and pip
- Existing Phase II setup (database, auth working)
- **AI API key** (one of the following):
  - Google Gemini API key (recommended - free tier available)
  - OpenAI API key (alternative)

## Setup Steps

### 1. Install Backend Dependencies

```bash
cd backend
source venv/bin/activate

# Install new dependencies
pip install dateparser>=1.2.0

# Verify SDKs are installed
python -c "from agents import Agent; print('Agents SDK OK')"
python -c "from mcp.server import FastMCP; print('MCP SDK OK')"
python -c "from google import genai; print('Gemini SDK OK')"
python -c "import openai; print('OpenAI SDK OK')"
```

### 2. Configure AI API Key

Choose ONE of the following options:

**Option A: Google Gemini (Recommended)**
```bash
# Add to backend/.env
GEMINI_API_KEY=your-gemini-api-key-here
```
Get your free key from: https://aistudio.google.com/app/apikey

**Option B: OpenAI**
```bash
# Add to backend/.env
OPENAI_API_KEY=sk-your-api-key-here
```
Get your key from: https://platform.openai.com/api-keys

**Note**: If both keys are configured, Gemini takes priority.

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install

# Verify ChatKit is installed
npm list @openai/chatkit-react
# Should show: @openai/chatkit-react@1.4.3
```

### 4. Configure ChatKit Domain Allowlist

**IMPORTANT**: ChatKit requires domain allowlisting in OpenAI dashboard.

1. Go to https://platform.openai.com/settings
2. Navigate to **Allowed Domains** (or **ChatKit Settings**)
3. Add your domains:
   - Development: `localhost:3000`
   - Production: `yourdomain.com`

Without this step, ChatKit will fail to render.

### 5. Start Development Servers

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 6. Verify Installation

1. Open http://localhost:3000/chat
2. Login with demo account: `demo@example.com` / `demo1234`
3. Type: "remind me to pay rent tomorrow"
4. Verify task is created

## Testing the Chat

### Basic Task Creation
```
User: "remind me to pay electricity bill next Friday"
AI: "I've created a task 'Pay electricity bill' due Friday, February 7th."
```

### Viewing Tasks
```
User: "show my tasks"
AI: "You have 3 active tasks:
1. Pay electricity bill - due Feb 7 (bills)
2. Review budget - due Feb 5 (review)
3. Transfer to savings - due Feb 10 (savings)"
```

### Completing Tasks
```
User: "mark electricity bill as done"
AI: "Done! Task 'Pay electricity bill' has been completed."
```

### Voice Input
1. Click the microphone button
2. Say: "add task to check investments tomorrow"
3. Review transcription
4. Confirm to send

### Urdu Support
1. Click language toggle to switch to "اردو"
2. Type: "میرے کام دکھاؤ"
3. Response will be in Urdu

## Troubleshooting

### ChatKit Not Rendering

**Symptom**: Chat page shows blank or error

**Solution**:
1. Check browser console for "domain not allowed" error
2. Ensure domain is added to OpenAI dashboard allowlist
3. Clear browser cache and reload

### Voice Input Not Working

**Symptom**: Microphone button doesn't respond

**Solution**:
1. Use Chrome, Edge, or Safari (Firefox not supported)
2. Allow microphone permission when prompted
3. Check that no other app is using microphone

### Tasks Not Creating

**Symptom**: AI acknowledges but task doesn't appear

**Solution**:
1. Check backend logs for errors
2. Verify OpenAI API key is valid
3. Check database connection

### Urdu Text Not Displaying

**Symptom**: Urdu text shows as squares or question marks

**Solution**:
1. Ensure Noto Nastaliq Urdu font is loading
2. Check browser supports Unicode
3. Verify RTL CSS is applied

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-...
JWT_SECRET_KEY=...
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Next Steps

After verifying basic functionality:

1. Run `/sp.tasks` to generate detailed implementation tasks
2. Implement OpenAI Agents SDK integration
3. Implement Official MCP SDK server
4. Enhance ChatKit integration
5. Add comprehensive tests
