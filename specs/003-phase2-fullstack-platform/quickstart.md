# Quickstart: Phase II Full-Stack Financial Platform

**Date**: 2026-01-19
**Branch**: `003-phase2-fullstack-platform`

## Prerequisites

- Python 3.11+
- Node.js 18+ (LTS)
- npm or yarn
- Git
- Neon PostgreSQL account (free tier available)

## Project Setup

### 1. Clone and Checkout Branch

```bash
git clone https://github.com/Syedazobiaamir/ai-wealth-companion.git
cd ai-wealth-companion
git checkout 003-phase2-fullstack-platform
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy environment template
cp .env.example .env

# Edit .env with your Neon PostgreSQL connection string
# DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
```

### 3. Database Setup

```bash
# Run migrations
alembic upgrade head

# Seed default categories (optional - done automatically on first run)
python -m src.db.seed
```

### 4. Frontend Setup

```bash
# Navigate to frontend directory (from repo root)
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local

# Edit .env.local with API URL
# NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs (Swagger UI)
- API Redoc: http://localhost:8000/redoc

### Running Tests

**Backend Tests:**
```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py -v
```

**Frontend Tests:**
```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

## Environment Variables

### Backend (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| DATABASE_URL | Neon PostgreSQL connection string | `postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require` |
| CORS_ORIGINS | Allowed CORS origins (comma-separated) | `http://localhost:3000` |
| RATE_LIMIT_PER_MINUTE | API rate limit | `100` |
| DEBUG | Enable debug mode | `true` |

### Frontend (.env.local)

| Variable | Description | Example |
|----------|-------------|---------|
| NEXT_PUBLIC_API_URL | Backend API base URL | `http://localhost:8000/api/v1` |

## Project Structure Overview

```
backend/
├── src/
│   ├── api/          # FastAPI routes
│   ├── models/       # SQLModel entities
│   ├── services/     # Business logic
│   ├── repositories/ # Data access
│   ├── db/           # Database config
│   └── core/         # Settings, exceptions
└── tests/            # Backend tests

frontend/
├── src/
│   ├── app/          # Next.js pages
│   ├── components/   # React components
│   ├── hooks/        # Custom hooks
│   ├── services/     # API clients
│   ├── types/        # TypeScript types
│   └── lib/          # Utilities
└── tests/            # Frontend tests
```

## Key Commands

| Task | Backend | Frontend |
|------|---------|----------|
| Start dev server | `uvicorn src.api.main:app --reload` | `npm run dev` |
| Run tests | `pytest` | `npm test` |
| Run linter | `ruff check src` | `npm run lint` |
| Format code | `ruff format src` | `npm run format` |
| Build for prod | N/A | `npm run build` |
| Type check | `mypy src` | `npm run type-check` |

## API Quick Reference

### Authentication (No Auth Required)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Register new user |
| `/api/v1/auth/login` | POST | Login and get tokens |
| `/api/v1/auth/refresh` | POST | Refresh access token |
| `/api/v1/auth/logout` | POST | Logout (requires auth) |
| `/api/v1/auth/me` | GET | Get current user (requires auth) |

### Transactions (Auth Required)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/transactions` | GET | List transactions (paginated) |
| `/api/v1/transactions` | POST | Create transaction |
| `/api/v1/transactions/{id}` | GET | Get single transaction |
| `/api/v1/transactions/{id}` | PUT | Update transaction |
| `/api/v1/transactions/{id}` | DELETE | Soft delete transaction |

### Categories (No Auth Required)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/categories` | GET | List all categories |
| `/api/v1/categories/{id}` | GET | Get category by ID |

### Budgets (Auth Required)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/budgets` | GET | List budgets for month |
| `/api/v1/budgets` | POST | Create/update budget |
| `/api/v1/budgets/status` | GET | Get budget status with spending |
| `/api/v1/budgets/alerts` | GET | Get exceeded/warning budgets |

### Wallets (Auth Required)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/wallets` | GET | List user wallets |
| `/api/v1/wallets` | POST | Create wallet |
| `/api/v1/wallets/{id}` | GET | Get wallet by ID |
| `/api/v1/wallets/{id}` | PUT | Update wallet |
| `/api/v1/wallets/{id}/set-default` | POST | Set as default wallet |

### Goals (Auth Required)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/goals` | GET | List user goals |
| `/api/v1/goals` | POST | Create goal |
| `/api/v1/goals/summary` | GET | Get goals summary |
| `/api/v1/goals/{id}/progress` | POST | Add progress to goal |
| `/api/v1/goals/{id}/complete` | POST | Mark goal as complete |

### Dashboard & Summary (Auth Required)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/summary/financial` | GET | Get financial summary |
| `/api/v1/summary/categories` | GET | Get category breakdown |
| `/api/v1/summary/trends` | GET | Get monthly trends |
| `/api/v1/dashboard/summary` | GET | Get dashboard data |
| `/api/v1/dashboard/charts/*` | GET | Get chart data |

### AI (Auth Required - Phase III Ready)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/ai/context` | GET | Get user context for AI |
| `/api/v1/ai/query` | POST | Execute AI query |
| `/api/v1/ai/insights` | GET | Get cached insights |

### Demo (Auth Required)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/demo/seed` | POST | Generate demo data |
| `/api/v1/demo/reset` | POST | Reset all user data |

## Troubleshooting

### Common Issues

**1. Database connection fails**
- Verify DATABASE_URL in .env
- Check Neon dashboard for connection string
- Ensure `?sslmode=require` is appended

**2. CORS errors in browser**
- Add frontend URL to CORS_ORIGINS in backend .env
- Restart backend server after changing .env

**3. Frontend can't reach API**
- Verify NEXT_PUBLIC_API_URL in .env.local
- Ensure backend is running on correct port
- Check browser console for actual error

**4. Migrations fail**
- Run `alembic downgrade base` then `alembic upgrade head`
- Check for syntax errors in migration files
- Verify database connection

## Next Steps

1. Run the backend tests to verify setup
2. Run the frontend tests to verify setup
3. Start both servers and access http://localhost:3000
4. Create your first transaction via the UI
5. Explore the API docs at http://localhost:8000/docs
