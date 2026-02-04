# Data Model: AI Financial Assistant (Phase III)

**Branch**: `004-ai-financial-assistant` | **Date**: 2026-02-01

## Existing Entities (Reused from Phase II)

These models already exist in `backend/src/models/` and require NO changes:

| Entity | Table | Purpose |
|--------|-------|---------|
| User | users | Authentication, preferences, currency/locale |
| Transaction | transactions | Income/expense records with categories, wallets, tags |
| Wallet | wallets | Financial accounts (bank, cash, credit, savings, investment) |
| Budget | budgets | Monthly spending limits per category |
| Category | category | Transaction classification with emoji |
| Goal | goals | Savings targets with progress tracking |
| Task | tasks | Financial reminders and to-dos |
| MonthlySnapshot | monthly_snapshots | Pre-computed monthly financial summaries |
| InsightCache | insight_cache | AI-generated insights with Urdu translation |
| AgentMemory | agent_memory | AI agent session context and memory |
| EventLog | event_logs | Audit trail for all system events |

## New Entities (Phase III)

### Conversation

Represents an ongoing chat session between a user and the AI assistant.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique conversation identifier |
| user_id | UUID | FK → users.id, indexed | Owner of the conversation |
| title | String(200) | Optional | Auto-generated conversation title |
| language | String(5) | Default: "en", enum: en/ur | Active language preference |
| is_active | Boolean | Default: true | Whether conversation is ongoing |
| message_count | Integer | Default: 0 | Total messages in conversation |
| created_at | DateTime | Auto | Session start time |
| updated_at | DateTime | Auto | Last activity time |

**Relationships**: One user → many conversations. One conversation → many messages.

### Message

An individual exchange within a conversation.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique message identifier |
| conversation_id | UUID | FK → conversations.id, indexed | Parent conversation |
| role | String(20) | Enum: user/assistant/system | Message sender type |
| content | Text | Required | Message text content |
| content_ur | Text | Optional | Urdu translation of content |
| intent | String(50) | Optional | Classified intent (query, create, update, analyze, predict) |
| entities | JSON | Optional | Extracted structured data (amounts, categories, dates) |
| tool_calls | JSON | Optional | MCP tool calls made for this message |
| confidence | Float | Optional, 0.0-1.0 | Intent classification confidence |
| input_method | String(10) | Default: "text", enum: text/voice | How the message was entered |
| processing_time_ms | Integer | Optional | Time taken to generate response |
| created_at | DateTime | Auto | Message timestamp |

**Relationships**: One conversation → many messages. Messages ordered by created_at.

### FinancialHealthScore

Monthly computed financial health metric.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique score identifier |
| user_id | UUID | FK → users.id, indexed | Score owner |
| month | Integer | 1-12 | Score month |
| year | Integer | Required | Score year |
| overall_score | Integer | 0-100 | Composite health score |
| budget_adherence | Float | 0.0-1.0 | Budget adherence component |
| savings_rate | Float | -1.0-1.0 | Savings rate component |
| spending_consistency | Float | 0.0-1.0 | Spending consistency component |
| goal_progress | Float | 0.0-1.0 | Goal progress component |
| factors | JSON | Required | Detailed breakdown of score factors |
| recommendations | JSON | Optional | AI-generated improvement suggestions |
| created_at | DateTime | Auto | Computation timestamp |

**Constraints**: Unique on (user_id, month, year).

### InvestmentSimulation

Results of a predictive investment scenario.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique simulation identifier |
| user_id | UUID | FK → users.id, indexed | Simulation owner |
| conversation_id | UUID | FK → conversations.id, optional | Related conversation |
| investment_amount | Decimal(15,2) | Required | Amount to invest |
| time_horizon_months | Integer | Required | Investment duration |
| conservative_projection | Decimal(15,2) | Required | 5% annual return projection |
| moderate_projection | Decimal(15,2) | Required | 8% annual return projection |
| aggressive_projection | Decimal(15,2) | Required | 12% annual return projection |
| feasibility_score | Float | 0.0-1.0 | Based on user's current finances |
| monthly_savings_needed | Decimal(15,2) | Required | Required monthly savings |
| assumptions | JSON | Required | Model assumptions and disclaimers |
| created_at | DateTime | Auto | Simulation timestamp |

## Entity Relationship Summary

```
User (1) ──→ (N) Conversation ──→ (N) Message
User (1) ──→ (N) FinancialHealthScore
User (1) ──→ (N) InvestmentSimulation
User (1) ──→ (N) InsightCache         [existing]
User (1) ──→ (N) AgentMemory          [existing]
User (1) ──→ (N) Transaction          [existing]
User (1) ──→ (N) Wallet               [existing]
User (1) ──→ (N) Budget               [existing]
User (1) ──→ (N) Goal                 [existing]

Conversation (1) ──→ (N) InvestmentSimulation
```

## State Transitions

### Conversation Lifecycle
```
Created → Active → Inactive (after 30 min idle or user closes)
```

### Message Processing Pipeline
```
Received → Intent Classified → Entities Extracted → Tool Called → Response Generated
```

### Insight Lifecycle (existing InsightCache)
```
Generated → Active → Viewed → Dismissed/Expired
```
