# Feature Specification: CLI Finance Manager

**Feature Branch**: `001-cli-finance-manager`
**Created**: 2026-01-18
**Status**: Draft
**Input**: User description: "CLI Application for managing finances with transaction CRUD, categories, budgets, search/filter, and sorting"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add and View Transactions (Priority: P1)

As a user, I want to add financial transactions and view them in a formatted table so that I can track my income and expenses.

**Why this priority**: Transaction management is the core functionality. Without the ability to add and view transactions, no other feature has value.

**Independent Test**: Can be fully tested by adding sample transactions via CLI commands and verifying they appear in the transaction list with correct formatting.

**Acceptance Scenarios**:

1. **Given** the application is running, **When** I enter `add expense 500 Food`, **Then** the system confirms the transaction was added with an expense emoji and displays the transaction details.
2. **Given** multiple transactions exist, **When** I enter `list`, **Then** the system displays all transactions in a formatted table with columns for ID, Type, Amount, Category, Date, and Recurring status.
3. **Given** I add an income transaction, **When** I view the list, **Then** income transactions display with a green indicator.
4. **Given** I enter an invalid amount (e.g., -50 or "abc"), **When** the system validates input, **Then** an error message is displayed and the transaction is not added.

---

### User Story 2 - Update and Delete Transactions (Priority: P2)

As a user, I want to modify or remove transactions so that I can correct mistakes or remove unwanted entries.

**Why this priority**: After adding transactions, users need the ability to correct errors. This completes basic CRUD operations.

**Independent Test**: Can be tested by adding a transaction, updating its amount/category, and verifying changes appear. Can also delete a transaction and verify it no longer appears in the list.

**Acceptance Scenarios**:

1. **Given** a transaction with ID 1 exists, **When** I enter `update 1 amount 750`, **Then** the system confirms the update and shows the modified transaction.
2. **Given** a transaction with ID 2 exists, **When** I enter `delete 2`, **Then** the system asks for confirmation, and upon confirmation, removes the transaction and confirms deletion.
3. **Given** I try to update a non-existent transaction ID, **When** the system processes the command, **Then** an error message indicates the transaction was not found.

---

### User Story 3 - Manage Categories (Priority: P3)

As a user, I want to create and assign categories to transactions so that I can organize my finances by type of expense or income.

**Why this priority**: Categories enable organization and are required for meaningful filtering and budget tracking.

**Independent Test**: Can be tested by creating a category, assigning it to a new transaction, and verifying the category appears in transaction details.

**Acceptance Scenarios**:

1. **Given** the application is running, **When** I enter `category add Groceries`, **Then** the system confirms the category was created.
2. **Given** "Groceries" category exists, **When** I add a transaction with `add expense 100 Groceries`, **Then** the transaction is associated with the Groceries category.
3. **Given** I try to add a duplicate category, **When** the system validates, **Then** an error message indicates the category already exists.

---

### User Story 4 - Set and Track Budgets (Priority: P4)

As a user, I want to set spending limits for categories so that I can monitor my spending against my budget.

**Why this priority**: Budgets provide financial awareness but depend on categories and transactions being in place first.

**Independent Test**: Can be tested by setting a budget for a category, adding expenses to that category, and viewing budget status.

**Acceptance Scenarios**:

1. **Given** the "Food" category exists, **When** I enter `budget set Food 1000`, **Then** the system confirms a budget of 1000 is set for Food.
2. **Given** a budget of 1000 is set for Food and 800 in Food expenses exist, **When** I enter `budget status`, **Then** the system shows Food: 800/1000 (80% used).
3. **Given** expenses exceed the budget, **When** I view budget status, **Then** the system displays a warning indicator showing the budget is exceeded.

---

### User Story 5 - Search and Filter Transactions (Priority: P5)

As a user, I want to search and filter transactions by various criteria so that I can find specific transactions quickly.

**Why this priority**: Search/filter becomes valuable once users have accumulated multiple transactions.

**Independent Test**: Can be tested by adding multiple transactions with different attributes, then filtering by category, date range, or amount range.

**Acceptance Scenarios**:

1. **Given** transactions exist in multiple categories, **When** I enter `filter category Food`, **Then** only transactions in the Food category are displayed.
2. **Given** transactions exist across different dates, **When** I enter `filter date 2026-01-01 2026-01-31`, **Then** only transactions within that date range are displayed.
3. **Given** transactions exist with various amounts, **When** I enter `search 500`, **Then** transactions with amount 500 are displayed.

---

### User Story 6 - Sort Transactions (Priority: P6)

As a user, I want to sort transactions by date or amount so that I can view them in a meaningful order.

**Why this priority**: Sorting enhances usability but is not required for basic functionality.

**Independent Test**: Can be tested by adding transactions with different dates/amounts and verifying sort order changes correctly.

**Acceptance Scenarios**:

1. **Given** multiple transactions exist, **When** I enter `sort date asc`, **Then** transactions are displayed oldest first.
2. **Given** multiple transactions exist, **When** I enter `sort amount desc`, **Then** transactions are displayed highest amount first.
3. **Given** no sort is specified, **When** I view transactions, **Then** they display in order of creation (most recent first).

---

### Edge Cases

- What happens when the user enters an empty command? System displays available commands.
- What happens when the user enters an unknown command? System displays "Unknown command" and shows help.
- What happens when filtering returns no results? System displays "No transactions match your criteria."
- What happens when the user tries to set a negative budget? System rejects with validation error.
- What happens when a transaction date is in invalid format? System rejects with "Invalid date format. Use YYYY-MM-DD."

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow adding transactions with type (income/expense), amount, and category via CLI commands.
- **FR-002**: System MUST validate that transaction amounts are greater than zero.
- **FR-003**: System MUST validate that transaction dates follow YYYY-MM-DD format.
- **FR-004**: System MUST validate that transaction types are one of: Income, Expense, or Transfer.
- **FR-005**: System MUST display transactions in a formatted table using the `tabulate` library.
- **FR-006**: System MUST allow updating transaction amount, category, date, or type by transaction ID.
- **FR-007**: System MUST allow deleting transactions by ID with confirmation prompt.
- **FR-008**: System MUST allow creating custom categories.
- **FR-009**: System MUST enforce unique category names.
- **FR-010**: System MUST allow setting budget limits per category.
- **FR-011**: System MUST display budget utilization as percentage when viewing budget status.
- **FR-012**: System MUST allow filtering transactions by category, date range, or amount.
- **FR-013**: System MUST allow sorting transactions by date or amount in ascending or descending order.
- **FR-014**: System MUST display color-coded output using emojis for transaction types.
- **FR-015**: System MUST provide confirmation messages for all successful operations.
- **FR-016**: System MUST provide clear error messages for all validation failures.
- **FR-017**: System MUST display a help menu when the user enters `help` or an invalid command.
- **FR-018**: System MUST support marking transactions as recurring (Yes/No flag).
- **FR-019**: System MUST store all data in-memory only; data resets when application restarts.
- **FR-020**: System MUST provide a main menu with numbered options for navigation.

### Key Entities

- **Transaction**: Represents a financial event. Attributes: unique ID, type (Income/Expense/Transfer), amount (positive number), date (YYYY-MM-DD), category reference, recurring flag (Yes/No).
- **Category**: Represents a classification for transactions. Attributes: unique name, emoji icon (optional).
- **Budget**: Represents a spending limit. Attributes: category reference, limit amount, current spent amount (calculated).
- **Account**: Represents a financial account. Attributes: unique ID, name, type (Checking/Savings/Investment), balance.

## Assumptions

- Default categories (Food, Rent, Utilities, Salary, Investment) are pre-loaded on application start.
- Transaction IDs are auto-generated integers starting from 1.
- Date defaults to today's date if not specified when adding a transaction.
- Budgets are monthly and reset conceptually each month (though data resets on restart per Phase I).
- Currency is not specified; amounts are treated as numeric values without currency symbols.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can add a new transaction in under 10 seconds using a single command.
- **SC-002**: Users can view all transactions in a formatted table within 1 second of entering the command.
- **SC-003**: 100% of input validation errors display user-friendly messages explaining the issue.
- **SC-004**: Users can complete any CRUD operation (add, update, delete, view) within 3 command entries.
- **SC-005**: Budget status accurately reflects total expenses per category against set limits.
- **SC-006**: Search and filter operations return correct results matching the specified criteria.
- **SC-007**: Demo presenters can showcase all core features (add, list, update, delete, budget) in under 5 minutes.
- **SC-008**: All transaction types display with correct color-coded indicators in the output.
