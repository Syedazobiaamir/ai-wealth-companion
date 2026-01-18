# AI Wealth & Spending Companion

A personal finance CLI application for tracking income, expenses, and budgets.

## Phase I - CLI Financial Core

This is **Phase I** of a multi-phase fintech project. Phase I establishes a stable, testable, in-memory financial core that will be reused by the web app and AI agents in subsequent phases.

### Features

| Feature | Description |
|---------|-------------|
| **Transaction Management** | Add, edit, delete income/expense transactions |
| **Category Support** | 5 default categories with emojis (Food, Rent, Utilities, Salary, Investment) |
| **Budget Tracking** | Set monthly spending limits per category |
| **Budget Alerts** | Warnings when budget exceeds 80% or 100% |
| **Filter & Search** | Filter by category, date range, or sort by amount |
| **Financial Summary** | View total income, expenses, and net balance |
| **Recurring Transactions** | Mark transactions as recurring |

### Visual Indicators

| Symbol | Meaning |
|--------|---------|
| 💚 | Income |
| ❤️ | Expense |
| 💛 | Recurring |
| ✅ OK | Budget under control |
| ⚡ Warning | Budget > 80% used |
| ⚠️ OVER | Budget exceeded |

### Default Categories

| Category | Emoji |
|----------|-------|
| Food | 🍔 |
| Rent | 🏠 |
| Utilities | 💡 |
| Salary | 💵 |
| Investment | 💎 |

## Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-wealth-companion.git
cd ai-wealth-companion

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies (for testing)
pip install -r requirements-dev.txt
```

## Usage

### Interactive CLI

```bash
python -m src
```

### Demo Script

```bash
python demo.py
```

### Run Tests

```bash
python -m pytest tests/ -v
```

## Project Structure

```
├── src/
│   ├── models/           # Domain entities
│   │   ├── result.py     # Result type for error handling
│   │   ├── category.py   # Category model
│   │   ├── transaction.py # Transaction model
│   │   └── budget.py     # Budget and BudgetStatus models
│   ├── repositories/     # Data access layer
│   │   ├── base.py       # Abstract interfaces
│   │   └── memory/       # In-memory implementations
│   ├── services/         # Business logic
│   │   ├── category_service.py
│   │   ├── transaction_service.py
│   │   └── budget_service.py
│   └── cli/              # Command-line interface
│       ├── main.py       # Entry point and main loop
│       ├── menus.py      # Menu handlers
│       └── formatters.py # Output formatting
├── tests/
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── specs/                # Feature specifications
├── demo.py               # Demo script
├── requirements.txt      # Production dependencies
└── requirements-dev.txt  # Development dependencies
```

## Architecture

Phase I follows a **3-layer architecture** with clean separation:

```
┌─────────────────────────────────────┐
│            CLI Layer                │
│   (menus.py, formatters.py)         │
├─────────────────────────────────────┤
│          Service Layer              │
│ (TransactionService, BudgetService) │
├─────────────────────────────────────┤
│        Repository Layer             │
│   (InMemoryTransactionRepository)   │
├─────────────────────────────────────┤
│          Model Layer                │
│ (Transaction, Category, Budget)     │
└─────────────────────────────────────┘
```

### Design Principles

- **Repository Pattern**: Swappable storage (in-memory now, database later)
- **TDD**: Tests written before implementation
- **Clean Architecture**: Business logic independent of framework
- **Result Type**: Explicit error handling without exceptions

## Phase I Constraints

| Constraint | Reason |
|------------|--------|
| CLI only | Foundation before web/mobile UI |
| In-memory storage | Data resets on exit (no database yet) |
| No AI features | Core logic first, AI assistant later |
| Mock data only | No real bank connections |

## Future Phases

| Phase | Description |
|-------|-------------|
| Phase II | Web Dashboard (Next.js + Tailwind) |
| Phase III | AI Chatbot + Voice Commands |
| Phase IV | Local Kubernetes Deployment |
| Phase V | Cloud Production (DigitalOcean) |

## Tech Stack

- **Language**: Python 3.10+
- **CLI Libraries**: colorama, tabulate
- **Testing**: pytest

## License

MIT License

## Author

Built with Spec-Driven Development using Claude Code.
