#!/usr/bin/env python3
"""Demo script for AI Wealth & Spending Companion Phase I.

This script demonstrates all features of the CLI application:
- Transaction management (add, list, filter, sort)
- Budget management (set, track, warnings)
- Financial summary

Run with: python demo.py
"""
from datetime import date, timedelta

from src.repositories.memory import (
    InMemoryTransactionRepository,
    InMemoryCategoryRepository,
    InMemoryBudgetRepository,
)
from src.services import TransactionService, BudgetService, CategoryService
from src.cli.formatters import (
    header, success_message, info_message, warning_message,
    format_transactions_table, format_categories_table, format_budget_status_table,
    green, red, bold,
)


def demo():
    """Run demo showcasing all features."""
    print(header("AI Wealth & Spending Companion - Demo"))
    print(info_message("This demo shows all Phase I features\n"))

    # Initialize services
    txn_repo = InMemoryTransactionRepository()
    cat_repo = InMemoryCategoryRepository()
    budget_repo = InMemoryBudgetRepository()

    cat_service = CategoryService(cat_repo)
    cat_service.load_default_categories()

    txn_service = TransactionService(txn_repo, cat_repo)
    budget_service = BudgetService(budget_repo, txn_repo, cat_repo)

    # Show categories
    print(header("Default Categories"))
    categories = cat_service.get_all_categories()
    print(format_categories_table(categories))
    print()

    # Add sample transactions
    print(header("Adding Sample Transactions"))
    today = date.today()
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)

    transactions_data = [
        ("income", 5000.0, "Salary", "Monthly salary", today, False),
        ("expense", 1500.0, "Rent", "Apartment rent", today, True),
        ("expense", 120.0, "Utilities", "Electric bill", yesterday, True),
        ("expense", 85.0, "Food", "Grocery shopping", yesterday, False),
        ("expense", 45.0, "Food", "Restaurant dinner", last_week, False),
        ("expense", 200.0, "Investment", "Stock purchase", last_week, False),
        ("income", 150.0, "Investment", "Dividend payment", today, False),
    ]

    for txn_type, amount, category, note, txn_date, recurring in transactions_data:
        result = txn_service.add_transaction(
            type=txn_type,
            amount=amount,
            category=category,
            note=note,
            date=txn_date.isoformat(),
            recurring=recurring,
        )
        if result.is_ok():
            txn = result.unwrap()
            emoji = "💚" if txn_type == "income" else "❤️"
            print(f"  {emoji} Added: {category} - ${amount:.2f} ({note})")

    print()

    # List all transactions
    print(header("All Transactions"))
    transactions = txn_service.list_transactions()
    cat_dict = {c.name.lower(): c for c in categories}
    print(format_transactions_table(transactions, cat_dict))
    print()

    # Set budgets
    print(header("Setting Budgets"))
    budgets_data = [
        ("Food", 300.0),
        ("Rent", 1600.0),
        ("Utilities", 200.0),
    ]

    for category, limit in budgets_data:
        result = budget_service.set_budget(category, limit)
        if result.is_ok():
            print(f"  📊 Budget set: ${limit:.2f}/month for {category}")

    print()

    # Show budget status
    print(header("Budget Status"))
    statuses = budget_service.get_all_budgets_status()
    print(format_budget_status_table(statuses))
    print()

    # Filter by category
    print(header("Transactions in 'Food' Category"))
    food_txns = txn_service.filter_by_category("Food")
    print(format_transactions_table(food_txns, cat_dict, show_summary=False))
    print()

    # Sort by amount
    print(header("Transactions Sorted by Amount (High to Low)"))
    sorted_txns = txn_service.sort_by_amount(descending=True)
    print(format_transactions_table(sorted_txns, cat_dict, show_summary=False))
    print()

    # Financial summary
    print(header("Financial Summary"))
    totals = txn_service.get_totals()
    income_str = f"${totals['income']:,.2f}"
    expense_str = f"${totals['expense']:,.2f}"
    print(f"  Total Income:   {green(income_str)}")
    print(f"  Total Expenses: {red(expense_str)}")
    net = totals["net"]
    net_color = green if net >= 0 else red
    net_str = f"${net:,.2f}"
    print(f"  Net Balance:    {net_color(net_str)}")
    print()

    # Demonstrate budget warning
    print(header("Budget Warning Demo"))
    print(info_message("Adding a large expense to trigger budget warning..."))
    result = txn_service.add_transaction(
        type="expense",
        amount=200.0,
        category="Food",
        note="Party catering",
    )

    if result.is_ok():
        status_result = budget_service.get_budget_status("Food")
        if status_result.is_ok():
            status = status_result.unwrap()
            if status.exceeded:
                print(warning_message(f"BUDGET EXCEEDED for Food!"))
                print(f"  Spent: ${status.spent:.2f} / Budget: ${status.limit:.2f}")
            elif status.percentage >= 80:
                print(warning_message(f"Budget warning: {status.percentage:.0f}% used for Food"))

    print()
    print(success_message("Demo complete! Run 'python -m src' for interactive mode."))


if __name__ == "__main__":
    demo()
