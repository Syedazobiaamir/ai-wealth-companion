# Tasks: Phase I Financial Core

**Input**: Design documents from `/specs/002-phase1-financial-core/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/service-interfaces.md, research.md, quickstart.md

**Tests**: Included per Constitution Principle V (Test-First Development is NON-NEGOTIABLE)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root (per plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure per plan.md in src/
- [x] T002 Create requirements.txt with colorama>=0.4.6 and tabulate>=0.9.0
- [x] T003 [P] Create requirements-dev.txt with pytest>=7.0.0 and pytest-cov>=4.0.0
- [x] T004 [P] Create src/__init__.py package file
- [x] T005 [P] Create src/models/__init__.py package file
- [x] T006 [P] Create src/repositories/__init__.py package file
- [x] T007 [P] Create src/services/__init__.py package file
- [x] T008 [P] Create src/cli/__init__.py package file
- [x] T009 [P] Create tests/__init__.py package file
- [x] T010 [P] Create tests/unit/__init__.py package file
- [x] T011 [P] Create tests/integration/__init__.py package file
- [x] T012 Create tests/conftest.py with shared pytest fixtures

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundational

- [x] T013 [P] Unit test for Category model in tests/unit/test_models.py
- [x] T014 [P] Unit test for Result type in tests/unit/test_models.py

### Implementation for Foundational

- [x] T015 [P] Create Result type (Ok/Err) in src/models/result.py
- [x] T016 [P] Create Category dataclass in src/models/category.py
- [x] T017 Create abstract CategoryRepository interface in src/repositories/base.py
- [x] T018 Implement InMemoryCategoryRepository in src/repositories/memory/category_repository.py
- [x] T019 [P] Create src/repositories/memory/__init__.py package file
- [x] T020 Create default categories loader with emojis (Food, Rent, Utilities, Salary, Investment) in src/services/category_service.py
- [x] T021 Create CLI formatters module with color and emoji helpers in src/cli/formatters.py
- [x] T022 Initialize colorama in src/cli/__init__.py

**Checkpoint**: Foundation ready - Category management and CLI formatting available

---

## Phase 3: User Story 1 - Create and Manage Transactions (Priority: P1) 🎯 MVP

**Goal**: Enable users to create, view, update, and delete financial transactions

**Independent Test**: Can be fully tested by creating sample transactions, viewing them in a list, updating amounts/categories, and deleting entries

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T023 [P] [US1] Unit test for Transaction dataclass in tests/unit/test_models.py
- [x] T024 [P] [US1] Unit test for TransactionRepository in tests/unit/test_transaction_repository.py
- [x] T025 [P] [US1] Unit test for TransactionService add_transaction in tests/unit/test_transaction_service.py
- [x] T026 [P] [US1] Unit test for TransactionService update_transaction in tests/unit/test_transaction_service.py
- [x] T027 [P] [US1] Unit test for TransactionService delete_transaction in tests/unit/test_transaction_service.py
- [x] T028 [P] [US1] Unit test for TransactionService list_transactions in tests/unit/test_transaction_service.py

### Implementation for User Story 1

- [x] T029 [P] [US1] Create Transaction dataclass in src/models/transaction.py
- [x] T030 [US1] Create abstract TransactionRepository interface in src/repositories/base.py
- [x] T031 [US1] Implement InMemoryTransactionRepository with CRUD operations in src/repositories/memory/transaction_repository.py
- [x] T032 [US1] Implement TransactionService with add_transaction (includes amount, type, date, category validation) in src/services/transaction_service.py
- [x] T033 [US1] Implement TransactionService update_transaction in src/services/transaction_service.py
- [x] T034 [US1] Implement TransactionService delete_transaction in src/services/transaction_service.py
- [x] T035 [US1] Implement TransactionService list_transactions in src/services/transaction_service.py
- [x] T036 [US1] Create transaction table formatter using tabulate in src/cli/formatters.py
- [x] T037 [US1] Implement Add Transaction CLI menu in src/cli/menus.py
- [x] T038 [US1] Implement View Transactions CLI menu in src/cli/menus.py
- [x] T039 [US1] Implement Update Transaction CLI menu in src/cli/menus.py
- [x] T040 [US1] Implement Delete Transaction CLI menu (with confirmation) in src/cli/menus.py
- [x] T041 [US1] Integration test for transaction CRUD flow in tests/integration/test_cli_flows.py

**Checkpoint**: At this point, User Story 1 should be fully functional - users can add, view, update, and delete transactions

---

## Phase 4: User Story 2 - Filter and Sort Transactions (Priority: P2)

**Goal**: Enable users to filter transactions by category/date and sort by amount

**Independent Test**: Can be tested by creating transactions with different categories/dates/amounts, then filtering and sorting to verify correct results

### Tests for User Story 2

- [x] T042 [P] [US2] Unit test for TransactionRepository filter_by_category in tests/unit/test_transaction_repository.py
- [x] T043 [P] [US2] Unit test for TransactionRepository filter_by_date_range in tests/unit/test_transaction_repository.py
- [x] T044 [P] [US2] Unit test for TransactionRepository sort_by_amount in tests/unit/test_transaction_repository.py
- [x] T045 [P] [US2] Unit test for TransactionService filter and sort methods in tests/unit/test_transaction_service.py

### Implementation for User Story 2

- [x] T046 [US2] Implement filter_by_category in InMemoryTransactionRepository in src/repositories/memory/transaction_repository.py
- [x] T047 [US2] Implement filter_by_date_range in InMemoryTransactionRepository in src/repositories/memory/transaction_repository.py
- [x] T048 [US2] Implement sort_by_amount in InMemoryTransactionRepository in src/repositories/memory/transaction_repository.py
- [x] T049 [US2] Implement TransactionService filter_by_category in src/services/transaction_service.py
- [x] T050 [US2] Implement TransactionService filter_by_date (with date validation) in src/services/transaction_service.py
- [x] T051 [US2] Implement TransactionService sort_by_amount in src/services/transaction_service.py
- [x] T052 [US2] Implement Search & Filter CLI menu in src/cli/menus.py
- [x] T053 [US2] Integration test for filter and sort flow in tests/integration/test_cli_flows.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - full transaction management with filtering/sorting

---

## Phase 5: User Story 3 - Set and Monitor Budgets (Priority: P3)

**Goal**: Enable users to set monthly budget limits per category and monitor spending

**Independent Test**: Can be tested by setting a budget for a category, adding expense transactions, and verifying budget status shows correct usage and warnings

### Tests for User Story 3

- [x] T054 [P] [US3] Unit test for Budget dataclass in tests/unit/test_models.py
- [x] T055 [P] [US3] Unit test for BudgetStatus dataclass in tests/unit/test_models.py
- [x] T056 [P] [US3] Unit test for BudgetRepository in tests/unit/test_budget_repository.py
- [x] T057 [P] [US3] Unit test for BudgetService set_budget in tests/unit/test_budget_service.py
- [x] T058 [P] [US3] Unit test for BudgetService get_budget_status in tests/unit/test_budget_service.py
- [x] T059 [P] [US3] Unit test for BudgetService overspend warning in tests/unit/test_budget_service.py

### Implementation for User Story 3

- [x] T060 [P] [US3] Create Budget dataclass in src/models/budget.py
- [x] T061 [P] [US3] Create BudgetStatus dataclass in src/models/budget.py
- [x] T062 [US3] Create abstract BudgetRepository interface in src/repositories/base.py
- [x] T063 [US3] Implement InMemoryBudgetRepository in src/repositories/memory/budget_repository.py
- [x] T064 [US3] Implement BudgetService set_budget (with category and limit validation) in src/services/budget_service.py
- [x] T065 [US3] Implement BudgetService get_budget_status (calculates spent, remaining, percentage, exceeded) in src/services/budget_service.py
- [x] T066 [US3] Implement BudgetService get_all_budgets_status in src/services/budget_service.py
- [x] T067 [US3] Create budget status table formatter with overspend warning indicators in src/cli/formatters.py
- [x] T068 [US3] Implement Budget Management CLI menu (set budget, view status) in src/cli/menus.py
- [x] T069 [US3] Integration test for budget workflow in tests/integration/test_cli_flows.py

**Checkpoint**: All user stories (1, 2, 3) should now be independently functional

---

## Phase 6: User Story 4 - CLI Integration & Main Loop (Priority: P4)

**Goal**: Assemble complete CLI application with main menu and consistent user experience

**Independent Test**: Can verify by starting the application, navigating all menus, and confirming data persists within session but clears on restart

### Tests for User Story 4

- [x] T070 [P] [US4] Integration test for main menu navigation in tests/integration/test_cli_flows.py
- [x] T071 [P] [US4] Integration test for data persistence within session in tests/integration/test_cli_flows.py
- [x] T072 [P] [US4] Integration test for data reset on restart in tests/integration/test_cli_flows.py

### Implementation for User Story 4

- [x] T073 [US4] Create main menu display with numbered options in src/cli/menus.py
- [x] T074 [US4] Implement main loop with input handling in src/cli/main.py
- [x] T075 [US4] Wire up all sub-menus (transactions, budgets, categories, search) in src/cli/main.py
- [x] T076 [US4] Implement Category Management CLI menu (view categories) in src/cli/menus.py
- [x] T077 [US4] Implement Exit command with confirmation in src/cli/main.py
- [x] T078 [US4] Create application initialization (load default categories, init colorama) in src/cli/main.py
- [x] T079 [US4] Create entry point script at main.py (repository root)

**Checkpoint**: Complete CLI application is functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and demo preparation

- [x] T080 [P] Add error handling for invalid menu input in src/cli/main.py
- [x] T081 [P] Add help command showing all available commands in src/cli/menus.py
- [x] T082 [P] Add transaction summary (total income, expenses, net) to View Transactions in src/cli/menus.py
- [x] T083 [P] Add recurring payment toggle to transaction operations in src/cli/menus.py
- [x] T084 Create demo script with sample data in demo.py
- [x] T085 Run quickstart.md validation (verify all documented commands work)
- [x] T086 Final integration test: complete user journey in tests/integration/test_cli_flows.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - Core MVP
- **User Story 2 (Phase 4)**: Depends on US1 completion (extends TransactionService)
- **User Story 3 (Phase 5)**: Can start after Foundational (parallel with US1/US2)
- **User Story 4 (Phase 6)**: Depends on US1, US2, US3 completion
- **Polish (Phase 7)**: Depends on US4 completion

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P2)**: Depends on US1 (extends TransactionRepository and TransactionService)
- **User Story 3 (P3)**: Can start after Foundational - Independent of US1/US2 but integrates for budget calculations
- **User Story 4 (P4)**: Depends on all other stories for integration

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before repositories
- Repositories before services
- Services before CLI menus
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks T004-T011 can run in parallel
- All Foundational tests T013-T014 can run in parallel
- Foundational implementations T015-T016 can run in parallel
- All US1 tests T023-T028 can run in parallel
- US1 implementations: T029 parallel, then T030-T035 sequential, then T036-T040 sequential
- All US2 tests T042-T045 can run in parallel
- US3 can run in parallel with US1/US2 (separate models, repos, services)
- All US3 tests T054-T059 can run in parallel
- US3 implementations: T060-T061 parallel, then T062-T069 sequential

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD - write first, ensure fail):
Task: "Unit test for Transaction dataclass in tests/unit/test_models.py"
Task: "Unit test for TransactionRepository in tests/unit/test_transaction_repository.py"
Task: "Unit test for TransactionService add_transaction in tests/unit/test_transaction_service.py"
Task: "Unit test for TransactionService update_transaction in tests/unit/test_transaction_service.py"
Task: "Unit test for TransactionService delete_transaction in tests/unit/test_transaction_service.py"
Task: "Unit test for TransactionService list_transactions in tests/unit/test_transaction_service.py"

# Then launch model implementation:
Task: "Create Transaction dataclass in src/models/transaction.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Transaction CRUD)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Demo/demo if ready - basic transaction management works!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Demo (MVP!)
3. Add User Story 2 → Test independently → Demo (filtering/sorting)
4. Add User Story 3 → Test independently → Demo (budgets)
5. Add User Story 4 → Test independently → Demo (complete CLI)
6. Polish → Final demo

### Parallel Strategy (if team available)

With multiple developers:
1. All complete Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 + User Story 2 (sequential - US2 extends US1)
   - Developer B: User Story 3 (independent)
3. US4 integrates all stories
4. Everyone helps with Polish

---

## Summary

| Phase | Tasks | Parallel Opportunities |
|-------|-------|------------------------|
| Setup | T001-T012 (12) | T004-T011 (8 parallel) |
| Foundational | T013-T022 (10) | T013-T016 (4 parallel) |
| US1 - Transactions | T023-T041 (19) | T023-T028 (6 parallel), T029 |
| US2 - Filter/Sort | T042-T053 (12) | T042-T045 (4 parallel) |
| US3 - Budgets | T054-T069 (16) | T054-T059 (6 parallel), T060-T061 |
| US4 - CLI Integration | T070-T079 (10) | T070-T072 (3 parallel) |
| Polish | T080-T086 (7) | T080-T083 (4 parallel) |
| **Total** | **86 tasks** | |

---

## Notes

- [P] tasks = different files, no dependencies
- [US#] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- TDD is NON-NEGOTIABLE per Constitution - verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
