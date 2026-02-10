# AI Wealth & Spending Companion

A full-stack personal finance application for tracking income, expenses, budgets, and financial goals with AI-powered insights.

## Live Demo

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Phase II - Full-Stack Platform (Current)

Phase II transforms the CLI application into a modern full-stack web platform with a beautiful UI and robust API.

### Features

| Feature | Description |
|---------|-------------|
| **User Authentication** | Secure JWT-based login/signup with refresh tokens |
| **Multi-Wallet Support** | Track multiple accounts (cash, bank, cards) |
| **Transaction Management** | Full CRUD with filtering, sorting, pagination |
| **Budget Tracking** | Set and monitor spending limits per category |
| **Financial Goals** | Save towards targets with progress tracking |
| **Task Management** | Financial to-dos with due dates and priorities |
| **Dashboard Analytics** | Visual charts and spending insights |
| **AI Chatbot** | Intelligent financial assistant (widget) |
| **Dark/Light Theme** | Modern glassmorphism UI design |
| **Responsive Design** | Mobile-first, works on all devices |

### Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS, Framer Motion |
| **Backend** | FastAPI, SQLModel, Pydantic v2 |
| **Database** | PostgreSQL (Neon) / SQLite (local dev) |
| **Auth** | JWT + Argon2 password hashing |
| **Charts** | Recharts |
| **API Docs** | Swagger/OpenAPI auto-generated |

### Screenshots

```
┌─────────────────────────────────────────────────────────┐
│  Dashboard                                              │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │ Balance │ │ Income  │ │ Expense │ │ Savings │       │
│  │ $12,450 │ │ $5,200  │ │ $2,800  │ │ $2,400  │       │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │
│                                                         │
│  [Monthly Trend Chart]    [Spending by Category Pie]   │
│                                                         │
│  Recent Transactions      Budget Progress              │
│  ├─ Grocery    -$150     Food     ████████░░ 80%      │
│  ├─ Salary    +$3,000    Rent     ██████████ 100%     │
│  └─ Electric   -$85      Utils    ████░░░░░░ 40%      │
└─────────────────────────────────────────────────────────┘
```

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Syedazobiaamir/ai-wealth-companion.git
cd ai-wealth-companion

# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
cp .env.example .env      # Configure your settings
uvicorn src.main:app --reload --port 8000

# Frontend Setup (new terminal)
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### Project Structure

```
├── backend/
│   ├── src/
│   │   ├── api/           # REST API endpoints
│   │   │   ├── routes/    # Auth routes
│   │   │   └── v1/        # API v1 endpoints
│   │   ├── core/          # Config, security
│   │   ├── db/            # Database session
│   │   ├── models/        # SQLModel entities
│   │   ├── repositories/  # Data access layer
│   │   └── services/      # Business logic
│   ├── tests/             # API tests
│   └── alembic/           # DB migrations
│
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js App Router pages
│   │   │   ├── (app)/     # Protected routes (dashboard, etc.)
│   │   │   └── (auth)/    # Auth routes (login, signup)
│   │   ├── components/    # React components
│   │   │   ├── ui/        # Base UI components
│   │   │   ├── charts/    # Recharts visualizations
│   │   │   ├── layout/    # Header, Sidebar, Nav
│   │   │   └── chatbot/   # AI chat widget
│   │   ├── contexts/      # React contexts (auth)
│   │   ├── hooks/         # Custom hooks
│   │   └── types/         # TypeScript types
│   └── __tests__/         # Component tests
│
├── specs/                 # Feature specifications
├── history/               # Prompt history records
└── docker-compose.yml     # Container orchestration
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Create new account |
| POST | `/api/v1/auth/login` | Login & get tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/wallets` | List user wallets |
| POST | `/api/v1/wallets` | Create wallet |
| GET | `/api/v1/transactions` | List transactions |
| POST | `/api/v1/transactions` | Create transaction |
| GET | `/api/v1/budgets` | List budgets |
| GET | `/api/v1/goals` | List savings goals |
| GET | `/api/v1/dashboard/summary` | Dashboard stats |

### Environment Variables

**Backend (.env)**
```env
DATABASE_URL=sqlite+aiosqlite:///./dev.db
JWT_SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:3000
```

**Frontend (.env.local)**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## Phase I - CLI Financial Core

Phase I established the foundation with a Python CLI application featuring in-memory storage, clean architecture, and comprehensive test coverage.

### CLI Features

| Feature | Description |
|---------|-------------|
| **Transaction Management** | Add, edit, delete income/expense transactions |
| **Category Support** | 5 default categories with emojis |
| **Budget Tracking** | Set monthly spending limits per category |
| **Budget Alerts** | Warnings at 80% and 100% thresholds |
| **Filter & Search** | Filter by category, date range, amount |

### Run CLI (Phase I)

```bash
python -m src
```

---

## Architecture

### Phase II Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                   │
│         React + TypeScript + Tailwind CSS               │
├─────────────────────────────────────────────────────────┤
│                        REST API                         │
├─────────────────────────────────────────────────────────┤
│                   Backend (FastAPI)                     │
│    ┌─────────────┬─────────────┬─────────────┐         │
│    │   Routes    │  Services   │   Repos     │         │
│    └─────────────┴─────────────┴─────────────┘         │
├─────────────────────────────────────────────────────────┤
│              Database (PostgreSQL/SQLite)               │
└─────────────────────────────────────────────────────────┘
```

### Design Principles

- **Repository Pattern**: Swappable storage backends
- **Service Layer**: Business logic separated from API
- **JWT Authentication**: Secure, stateless auth
- **Result Type**: Explicit error handling
- **Type Safety**: Full TypeScript + Pydantic validation

---

## Phase IV - Local Kubernetes Deployment

Deploy the application to a local Kubernetes cluster using Minikube, Helm, and AI-powered operations.

### Features

| Feature | Description |
|---------|-------------|
| **Minikube Cluster** | Local Kubernetes with ingress support |
| **Helm 3.x Charts** | Production-ready deployment templates |
| **kubectl-ai** | Natural language cluster operations |
| **kagent** | AI workload governance and scaling |
| **HPA Autoscaling** | CPU/memory-based pod scaling |
| **Secret Management** | Kubernetes Secrets for credentials |
| **Health Probes** | Liveness/readiness for self-healing |

### Quick Start (Kubernetes)

```bash
# 1. Setup Minikube cluster
./scripts/k8s-setup.sh

# 2. Create secrets
./scripts/k8s-secrets.sh --all

# 3. Build and deploy (local Minikube)
./scripts/k8s-deploy.sh --build

# 4. Add hosts entry
echo "$(minikube ip) ai-wealth.local" | sudo tee -a /etc/hosts

# 5. Access the app
open http://ai-wealth.local
```

### Docker Hub Deployment

```bash
# 1. Push images to Docker Hub
DOCKER_USERNAME=yourusername ./scripts/k8s-deploy.sh --dockerhub

# 2. Update values with your username
cp helm/ai-wealth-companion/values-dockerhub.yaml helm/ai-wealth-companion/values-custom.yaml
# Edit values-custom.yaml and replace YOUR_DOCKER_USERNAME

# 3. Deploy with Docker Hub images
helm install ai-wealth ./helm/ai-wealth-companion \
  -n ai-wealth \
  -f helm/ai-wealth-companion/values-custom.yaml
```

### kubectl-ai Commands

```bash
# Natural language cluster operations
kubectl-ai "show me all pods in ai-wealth namespace"
kubectl-ai "why is the backend pod failing?"
kubectl-ai "scale frontend to 3 replicas"
kubectl-ai "get logs from backend pod"
```

### Project Structure (Phase IV)

```
├── helm/ai-wealth-companion/
│   ├── Chart.yaml              # Helm chart metadata
│   ├── values.yaml             # Default configuration
│   ├── values-dev.yaml         # Development overrides
│   ├── values-dockerhub.yaml   # Docker Hub template
│   └── templates/
│       ├── backend-deployment.yaml
│       ├── frontend-deployment.yaml
│       ├── ingress.yaml
│       ├── hpa.yaml
│       └── ...
│
├── scripts/
│   ├── k8s-setup.sh            # Minikube setup
│   ├── k8s-deploy.sh           # Helm deployment
│   ├── k8s-secrets.sh          # Secret creation
│   └── k8s-teardown.sh         # Cleanup
```

---

## Project Phases

| Phase | Description | Status |
|-------|-------------|--------|
| Phase I | CLI Financial Core | ✅ Complete |
| Phase II | Full-Stack Platform | ✅ Complete |
| Phase III | AI Chatbot + Gemini Integration | ✅ Complete |
| Phase IV | Local Kubernetes Deployment | ✅ Complete |
| Phase V | Cloud Production (DigitalOcean) | 🔜 Planned |

---

## Development

### Run Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

### Docker Development

```bash
docker-compose -f docker-compose.dev.yml up
```

---

## License

MIT License

## Author

Built with Spec-Driven Development using Claude Code.
