# Data Model: Phase I Financial Core

**Feature**: 002-phase1-financial-core
**Date**: 2026-01-18

## Entities

### Transaction

Represents a financial event (income or expense).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | integer | Auto-generated, unique, >= 1 | Unique identifier |
| type | enum | "income" or "expense" | Transaction direction |
| amount | decimal | > 0 | Transaction value |
| category | string | Must reference existing Category | Classification |
| note | string | Optional, max 500 chars | User notes |
| date | date | YYYY-MM-DD format | Transaction date |
| recurring | boolean | Optional, default false | Recurring flag |

**Validation Rules**:
- Amount MUST be greater than zero
- Category MUST exist before transaction creation
- Date MUST be valid YYYY-MM-DD format
- Type MUST be "income" or "expense"

### Category

Represents a classification for transactions.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| name | string | Unique, non-empty | Category identifier |
| emoji | string | Optional | Display icon |

**Default Categories** (pre-loaded on startup):

| Name | Emoji |
|------|-------|
| Food | 🍔 |
| Rent | 🏠 |
| Utilities | 💡 |
| Salary | 💵 |
| Investment | 💎 |

**Validation Rules**:
- Name MUST be unique (case-insensitive comparison)
- Name MUST NOT be empty

### Budget

Represents a spending limit for a category.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| category | string | Must reference existing Category | Linked category |
| limit | decimal | > 0 | Monthly spending limit |

**Calculated Fields** (not stored, computed on demand):
- `spent`: Sum of expense transactions in category (current session)
- `remaining`: limit - spent
- `percentage`: (spent / limit) * 100
- `exceeded`: spent > limit

**Validation Rules**:
- Category MUST exist before budget creation
- Limit MUST be greater than zero

## Relationships

```
┌─────────────┐       ┌─────────────┐
│  Category   │◄──────│ Transaction │
│             │   *   │             │
│ name (PK)   │       │ category    │
│ emoji       │       │ id (PK)     │
└─────────────┘       │ type        │
      ▲               │ amount      │
      │               │ note        │
      │               │ date        │
      │               │ recurring   │
      │               └─────────────┘
      │
┌─────────────┐
│   Budget    │
│             │
│ category(PK)│
│ limit       │
└─────────────┘
```

- **Category → Transaction**: One-to-many (one category has many transactions)
- **Category → Budget**: One-to-one (one budget per category)

## State Transitions

### Transaction Lifecycle

```
[Created] → [Active] → [Deleted]
              │
              └──────► [Updated]
                          │
                          └──► [Active]
```

### Budget Lifecycle

```
[Not Set] → [Set] → [Updated]
              │
              └──► [Exceeded] (calculated state)
```

## Storage Structures (In-Memory)

Per constitution Phase I Data Storage requirements:

```python
# Transactions: Dictionary keyed by ID
transactions: Dict[int, Transaction] = {}

# Categories: Dictionary keyed by name
categories: Dict[str, Category] = {}

# Budgets: Dictionary keyed by category name
budgets: Dict[str, Budget] = {}

# ID Counter for auto-generation
next_transaction_id: int = 1
```

## Data Integrity Rules

1. **Referential Integrity**: Transaction category MUST exist in categories dict
2. **Unique Constraints**: Transaction ID unique; Category name unique; Budget category unique
3. **Cascade Behavior**: Deleting a category is NOT allowed if transactions reference it
4. **Session Scope**: All data cleared on application restart (no persistence)
