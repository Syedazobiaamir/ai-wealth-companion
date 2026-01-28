# SpecKit Plus Configuration

This directory contains AI-native SDLC configuration for the AI Wealth Companion project.

---

## Subagents

Specialized AI agents for different domains:

| Subagent | File | Purpose |
|----------|------|---------|
| **UI-ARCHITECT** | `subagents/ui-architect.md` | UI/UX design and frontend implementation |
| **QA-ENGINEER** | `subagents/qa-engineer.md` | Quality assurance and testing |

### Invoking Subagents

```
You are UI-ARCHITECT. [Your task here]
```

```
You are QA-ENGINEER. [Your task here]
```

---

## Skills

Executable commands for common tasks:

| Skill | Trigger | Description |
|-------|---------|-------------|
| `qa.test-backend` | `/qa.test-backend` | Run backend tests with coverage |
| `qa.test-frontend` | `/qa.test-frontend` | Run frontend tests (unit + E2E) |
| `qa.test-api` | `/qa.test-api` | Test API endpoints |
| `qa.audit` | `/qa.audit` | Full QA audit |

---

## Documentation

| Document | Path | Description |
|----------|------|-------------|
| Database Config | `docs/database-config.md` | Database setup and configuration |

---

## Directory Structure

```
.specify/
├── README.md           # This file
├── memory/
│   └── constitution.md # Project principles
├── templates/
│   └── phr-template.prompt.md
├── subagents/
│   ├── ui-architect.md # UI/UX subagent
│   └── qa-engineer.md  # QA subagent
├── skills/
│   ├── qa.test-backend.md
│   ├── qa.test-frontend.md
│   ├── qa.test-api.md
│   └── qa.audit.md
└── docs/
    └── database-config.md
```

---

## Quick Reference

### Database Location
```
backend/.env → DATABASE_URL
```

### Current Config (SQLite)
```bash
DATABASE_URL=sqlite+aiosqlite:///./finance.db
```

### Production Config (Neon PostgreSQL)
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host/db?sslmode=require
```

---

## Running Tests

### Backend
```bash
cd backend
source venv/bin/activate
pytest --cov=src
```

### Frontend
```bash
cd frontend
npm test
npx playwright test
```
