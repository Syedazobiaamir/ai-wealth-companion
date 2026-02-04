# Data Model: AI-Powered Todo Chatbot

**Feature**: 005-ai-todo-chatbot
**Date**: 2026-02-03

## Overview

This feature reuses existing models from Phase II. No new database tables are required.

## Existing Models (Reused)

### Task

**Location**: `backend/src/models/task.py`

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to users |
| title | string(200) | Task title (required) |
| description | string(1000) | Optional description |
| priority | enum | high, medium, low |
| category | enum | bills, savings, review, investment, budget, other |
| due_date | date | Optional due date |
| is_recurring | boolean | Whether task repeats |
| recurring_frequency | enum | daily, weekly, monthly (if recurring) |
| is_completed | boolean | Completion status |
| created_at | datetime | Creation timestamp |
| updated_at | datetime | Last update timestamp |
| completed_at | datetime | When completed (if completed) |

**Relationships**:
- `user_id` → `users.id` (many-to-one)

---

### Conversation

**Location**: `backend/src/models/conversation.py`

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to users |
| title | string(200) | Optional conversation title |
| language | string(5) | Language code (en, ur) |
| is_active | boolean | Whether conversation is active |
| message_count | integer | Number of messages |
| created_at | datetime | Creation timestamp |
| updated_at | datetime | Last update timestamp |

**Relationships**:
- `user_id` → `users.id` (many-to-one)
- `messages` → `messages` (one-to-many)

---

### Message

**Location**: `backend/src/models/message.py`

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| conversation_id | UUID | Foreign key to conversations |
| role | enum | user, assistant, system |
| content | text | Message content (English) |
| content_ur | text | Message content (Urdu, optional) |
| intent | string(50) | Detected intent |
| entities | JSON | Extracted entities |
| tool_calls | JSON | MCP tool calls made |
| confidence | float | Intent confidence score |
| input_method | enum | text, voice |
| processing_time_ms | integer | Response time in ms |
| created_at | datetime | Creation timestamp |

**Relationships**:
- `conversation_id` → `conversations.id` (many-to-one)

---

## Entity Relationships

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────┐
│    User      │       │   Conversation   │       │   Message    │
├──────────────┤       ├──────────────────┤       ├──────────────┤
│ id (PK)      │───┬──▶│ id (PK)          │──────▶│ id (PK)      │
│ email        │   │   │ user_id (FK)     │       │ conv_id (FK) │
│ ...          │   │   │ language         │       │ role         │
└──────────────┘   │   │ ...              │       │ content      │
                   │   └──────────────────┘       │ tool_calls   │
                   │                              │ ...          │
                   │   ┌──────────────────┐       └──────────────┘
                   │   │      Task        │
                   │   ├──────────────────┤
                   └──▶│ id (PK)          │
                       │ user_id (FK)     │
                       │ title            │
                       │ due_date         │
                       │ is_completed     │
                       │ ...              │
                       └──────────────────┘
```

## Validation Rules

### Task Validation

| Field | Rule |
|-------|------|
| title | Required, max 200 chars |
| priority | Must be: high, medium, low |
| category | Must be: bills, savings, review, investment, budget, other |
| due_date | Must be valid date (can be past for overdue) |

### Message Validation

| Field | Rule |
|-------|------|
| conversation_id | Must exist in conversations |
| role | Must be: user, assistant, system |
| content | Required, non-empty |
| input_method | Must be: text, voice |

## State Transitions

### Task States

```
              create
    ┌─────────────────────────────────┐
    │                                 ▼
┌───────┐  complete  ┌───────────────────┐
│ ACTIVE│───────────▶│     COMPLETED     │
└───────┘            └───────────────────┘
    │                         │
    │ update                  │ reopen
    ▼                         │
┌───────┐                     │
│ ACTIVE│◀────────────────────┘
└───────┘
```

### Conversation States

```
    create           close
┌────────┐  ┌───────────────┐
│        ▼  ▼               │
│     ┌────────┐     ┌──────┴───┐
└─────│ ACTIVE │────▶│ INACTIVE │
      └────────┘     └──────────┘
           │               │
           │ add message   │ reopen
           ▼               │
      ┌────────┐           │
      │ ACTIVE │◀──────────┘
      └────────┘
```

## No Schema Changes Required

All required fields already exist in the Phase II models. The AI-Powered Todo Chatbot feature can be implemented using:

1. **Task model**: Store tasks created via chat
2. **Conversation model**: Track chat sessions
3. **Message model**: Store chat history with tool call metadata

The `tool_calls` JSON field in Message captures MCP tool invocations for audit and debugging.
