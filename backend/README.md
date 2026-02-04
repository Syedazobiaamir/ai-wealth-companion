---
title: AI Wealth Companion API
emoji: 💰
colorFrom: purple
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# AI Wealth Companion - Backend API

FastAPI backend for the AI Wealth Companion financial management platform.

## Features

- **AI Chatbot API** - Natural language financial assistant
- **Transaction Management** - Track income and expenses
- **Budget Tracking** - Create and monitor spending limits
- **Investment Simulation** - Project investment returns
- **Task Management** - Financial reminders and todos
- **Multi-language** - English and Urdu support

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/ai/chat` | POST | Chat with AI assistant |
| `/api/v1/transactions` | GET/POST | Manage transactions |
| `/api/v1/budgets` | GET/POST | Manage budgets |
| `/api/v1/tasks` | GET/POST | Manage tasks |
| `/api/v1/ai/insights` | GET | Get AI insights |
| `/api/v1/ai/health-score` | GET | Financial health score |
| `/health` | GET | Health check |

## Environment Variables

Set these in your Space secrets:

- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - JWT signing key
- `GEMINI_API_KEY` - Google Gemini API key
- `CORS_ORIGINS` - Allowed frontend URLs

## Tech Stack

- FastAPI
- SQLAlchemy (async)
- Neon PostgreSQL
- Google Gemini AI
- Pydantic v2

## Links

- [Frontend (Vercel)](https://ai-wealth-companion.vercel.app)
- [GitHub](https://github.com/Syedazobiaamir/ai-wealth-companion)
