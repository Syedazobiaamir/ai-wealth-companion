# API Contracts: AI Financial Assistant

**Branch**: `004-ai-financial-assistant` | **Date**: 2026-02-01
**Base path**: `/api/v1/ai`

## Endpoints

### POST /api/v1/ai/chat

Send a message to the AI assistant and receive a response.

**Auth**: JWT required

**Request**:
```json
{
  "message": "Add grocery budget 15,000",
  "conversation_id": "uuid-or-null",
  "language": "en",
  "input_method": "text"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message | string | Yes | User's natural language input |
| conversation_id | string (UUID) | No | Existing conversation ID; null creates new |
| language | string | No | Override language: "en" or "ur". Default: auto-detect |
| input_method | string | No | "text" or "voice". Default: "text" |

**Response 200**:
```json
{
  "conversation_id": "abc-123",
  "message_id": "msg-456",
  "response": "Budget created for Food category: PKR 15,000 for February 2026.",
  "response_ur": "فوڈ کیٹیگری کے لیے بجٹ بنایا گیا: ₨15,000 فروری 2026",
  "intent": "create",
  "entities": {
    "category": "Food",
    "amount": 15000,
    "currency": "PKR"
  },
  "tool_calls": [
    {
      "tool": "create_budget",
      "status": "success",
      "result_summary": "Budget created: Food PKR 15,000"
    }
  ],
  "confidence": 0.95,
  "language_detected": "en"
}
```

**Response 400**: Invalid input
**Response 401**: Unauthorized
**Response 429**: Rate limited (max 30 messages/minute)

---

### GET /api/v1/ai/conversations

List user's conversations.

**Auth**: JWT required

**Query params**:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| limit | int | 20 | Max conversations to return |
| offset | int | 0 | Pagination offset |
| active_only | bool | true | Filter to active conversations |

**Response 200**:
```json
{
  "conversations": [
    {
      "id": "abc-123",
      "title": "Budget Planning",
      "language": "en",
      "message_count": 5,
      "is_active": true,
      "created_at": "2026-02-01T10:00:00Z",
      "updated_at": "2026-02-01T10:05:00Z"
    }
  ],
  "total": 1
}
```

---

### GET /api/v1/ai/conversations/{conversation_id}/messages

Get messages in a conversation.

**Auth**: JWT required

**Query params**:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| limit | int | 50 | Max messages to return |
| before | string (UUID) | null | Messages before this message ID |

**Response 200**:
```json
{
  "messages": [
    {
      "id": "msg-456",
      "role": "user",
      "content": "Add grocery budget 15,000",
      "intent": "create",
      "input_method": "text",
      "created_at": "2026-02-01T10:00:00Z"
    },
    {
      "id": "msg-789",
      "role": "assistant",
      "content": "Budget created for Food category: PKR 15,000 for February 2026.",
      "content_ur": "فوڈ کیٹیگری کے لیے بجٹ بنایا گیا",
      "tool_calls": [...],
      "confidence": 0.95,
      "processing_time_ms": 1200,
      "created_at": "2026-02-01T10:00:01Z"
    }
  ],
  "has_more": false
}
```

---

### GET /api/v1/ai/insights

Get AI-generated financial insights for the dashboard.

**Auth**: JWT required

**Query params**:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| limit | int | 5 | Max insights to return |
| type | string | null | Filter: spending_pattern, budget_recommendation, saving_tip, anomaly |
| severity | string | null | Filter: info, suggestion, warning, alert |

**Response 200**:
```json
{
  "insights": [
    {
      "id": "ins-001",
      "type": "budget_recommendation",
      "severity": "warning",
      "title": "Entertainment Overspending",
      "content": "Your entertainment spending is 40% above your budget this month.",
      "content_ur": "آپ کے تفریح کے اخراجات اس مہینے بجٹ سے 40% زیادہ ہیں",
      "action_suggestion": "Consider reducing streaming subscriptions",
      "data": {
        "category": "Entertainment",
        "budget": 5000,
        "spent": 7000,
        "percentage": 140
      },
      "confidence": 0.88,
      "created_at": "2026-02-01T08:00:00Z"
    }
  ]
}
```

---

### GET /api/v1/ai/health-score

Get the user's monthly financial health score.

**Auth**: JWT required

**Query params**:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| month | int | current | Month (1-12) |
| year | int | current | Year |

**Response 200**:
```json
{
  "overall_score": 72,
  "grade": "Good",
  "components": {
    "budget_adherence": { "score": 65, "weight": 0.4, "detail": "3 of 5 budgets within limit" },
    "savings_rate": { "score": 80, "weight": 0.3, "detail": "Saving 20% of income" },
    "spending_consistency": { "score": 70, "weight": 0.2, "detail": "Moderate daily variation" },
    "goal_progress": { "score": 85, "weight": 0.1, "detail": "2 goals on track" }
  },
  "recommendations": [
    "Reduce Food spending by PKR 3,000 to meet budget",
    "Your savings rate improved 5% from last month"
  ],
  "month": 2,
  "year": 2026,
  "trend": "improving"
}
```

---

### POST /api/v1/ai/simulate-investment

Run an investment simulation.

**Auth**: JWT required

**Request**:
```json
{
  "investment_amount": 10000,
  "time_horizon_months": 12,
  "currency": "PKR"
}
```

**Response 200**:
```json
{
  "simulation_id": "sim-001",
  "investment_amount": 10000,
  "time_horizon_months": 12,
  "projections": {
    "conservative": { "return_rate": 0.05, "projected_value": 10500, "monthly_gain": 42 },
    "moderate": { "return_rate": 0.08, "projected_value": 10800, "monthly_gain": 67 },
    "aggressive": { "return_rate": 0.12, "projected_value": 11200, "monthly_gain": 100 }
  },
  "feasibility": {
    "score": 0.75,
    "monthly_savings_available": 15000,
    "monthly_savings_needed": 10000,
    "verdict": "Feasible - you can invest this amount based on current savings pattern"
  },
  "disclaimer": "This is an educational simulation only. Past performance does not guarantee future results. Consult a licensed financial advisor before making investment decisions."
}
```

---

### POST /api/v1/ai/language

Set user's preferred AI language.

**Auth**: JWT required

**Request**:
```json
{
  "language": "ur"
}
```

**Response 200**:
```json
{
  "language": "ur",
  "message": "Language preference updated to Urdu"
}
```

## MCP Tool Definitions

These tools are exposed via the MCP server for agent consumption:

| Tool | Description | Input | Output |
|------|-------------|-------|--------|
| `get_financial_summary` | User's financial overview | user_id, period | income, expenses, savings, by_category |
| `create_budget` | Create a monthly budget | category, amount, month, year | budget object |
| `add_transaction` | Record a transaction | type, amount, category, wallet, date, note | transaction object |
| `analyze_spending` | Analyze spending patterns | user_id, period, category? | trends, anomalies, comparisons |
| `simulate_investment` | Run investment projection | amount, months | projections at 3 risk levels |
| `generate_dashboard_metrics` | Dashboard data for AI cards | user_id | scores, alerts, recommendations |

## Error Response Format

All endpoints return errors in this format:
```json
{
  "detail": "Human-readable error message",
  "code": "MACHINE_READABLE_CODE",
  "context": {}
}
```

| Code | HTTP Status | Description |
|------|-------------|-------------|
| INVALID_MESSAGE | 400 | Empty or malformed message |
| CONVERSATION_NOT_FOUND | 404 | Invalid conversation_id |
| RATE_LIMITED | 429 | Too many requests |
| AI_PROCESSING_ERROR | 500 | Agent/model failure |
| TOOL_EXECUTION_ERROR | 500 | MCP tool call failed |
