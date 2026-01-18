# Feature Specification: Phase I Financial Core

**Feature Branch**: `002-phase1-financial-core`
**Created**: 2026-01-18
**Status**: Draft
**Input**: User description: "Phase I Financial Core - Transactions, Budgeting, and In-Memory Storage layer for CLI application"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and Manage Transactions (Priority: P1)

As a user, I want to create, view, update, and delete financial transactions so that I can track my income and expenses.

**Why this priority**: Transactions are the foundational data entity. Without transaction management, budgeting and reporting have no data to work with.

**Independent Test**: Can be fully tested by creating sample transactions, viewing them in a list, updating amounts/categories, and deleting entries.

**Acceptance Scenarios**:

1. **Given** the application is running, **When** I create a new expense transaction with amount 500 and category "Food", **Then** the transaction is stored and appears in the transaction list.
2. **Given** a transaction exists with ID 1, **When** I update its amount to 750, **Then** the updated amount is reflected when viewing the transaction.
3. **Given** a transaction exists with ID 2, **When** I delete it, **Then** the transaction no longer appears in the list.
4. **Given** multiple transactions exist, **When** I request all transactions, **Then** a complete list is returned with all transaction details.

---

### User Story 2 - Filter and Sort Transactions (Priority: P2)

As a user, I want to filter transactions by category or date and sort them by amount so that I can analyze my spending patterns.

**Why this priority**: Filtering and sorting enable meaningful analysis of transaction data, building on the P1 foundation.

**Independent Test**: Can be tested by creating transactions with different categories/dates/amounts, then filtering and sorting to verify correct results.

**Acceptance Scenarios**:

1. **Given** transactions exist in categories "Food" and "Rent", **When** I filter by category "Food", **Then** only Food transactions are returned.
2. **Given** transactions exist across multiple dates, **When** I filter by date range 2026-01-01 to 2026-01-31, **Then** only transactions within that range are returned.
3. **Given** transactions exist with amounts 100, 500, and 250, **When** I sort by amount descending, **Then** transactions are returned in order: 500, 250, 100.

---

### User Story 3 - Set and Monitor Budgets (Priority: P3)

As a user, I want to set monthly spending limits per category and see my progress against those limits so that I can control my spending.

**Why this priority**: Budgeting provides actionable insights but depends on having transactions to track against.

**Independent Test**: Can be tested by setting a budget for a category, adding expense transactions, and verifying budget status shows correct usage.

**Acceptance Scenarios**:

1. **Given** the "Food" category exists, **When** I set a monthly budget of 1000 for Food, **Then** the budget is stored and can be retrieved.
2. **Given** a Food budget of 1000 exists and I have 800 in Food expenses, **When** I check budget status, **Then** it shows 800/1000 used (80%).
3. **Given** a Food budget of 1000 exists and I have 1200 in Food expenses, **When** I check budget status, **Then** it shows an overspend warning indicating 200 over budget.
4. **Given** a Food budget of 1000 exists, **When** I check remaining balance, **Then** it shows the correct remaining amount.

---

### User Story 4 - Data Persistence Within Session (Priority: P4)

As a user, I want my data to remain consistent throughout my session so that I can trust the information displayed.

**Why this priority**: Data integrity is essential but is an infrastructure concern that supports other features.

**Independent Test**: Can be tested by performing multiple operations and verifying data consistency throughout the session.

**Acceptance Scenarios**:

1. **Given** I create a transaction, **When** I view transactions multiple times during the session, **Then** the transaction consistently appears.
2. **Given** I have created transactions and budgets, **When** I restart the application, **Then** all data is cleared (Phase I in-memory constraint).
3. **Given** multiple operations occur during a session, **When** I query data, **Then** all changes are reflected accurately without data loss.

---

### Edge Cases

- What happens when filtering returns no results? System returns an empty list with a message indicating no matches found.
- What happens when setting a budget for a non-existent category? System rejects with an error indicating the category must exist first.
- What happens when creating a transaction with amount zero or negative? System rejects with a validation error.
- What happens when updating a non-existent transaction? System returns an error indicating the transaction was not found.
- What happens when deleting an already-deleted transaction? System returns an error indicating the transaction was not found.
- What happens when budget calculation encounters no transactions? Budget shows 0% used with full amount remaining.

## Requirements *(mandatory)*

### Functional Requirements

**Transaction Management**
- **FR-001**: System MUST allow creating transactions with id, type (income/expense), amount, category, note, date, and optional recurring flag.
- **FR-002**: System MUST allow updating any field of an existing transaction by its ID.
- **FR-003**: System MUST allow deleting a transaction by its ID.
- **FR-004**: System MUST allow listing all transactions.
- **FR-005**: System MUST allow filtering transactions by category.
- **FR-006**: System MUST allow filtering transactions by date or date range.
- **FR-007**: System MUST allow sorting transactions by amount (ascending or descending).
- **FR-008**: System MUST validate that transaction amounts are greater than zero.
- **FR-009**: System MUST auto-generate unique transaction IDs.

**Budgeting**
- **FR-010**: System MUST allow setting a monthly budget amount for a category.
- **FR-011**: System MUST track total spending per category against the budget.
- **FR-012**: System MUST display remaining budget balance per category.
- **FR-013**: System MUST warn when spending exceeds the budget for a category.
- **FR-014**: System MUST allow updating budget amounts for existing categories.

**Storage Layer**
- **FR-015**: System MUST store all transactions in memory during the session.
- **FR-016**: System MUST store all categories in memory during the session.
- **FR-017**: System MUST store all budgets in memory during the session.
- **FR-018**: System MUST clear all data when the application restarts.
- **FR-019**: Storage layer MUST NOT contain CLI/presentation code.
- **FR-020**: Storage layer MUST NOT contain business logic (validation, calculations).
- **FR-021**: Storage layer MUST follow the repository pattern for data access.

### Key Entities

- **Transaction**: Represents a financial event. Attributes: unique ID, type (income/expense), amount (positive number), category reference, note (optional text), date (YYYY-MM-DD), recurring flag (optional boolean).
- **Category**: Represents a classification for transactions. Attributes: unique name.
- **Budget**: Represents a spending limit for a category. Attributes: category reference, monthly limit amount.

## Architectural Constraints

Per Phase I Constitution:
- **In-Memory Only**: No database or file persistence. Data exists only during application runtime.
- **Repository Pattern**: Storage access MUST use repository interfaces to enable future database swap.
- **Layer Separation**: Storage layer is isolated from CLI and business logic layers.
- **Deterministic Operations**: All operations produce predictable, reproducible results.

## Assumptions

- Transaction IDs are auto-generated integers starting from 1.
- Categories must be created before transactions can reference them (referential integrity).
- Budgets are per-category and monthly (conceptually, though data resets on restart).
- Date format is YYYY-MM-DD for all date inputs.
- Amount values are numeric without currency specification.
- Default categories (Food, Rent, Utilities, Salary, Investment) are pre-loaded on startup.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a new transaction in under 5 seconds.
- **SC-002**: Users can view all transactions within 1 second of requesting.
- **SC-003**: Filter operations return correct results 100% of the time when criteria match data.
- **SC-004**: Budget status calculations accurately reflect total category spending.
- **SC-005**: Overspend warnings appear immediately when budget threshold is exceeded.
- **SC-006**: All CRUD operations (create, read, update, delete) complete successfully on valid input.
- **SC-007**: 100% of validation errors display clear messages explaining the issue.
- **SC-008**: Data remains consistent throughout the entire session without corruption.
- **SC-009**: Application restart results in complete data reset (Phase I requirement).
