# Quickstart: Phase I Financial Core

**Feature**: 002-phase1-financial-core
**Date**: 2026-01-18

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

## Installation

```bash
# Clone the repository (if not already done)
cd hackathone2

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install colorama tabulate

# For development (testing)
pip install pytest
```

## Running the Application

```bash
# From repository root
python -m src.cli.main

# Or if entry point is configured
python main.py
```

## Basic Usage

### Main Menu

When you start the application, you'll see:

```
═══════════════════════════════════════
   💰 AI Wealth & Spending Companion
═══════════════════════════════════════

1. 📝 Add Transaction
2. 📋 List Transactions
3. ✏️  Update Transaction
4. 🗑️  Delete Transaction
5. 🏷️  Manage Categories
6. 💰 Budget Management
7. 🔍 Search & Filter
8. ❌ Exit

Enter choice:
```

### Adding a Transaction

```
Enter choice: 1

Transaction Type:
1. 💚 Income
2. ❤️  Expense

Select type: 2
Enter amount: 500
Select category:
1. 🍔 Food
2. 🏠 Rent
3. 💡 Utilities
Enter note (optional): Grocery shopping
Enter date (YYYY-MM-DD) [today]: 2026-01-18
Recurring? (y/n): n

✅ Transaction added successfully!
ID: 1 | ❤️ Expense | $500.00 | 🍔 Food | 2026-01-18
```

### Viewing Transactions

```
Enter choice: 2

📋 All Transactions
┌────┬──────────┬──────────┬──────────┬─────────────┬────────────┬───────────┐
│ ID │ Type     │ Amount   │ Category │ Note        │ Date       │ Recurring │
├────┼──────────┼──────────┼──────────┼─────────────┼────────────┼───────────┤
│ 1  │ ❤️ Expense│ $500.00  │ 🍔 Food  │ Grocery...  │ 2026-01-18 │ No        │
│ 2  │ 💚 Income │ $3000.00 │ 💵 Salary│ January pay │ 2026-01-15 │ Yes       │
└────┴──────────┴──────────┴──────────┴─────────────┴────────────┴───────────┘

Total Income: $3000.00
Total Expenses: $500.00
Net: $2500.00
```

### Budget Management

```
Enter choice: 6

💰 Budget Management
1. Set Budget
2. View Budget Status
3. Back

Select: 2

📊 Budget Status
┌──────────┬─────────┬─────────┬───────────┬────────────┬──────────┐
│ Category │ Limit   │ Spent   │ Remaining │ Percentage │ Status   │
├──────────┼─────────┼─────────┼───────────┼────────────┼──────────┤
│ 🍔 Food  │ $1000   │ $500    │ $500      │ 50%        │ ✅ OK    │
│ 🏠 Rent  │ $2000   │ $2200   │ -$200     │ 110%       │ ⚠️ OVER  │
└──────────┴─────────┴─────────┴───────────┴────────────┴──────────┘
```

### Filtering Transactions

```
Enter choice: 7

🔍 Search & Filter
1. Filter by Category
2. Filter by Date Range
3. Sort by Amount
4. Back

Select: 1
Select category: Food

📋 Transactions in 🍔 Food
┌────┬──────────┬──────────┬─────────────┬────────────┐
│ ID │ Type     │ Amount   │ Note        │ Date       │
├────┼──────────┼──────────┼─────────────┼────────────┤
│ 1  │ ❤️ Expense│ $500.00  │ Grocery...  │ 2026-01-18 │
└────┴──────────┴──────────┴─────────────┴────────────┘
```

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_transaction_service.py

# Run with coverage
pytest --cov=src
```

## Project Structure

```
hackathone2/
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── transaction.py
│   │   ├── category.py
│   │   └── budget.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── transaction_repository.py
│   │   ├── category_repository.py
│   │   └── budget_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── transaction_service.py
│   │   └── budget_service.py
│   └── cli/
│       ├── __init__.py
│       ├── main.py
│       ├── menus.py
│       └── formatters.py
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_transaction_service.py
│   │   └── test_budget_service.py
│   └── integration/
│       └── test_cli_flows.py
├── requirements.txt
└── main.py
```

## Troubleshooting

### Colors not displaying on Windows

Install and enable colorama:

```python
import colorama
colorama.init()
```

### Table formatting issues

Ensure terminal width is sufficient (80+ columns recommended).

### Data disappeared after restart

This is expected behavior for Phase I. All data is stored in-memory and resets on restart.

## Next Steps

After completing Phase I:
- Run `/sp.tasks` to generate implementation tasks
- Follow TDD: Write tests first, then implement
- Commit after each milestone
