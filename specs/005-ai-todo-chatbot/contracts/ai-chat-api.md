# API Contract: AI Chat Endpoints

**Feature**: 005-ai-todo-chatbot
**Date**: 2026-02-03
**Base URL**: `/api/v1/ai`

## Overview

These endpoints power the AI-powered todo chatbot. Most endpoints already exist from Phase II; this document specifies enhancements and new MCP tools.

---

## Chat Endpoint

### POST `/api/v1/ai/chat`

Send a message to the AI chatbot and receive a response.

**Authentication**: Required (JWT Bearer token)

**Request Body**:
```json
{
  "message": "remind me to pay rent tomorrow",
  "conversation_id": "uuid-optional",
  "language": "en",
  "input_method": "text"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message | string | Yes | User's message |
| conversation_id | UUID | No | Existing conversation ID (creates new if omitted) |
| language | string | No | "en" or "ur" (default: "en") |
| input_method | string | No | "text" or "voice" (default: "text") |

**Response (200 OK)**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "role": "assistant",
    "content": "I've created a task to pay rent, due tomorrow (February 4th).",
    "content_ur": "میں نے کل (4 فروری) کے لیے کرایہ ادا کرنے کا کام بنا دیا ہے۔",
    "intent": "create_task",
    "tool_calls": [
      {
        "tool": "create_task",
        "arguments": {
          "title": "Pay rent",
          "due_date": "2026-02-04",
          "category": "bills"
        },
        "result": {
          "status": "success",
          "task_id": "550e8400-e29b-41d4-a716-446655440002"
        }
      }
    ],
    "confidence": 0.95,
    "processing_time_ms": 450
  }
}
```

**Error Responses**:

| Status | Code | Description |
|--------|------|-------------|
| 400 | INVALID_MESSAGE | Message is empty or too long |
| 401 | UNAUTHORIZED | Invalid or missing token |
| 429 | RATE_LIMITED | Too many requests |
| 500 | INTERNAL_ERROR | Server error |

---

## MCP Tools

All tools are registered with the Official MCP SDK and callable by the OpenAI Agents SDK agent.

### create_task

Create a new task for the user.

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "Task title (required)"
    },
    "priority": {
      "type": "string",
      "enum": ["high", "medium", "low"],
      "default": "medium"
    },
    "category": {
      "type": "string",
      "enum": ["bills", "savings", "review", "investment", "budget", "other"],
      "default": "other"
    },
    "due_date": {
      "type": "string",
      "description": "Due date in YYYY-MM-DD format"
    }
  },
  "required": ["title"]
}
```

**Response**:
```json
{
  "status": "success",
  "task_id": "550e8400-e29b-41d4-a716-446655440002",
  "title": "Pay rent",
  "priority": "medium",
  "category": "bills",
  "due_date": "2026-02-04",
  "message": "Task created: Pay rent (due 2026-02-04)"
}
```

---

### list_tasks

List user's tasks filtered by status.

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["active", "overdue", "completed", "all"],
      "default": "active"
    }
  }
}
```

**Response**:
```json
{
  "count": 3,
  "status_filter": "active",
  "tasks": [
    {
      "id": "uuid",
      "title": "Pay rent",
      "priority": "medium",
      "category": "bills",
      "due_date": "2026-02-04",
      "is_completed": false
    }
  ]
}
```

---

### complete_task (NEW)

Mark a task as completed.

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "description": "Task UUID"
    },
    "title_match": {
      "type": "string",
      "description": "Partial title to match (if task_id not provided)"
    }
  }
}
```

**Response**:
```json
{
  "status": "success",
  "task_id": "uuid",
  "title": "Pay rent",
  "message": "Task 'Pay rent' marked as completed",
  "completed_at": "2026-02-03T14:30:00Z"
}
```

**Error Response** (task not found):
```json
{
  "status": "error",
  "error": "NOT_FOUND",
  "message": "No task found matching 'electricity bill'. Did you mean one of: 'Pay rent', 'Review budget'?"
}
```

---

### update_task (NEW)

Update task fields (due date, priority, title).

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "description": "Task UUID"
    },
    "title_match": {
      "type": "string",
      "description": "Partial title to match"
    },
    "new_title": {
      "type": "string"
    },
    "new_due_date": {
      "type": "string",
      "description": "New due date in YYYY-MM-DD"
    },
    "new_priority": {
      "type": "string",
      "enum": ["high", "medium", "low"]
    }
  }
}
```

**Response**:
```json
{
  "status": "success",
  "task_id": "uuid",
  "title": "Pay rent",
  "changes": {
    "due_date": {
      "old": "2026-02-04",
      "new": "2026-02-11"
    }
  },
  "message": "Task 'Pay rent' updated: due date changed to February 11th"
}
```

---

### get_task_summary

Get summary counts of user's tasks.

**Parameters**: None

**Response**:
```json
{
  "total": 10,
  "active": 5,
  "completed": 3,
  "overdue": 2,
  "due_soon": 1,
  "by_category": {
    "bills": 3,
    "savings": 2,
    "review": 2,
    "other": 3
  },
  "by_priority": {
    "high": 2,
    "medium": 5,
    "low": 3
  }
}
```

---

## Existing Endpoints (No Changes)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/ai/conversations` | GET | List user's conversations |
| `/api/v1/ai/conversations/{id}/messages` | GET | Get messages in conversation |
| `/api/v1/ai/language` | POST | Set language preference |
| `/api/v1/ai/health-score` | GET | Get financial health score |
| `/api/v1/ai/insights` | GET | Get AI insights |

---

## WebSocket (Future Enhancement)

For real-time streaming responses, a WebSocket endpoint may be added:

```
WS /api/v1/ai/chat/stream
```

This is **optional** for Phase III and can use HTTP long-polling initially.

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| POST /chat | 30 requests/minute |
| GET /* | 100 requests/minute |

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| INVALID_MESSAGE | 400 | Empty or malformed message |
| INVALID_LANGUAGE | 400 | Unsupported language code |
| CONVERSATION_NOT_FOUND | 404 | Conversation ID doesn't exist |
| TASK_NOT_FOUND | 404 | Task ID or title match failed |
| AMBIGUOUS_TASK | 400 | Multiple tasks match, clarification needed |
| UNAUTHORIZED | 401 | Invalid or expired token |
| RATE_LIMITED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Server error |
