# Feature Specification: AI Wealth Companion Chatbot

**Feature Branch**: `005-ai-todo-chatbot`
**Created**: 2026-02-03
**Updated**: 2026-02-03
**Status**: Draft
**Input**: User description: "Phase III: AI Wealth Companion Chatbot with OpenAI ChatKit, Agents SDK, Official MCP SDK"

## Overview

An AI-powered chatbot that serves as the primary interface for the AI Wealth Companion platform. Users can manage their entire financial life through natural language conversation - tracking expenses, creating budgets, analyzing spending patterns, simulating investments, managing tasks/reminders, and checking their financial health. Built using OpenAI's official SDKs: ChatKit for the frontend UI, Agents SDK for backend orchestration, and the official MCP SDK for tool integration.

The chatbot integrates with ALL existing platform capabilities:
- **Spending Agent**: Record transactions, analyze spending patterns
- **Budget Agent**: Create and monitor budgets
- **Investment Agent**: Run investment simulations
- **Task Agent**: Manage financial tasks and reminders
- **Health Score**: Check overall financial wellness

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record Transactions via Chat (Priority: P1)

As a user, I want to record my income and expenses by typing or speaking natural language so that I can quickly track my finances without navigating through forms.

**Why this priority**: Transaction recording is the most frequent user action. Quick capture via chat makes the app immediately useful.

**Independent Test**: Can be fully tested by sending a message like "spent 500 on groceries" and verifying a transaction is created with correct amount, category, and date.

**Acceptance Scenarios**:

1. **Given** I am logged in and on the chat interface, **When** I type "spent 2000 on food today", **Then** an expense transaction is created with amount 2000, category "Food", and today's date
2. **Given** I am using voice input, **When** I say "received salary 85000", **Then** an income transaction is created with amount 85000 and category "Salary"
3. **Given** I type "kharcha 500 kirana pe" (Urdu/Roman Urdu), **When** the message is processed, **Then** an expense of 500 is created with category "Groceries"

---

### User Story 2 - Query Spending & Financial Summary (Priority: P1)

As a user, I want to ask the chatbot about my spending and financial status so that I can understand my finances through conversation.

**Why this priority**: Users need visibility into their financial data. This completes the core record/view cycle.

**Independent Test**: Can be fully tested by asking "show my spending this month" and verifying the response shows accurate totals and breakdowns.

**Acceptance Scenarios**:

1. **Given** I have recorded transactions, **When** I ask "show my spending this month", **Then** the chatbot displays total expenses, income, net, and top categories
2. **Given** I have expenses in multiple categories, **When** I ask "where did my money go?", **Then** I see a breakdown by category with amounts and percentages
3. **Given** I ask "what's my savings rate?", **Then** the chatbot calculates and displays my savings rate with context

---

### User Story 3 - Budget Management via Chat (Priority: P1)

As a user, I want to create and check budgets through chat commands so that I can set spending limits conversationally.

**Why this priority**: Budgets are core to financial planning. Users should be able to create and monitor them easily.

**Independent Test**: Can be tested by saying "set food budget to 15000" and verifying budget creation, then asking "how's my food budget?" to verify status.

**Acceptance Scenarios**:

1. **Given** I want to control spending, **When** I say "set food budget to 15000", **Then** a monthly budget is created for Food category with 15000 limit
2. **Given** I have a food budget of 15000 and spent 12000, **When** I ask "how's my food budget?", **Then** I see "You've spent 12,000 of 15,000 (80%) - Warning: approaching limit"
3. **Given** I have multiple budgets, **When** I ask "show my budgets", **Then** I see all budgets with status (on-track, warning, exceeded)

---

### User Story 4 - Investment Simulation (Priority: P2)

As a user, I want to simulate investment scenarios through chat so that I can make informed decisions about investing.

**Why this priority**: Investment planning is valuable but less frequent than daily transactions/budgets.

**Independent Test**: Can be tested by asking "what if I invest 50000 for 6 months?" and verifying projections are returned.

**Acceptance Scenarios**:

1. **Given** I'm considering investing, **When** I ask "what if I invest 50000 for 12 months?", **Then** I see projections at conservative, moderate, and aggressive risk levels
2. **Given** my current savings pattern, **When** I ask "can I invest 100000?", **Then** I see feasibility analysis based on my finances
3. **Given** I ask in Urdu "50 hazar invest karun to?", **Then** I receive investment projections

---

### User Story 5 - Task & Reminder Management (Priority: P2)

As a user, I want to create and manage financial tasks/reminders through chat so that I don't miss important financial deadlines.

**Why this priority**: Tasks support financial planning but aren't the core transaction/budget functionality.

**Independent Test**: Can be tested by saying "remind me to pay rent on the 5th" and verifying task creation.

**Acceptance Scenarios**:

1. **Given** I need to remember a payment, **When** I say "remind me to pay electricity bill next Friday", **Then** a task is created with title, due date, and category "bills"
2. **Given** I have active tasks, **When** I ask "what tasks are due?", **Then** I see my upcoming and overdue tasks
3. **Given** I have a task "pay rent", **When** I say "mark rent as done", **Then** the task is marked completed

---

### User Story 6 - Financial Health Check (Priority: P2)

As a user, I want to ask about my overall financial health so that I understand how I'm doing financially.

**Why this priority**: Provides valuable insight but requires other features to be meaningful.

**Independent Test**: Can be tested by asking "what's my financial health?" and verifying a score and recommendations are returned.

**Acceptance Scenarios**:

1. **Given** I have financial activity, **When** I ask "what's my financial health score?", **Then** I see a score (0-100) with grade and breakdown
2. **Given** I have budget issues, **When** I ask "how am I doing financially?", **Then** I see personalized recommendations for improvement

---

### User Story 7 - Bilingual Urdu Support (Priority: P3)

As an Urdu-speaking user, I want to interact with the chatbot in Urdu so that I can manage finances in my preferred language.

**Why this priority**: Extends accessibility to Urdu speakers. Core functionality works in English first.

**Independent Test**: Can be tested by switching to Urdu and typing "میرے اخراجات دکھاؤ" and verifying response in Urdu.

**Acceptance Scenarios**:

1. **Given** I have language set to Urdu, **When** I type "میرے اخراجات دکھاؤ", **Then** spending is displayed with Urdu labels
2. **Given** I speak Roman Urdu, **When** I type "aaj 500 kharcha hua khane pe", **Then** expense is recorded correctly
3. **Given** I'm using voice in Urdu, **When** I say Urdu command, **Then** the system recognizes ur-PK locale

---

### Edge Cases

- What happens when user's message is ambiguous (e.g., "spent some money")?
  - Chatbot asks for clarification: "How much did you spend and on what?"
- How does the system handle amounts without currency (e.g., "spent 500")?
  - System assumes PKR by default
- What if user asks about a category that doesn't exist?
  - System maps to closest category or suggests options
- How does voice recognition handle background noise?
  - System shows transcription for user confirmation before processing
- What happens when user is off-topic (e.g., "what's the weather?")?
  - Chatbot redirects: "I'm your financial assistant. I can help with spending, budgets, investments, and tasks."

## Requirements *(mandatory)*

### Functional Requirements

**Chat Interface**
- **FR-001**: System MUST provide a chat interface using OpenAI ChatKit component
- **FR-002**: System MUST support both text input and voice input
- **FR-003**: System MUST display chat history within the current session
- **FR-004**: System MUST show typing indicator while AI is processing
- **FR-005**: System MUST persist conversation history for future reference

**Transaction Management**
- **FR-006**: System MUST parse natural language to extract amount, category, and date from messages
- **FR-007**: System MUST handle both income and expense transactions via chat
- **FR-008**: System MUST support Urdu amount formats ("15 hazar", "500 rupay")
- **FR-009**: System MUST auto-categorize transactions based on keywords
- **FR-010**: System MUST confirm transaction creation with details shown to user

**Financial Queries**
- **FR-011**: System MUST provide spending summary when asked variants of "show spending"
- **FR-012**: System MUST show category breakdown with percentages
- **FR-013**: System MUST calculate and display savings rate
- **FR-014**: System MUST show trends when asked about spending patterns

**Budget Management**
- **FR-015**: System MUST create budgets via natural language (e.g., "set food budget to 15000")
- **FR-016**: System MUST report budget status (spent/remaining/percentage)
- **FR-017**: System MUST identify budgets as on-track, warning, or exceeded
- **FR-018**: System MUST provide budget coaching and recommendations

**Investment Simulation**
- **FR-019**: System MUST run investment projections at multiple risk levels
- **FR-020**: System MUST assess investment feasibility against current finances
- **FR-021**: System MUST include financial disclaimer in investment responses

**Task Management**
- **FR-022**: System MUST create tasks with title, due date, priority, category
- **FR-023**: System MUST parse relative dates ("tomorrow", "next Friday")
- **FR-024**: System MUST list active, overdue, and completed tasks
- **FR-025**: System MUST mark tasks complete via chat commands

**Financial Health**
- **FR-026**: System MUST calculate financial health score (0-100)
- **FR-027**: System MUST provide health grade (Excellent/Good/Fair/Needs Improvement)
- **FR-028**: System MUST give personalized recommendations

**AI Agent Integration**
- **FR-029**: System MUST use OpenAI Agents SDK for chat processing
- **FR-030**: System MUST expose all operations as MCP tools using official MCP SDK
- **FR-031**: System MUST route queries to appropriate subagent (Spending/Budget/Investment/Task)
- **FR-032**: System MUST handle off-topic messages gracefully

**Language Support**
- **FR-033**: System MUST support English and Urdu languages
- **FR-034**: System MUST detect input language and respond accordingly
- **FR-035**: System MUST support Roman Urdu keywords (kharcha, kamai, bajat)
- **FR-036**: System MUST support Urdu voice recognition (ur-PK locale)

### Key Entities

- **Transaction**: Income or expense with amount, category, date, wallet
- **Budget**: Monthly spending limit for a category
- **Task**: A user's todo item with title, due date, priority, category
- **Conversation**: A chat session containing messages between user and AI
- **Message**: Individual chat message with content, intent, tool_calls, confidence
- **Agent**: AI component that processes messages (SpendingAgent, BudgetAgent, InvestmentAgent, TaskAgent)
- **MCP Tool**: Functions exposed to the AI agent for executing operations

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can record a transaction via chat in under 3 seconds
- **SC-002**: Transaction parsing from natural language succeeds 90% of the time
- **SC-003**: System correctly extracts amounts from text (including "15k", "15 thousand") with 95% accuracy
- **SC-004**: Users can view spending summary in under 2 seconds
- **SC-005**: Budget creation via chat works with 90% success rate
- **SC-006**: Investment simulations return in under 5 seconds
- **SC-007**: Chat interface loads and becomes interactive within 3 seconds
- **SC-008**: System handles 100 concurrent chat sessions without degradation
- **SC-009**: Off-topic detection correctly redirects 95% of unrelated queries
- **SC-010**: Urdu/Roman Urdu support covers all core operations

## Assumptions

- Users are authenticated before accessing the chat interface
- The existing database schema from Phase II remains unchanged
- OpenAI API key is configured and has sufficient quota
- Voice input uses browser's Web Speech API
- ChatKit requires domain allowlisting in OpenAI dashboard
- Existing subagents and MCP tools are leveraged (not replaced)

## Out of Scope

- Direct bank account connections
- Bill pay automation
- Multi-user/family financial management
- Offline mode / local storage
- Rich media attachments in chat
- External calendar integration
- Real-time stock/investment data

## Dependencies

- OpenAI ChatKit React SDK (`@openai/chatkit-react`)
- OpenAI Agents SDK (`openai-agents`)
- Official MCP SDK (`mcp`)
- Existing subagents: SpendingAgent, BudgetAgent, InvestmentAgent, TaskAgent
- Existing MCP tools: create_budget, add_transaction, get_financial_summary, etc.
- Existing services: TransactionService, BudgetService, TaskService
- Existing authentication system from Phase II
