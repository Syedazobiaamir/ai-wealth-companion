# Tasks: Phase II Full-Stack Financial Platform

**Input**: Design documents from `/specs/003-phase2-fullstack-platform/`
**Prerequisites**: plan.md, spec.md, 02-database.md, 03-api.md, 12-uiux.md
**Branch**: `003-phase2-fullstack-platform`
**Generated**: 2026-01-25

## Format: `[ID] [P?] [Category] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Category]**: DB, Auth, Backend, Dashboard, UI, Security, AI, Testing
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/` (Python/FastAPI)
- **Frontend**: `frontend/src/` (Next.js 14/TypeScript)
- **Tests**: `backend/tests/`, `frontend/tests/`

---

## Phase 1: Setup (Project Infrastructure)

**Purpose**: Initialize projects and configure development environment

- [ ] T001 Create project directory structure per plan.md (`backend/`, `frontend/`)
- [ ] T002 [P] Initialize Python backend with FastAPI in `backend/pyproject.toml`
- [ ] T003 [P] Initialize Next.js 14 frontend with TypeScript in `frontend/package.json`
- [ ] T004 [P] Configure backend linting (ruff, black) in `backend/pyproject.toml`
- [ ] T005 [P] Configure frontend linting (ESLint, Prettier) in `frontend/.eslintrc.js`
- [ ] T006 [P] Create `backend/.env.example` with Neon PostgreSQL connection template
- [ ] T007 [P] Create `frontend/.env.example` with API URL template
- [ ] T008 Create `docker-compose.yml` for local development environment
- [ ] T009 [P] Configure Tailwind CSS with design tokens in `frontend/tailwind.config.js`

**Checkpoint**: Both projects initialized, ready for implementation

---

## Phase 2: DB - Database Schema

**Purpose**: Establish Neon PostgreSQL database with all entities from 02-database.md

**Goal**: Complete database layer with 10 entities, indexes, and migrations

**Independent Test**: `alembic upgrade head` runs without errors; seed data populates

### Models

- [ ] T010 [P] [DB] Create SQLModel base configuration in `backend/src/db/database.py`
- [ ] T011 [P] [DB] Configure Alembic migrations in `backend/alembic.ini` and `backend/src/db/migrations/`
- [ ] T012 [P] [DB] Implement User model in `backend/src/models/user.py`
- [ ] T013 [P] [DB] Implement Wallet model in `backend/src/models/wallet.py`
- [ ] T014 [P] [DB] Implement Category model in `backend/src/models/category.py`
- [ ] T015 [P] [DB] Implement Transaction model in `backend/src/models/transaction.py`
- [ ] T016 [P] [DB] Implement Budget model in `backend/src/models/budget.py`
- [ ] T017 [P] [DB] Implement Goal model in `backend/src/models/goal.py`
- [ ] T018 [P] [DB] Implement MonthlySnapshot model in `backend/src/models/monthly_snapshot.py`
- [ ] T019 [P] [DB] Implement InsightCache model in `backend/src/models/insight_cache.py`
- [ ] T020 [P] [DB] Implement AgentMemory model in `backend/src/models/agent_memory.py`
- [ ] T021 [P] [DB] Implement EventLog model in `backend/src/models/event_log.py`

### Migrations & Seeds

- [ ] T022 [DB] Create initial migration with all tables in `backend/src/db/migrations/versions/001_initial_schema.py`
- [ ] T023 [DB] Add database indexes per 02-database.md in migration file
- [ ] T024 [DB] Create seed script for system categories with Urdu translations in `backend/src/db/seed.py`
- [ ] T025 [DB] Test migration with Neon PostgreSQL connection

**Checkpoint**: Database schema complete, migrations applied, categories seeded

---

## Phase 3: Auth - JWT Authentication Bridge

**Purpose**: Implement JWT-based authentication per Security Laws

**Goal**: Secure authentication with access/refresh tokens, rate limiting

**Independent Test**: Register -> Login -> Access protected route -> Refresh -> Logout flow works

### Core Security

- [ ] T026 [P] [Auth] Implement password hashing with argon2 in `backend/src/core/security.py`
- [ ] T027 [P] [Auth] Implement JWT token generation (access + refresh) in `backend/src/core/security.py`
- [ ] T028 [P] [Auth] Configure JWT settings (1hr access, 7-day refresh) in `backend/src/core/config.py`
- [ ] T029 [Auth] Create auth service with token management in `backend/src/services/auth_service.py`

### Auth Endpoints

- [ ] T030 [Auth] Implement POST /auth/register in `backend/src/api/routes/auth.py`
- [ ] T031 [Auth] Implement POST /auth/login in `backend/src/api/routes/auth.py`
- [ ] T032 [Auth] Implement POST /auth/refresh with httpOnly cookie in `backend/src/api/routes/auth.py`
- [ ] T033 [Auth] Implement POST /auth/logout in `backend/src/api/routes/auth.py`
- [ ] T034 [Auth] Implement GET /auth/me in `backend/src/api/routes/auth.py`

### Auth Middleware

- [ ] T035 [Auth] Create JWT validation dependency in `backend/src/api/dependencies.py`
- [ ] T036 [Auth] Implement get_current_user dependency in `backend/src/api/dependencies.py`
- [ ] T037 [Auth] Configure httpOnly cookies for refresh tokens in auth routes
- [ ] T038 [Auth] Add rate limiting (5/minute) to auth endpoints in `backend/src/api/middleware.py`

**Checkpoint**: Authentication flow complete, tokens work, rate limiting active

---

## Phase 4: Backend - Core API Endpoints

**Purpose**: Build all REST endpoints from 03-api.md

**Goal**: Complete CRUD operations with event emission

**Independent Test**: All endpoints return correct JSON per API spec

### Repositories

- [ ] T039 [P] [Backend] Create base repository pattern in `backend/src/repositories/base.py`
- [ ] T040 [P] [Backend] Implement UserRepository in `backend/src/repositories/user_repository.py`
- [ ] T041 [P] [Backend] Implement TransactionRepository in `backend/src/repositories/transaction_repository.py`
- [ ] T042 [P] [Backend] Implement CategoryRepository in `backend/src/repositories/category_repository.py`
- [ ] T043 [P] [Backend] Implement BudgetRepository in `backend/src/repositories/budget_repository.py`
- [ ] T044 [P] [Backend] Implement WalletRepository in `backend/src/repositories/wallet_repository.py`
- [ ] T045 [P] [Backend] Implement GoalRepository in `backend/src/repositories/goal_repository.py`

### Services

- [ ] T046 [P] [Backend] Implement TransactionService in `backend/src/services/transaction_service.py`
- [ ] T047 [P] [Backend] Implement BudgetService in `backend/src/services/budget_service.py`
- [ ] T048 [P] [Backend] Implement WalletService in `backend/src/services/wallet_service.py`
- [ ] T049 [P] [Backend] Implement GoalService in `backend/src/services/goal_service.py`
- [ ] T050 [P] [Backend] Implement EventService for event emission in `backend/src/services/event_service.py`

### Response Schemas

- [ ] T051 [P] [Backend] Create Pydantic response schemas in `backend/src/models/schemas.py`
- [ ] T052 [P] [Backend] Create error response schema in `backend/src/core/exceptions.py`
- [ ] T053 [Backend] Create pagination schema in `backend/src/models/schemas.py`

### Transaction Endpoints

- [ ] T054 [Backend] Implement GET /transactions with pagination in `backend/src/api/routes/transactions.py`
- [ ] T055 [Backend] Implement POST /transactions in `backend/src/api/routes/transactions.py`
- [ ] T056 [Backend] Implement GET /transactions/{id} in `backend/src/api/routes/transactions.py`
- [ ] T057 [Backend] Implement PUT /transactions/{id} in `backend/src/api/routes/transactions.py`
- [ ] T058 [Backend] Implement DELETE /transactions/{id} (soft delete) in `backend/src/api/routes/transactions.py`
- [ ] T059 [Backend] Implement POST /transactions/batch for AI optimization in `backend/src/api/routes/transactions.py`

### Category Endpoints

- [ ] T060 [Backend] Implement GET /categories in `backend/src/api/routes/categories.py`
- [ ] T061 [Backend] Implement POST /categories (custom) in `backend/src/api/routes/categories.py`

### Budget Endpoints

- [ ] T062 [Backend] Implement GET /budgets with status in `backend/src/api/routes/budgets.py`
- [ ] T063 [Backend] Implement POST /budgets in `backend/src/api/routes/budgets.py`
- [ ] T064 [Backend] Implement GET /budgets/{category_id} in `backend/src/api/routes/budgets.py`
- [ ] T065 [Backend] Implement PUT /budgets/{id} in `backend/src/api/routes/budgets.py`

### Wallet Endpoints

- [ ] T066 [Backend] Implement GET /wallets in `backend/src/api/routes/wallets.py`
- [ ] T067 [Backend] Implement POST /wallets in `backend/src/api/routes/wallets.py`
- [ ] T068 [Backend] Implement PUT /wallets/{id} in `backend/src/api/routes/wallets.py`

### Goal Endpoints

- [ ] T069 [Backend] Implement GET /goals in `backend/src/api/routes/goals.py`
- [ ] T070 [Backend] Implement POST /goals in `backend/src/api/routes/goals.py`
- [ ] T071 [Backend] Implement PUT /goals/{id} in `backend/src/api/routes/goals.py`

### App Entry

- [ ] T072 [Backend] Create FastAPI app with all routes in `backend/src/main.py`
- [ ] T073 [Backend] Register all routers in main app
- [ ] T074 [Backend] Add events_emitted to mutation responses

**Checkpoint**: All CRUD endpoints functional, event emission working

---

## Phase 5: Dashboard - Aggregation APIs

**Purpose**: Implement dashboard data aggregation endpoints

**Goal**: Fast, cached dashboard data for charts and summaries

**Independent Test**: Dashboard summary returns accurate totals matching transaction sum

### Dashboard Service

- [ ] T075 [Dashboard] Implement DashboardService in `backend/src/services/dashboard_service.py`
- [ ] T076 [Dashboard] Add income/expense aggregation logic
- [ ] T077 [Dashboard] Add month-over-month comparison calculations
- [ ] T078 [Dashboard] Implement caching strategy for aggregations

### Dashboard Endpoints

- [ ] T079 [Dashboard] Implement GET /dashboard/summary in `backend/src/api/routes/dashboard.py`
- [ ] T080 [Dashboard] Implement GET /dashboard/charts/spending-by-category in `backend/src/api/routes/dashboard.py`
- [ ] T081 [Dashboard] Implement GET /dashboard/charts/spending-trend in `backend/src/api/routes/dashboard.py`
- [ ] T082 [Dashboard] Implement GET /dashboard/charts/budget-progress in `backend/src/api/routes/dashboard.py`
- [ ] T083 [Dashboard] Add period filtering (week, month, year, custom) to all endpoints

**Checkpoint**: Dashboard APIs return accurate chart data

---

## Phase 6: UI - Frontend Foundation

**Purpose**: Build Next.js frontend consuming backend APIs

**Goal**: Complete dashboard UI with auth, navigation, and data display

**Independent Test**: User can login, view dashboard, add transaction

### Core Setup

- [ ] T084 [P] [UI] Create root layout with providers in `frontend/src/app/layout.tsx`
- [ ] T085 [P] [UI] Configure API client with SWR in `frontend/src/services/api.ts`
- [ ] T086 [P] [UI] Implement auth service in `frontend/src/services/auth.ts`
- [ ] T087 [P] [UI] Create useAuth hook in `frontend/src/hooks/useAuth.ts`
- [ ] T088 [P] [UI] Create useTheme hook in `frontend/src/hooks/useTheme.ts`

### TypeScript Types

- [ ] T089 [P] [UI] Define API types in `frontend/src/types/api.ts`
- [ ] T090 [P] [UI] Define transaction types in `frontend/src/types/transaction.ts`
- [ ] T091 [P] [UI] Define budget types in `frontend/src/types/budget.ts`
- [ ] T092 [P] [UI] Define user types in `frontend/src/types/user.ts`

### Base UI Components

- [ ] T093 [P] [UI] Create Button component with variants in `frontend/src/components/ui/Button.tsx`
- [ ] T094 [P] [UI] Create Card component with glassmorphism in `frontend/src/components/ui/Card.tsx`
- [ ] T095 [P] [UI] Create Input component in `frontend/src/components/ui/Input.tsx`
- [ ] T096 [P] [UI] Create Modal component in `frontend/src/components/ui/Modal.tsx`
- [ ] T097 [P] [UI] Create loading spinner in `frontend/src/components/ui/Spinner.tsx`
- [ ] T098 [P] [UI] Create toast/notification component in `frontend/src/components/ui/Toast.tsx`

### Auth Pages

- [ ] T099 [UI] Create login page in `frontend/src/app/(auth)/login/page.tsx`
- [ ] T100 [UI] Create register page in `frontend/src/app/(auth)/register/page.tsx`
- [ ] T101 [UI] Implement auth guard HOC in `frontend/src/components/AuthGuard.tsx`

### Layout Components

- [ ] T102 [P] [UI] Create Navbar in `frontend/src/components/layout/Navbar.tsx`
- [ ] T103 [P] [UI] Create Sidebar with navigation in `frontend/src/components/layout/Sidebar.tsx`
- [ ] T104 [UI] Create dashboard layout in `frontend/src/app/dashboard/layout.tsx`

### Dashboard Page

- [ ] T105 [UI] Create main dashboard page in `frontend/src/app/dashboard/page.tsx`
- [ ] T106 [P] [UI] Create BalanceCard component in `frontend/src/components/dashboard/BalanceCard.tsx`
- [ ] T107 [P] [UI] Create BudgetMeter component in `frontend/src/components/dashboard/BudgetMeter.tsx`
- [ ] T108 [P] [UI] Create RecentTransactions component in `frontend/src/components/dashboard/RecentTransactions.tsx`
- [ ] T109 [P] [UI] Create InsightsCard component in `frontend/src/components/dashboard/InsightsCard.tsx`

### Transactions Page

- [ ] T110 [UI] Create transactions page in `frontend/src/app/dashboard/transactions/page.tsx`
- [ ] T111 [UI] Create TransactionList component in `frontend/src/components/transactions/TransactionList.tsx`
- [ ] T112 [UI] Create TransactionForm component in `frontend/src/components/transactions/TransactionForm.tsx`
- [ ] T113 [UI] Create TransactionFilters component in `frontend/src/components/transactions/TransactionFilters.tsx`
- [ ] T114 [UI] Implement useTransactions hook in `frontend/src/hooks/useTransactions.ts`

### Budgets Page

- [ ] T115 [UI] Create budgets page in `frontend/src/app/dashboard/budgets/page.tsx`
- [ ] T116 [UI] Implement useBudgets hook in `frontend/src/hooks/useBudgets.ts`
- [ ] T117 [UI] Create budget creation/edit form

### Analytics Page

- [ ] T118 [UI] Create analytics page in `frontend/src/app/dashboard/analytics/page.tsx`

### Settings Page

- [ ] T119 [UI] Create settings page in `frontend/src/app/dashboard/settings/page.tsx`
- [ ] T120 [UI] Implement theme toggle functionality

### State & Data

- [ ] T121 [UI] Implement loading states for all data-fetching components
- [ ] T122 [UI] Implement error states with retry functionality
- [ ] T123 [UI] Add refetch after mutations (optimistic updates)

**Checkpoint**: Complete frontend with auth, dashboard, and CRUD pages

---

## Phase 7: UI - Charts Integration

**Purpose**: Implement interactive charts with Recharts

**Goal**: Beautiful, animated charts with glassmorphism design

**Independent Test**: Charts render correct data from API

### Chart Components

- [ ] T124 [P] [UI] Create SpendingPieChart in `frontend/src/components/charts/SpendingPieChart.tsx`
- [ ] T125 [P] [UI] Create TrendLineChart in `frontend/src/components/charts/TrendLineChart.tsx`
- [ ] T126 [P] [UI] Create BudgetRadialChart in `frontend/src/components/charts/BudgetRadialChart.tsx`
- [ ] T127 [P] [UI] Create CategoryBarChart in `frontend/src/components/charts/CategoryBarChart.tsx`

### Chart Styling

- [ ] T128 [UI] Implement glassmorphism tooltips for charts
- [ ] T129 [UI] Add chart animations (300ms duration per 12-uiux.md)
- [ ] T130 [UI] Create empty state for no-data charts
- [ ] T131 [UI] Implement lazy loading for chart components

### Chart Integration

- [ ] T132 [UI] Integrate charts into dashboard page
- [ ] T133 [UI] Integrate charts into analytics page

**Checkpoint**: All charts render with correct data and animations

---

## Phase 8: Backend - Demo Data

**Purpose**: Create demo mode for hackathon presentations

**Goal**: One-click demo with 50 realistic transactions

**Independent Test**: POST /demo/reset creates complete demo data

### Demo Data

- [ ] T134 [Backend] Create seed_demo_data.py script in `backend/src/db/seed_demo.py`
- [ ] T135 [Backend] Generate 50 realistic transactions over 3 months
- [ ] T136 [Backend] Create budgets with varied statuses (normal, warning, exceeded)
- [ ] T137 [Backend] Create demo user account (demo@example.com)
- [ ] T138 [Backend] Create demo wallets (Cash, Bank, Savings)

### Demo Endpoints

- [ ] T139 [Backend] Implement POST /api/v1/demo/reset in `backend/src/api/routes/demo.py`
- [ ] T140 [Backend] Implement GET /api/v1/demo/status in `backend/src/api/routes/demo.py`

### Demo UI

- [ ] T141 [UI] Add demo mode banner to dashboard in `frontend/src/components/DemoBanner.tsx`
- [ ] T142 [UI] Add demo login shortcut on login page
- [ ] T143 [UI] Show reset demo data button in settings

**Checkpoint**: Demo mode fully functional with realistic data

---

## Phase 9: AI - AI-Ready Hooks

**Purpose**: Implement AI-ready APIs and chatbot shell

**Goal**: Prepared for Phase III AI agent integration

**Independent Test**: GET /ai/context returns complete user financial context

### AI Endpoints

- [ ] T144 [AI] Implement GET /ai/context in `backend/src/api/routes/ai.py`
- [ ] T145 [AI] Implement POST /ai/query (stub) in `backend/src/api/routes/ai.py`
- [ ] T146 [AI] Implement POST /ai/insights/generate (stub) in `backend/src/api/routes/ai.py`
- [ ] T147 [AI] Add machine-readable response format for AI consumption

### Chatbot Shell

- [ ] T148 [AI] Create ChatbotShell component in `frontend/src/components/chatbot/ChatbotShell.tsx`
- [ ] T149 [AI] Implement expand/collapse animation for chatbot
- [ ] T150 [AI] Add placeholder "AI coming soon" state
- [ ] T151 [AI] Position chatbot FAB in bottom-right corner

### AI Infrastructure

- [ ] T152 [AI] Document AI integration points in `specs/003-phase2-fullstack-platform/ai-integration.md`
- [ ] T153 [AI] Prepare AgentMemory table queries for Phase III

**Checkpoint**: AI endpoints ready, chatbot shell visible

---

## Phase 10: Security - Hardening

**Purpose**: Implement security middleware and hardening

**Goal**: Production-ready security per constitution Security Laws

**Independent Test**: Security headers present, rate limiting works

### Middleware

- [ ] T154 [P] [Security] Implement CORS middleware in `backend/src/api/middleware.py`
- [ ] T155 [P] [Security] Implement rate limiting middleware in `backend/src/api/middleware.py`
- [ ] T156 [P] [Security] Add security headers middleware in `backend/src/api/middleware.py`

### Rate Limits (per 03-api.md)

- [ ] T157 [Security] Configure auth rate limit: 5 req/min
- [ ] T158 [Security] Configure write rate limit: 30 req/min
- [ ] T159 [Security] Configure read rate limit: 100 req/min
- [ ] T160 [Security] Configure AI rate limit: 10 req/min

### Security Headers

- [ ] T161 [Security] Add X-Content-Type-Options: nosniff
- [ ] T162 [Security] Add X-Frame-Options: DENY
- [ ] T163 [Security] Add Strict-Transport-Security header
- [ ] T164 [Security] Configure Content-Security-Policy

### Input Validation

- [ ] T165 [Security] Validate all user inputs with Pydantic
- [ ] T166 [Security] Sanitize search queries to prevent injection
- [ ] T167 [Security] Validate UUID parameters

**Checkpoint**: All security measures in place

---

## Phase 11: Testing

**Purpose**: Comprehensive test coverage

**Goal**: Confident deployment with automated tests

**Independent Test**: All tests pass in CI

### Backend Unit Tests

- [ ] T168 [P] [Testing] Create test configuration in `backend/tests/conftest.py`
- [ ] T169 [P] [Testing] Write unit tests for User model in `backend/tests/unit/test_user_model.py`
- [ ] T170 [P] [Testing] Write unit tests for Transaction model in `backend/tests/unit/test_transaction_model.py`
- [ ] T171 [P] [Testing] Write unit tests for auth_service in `backend/tests/unit/test_auth_service.py`
- [ ] T172 [P] [Testing] Write unit tests for transaction_service in `backend/tests/unit/test_transaction_service.py`
- [ ] T173 [P] [Testing] Write unit tests for dashboard_service in `backend/tests/unit/test_dashboard_service.py`

### Backend Integration Tests

- [ ] T174 [Testing] Write auth flow integration test in `backend/tests/integration/test_auth_flow.py`
- [ ] T175 [Testing] Write transaction CRUD integration test in `backend/tests/integration/test_transactions.py`
- [ ] T176 [Testing] Write budget management integration test in `backend/tests/integration/test_budgets.py`
- [ ] T177 [Testing] Write dashboard aggregation integration test in `backend/tests/integration/test_dashboard.py`

### Backend Contract Tests

- [ ] T178 [P] [Testing] Write contract test for auth endpoints in `backend/tests/contract/test_auth_contract.py`
- [ ] T179 [P] [Testing] Write contract test for transactions in `backend/tests/contract/test_transactions_contract.py`
- [ ] T180 [P] [Testing] Write contract test for dashboard in `backend/tests/contract/test_dashboard_contract.py`

### Frontend Tests

- [ ] T181 [P] [Testing] Configure Jest in `frontend/jest.config.js`
- [ ] T182 [P] [Testing] Write component test for Button in `frontend/tests/components/Button.test.tsx`
- [ ] T183 [P] [Testing] Write component test for Card in `frontend/tests/components/Card.test.tsx`
- [ ] T184 [P] [Testing] Write hook test for useAuth in `frontend/tests/hooks/useAuth.test.ts`
- [ ] T185 [Testing] Write integration test for login flow in `frontend/tests/integration/login.test.tsx`
- [ ] T186 [Testing] Write integration test for dashboard in `frontend/tests/integration/dashboard.test.tsx`

**Checkpoint**: Test suite passes, coverage meets threshold

---

## Phase 12: Polish & Cross-Cutting

**Purpose**: Final improvements across all categories

- [ ] T187 [P] Add API documentation with OpenAPI in `backend/src/main.py`
- [ ] T188 [P] Create quickstart validation script in `scripts/validate-quickstart.sh`
- [ ] T189 Performance optimization: Add database query caching
- [ ] T190 Performance optimization: Lazy load frontend routes
- [ ] T191 [P] Add structured logging in `backend/src/core/logging.py`
- [ ] T192 Create Dockerfile for backend in `backend/Dockerfile`
- [ ] T193 Create Dockerfile for frontend in `frontend/Dockerfile`
- [ ] T194 Update docker-compose.yml with production config
- [ ] T195 Final accessibility audit per WCAG 2.1 AA
- [ ] T196 Mobile responsiveness final check

**Checkpoint**: Production-ready deployment

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ─────────────────────────────────────────────────────►
                │
Phase 2 (DB) ◄──┘
                │
Phase 3 (Auth) ◄┘
                │
                ├──► Phase 4 (Backend) ──► Phase 5 (Dashboard)
                │
                ├──► Phase 6 (UI) ──► Phase 7 (Charts)
                │
                ├──► Phase 8 (Demo Data)
                │
                └──► Phase 9 (AI)

Phase 10 (Security) ◄── Can start after Phase 3
Phase 11 (Testing) ◄── Can start after Phase 4
Phase 12 (Polish) ◄── After all phases complete
```

### Critical Path

1. **Setup** -> **DB** -> **Auth** (BLOCKING - must complete first)
2. Backend APIs can start after Auth
3. UI can start after Auth (can mock API initially)
4. Security can run parallel with Backend/UI
5. Testing runs throughout

### Parallel Opportunities

**After Phase 3 (Auth) completes:**
- Backend APIs (Phase 4) and UI (Phase 6) can run in parallel
- Security (Phase 10) can start
- Demo Data (Phase 8) can start after basic APIs

**Within Each Phase:**
- All tasks marked [P] can run in parallel
- Models can be created in parallel
- Services can be created in parallel (after models)
- Endpoints can be created in parallel (after services)

---

## Task Summary

| Category | Task Count | Priority |
|----------|------------|----------|
| Setup | 9 | P1 (Blocking) |
| DB | 16 | P1 (Blocking) |
| Auth | 13 | P1 (Blocking) |
| Backend | 36 | P1 |
| Dashboard | 9 | P1 |
| UI | 50 | P1 |
| AI | 10 | P2 |
| Security | 14 | P1 |
| Testing | 19 | P2 |
| Polish | 10 | P3 |

**Total Tasks: 196**

---

## Implementation Strategy

### MVP First (Hackathon Demo)

1. Complete Setup + DB + Auth (Phases 1-3)
2. Complete core Backend APIs (Phase 4: Transactions, Categories, Budgets)
3. Complete Dashboard API (Phase 5)
4. Complete core UI (Phase 6: Auth, Dashboard, Transactions)
5. Add Demo Data (Phase 8)
6. **STOP and DEMO** - Basic functionality complete

### Full Implementation

Continue with:
- Charts (Phase 7)
- AI Hooks (Phase 9)
- Security hardening (Phase 10)
- Full test coverage (Phase 11)
- Polish (Phase 12)

---

## Notes

- [P] tasks = different files, no dependencies
- [Category] label maps to the 8 requested categories
- Commit after each task or logical group
- All data from Neon PostgreSQL (no hardcoded data)
- Backend first rule: API before UI
- Event emission on all mutations
- JWT tokens for all authenticated endpoints
