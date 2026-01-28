# API Specification: Phase II REST API

**Feature Branch**: `003-phase2-fullstack-platform`
**Created**: 2026-01-25
**Status**: Active
**Base URL**: `/api/v1`
**Input**: Auth verification, All CRUD endpoints, Dashboard aggregation APIs, AI-ready APIs, Secure middleware, Pagination, filters

## Overview

This specification defines the complete REST API for the AI Wealth & Spending Companion Phase II platform. All endpoints are designed to serve both human users and future AI agents.

### Design Principles

1. **Backend is Single Source of Truth**: All data served from Neon PostgreSQL
2. **JWT Authentication**: All protected endpoints require valid JWT tokens
3. **Consistent Response Schema**: Predictable JSON structure for all responses
4. **AI-Ready**: Responses include machine-readable metadata
5. **Pagination by Default**: All list endpoints support cursor-based pagination
6. **Comprehensive Error Codes**: Machine-parseable error responses

## Authentication & Security

### JWT Token Structure

```json
{
  "sub": "user_uuid",
  "email": "user@example.com",
  "iat": 1706140800,
  "exp": 1706144400,
  "type": "access"
}
```

### Token Lifecycle

| Token Type | Expiration | Storage |
|------------|------------|---------|
| Access Token | 1 hour | Memory only (NOT localStorage) |
| Refresh Token | 7 days | httpOnly cookie |

### Authentication Endpoints

#### POST /auth/register

Create a new user account.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecureP@ssw0rd!",
  "display_name": "John Doe",
  "preferred_currency": "PKR",
  "preferred_locale": "en"
}
```

**Validation Rules**:
- `email`: Valid email format, unique
- `password`: Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char
- `display_name`: Optional, max 100 chars
- `preferred_currency`: Valid ISO 4217 code
- `preferred_locale`: 'en' or 'ur'

**Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "display_name": "John Doe",
      "preferred_currency": "PKR",
      "preferred_locale": "en",
      "created_at": "2026-01-25T10:30:00Z"
    },
    "tokens": {
      "access_token": "eyJhbGciOiJIUzI1NiIs...",
      "token_type": "Bearer",
      "expires_in": 3600
    }
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2026-01-25T10:30:00Z"
  }
}
```

---

#### POST /auth/login

Authenticate user and receive tokens.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecureP@ssw0rd!"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "display_name": "John Doe",
      "last_login_at": "2026-01-25T10:30:00Z"
    },
    "tokens": {
      "access_token": "eyJhbGciOiJIUzI1NiIs...",
      "token_type": "Bearer",
      "expires_in": 3600
    }
  },
  "meta": {
    "request_id": "req_abc123"
  }
}
```

**Error Response (401 Unauthorized)**:
```json
{
  "success": false,
  "error": {
    "code": "AUTH_INVALID_CREDENTIALS",
    "message": "Invalid email or password",
    "details": null
  },
  "meta": {
    "request_id": "req_abc123"
  }
}
```

---

#### POST /auth/refresh

Refresh access token using refresh token cookie.

**Request**: No body (refresh token sent via httpOnly cookie)

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

---

#### POST /auth/logout

Invalidate refresh token and clear cookie.

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "message": "Logged out successfully"
  }
}
```

---

#### GET /auth/me

Get current authenticated user profile.

**Headers**: `Authorization: Bearer <access_token>`

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "display_name": "John Doe",
    "preferred_currency": "PKR",
    "preferred_locale": "en",
    "theme_preference": "dark",
    "created_at": "2026-01-25T10:30:00Z"
  }
}
```

## Transaction Endpoints

### GET /transactions

List user's transactions with pagination and filtering.

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | integer | 1 | Page number |
| limit | integer | 20 | Items per page (max 100) |
| cursor | string | null | Cursor for pagination |
| category_id | uuid | null | Filter by category |
| wallet_id | uuid | null | Filter by wallet |
| type | string | null | Filter: 'income', 'expense', 'transfer' |
| start_date | date | null | Filter: transactions on or after |
| end_date | date | null | Filter: transactions on or before |
| search | string | null | Search in description/tags |
| sort | string | 'date_desc' | Sort: 'date_desc', 'date_asc', 'amount_desc', 'amount_asc' |
| is_recurring | boolean | null | Filter recurring transactions |

**Response (200 OK)**:
```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "wallet_id": "550e8400-e29b-41d4-a716-446655440010",
      "category": {
        "id": "550e8400-e29b-41d4-a716-446655440020",
        "name": "Food & Dining",
        "emoji": "🍔",
        "type": "expense"
      },
      "type": "expense",
      "amount": 1500.00,
      "currency": "PKR",
      "description": "Lunch at office",
      "transaction_date": "2026-01-25",
      "is_recurring": false,
      "tags": ["lunch", "work"],
      "created_at": "2026-01-25T12:00:00Z"
    }
  ],
  "meta": {
    "pagination": {
      "page": 1,
      "limit": 20,
      "total_items": 150,
      "total_pages": 8,
      "has_next": true,
      "has_prev": false,
      "next_cursor": "eyJpZCI6IjU1MGU4..."
    },
    "filters_applied": {
      "type": "expense",
      "start_date": "2026-01-01"
    },
    "request_id": "req_abc123"
  }
}
```

---

### POST /transactions

Create a new transaction.

**Request**:
```json
{
  "wallet_id": "550e8400-e29b-41d4-a716-446655440010",
  "category_id": "550e8400-e29b-41d4-a716-446655440020",
  "type": "expense",
  "amount": 1500.00,
  "description": "Lunch at office",
  "transaction_date": "2026-01-25",
  "is_recurring": false,
  "recurring_frequency": null,
  "tags": ["lunch", "work"]
}
```

**Validation Rules**:
- `wallet_id`: Required, must belong to user
- `category_id`: Required, must exist
- `type`: Required, must match category type
- `amount`: Required, > 0
- `transaction_date`: Required, valid date, not more than 1 year in future
- `is_recurring`: If true, `recurring_frequency` required

**Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "wallet_id": "550e8400-e29b-41d4-a716-446655440010",
    "category": {
      "id": "550e8400-e29b-41d4-a716-446655440020",
      "name": "Food & Dining",
      "emoji": "🍔"
    },
    "type": "expense",
    "amount": 1500.00,
    "currency": "PKR",
    "description": "Lunch at office",
    "transaction_date": "2026-01-25",
    "is_recurring": false,
    "created_at": "2026-01-25T12:00:00Z"
  },
  "meta": {
    "events_emitted": ["TransactionCreated"],
    "request_id": "req_abc123"
  }
}
```

---

### GET /transactions/{id}

Get a single transaction.

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "wallet": {
      "id": "550e8400-e29b-41d4-a716-446655440010",
      "name": "Main Account"
    },
    "category": {
      "id": "550e8400-e29b-41d4-a716-446655440020",
      "name": "Food & Dining",
      "emoji": "🍔",
      "type": "expense"
    },
    "type": "expense",
    "amount": 1500.00,
    "currency": "PKR",
    "description": "Lunch at office",
    "transaction_date": "2026-01-25",
    "is_recurring": false,
    "tags": ["lunch", "work"],
    "created_at": "2026-01-25T12:00:00Z",
    "updated_at": "2026-01-25T12:00:00Z"
  }
}
```

---

### PUT /transactions/{id}

Update a transaction.

**Request**:
```json
{
  "amount": 1800.00,
  "description": "Lunch at office (updated)"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "amount": 1800.00,
    "description": "Lunch at office (updated)",
    "updated_at": "2026-01-25T14:00:00Z"
  },
  "meta": {
    "events_emitted": ["TransactionUpdated"],
    "request_id": "req_abc123"
  }
}
```

---

### DELETE /transactions/{id}

Soft delete a transaction.

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "deleted_at": "2026-01-25T14:30:00Z"
  },
  "meta": {
    "events_emitted": ["TransactionDeleted"],
    "recoverable_until": "2026-01-25T14:30:00Z"
  }
}
```

---

### POST /transactions/batch

Create multiple transactions (AI agent optimization).

**Request**:
```json
{
  "transactions": [
    {
      "wallet_id": "...",
      "category_id": "...",
      "type": "expense",
      "amount": 500.00,
      "transaction_date": "2026-01-25"
    },
    {
      "wallet_id": "...",
      "category_id": "...",
      "type": "income",
      "amount": 50000.00,
      "transaction_date": "2026-01-25"
    }
  ]
}
```

**Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "created": 2,
    "failed": 0,
    "transactions": [...]
  },
  "meta": {
    "events_emitted": ["TransactionCreated", "TransactionCreated"]
  }
}
```

## Category Endpoints

### GET /categories

List all categories (system + user custom).

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| type | string | null | Filter: 'income', 'expense', 'transfer' |
| include_system | boolean | true | Include system categories |

**Response (200 OK)**:
```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440020",
      "name": "Food & Dining",
      "name_ur": "کھانا",
      "type": "expense",
      "emoji": "🍔",
      "color": "#FF6B6B",
      "is_system": true,
      "sort_order": 1
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440021",
      "name": "Salary",
      "name_ur": "تنخواہ",
      "type": "income",
      "emoji": "💵",
      "color": "#4CAF50",
      "is_system": true,
      "sort_order": 1
    }
  ],
  "meta": {
    "total_count": 15
  }
}
```

---

### POST /categories

Create a custom category.

**Request**:
```json
{
  "name": "Subscriptions",
  "type": "expense",
  "emoji": "📺",
  "color": "#9C27B0"
}
```

**Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440030",
    "name": "Subscriptions",
    "type": "expense",
    "emoji": "📺",
    "color": "#9C27B0",
    "is_system": false
  }
}
```

## Budget Endpoints

### GET /budgets

List all budgets with current status.

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| month | integer | current | Month (1-12) |
| year | integer | current | Year |
| status | string | null | Filter: 'normal', 'warning', 'exceeded' |

**Response (200 OK)**:
```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440040",
      "category": {
        "id": "550e8400-e29b-41d4-a716-446655440020",
        "name": "Food & Dining",
        "emoji": "🍔"
      },
      "amount_limit": 15000.00,
      "period_type": "monthly",
      "period_start": "2026-01-01",
      "period_end": "2026-01-31",
      "alert_threshold": 80,
      "status": {
        "spent_amount": 12500.00,
        "remaining_amount": 2500.00,
        "percentage_used": 83.33,
        "status": "warning",
        "days_remaining": 6
      }
    }
  ],
  "meta": {
    "period": {
      "month": 1,
      "year": 2026
    },
    "total_budgeted": 50000.00,
    "total_spent": 35000.00
  }
}
```

---

### POST /budgets

Create or update a budget.

**Request**:
```json
{
  "category_id": "550e8400-e29b-41d4-a716-446655440020",
  "amount_limit": 15000.00,
  "period_type": "monthly",
  "period_start": "2026-01-01",
  "alert_threshold": 80,
  "rollover_enabled": false
}
```

**Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440040",
    "category_id": "550e8400-e29b-41d4-a716-446655440020",
    "amount_limit": 15000.00,
    "period_type": "monthly",
    "created_at": "2026-01-25T10:00:00Z"
  },
  "meta": {
    "events_emitted": ["BudgetCreated"]
  }
}
```

---

### GET /budgets/{category_id}

Get budget status for a specific category.

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "budget": {
      "id": "550e8400-e29b-41d4-a716-446655440040",
      "amount_limit": 15000.00
    },
    "category": {
      "id": "550e8400-e29b-41d4-a716-446655440020",
      "name": "Food & Dining",
      "emoji": "🍔"
    },
    "status": {
      "spent_amount": 12500.00,
      "remaining_amount": 2500.00,
      "percentage_used": 83.33,
      "status": "warning",
      "transactions_count": 25
    },
    "history": [
      {
        "month": 12,
        "year": 2025,
        "spent": 14200.00,
        "limit": 15000.00
      }
    ]
  }
}
```

## Dashboard Aggregation APIs

### GET /dashboard/summary

Get financial overview for dashboard.

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| period | string | 'month' | 'week', 'month', 'year', 'custom' |
| start_date | date | null | Custom period start |
| end_date | date | null | Custom period end |

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "totals": {
      "income": 75000.00,
      "expenses": 45000.00,
      "net": 30000.00,
      "savings_rate": 40.0
    },
    "comparison": {
      "income_change": 5.2,
      "expense_change": -3.1,
      "trend": "improving"
    },
    "top_categories": [
      {
        "category": {
          "name": "Food & Dining",
          "emoji": "🍔"
        },
        "amount": 15000.00,
        "percentage": 33.3
      }
    ],
    "recent_transactions": [
      {
        "id": "...",
        "description": "Lunch",
        "amount": 500.00,
        "type": "expense",
        "category_emoji": "🍔",
        "transaction_date": "2026-01-25"
      }
    ],
    "budgets_summary": {
      "total_budgets": 5,
      "on_track": 3,
      "warning": 1,
      "exceeded": 1
    }
  },
  "meta": {
    "period": {
      "start": "2026-01-01",
      "end": "2026-01-31",
      "type": "month"
    },
    "cache_until": "2026-01-25T11:00:00Z"
  }
}
```

---

### GET /dashboard/charts/spending-by-category

Get data for category breakdown pie chart.

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "chart_type": "pie",
    "labels": ["Food & Dining", "Transportation", "Utilities", "Entertainment"],
    "datasets": [
      {
        "data": [15000, 8000, 5000, 3000],
        "colors": ["#FF6B6B", "#4ECDC4", "#FFE66D", "#95E1D3"]
      }
    ],
    "total": 31000.00
  },
  "meta": {
    "period": "2026-01"
  }
}
```

---

### GET /dashboard/charts/spending-trend

Get data for spending trend line chart.

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| months | integer | 6 | Number of months (1-12) |

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "chart_type": "line",
    "labels": ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan"],
    "datasets": [
      {
        "label": "Income",
        "data": [70000, 72000, 75000, 73000, 78000, 75000],
        "color": "#4CAF50"
      },
      {
        "label": "Expenses",
        "data": [45000, 48000, 42000, 50000, 55000, 45000],
        "color": "#FF6B6B"
      }
    ]
  }
}
```

## AI-Ready APIs

### GET /ai/context

Get user context for AI agents.

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "user_profile": {
      "display_name": "John",
      "preferred_currency": "PKR",
      "locale": "en",
      "member_since": "2026-01-01"
    },
    "financial_snapshot": {
      "current_balance": 125000.00,
      "monthly_income_avg": 75000.00,
      "monthly_expense_avg": 45000.00,
      "savings_rate_avg": 40.0
    },
    "active_budgets": [
      {
        "category": "Food & Dining",
        "limit": 15000.00,
        "spent": 12500.00,
        "status": "warning"
      }
    ],
    "recent_patterns": {
      "top_expense_category": "Food & Dining",
      "spending_trend": "stable",
      "unusual_transactions": []
    }
  },
  "meta": {
    "generated_at": "2026-01-25T10:00:00Z",
    "valid_for_seconds": 300
  }
}
```

---

### POST /ai/query

Execute natural language query (Phase III ready).

**Request**:
```json
{
  "query": "How much did I spend on food this month?",
  "context": {
    "conversation_id": "conv_123",
    "previous_messages": 3
  }
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "answer": "You've spent PKR 12,500 on Food & Dining this month, which is 83% of your PKR 15,000 budget.",
    "answer_ur": null,
    "data_points": [
      {
        "label": "Food & Dining spending",
        "value": 12500,
        "unit": "PKR"
      }
    ],
    "suggested_actions": [
      {
        "action": "view_transactions",
        "label": "View food transactions",
        "params": {
          "category": "food-dining",
          "month": "2026-01"
        }
      }
    ],
    "confidence": 0.95
  },
  "meta": {
    "processing_time_ms": 150,
    "model_version": "v1"
  }
}
```

---

### POST /ai/insights/generate

Trigger insight generation (AI agent endpoint).

**Request**:
```json
{
  "insight_types": ["spending_pattern", "budget_recommendation"],
  "force_refresh": false
}
```

**Response (202 Accepted)**:
```json
{
  "success": true,
  "data": {
    "job_id": "job_abc123",
    "status": "processing",
    "estimated_completion": "2026-01-25T10:05:00Z"
  }
}
```

## Secure Middleware

### Rate Limiting

| Endpoint Group | Rate Limit | Window |
|----------------|------------|--------|
| Authentication | 5 requests | 1 minute |
| Write operations | 30 requests | 1 minute |
| Read operations | 100 requests | 1 minute |
| AI endpoints | 10 requests | 1 minute |

### CORS Configuration

```json
{
  "allowed_origins": [
    "https://localhost:3000",
    "https://app.example.com"
  ],
  "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
  "allowed_headers": ["Authorization", "Content-Type", "X-Request-ID"],
  "expose_headers": ["X-RateLimit-Remaining", "X-Request-ID"],
  "max_age": 86400
}
```

### Security Headers

| Header | Value |
|--------|-------|
| X-Content-Type-Options | nosniff |
| X-Frame-Options | DENY |
| X-XSS-Protection | 1; mode=block |
| Strict-Transport-Security | max-age=31536000; includeSubDomains |
| Content-Security-Policy | default-src 'self' |

## Error Response Schema

All errors follow this consistent schema:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {
      "field": "specific field",
      "reason": "why it failed"
    }
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2026-01-25T10:00:00Z"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| AUTH_INVALID_CREDENTIALS | 401 | Wrong email/password |
| AUTH_TOKEN_EXPIRED | 401 | JWT expired |
| AUTH_TOKEN_INVALID | 401 | Malformed JWT |
| AUTH_UNAUTHORIZED | 403 | No permission |
| RESOURCE_NOT_FOUND | 404 | Entity not found |
| VALIDATION_ERROR | 422 | Input validation failed |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Server error |

## Pagination Schema

All list endpoints use cursor-based pagination:

```json
{
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_items": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false,
    "next_cursor": "eyJpZCI6IjU1MGU4...",
    "prev_cursor": null
  }
}
```

**Query Parameters**:
- `page`: Page number (integer, default 1)
- `limit`: Items per page (integer, default 20, max 100)
- `cursor`: Cursor for efficient pagination (string, alternative to page)

## Success Criteria

| Metric | Target |
|--------|--------|
| API response time (p95) | < 200ms |
| Error rate | < 0.1% |
| JWT validation time | < 10ms |
| Rate limit accuracy | 100% |
| CORS compliance | All browsers |
