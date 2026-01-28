# Data Model: Phase II Full-Stack Financial Platform

**Date**: 2026-01-19
**Branch**: `003-phase2-fullstack-platform`

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐
│      User       │       │    Category     │
├─────────────────┤       ├─────────────────┤
│ id (UUID) PK    │       │ id (UUID) PK    │
│ theme           │       │ name            │
│ created_at      │       │ emoji           │
│ updated_at      │       │ created_at      │
└─────────────────┘       └────────┬────────┘
                                   │
                                   │ 1:N
                                   ▼
┌─────────────────┐       ┌─────────────────┐
│     Budget      │       │   Transaction   │
├─────────────────┤       ├─────────────────┤
│ id (UUID) PK    │       │ id (UUID) PK    │
│ category_id FK  │◄──────│ category_id FK  │
│ limit_amount    │       │ type            │
│ month           │       │ amount          │
│ year            │       │ date            │
│ created_at      │       │ note            │
│ updated_at      │       │ recurring       │
└─────────────────┘       │ deleted_at      │
                          │ created_at      │
                          │ updated_at      │
                          └─────────────────┘
```

## Entities

### User

Stores user preferences. Single-user in Phase II (no authentication).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Unique identifier |
| theme | VARCHAR(10) | NOT NULL, default 'system' | Theme preference: 'light', 'dark', 'system' |
| created_at | TIMESTAMP | NOT NULL, default now() | Record creation time |
| updated_at | TIMESTAMP | NOT NULL, auto-update | Last modification time |

**Indexes**: None (single record)

### Category

Predefined transaction categories with emoji icons.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Unique identifier |
| name | VARCHAR(50) | NOT NULL, UNIQUE | Category name |
| emoji | VARCHAR(10) | NOT NULL | Emoji icon for display |
| created_at | TIMESTAMP | NOT NULL, default now() | Record creation time |

**Indexes**:
- UNIQUE on `name`

**Default Data** (seeded on init):

| name | emoji |
|------|-------|
| Food | 🍔 |
| Rent | 🏠 |
| Utilities | 💡 |
| Salary | 💵 |
| Investment | 💎 |

### Transaction

Financial record of income or expense.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Unique identifier |
| type | VARCHAR(10) | NOT NULL, CHECK IN ('income', 'expense') | Transaction type |
| amount | DECIMAL(12,2) | NOT NULL, CHECK > 0 | Transaction amount |
| category_id | UUID | FK → Category.id, NOT NULL | Associated category |
| date | DATE | NOT NULL | Transaction date |
| note | VARCHAR(255) | NULL | Optional description |
| recurring | BOOLEAN | NOT NULL, default false | Recurring transaction flag |
| deleted_at | TIMESTAMP | NULL | Soft delete timestamp |
| created_at | TIMESTAMP | NOT NULL, default now() | Record creation time |
| updated_at | TIMESTAMP | NOT NULL, auto-update | Last modification time |

**Indexes**:
- INDEX on `date` (for date range queries)
- INDEX on `category_id` (for category filtering)
- INDEX on `type` (for income/expense filtering)
- INDEX on `deleted_at` (for soft delete queries)

**Validation Rules**:
- `amount` must be positive (> 0)
- `type` must be 'income' or 'expense'
- `date` must be valid date format (YYYY-MM-DD)
- `category_id` must reference existing category

### Budget

Monthly spending limit per category.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Unique identifier |
| category_id | UUID | FK → Category.id, NOT NULL | Target category |
| limit_amount | DECIMAL(12,2) | NOT NULL, CHECK > 0 | Monthly spending limit |
| month | INTEGER | NOT NULL, CHECK 1-12 | Budget month |
| year | INTEGER | NOT NULL, CHECK >= 2020 | Budget year |
| created_at | TIMESTAMP | NOT NULL, default now() | Record creation time |
| updated_at | TIMESTAMP | NOT NULL, auto-update | Last modification time |

**Indexes**:
- UNIQUE on `(category_id, month, year)` - one budget per category per month

**Validation Rules**:
- `limit_amount` must be positive (> 0)
- `month` must be 1-12
- `year` must be >= 2020
- Only one budget per category per month/year combination

## Computed/Derived Models

### BudgetStatus (not persisted)

Calculated view of budget vs actual spending.

| Field | Type | Description |
|-------|------|-------------|
| category | string | Category name |
| emoji | string | Category emoji |
| limit | decimal | Budget limit amount |
| spent | decimal | Sum of expenses in category for month |
| remaining | decimal | limit - spent |
| percentage | decimal | (spent / limit) * 100 |
| exceeded | boolean | spent > limit |
| warning | boolean | percentage >= 80 |

### FinancialSummary (not persisted)

Aggregated financial totals.

| Field | Type | Description |
|-------|------|-------------|
| total_income | decimal | Sum of all income transactions |
| total_expense | decimal | Sum of all expense transactions |
| net_balance | decimal | total_income - total_expense |
| period_start | date | Start of calculation period |
| period_end | date | End of calculation period |

## SQLModel Definitions

### Backend Models (Python)

```python
# models/category.py
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class CategoryBase(SQLModel):
    name: str = Field(max_length=50, unique=True)
    emoji: str = Field(max_length=10)

class Category(CategoryBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CategoryRead(CategoryBase):
    id: UUID
```

```python
# models/transaction.py
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from enum import Enum

class TransactionType(str, Enum):
    income = "income"
    expense = "expense"

class TransactionBase(SQLModel):
    type: TransactionType
    amount: Decimal = Field(gt=0, decimal_places=2)
    category_id: UUID = Field(foreign_key="category.id")
    date: date
    note: Optional[str] = Field(default=None, max_length=255)
    recurring: bool = Field(default=False)

class Transaction(TransactionBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    deleted_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(SQLModel):
    type: Optional[TransactionType] = None
    amount: Optional[Decimal] = Field(default=None, gt=0)
    category_id: Optional[UUID] = None
    date: Optional[date] = None
    note: Optional[str] = Field(default=None, max_length=255)
    recurring: Optional[bool] = None

class TransactionRead(TransactionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
```

```python
# models/budget.py
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from decimal import Decimal
from typing import Optional

class BudgetBase(SQLModel):
    category_id: UUID = Field(foreign_key="category.id")
    limit_amount: Decimal = Field(gt=0, decimal_places=2)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2020)

class Budget(BudgetBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        # Unique constraint on category_id + month + year
        table_args = (
            UniqueConstraint('category_id', 'month', 'year'),
        )

class BudgetCreate(BudgetBase):
    pass

class BudgetRead(BudgetBase):
    id: UUID

class BudgetStatus(SQLModel):
    category: str
    emoji: str
    limit: Decimal
    spent: Decimal
    remaining: Decimal
    percentage: Decimal
    exceeded: bool
    warning: bool
```

```python
# models/user.py
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

class ThemePreference(str, Enum):
    light = "light"
    dark = "dark"
    system = "system"

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    theme: ThemePreference = Field(default=ThemePreference.system)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Frontend Types (TypeScript)

```typescript
// types/category.ts
export interface Category {
  id: string;
  name: string;
  emoji: string;
}

// types/transaction.ts
export type TransactionType = 'income' | 'expense';

export interface Transaction {
  id: string;
  type: TransactionType;
  amount: number;
  category_id: string;
  date: string; // ISO date string YYYY-MM-DD
  note: string | null;
  recurring: boolean;
  created_at: string;
  updated_at: string;
}

export interface TransactionCreate {
  type: TransactionType;
  amount: number;
  category_id: string;
  date: string;
  note?: string;
  recurring?: boolean;
}

export interface TransactionUpdate {
  type?: TransactionType;
  amount?: number;
  category_id?: string;
  date?: string;
  note?: string;
  recurring?: boolean;
}

// types/budget.ts
export interface Budget {
  id: string;
  category_id: string;
  limit_amount: number;
  month: number;
  year: number;
}

export interface BudgetCreate {
  category_id: string;
  limit_amount: number;
  month: number;
  year: number;
}

export interface BudgetStatus {
  category: string;
  emoji: string;
  limit: number;
  spent: number;
  remaining: number;
  percentage: number;
  exceeded: boolean;
  warning: boolean;
}

// types/summary.ts
export interface FinancialSummary {
  total_income: number;
  total_expense: number;
  net_balance: number;
  period_start: string;
  period_end: string;
}
```

## Migration Strategy

### Initial Migration (M2)

1. Create `category` table
2. Create `transaction` table with FK to category
3. Create `budget` table with FK to category
4. Create `user` table
5. Seed default categories

### Rollback Plan

Each migration includes down migration:
- Drop tables in reverse order (budget → transaction → category → user)
- No data migration needed for Phase II (fresh start)
