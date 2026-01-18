"""CLI formatters for colored output and table display."""
from typing import List, Optional
from colorama import Fore, Style
from tabulate import tabulate

from src.models import Transaction, Category, BudgetStatus


# Color helpers
def green(text: str) -> str:
    """Return green colored text."""
    return f"{Fore.GREEN}{text}{Style.RESET_ALL}"


def red(text: str) -> str:
    """Return red colored text."""
    return f"{Fore.RED}{text}{Style.RESET_ALL}"


def yellow(text: str) -> str:
    """Return yellow colored text."""
    return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"


def cyan(text: str) -> str:
    """Return cyan colored text."""
    return f"{Fore.CYAN}{text}{Style.RESET_ALL}"


def bold(text: str) -> str:
    """Return bold text."""
    return f"{Style.BRIGHT}{text}{Style.RESET_ALL}"


# Emoji helpers
INCOME_EMOJI = "💚"
EXPENSE_EMOJI = "❤️"
RECURRING_EMOJI = "💛"


def transaction_type_display(txn_type: str) -> str:
    """Return colored transaction type with emoji."""
    if txn_type == "income":
        return f"{INCOME_EMOJI} {green('Income')}"
    return f"{EXPENSE_EMOJI} {red('Expense')}"


def amount_display(amount: float, txn_type: str = None) -> str:
    """Return formatted amount with optional color."""
    formatted = f"${amount:,.2f}"
    if txn_type == "income":
        return green(formatted)
    elif txn_type == "expense":
        return red(formatted)
    return formatted


def recurring_display(recurring: bool) -> str:
    """Return recurring status with emoji."""
    if recurring:
        return f"{RECURRING_EMOJI} Yes"
    return "No"


# Table formatters
def format_transactions_table(
    transactions: List[Transaction],
    categories: dict = None,
    show_summary: bool = True
) -> str:
    """
    Format transactions as a table.

    Args:
        transactions: List of transactions to display
        categories: Optional dict of category name -> Category for emoji lookup
        show_summary: Whether to show totals at the bottom

    Returns:
        Formatted table string
    """
    if not transactions:
        return yellow("No transactions found.")

    headers = ["ID", "Type", "Amount", "Category", "Note", "Date", "Recurring"]
    rows = []

    for txn in transactions:
        cat_display = txn.category
        if categories and txn.category.lower() in categories:
            cat_display = categories[txn.category.lower()].display()

        note = txn.note[:20] + "..." if len(txn.note) > 20 else txn.note

        rows.append([
            txn.id,
            transaction_type_display(txn.type),
            amount_display(txn.amount, txn.type),
            cat_display,
            note or "-",
            txn.date.strftime("%Y-%m-%d"),
            recurring_display(txn.recurring),
        ])

    table = tabulate(rows, headers=headers, tablefmt="simple")

    if show_summary:
        total_income = sum(t.amount for t in transactions if t.is_income())
        total_expense = sum(t.amount for t in transactions if t.is_expense())
        net = total_income - total_expense

        summary = f"\n{bold('Summary:')}\n"
        summary += f"  Total Income:   {green(f'${total_income:,.2f}')}\n"
        summary += f"  Total Expenses: {red(f'${total_expense:,.2f}')}\n"
        net_color = green if net >= 0 else red
        summary += f"  Net:            {net_color(f'${net:,.2f}')}"
        table += summary

    return table


def format_categories_table(categories: List[Category]) -> str:
    """Format categories as a numbered list."""
    if not categories:
        return yellow("No categories found.")

    lines = []
    for i, cat in enumerate(categories, 1):
        lines.append(f"  {i}. {cat.display()}")

    return "\n".join(lines)


def format_budget_status_table(statuses: List[BudgetStatus]) -> str:
    """
    Format budget statuses as a table with overspend warnings.

    Args:
        statuses: List of budget statuses to display

    Returns:
        Formatted table string
    """
    if not statuses:
        return yellow("No budgets set.")

    headers = ["Category", "Limit", "Spent", "Remaining", "Usage", "Status"]
    rows = []

    for status in statuses:
        # Status indicator
        if status.exceeded:
            status_str = red("⚠️ OVER")
        elif status.percentage >= 80:
            status_str = yellow("⚡ Warning")
        else:
            status_str = green("✅ OK")

        # Remaining color
        remaining_str = amount_display(abs(status.remaining))
        if status.remaining < 0:
            remaining_str = red(f"-${abs(status.remaining):,.2f}")
        else:
            remaining_str = green(f"${status.remaining:,.2f}")

        rows.append([
            status.category,
            f"${status.limit:,.2f}",
            f"${status.spent:,.2f}",
            remaining_str,
            f"{status.percentage:.0f}%",
            status_str,
        ])

    return tabulate(rows, headers=headers, tablefmt="simple")


# Message formatters
def success_message(message: str) -> str:
    """Format success message."""
    return green(f"✅ {message}")


def error_message(message: str) -> str:
    """Format error message."""
    return red(f"❌ {message}")


def warning_message(message: str) -> str:
    """Format warning message."""
    return yellow(f"⚠️ {message}")


def info_message(message: str) -> str:
    """Format info message."""
    return cyan(f"ℹ️ {message}")


def header(title: str) -> str:
    """Format section header."""
    border = "═" * 40
    return f"\n{cyan(border)}\n   {bold(title)}\n{cyan(border)}\n"


def menu_header(title: str) -> str:
    """Format menu header with emoji."""
    return f"\n{bold(title)}\n"
