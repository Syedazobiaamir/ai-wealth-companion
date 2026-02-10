# Data Model: Phase V Cloud-Native Production System

**Branch**: `007-phase-v-cloud-native`
**Date**: 2026-02-10

## Overview

This document defines the event-driven data model for Phase V. The primary entities are **Events** that flow between services via Dapr pub/sub. Existing database models (Transaction, Budget, Goal, etc.) remain unchanged from Phase IV.

## Event Entities

### 1. DomainEvent (Base)

All events inherit from this base structure following CloudEvents 1.0 specification.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| specversion | string | Yes | CloudEvents spec version ("1.0") |
| id | uuid | Yes | Unique event identifier |
| type | string | Yes | Event type (e.g., "finance.transaction.created") |
| source | string | Yes | Service that generated the event |
| time | ISO8601 | Yes | Event timestamp |
| datacontenttype | string | Yes | Payload format ("application/json") |
| data | object | Yes | Event-specific payload |
| correlationid | uuid | No | Request correlation for tracing |
| traceparent | string | No | W3C trace context |

### 2. TransactionCreatedEvent

Published when a new transaction is created.

**Type**: `finance.transaction.created`
**Publisher**: Backend
**Consumers**: Analytics Agent, Notification Agent

| Data Field | Type | Required | Description |
|------------|------|----------|-------------|
| transactionId | uuid | Yes | Transaction unique identifier |
| userId | uuid | Yes | User who created the transaction |
| amount | decimal | Yes | Transaction amount (positive) |
| type | enum | Yes | "income" | "expense" | "transfer" |
| category | string | Yes | Transaction category |
| description | string | No | Optional description |
| walletId | uuid | Yes | Source wallet |
| timestamp | ISO8601 | Yes | Transaction date/time |

### 3. TransactionUpdatedEvent

Published when a transaction is modified.

**Type**: `finance.transaction.updated`
**Publisher**: Backend
**Consumers**: Analytics Agent

| Data Field | Type | Required | Description |
|------------|------|----------|-------------|
| transactionId | uuid | Yes | Transaction unique identifier |
| userId | uuid | Yes | User who owns the transaction |
| changes | object | Yes | Fields that changed (before/after) |
| updatedAt | ISO8601 | Yes | Update timestamp |

### 4. BudgetExceededEvent

Published when a user's spending exceeds their budget.

**Type**: `finance.budget.exceeded`
**Publisher**: Analytics Agent
**Consumers**: Notification Agent

| Data Field | Type | Required | Description |
|------------|------|----------|-------------|
| userId | uuid | Yes | Affected user |
| budgetId | uuid | Yes | Budget that was exceeded |
| category | string | Yes | Budget category |
| budgetAmount | decimal | Yes | Budget limit |
| actualAmount | decimal | Yes | Actual spending |
| percentOver | decimal | Yes | Percentage over budget |
| period | string | Yes | Budget period (monthly/weekly) |

### 5. AIInsightGeneratedEvent

Published when AI generates a financial insight.

**Type**: `ai.insight.generated`
**Publisher**: Analytics Agent
**Consumers**: Backend, Notification Agent

| Data Field | Type | Required | Description |
|------------|------|----------|-------------|
| insightId | uuid | Yes | Unique insight identifier |
| userId | uuid | Yes | Target user |
| insightType | enum | Yes | "spending_pattern" | "budget_warning" | "savings_tip" |
| title | string | Yes | Insight headline |
| message | string | Yes | Detailed insight message |
| confidence | decimal | Yes | AI confidence score (0-1) |
| relatedEntities | array | No | IDs of related transactions/budgets |
| expiresAt | ISO8601 | No | When insight becomes stale |

### 6. UserAlertSentEvent

Published when a notification is delivered to a user.

**Type**: `notification.alert.sent`
**Publisher**: Notification Agent
**Consumers**: Backend (audit)

| Data Field | Type | Required | Description |
|------------|------|----------|-------------|
| alertId | uuid | Yes | Unique alert identifier |
| userId | uuid | Yes | Recipient user |
| channel | enum | Yes | "push" | "email" | "in_app" |
| sourceEvent | string | Yes | Event type that triggered alert |
| sourceEventId | uuid | Yes | ID of triggering event |
| deliveredAt | ISO8601 | Yes | Delivery timestamp |
| status | enum | Yes | "delivered" | "failed" | "pending" |

## Topic Naming Convention

Topics follow the pattern: `{domain}.{entity}.{action}`

| Topic Name | Description |
|------------|-------------|
| `finance.transaction.created` | New transactions |
| `finance.transaction.updated` | Transaction modifications |
| `finance.budget.exceeded` | Budget threshold breaches |
| `ai.insight.generated` | AI-generated insights |
| `notification.alert.sent` | Notification audit trail |
| `dlq.{topic}` | Dead letter queues for each topic |

## State Transitions

### Event Flow Diagram

```
Transaction Created
        │
        ▼
┌───────────────────┐
│  Backend Service  │
│  (Publisher)      │
└─────────┬─────────┘
          │ finance.transaction.created
          ▼
┌───────────────────┐
│   Kafka Topic     │
│   (via Dapr)      │
└─────────┬─────────┘
          │
    ┌─────┴─────┐
    ▼           ▼
┌────────┐  ┌────────────┐
│Analytics│  │Notification│
│ Agent   │  │   Agent    │
└────┬────┘  └────────────┘
     │
     │ (if budget exceeded)
     ▼
┌───────────────────┐
│ finance.budget.   │
│    exceeded       │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Notification Agent│
│ (sends alert)     │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ notification.     │
│    alert.sent     │
└───────────────────┘
```

## Validation Rules

### Event Validation

| Rule | Enforcement |
|------|-------------|
| Event ID must be UUID v4 | Schema validation |
| Timestamp must be valid ISO8601 | Schema validation |
| Amount must be positive decimal | Business logic |
| User ID must exist in database | Runtime validation |
| Correlation ID propagated if present | Middleware |

### Idempotency Rules

| Rule | Implementation |
|------|----------------|
| Each event processed exactly once | Event ID tracked in Redis |
| Duplicate events are logged and skipped | Handler middleware |
| Event ID TTL is 7 days | Redis TTL configuration |

## Relationships

### Event Dependencies

```
TransactionCreatedEvent
    └── triggers → BudgetExceededEvent (if over budget)
                       └── triggers → UserAlertSentEvent

TransactionUpdatedEvent
    └── triggers → (recalculation in Analytics Agent)

AIInsightGeneratedEvent
    └── triggers → UserAlertSentEvent (if actionable)
```

### Service Ownership

| Service | Publishes | Consumes |
|---------|-----------|----------|
| Backend | transaction.created, transaction.updated | ai.insight.generated, alert.sent |
| Analytics Agent | budget.exceeded, ai.insight.generated | transaction.created, transaction.updated |
| Notification Agent | alert.sent | budget.exceeded, ai.insight.generated |
