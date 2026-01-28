# Database Specification: Phase II Data Model

**Feature Branch**: `003-phase2-fullstack-platform`
**Created**: 2026-01-25
**Status**: Active
**Database**: Neon PostgreSQL (serverless)
**Input**: User, Wallet, Transaction, Budget, Goal, Category, Monthly snapshot, Insight cache, Agent memory, Event log

## Overview

This specification defines the complete data model for the AI Wealth & Spending Companion Phase II platform. All entities are designed with Phase III AI integration in mind, supporting event-driven architecture and AI agent data access patterns.

### Design Principles

1. **Backend is Single Source of Truth**: All data originates from and persists to Neon PostgreSQL
2. **UUID Primary Keys**: All entities use UUIDs for distributed-friendly identification
3. **Soft Delete Support**: Critical entities support soft deletion for recovery
4. **Audit Trail**: All entities track creation and modification timestamps
5. **AI-Ready**: Entities include fields for AI agent context and memory

## Entity Definitions

### 1. User

Represents an authenticated user of the platform.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email for authentication |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt/Argon2 hashed password |
| display_name | VARCHAR(100) | NULL | User's preferred display name |
| preferred_currency | VARCHAR(3) | DEFAULT 'PKR' | ISO currency code |
| preferred_locale | VARCHAR(10) | DEFAULT 'en' | Language/locale preference |
| theme_preference | VARCHAR(10) | DEFAULT 'system' | 'light', 'dark', or 'system' |
| timezone | VARCHAR(50) | DEFAULT 'UTC' | User's timezone |
| is_active | BOOLEAN | DEFAULT TRUE | Account active status |
| is_demo_user | BOOLEAN | DEFAULT FALSE | Demo account flag |
| created_at | TIMESTAMP | NOT NULL | Account creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update time |
| last_login_at | TIMESTAMP | NULL | Last successful login |

**Indexes**:
- `idx_user_email` on `email` (for authentication lookups)
- `idx_user_active` on `is_active` (for active user queries)

**Relationships**:
- One-to-many with Wallet
- One-to-many with Transaction
- One-to-many with Budget
- One-to-many with Goal
- One-to-many with AgentMemory

---

### 2. Wallet

Represents a financial account or wallet belonging to a user.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique wallet identifier |
| user_id | UUID | FOREIGN KEY (User), NOT NULL | Owner of the wallet |
| name | VARCHAR(100) | NOT NULL | Wallet display name |
| type | VARCHAR(20) | NOT NULL | 'cash', 'bank', 'credit', 'savings', 'investment' |
| currency | VARCHAR(3) | DEFAULT 'PKR' | Wallet currency |
| initial_balance | DECIMAL(15,2) | DEFAULT 0.00 | Starting balance |
| current_balance | DECIMAL(15,2) | DEFAULT 0.00 | Computed current balance |
| color | VARCHAR(7) | NULL | Hex color for UI display |
| icon | VARCHAR(50) | NULL | Icon identifier |
| is_active | BOOLEAN | DEFAULT TRUE | Wallet active status |
| is_default | BOOLEAN | DEFAULT FALSE | Default wallet for transactions |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update time |

**Indexes**:
- `idx_wallet_user` on `user_id` (for user's wallets)
- `idx_wallet_user_default` on `user_id, is_default` (for default wallet lookup)

**Constraints**:
- Only one wallet per user can have `is_default = TRUE`

---

### 3. Category

Represents a transaction category for classification.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique category identifier |
| user_id | UUID | FOREIGN KEY (User), NULL | NULL = system category, set = user custom |
| name | VARCHAR(50) | NOT NULL | Category display name |
| name_ur | VARCHAR(100) | NULL | Urdu translation (Phase III ready) |
| type | VARCHAR(10) | NOT NULL | 'income', 'expense', 'transfer' |
| emoji | VARCHAR(10) | NOT NULL | Emoji icon for display |
| color | VARCHAR(7) | NULL | Hex color for UI |
| parent_id | UUID | FOREIGN KEY (Category), NULL | Parent for subcategories |
| sort_order | INTEGER | DEFAULT 0 | Display order |
| is_system | BOOLEAN | DEFAULT FALSE | System-defined vs user-defined |
| is_active | BOOLEAN | DEFAULT TRUE | Category active status |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update time |

**Default System Categories**:

| Name | Type | Emoji | Name (Urdu) |
|------|------|-------|-------------|
| Salary | income | 💵 | تنخواہ |
| Freelance | income | 💼 | آزاد کام |
| Investment Return | income | 📈 | سرمایہ کاری کی واپسی |
| Gift | income | 🎁 | تحفہ |
| Food & Dining | expense | 🍔 | کھانا |
| Transportation | expense | 🚗 | نقل و حمل |
| Rent | expense | 🏠 | کرایہ |
| Utilities | expense | 💡 | یوٹیلیٹیز |
| Shopping | expense | 🛍️ | خریداری |
| Entertainment | expense | 🎬 | تفریح |
| Healthcare | expense | 🏥 | صحت |
| Education | expense | 📚 | تعلیم |
| Investment | expense | 💎 | سرمایہ کاری |

**Indexes**:
- `idx_category_user` on `user_id` (for user's custom categories)
- `idx_category_type` on `type` (for filtering by type)
- `idx_category_parent` on `parent_id` (for hierarchy queries)

---

### 4. Transaction

Represents a financial transaction (income, expense, or transfer).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique transaction identifier |
| user_id | UUID | FOREIGN KEY (User), NOT NULL | Transaction owner |
| wallet_id | UUID | FOREIGN KEY (Wallet), NOT NULL | Source/target wallet |
| category_id | UUID | FOREIGN KEY (Category), NOT NULL | Transaction category |
| type | VARCHAR(10) | NOT NULL | 'income', 'expense', 'transfer' |
| amount | DECIMAL(15,2) | NOT NULL, > 0 | Transaction amount |
| currency | VARCHAR(3) | DEFAULT 'PKR' | Transaction currency |
| description | VARCHAR(500) | NULL | Transaction note/description |
| transaction_date | DATE | NOT NULL | Date of transaction |
| is_recurring | BOOLEAN | DEFAULT FALSE | Recurring transaction flag |
| recurring_frequency | VARCHAR(20) | NULL | 'daily', 'weekly', 'monthly', 'yearly' |
| recurring_end_date | DATE | NULL | When recurring ends |
| tags | VARCHAR(500) | NULL | Comma-separated tags for search |
| attachment_url | VARCHAR(500) | NULL | Receipt/document URL |
| is_deleted | BOOLEAN | DEFAULT FALSE | Soft delete flag |
| deleted_at | TIMESTAMP | NULL | Soft delete timestamp |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update time |

**Indexes**:
- `idx_transaction_user` on `user_id` (for user's transactions)
- `idx_transaction_user_date` on `user_id, transaction_date DESC` (for date-sorted listings)
- `idx_transaction_user_category` on `user_id, category_id` (for category filtering)
- `idx_transaction_user_wallet` on `user_id, wallet_id` (for wallet filtering)
- `idx_transaction_not_deleted` on `is_deleted` WHERE `is_deleted = FALSE` (partial index)

**Constraints**:
- `amount > 0`
- `recurring_frequency` required if `is_recurring = TRUE`

---

### 5. Budget

Represents a spending budget for a category within a time period.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique budget identifier |
| user_id | UUID | FOREIGN KEY (User), NOT NULL | Budget owner |
| category_id | UUID | FOREIGN KEY (Category), NOT NULL | Budget category |
| amount_limit | DECIMAL(15,2) | NOT NULL, > 0 | Budget limit amount |
| period_type | VARCHAR(10) | NOT NULL | 'monthly', 'weekly', 'yearly' |
| period_start | DATE | NOT NULL | Budget period start |
| period_end | DATE | NOT NULL | Budget period end |
| rollover_enabled | BOOLEAN | DEFAULT FALSE | Carry unused to next period |
| alert_threshold | INTEGER | DEFAULT 80 | Percentage to trigger warning |
| is_active | BOOLEAN | DEFAULT TRUE | Budget active status |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update time |

**Computed Fields (via query)**:
- `spent_amount`: SUM of expenses in category during period
- `remaining_amount`: `amount_limit - spent_amount`
- `percentage_used`: `(spent_amount / amount_limit) * 100`
- `status`: 'normal', 'warning', 'exceeded' based on percentage

**Indexes**:
- `idx_budget_user` on `user_id` (for user's budgets)
- `idx_budget_user_period` on `user_id, period_start, period_end` (for period queries)
- `idx_budget_user_category` on `user_id, category_id` (for category budgets)

**Constraints**:
- `period_end > period_start`
- `alert_threshold BETWEEN 1 AND 100`

---

### 6. Goal

Represents a financial goal (savings target, debt payoff, etc.).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique goal identifier |
| user_id | UUID | FOREIGN KEY (User), NOT NULL | Goal owner |
| name | VARCHAR(100) | NOT NULL | Goal display name |
| description | VARCHAR(500) | NULL | Goal description |
| target_amount | DECIMAL(15,2) | NOT NULL, > 0 | Target amount to reach |
| current_amount | DECIMAL(15,2) | DEFAULT 0.00 | Current progress amount |
| currency | VARCHAR(3) | DEFAULT 'PKR' | Goal currency |
| target_date | DATE | NULL | Target completion date |
| emoji | VARCHAR(10) | DEFAULT '🎯' | Display emoji |
| color | VARCHAR(7) | NULL | Progress bar color |
| status | VARCHAR(20) | DEFAULT 'active' | 'active', 'completed', 'paused', 'cancelled' |
| priority | INTEGER | DEFAULT 0 | Display priority |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update time |
| completed_at | TIMESTAMP | NULL | Completion timestamp |

**Computed Fields**:
- `percentage_complete`: `(current_amount / target_amount) * 100`
- `remaining_amount`: `target_amount - current_amount`

**Indexes**:
- `idx_goal_user` on `user_id` (for user's goals)
- `idx_goal_user_status` on `user_id, status` (for active goals)

---

### 7. MonthlySnapshot

Pre-computed monthly financial summary for performance and historical reporting.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique snapshot identifier |
| user_id | UUID | FOREIGN KEY (User), NOT NULL | Snapshot owner |
| year | INTEGER | NOT NULL | Snapshot year |
| month | INTEGER | NOT NULL | Snapshot month (1-12) |
| total_income | DECIMAL(15,2) | DEFAULT 0.00 | Total income for month |
| total_expenses | DECIMAL(15,2) | DEFAULT 0.00 | Total expenses for month |
| net_savings | DECIMAL(15,2) | DEFAULT 0.00 | Income - Expenses |
| savings_rate | DECIMAL(5,2) | DEFAULT 0.00 | Percentage saved |
| top_expense_category | VARCHAR(50) | NULL | Highest expense category |
| top_expense_amount | DECIMAL(15,2) | DEFAULT 0.00 | Top category amount |
| transaction_count | INTEGER | DEFAULT 0 | Number of transactions |
| budget_adherence_rate | DECIMAL(5,2) | DEFAULT 0.00 | % of budgets met |
| category_breakdown | JSONB | NULL | Spending by category JSON |
| computed_at | TIMESTAMP | NOT NULL | When snapshot was computed |
| created_at | TIMESTAMP | NOT NULL | Creation time |

**Indexes**:
- `idx_snapshot_user` on `user_id` (for user's snapshots)
- `idx_snapshot_user_period` on `user_id, year DESC, month DESC` (for historical queries)

**Constraints**:
- `month BETWEEN 1 AND 12`
- UNIQUE constraint on `user_id, year, month`

---

### 8. InsightCache

Cached AI-generated insights for performance optimization.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique cache entry identifier |
| user_id | UUID | FOREIGN KEY (User), NOT NULL | Insight owner |
| insight_type | VARCHAR(50) | NOT NULL | 'spending_pattern', 'budget_recommendation', 'saving_tip', 'anomaly' |
| insight_key | VARCHAR(100) | NOT NULL | Cache key for deduplication |
| title | VARCHAR(200) | NOT NULL | Insight headline |
| content | TEXT | NOT NULL | Full insight text |
| content_ur | TEXT | NULL | Urdu translation (Phase III) |
| severity | VARCHAR(20) | DEFAULT 'info' | 'info', 'suggestion', 'warning', 'alert' |
| related_category | UUID | FOREIGN KEY (Category), NULL | Related category if applicable |
| related_amount | DECIMAL(15,2) | NULL | Related amount if applicable |
| metadata | JSONB | NULL | Additional context data |
| is_read | BOOLEAN | DEFAULT FALSE | User has seen this |
| is_dismissed | BOOLEAN | DEFAULT FALSE | User dismissed this |
| valid_from | TIMESTAMP | NOT NULL | When insight becomes valid |
| valid_until | TIMESTAMP | NOT NULL | Expiration timestamp |
| created_at | TIMESTAMP | NOT NULL | Creation time |

**Indexes**:
- `idx_insight_user` on `user_id` (for user's insights)
- `idx_insight_user_type` on `user_id, insight_type` (for type filtering)
- `idx_insight_valid` on `valid_from, valid_until` (for validity checks)
- `idx_insight_unread` on `user_id, is_read` WHERE `is_read = FALSE` (partial)

**Constraints**:
- `valid_until > valid_from`
- UNIQUE constraint on `user_id, insight_key`

---

### 9. AgentMemory

Stores conversational context and memory for AI agents.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique memory identifier |
| user_id | UUID | FOREIGN KEY (User), NOT NULL | Memory owner |
| agent_type | VARCHAR(50) | NOT NULL | 'chatbot', 'analytics', 'notification', 'budget' |
| memory_type | VARCHAR(50) | NOT NULL | 'conversation', 'preference', 'context', 'summary' |
| memory_key | VARCHAR(100) | NOT NULL | Lookup key |
| content | TEXT | NOT NULL | Memory content |
| embedding_vector | VECTOR(1536) | NULL | OpenAI-compatible embedding (Phase III) |
| importance_score | DECIMAL(3,2) | DEFAULT 0.50 | Memory importance (0-1) |
| access_count | INTEGER | DEFAULT 0 | Times accessed |
| last_accessed_at | TIMESTAMP | NULL | Last access time |
| expires_at | TIMESTAMP | NULL | Memory expiration |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update time |

**Indexes**:
- `idx_memory_user` on `user_id` (for user's memories)
- `idx_memory_user_agent` on `user_id, agent_type` (for agent-specific)
- `idx_memory_user_key` on `user_id, memory_key` (for key lookup)
- `idx_memory_vector` using HNSW on `embedding_vector` (for similarity search, Phase III)

**Constraints**:
- `importance_score BETWEEN 0 AND 1`
- UNIQUE constraint on `user_id, agent_type, memory_key`

---

### 10. EventLog

Immutable event log for event-driven architecture and audit trail.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique event identifier |
| user_id | UUID | FOREIGN KEY (User), NOT NULL | Event owner |
| event_type | VARCHAR(50) | NOT NULL | Event type identifier |
| event_source | VARCHAR(50) | NOT NULL | 'api', 'ui', 'agent', 'system', 'scheduler' |
| aggregate_type | VARCHAR(50) | NOT NULL | Entity type affected |
| aggregate_id | UUID | NOT NULL | Entity ID affected |
| event_data | JSONB | NOT NULL | Event payload |
| metadata | JSONB | NULL | Additional context |
| correlation_id | UUID | NULL | Request correlation ID |
| causation_id | UUID | NULL | Causing event ID |
| version | INTEGER | NOT NULL | Event version for schema evolution |
| is_processed | BOOLEAN | DEFAULT FALSE | Processing status |
| processed_at | TIMESTAMP | NULL | When processed |
| created_at | TIMESTAMP | NOT NULL | Event timestamp |

**Event Types**:

| Event Type | Aggregate | Trigger |
|------------|-----------|---------|
| TransactionCreated | Transaction | New transaction |
| TransactionUpdated | Transaction | Transaction modified |
| TransactionDeleted | Transaction | Transaction soft deleted |
| BudgetCreated | Budget | New budget |
| BudgetUpdated | Budget | Budget modified |
| BudgetExceeded | Budget | Spending > limit |
| BudgetWarning | Budget | Spending > 80% |
| GoalCreated | Goal | New goal |
| GoalUpdated | Goal | Goal modified |
| GoalCompleted | Goal | Target reached |
| InsightGenerated | Insight | AI insight created |
| UserLogin | User | Successful login |
| UserPreferenceChanged | User | Settings updated |

**Indexes**:
- `idx_event_user` on `user_id` (for user's events)
- `idx_event_user_type` on `user_id, event_type` (for type filtering)
- `idx_event_aggregate` on `aggregate_type, aggregate_id` (for entity history)
- `idx_event_correlation` on `correlation_id` (for request tracing)
- `idx_event_unprocessed` on `is_processed` WHERE `is_processed = FALSE` (partial)
- `idx_event_created` on `created_at DESC` (for chronological queries)

**Constraints**:
- `version >= 1`
- Events are immutable (no UPDATE allowed, enforced at application level)

## Database Configuration

### Neon PostgreSQL Settings

| Setting | Value | Rationale |
|---------|-------|-----------|
| Connection Pooling | Enabled | Serverless connection management |
| SSL Mode | Required | Data encryption in transit |
| Statement Timeout | 30s | Prevent runaway queries |
| Idle Timeout | 5min | Release unused connections |

### Required Extensions

| Extension | Purpose |
|-----------|---------|
| uuid-ossp | UUID generation |
| pgcrypto | Password hashing |
| pg_trgm | Full-text search trigrams |
| vector | Embedding similarity search (Phase III) |

### Migration Strategy

1. **Forward-only migrations**: No destructive rollbacks
2. **Versioned schemas**: All changes tracked in migration files
3. **Zero-downtime**: Migrations must not lock tables
4. **Seed data**: System categories created on first migration

## Success Criteria

| Metric | Target |
|--------|--------|
| Query latency (p95) | < 100ms |
| Data integrity | 100% referential integrity |
| Backup capability | Point-in-time recovery |
| Schema flexibility | Add columns without downtime |
