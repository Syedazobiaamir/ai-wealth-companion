"""CLI menu handlers for AI Wealth & Spending Companion."""
from typing import Optional, List
from datetime import date

from src.models import Category
from src.services import TransactionService, BudgetService, CategoryService
from src.cli.formatters import (
    header, menu_header, success_message, error_message, warning_message, info_message,
    format_transactions_table, format_categories_table, format_budget_status_table,
    green, red, yellow, cyan, bold,
)


class MenuHandler:
    """Handles CLI menu interactions."""

    def __init__(
        self,
        txn_service: TransactionService,
        budget_service: BudgetService,
        cat_service: CategoryService,
    ):
        self.txn_service = txn_service
        self.budget_service = budget_service
        self.cat_service = cat_service

    def _resolve_category(self, user_input: str, categories: List[Category]) -> Optional[str]:
        """
        Resolve category from user input - accepts number (1-5) or name (Food).
        Returns category name or None if not found.
        """
        user_input = user_input.strip()

        # Try as number first
        try:
            index = int(user_input) - 1  # Convert to 0-based index
            if 0 <= index < len(categories):
                return categories[index].name
        except ValueError:
            pass

        # Try as name (case-insensitive)
        for cat in categories:
            if cat.name.lower() == user_input.lower():
                return cat.name

        return None

    def show_main_menu(self) -> None:
        """Display main menu options."""
        print(header("AI Wealth & Spending Companion"))
        print(menu_header("Main Menu"))
        print("  1. 💰 Add Transaction")
        print("  2. 📋 List Transactions")
        print("  3. ✏️  Edit Transaction")
        print("  4. 🗑️  Delete Transaction")
        print("  5. 🔍 Search & Filter")
        print("  6. 📊 Budget Management")
        print("  7. 📈 View Summary")
        print("  8. ❓ Help")
        print("  0. 🚪 Exit")
        print()

    def add_transaction(self) -> None:
        """Handle add transaction flow."""
        print(header("Add Transaction"))

        # Get type
        print("Transaction type:")
        print("  1. 💚 Income")
        print("  2. ❤️  Expense")
        choice = input("Select (1-2): ").strip()
        txn_type = "income" if choice == "1" else "expense"

        # Get amount
        try:
            amount = float(input("Amount: $").strip())
        except ValueError:
            print(error_message("Invalid amount. Please enter a number."))
            return

        # Get category
        categories = self.cat_service.get_all_categories()
        print("\nCategories:")
        print(format_categories_table(categories))
        cat_input = input("\nSelect category (number or name): ").strip()

        # Resolve category (accepts "1" or "Food")
        category = self._resolve_category(cat_input, categories)
        if not category:
            print(error_message(f"Category '{cat_input}' not found. Use number (1-5) or name."))
            return

        # Get note
        note = input("Note (optional): ").strip()

        # Get date
        date_input = input(f"Date (YYYY-MM-DD, default today): ").strip()
        if not date_input:
            date_input = None

        # Get recurring
        recurring_input = input("Recurring? (y/N): ").strip().lower()
        recurring = recurring_input == "y"

        # Create transaction
        result = self.txn_service.add_transaction(
            type=txn_type,
            amount=amount,
            category=category,
            note=note,
            date=date_input,
            recurring=recurring,
        )

        if result.is_ok():
            txn = result.unwrap()
            print(success_message(f"Transaction #{txn.id} added successfully!"))

            # Check budget warning
            if txn_type == "expense":
                budget_result = self.budget_service.get_budget_status(category)
                if budget_result.is_ok():
                    status = budget_result.unwrap()
                    if status.exceeded:
                        print(warning_message(f"Budget exceeded for {category}! Spent ${status.spent:.2f} of ${status.limit:.2f}"))
                    elif status.percentage >= 80:
                        print(warning_message(f"Budget warning: {status.percentage:.0f}% used for {category}"))
        else:
            print(error_message(result.unwrap_err()))

    def list_transactions(self) -> None:
        """Handle list transactions flow."""
        print(header("All Transactions"))

        transactions = self.txn_service.list_transactions()
        categories = {c.name.lower(): c for c in self.cat_service.get_all_categories()}

        print(format_transactions_table(transactions, categories))

    def edit_transaction(self) -> None:
        """Handle edit transaction flow."""
        print(header("Edit Transaction"))

        try:
            txn_id = int(input("Transaction ID to edit: ").strip())
        except ValueError:
            print(error_message("Invalid ID. Please enter a number."))
            return

        txn = self.txn_service.get_transaction(txn_id)
        if txn is None:
            print(error_message(f"Transaction #{txn_id} not found."))
            return

        print(f"\nCurrent values:")
        print(f"  Type: {txn.type}")
        print(f"  Amount: ${txn.amount:.2f}")
        print(f"  Category: {txn.category}")
        print(f"  Note: {txn.note or '-'}")
        print(f"  Date: {txn.date}")
        print(f"  Recurring: {'Yes' if txn.recurring else 'No'}")
        print("\nPress Enter to keep current value, or enter new value:")

        updates = {}

        # Type
        new_type = input(f"Type (income/expense) [{txn.type}]: ").strip()
        if new_type:
            updates["type"] = new_type

        # Amount
        new_amount = input(f"Amount [{txn.amount}]: ").strip()
        if new_amount:
            try:
                updates["amount"] = float(new_amount)
            except ValueError:
                print(error_message("Invalid amount."))
                return

        # Category
        new_cat = input(f"Category [{txn.category}]: ").strip()
        if new_cat:
            updates["category"] = new_cat

        # Note
        new_note = input(f"Note [{txn.note or '-'}]: ").strip()
        if new_note:
            updates["note"] = new_note

        # Date
        new_date = input(f"Date [{txn.date}]: ").strip()
        if new_date:
            updates["date"] = new_date

        # Recurring
        new_recurring = input(f"Recurring (y/n) [{'y' if txn.recurring else 'n'}]: ").strip().lower()
        if new_recurring:
            updates["recurring"] = new_recurring == "y"

        if updates:
            result = self.txn_service.update_transaction(txn_id, **updates)
            if result.is_ok():
                print(success_message(f"Transaction #{txn_id} updated!"))
            else:
                print(error_message(result.unwrap_err()))
        else:
            print(info_message("No changes made."))

    def delete_transaction(self) -> None:
        """Handle delete transaction flow."""
        print(header("Delete Transaction"))

        try:
            txn_id = int(input("Transaction ID to delete: ").strip())
        except ValueError:
            print(error_message("Invalid ID. Please enter a number."))
            return

        txn = self.txn_service.get_transaction(txn_id)
        if txn is None:
            print(error_message(f"Transaction #{txn_id} not found."))
            return

        print(f"\nTransaction to delete:")
        print(f"  ID: {txn.id}")
        print(f"  Type: {txn.type}")
        print(f"  Amount: ${txn.amount:.2f}")
        print(f"  Category: {txn.category}")

        confirm = input("\nAre you sure? (y/N): ").strip().lower()
        if confirm == "y":
            result = self.txn_service.delete_transaction(txn_id)
            if result.is_ok():
                print(success_message(f"Transaction #{txn_id} deleted."))
            else:
                print(error_message(result.unwrap_err()))
        else:
            print(info_message("Deletion cancelled."))

    def search_filter_menu(self) -> None:
        """Handle search and filter menu."""
        print(header("Search & Filter"))
        print("  1. 🏷️  Filter by Category")
        print("  2. 📅 Filter by Date Range")
        print("  3. 💵 Sort by Amount")
        print("  0. ↩️  Back to Main Menu")
        print()

        choice = input("Select option: ").strip()

        if choice == "1":
            self.filter_by_category()
        elif choice == "2":
            self.filter_by_date()
        elif choice == "3":
            self.sort_by_amount()

    def filter_by_category(self) -> None:
        """Filter transactions by category."""
        print("\nCategories:")
        categories = self.cat_service.get_all_categories()
        print(format_categories_table(categories))

        cat_input = input("\nSelect category (number or name): ").strip()
        category = self._resolve_category(cat_input, categories)
        if not category:
            print(error_message(f"Category '{cat_input}' not found."))
            return

        transactions = self.txn_service.filter_by_category(category)

        print(header(f"Transactions in '{category}'"))
        cat_dict = {c.name.lower(): c for c in categories}
        print(format_transactions_table(transactions, cat_dict))

    def filter_by_date(self) -> None:
        """Filter transactions by date range."""
        start = input("Start date (YYYY-MM-DD): ").strip()
        end = input("End date (YYYY-MM-DD): ").strip()

        result = self.txn_service.filter_by_date(start, end)
        if result.is_ok():
            transactions = result.unwrap()
            print(header(f"Transactions from {start} to {end}"))
            categories = {c.name.lower(): c for c in self.cat_service.get_all_categories()}
            print(format_transactions_table(transactions, categories))
        else:
            print(error_message(result.unwrap_err()))

    def sort_by_amount(self) -> None:
        """Sort transactions by amount."""
        order = input("Order (1=Low to High, 2=High to Low): ").strip()
        descending = order == "2"

        transactions = self.txn_service.sort_by_amount(descending=descending)
        print(header("Transactions Sorted by Amount"))
        categories = {c.name.lower(): c for c in self.cat_service.get_all_categories()}
        print(format_transactions_table(transactions, categories))

    def budget_menu(self) -> None:
        """Handle budget management menu."""
        print(header("Budget Management"))
        print("  1. 💰 Set Budget")
        print("  2. 📊 View Budget Status")
        print("  3. 📋 View All Budgets")
        print("  0. ↩️  Back to Main Menu")
        print()

        choice = input("Select option: ").strip()

        if choice == "1":
            self.set_budget()
        elif choice == "2":
            self.view_budget_status()
        elif choice == "3":
            self.view_all_budgets()

    def set_budget(self) -> None:
        """Set budget for a category."""
        print("\nCategories:")
        categories = self.cat_service.get_all_categories()
        print(format_categories_table(categories))

        cat_input = input("\nSelect category (number or name): ").strip()
        category = self._resolve_category(cat_input, categories)
        if not category:
            print(error_message(f"Category '{cat_input}' not found."))
            return

        try:
            limit = float(input("Monthly budget limit: $").strip())
        except ValueError:
            print(error_message("Invalid amount."))
            return

        result = self.budget_service.set_budget(category, limit)
        if result.is_ok():
            print(success_message(f"Budget set: ${limit:.2f}/month for {category}"))
        else:
            print(error_message(result.unwrap_err()))

    def view_budget_status(self) -> None:
        """View budget status for a category."""
        print("\nCategories:")
        categories = self.cat_service.get_all_categories()
        print(format_categories_table(categories))

        cat_input = input("\nSelect category (number or name): ").strip()
        category = self._resolve_category(cat_input, categories)
        if not category:
            print(error_message(f"Category '{cat_input}' not found."))
            return

        result = self.budget_service.get_budget_status(category)
        if result.is_ok():
            status = result.unwrap()
            print(header(f"Budget Status: {status.category}"))
            print(f"  Limit:     ${status.limit:,.2f}")
            print(f"  Spent:     ${status.spent:,.2f}")
            remaining_color = green if status.remaining >= 0 else red
            print(f"  Remaining: {remaining_color(f'${status.remaining:,.2f}')}")
            print(f"  Usage:     {status.percentage:.0f}%")
            if status.exceeded:
                print(red("\n  ⚠️  BUDGET EXCEEDED!"))
            elif status.percentage >= 80:
                print(yellow("\n  ⚡ Warning: Budget almost exhausted"))
        else:
            print(error_message(result.unwrap_err()))

    def view_all_budgets(self) -> None:
        """View all budget statuses."""
        print(header("All Budgets"))
        statuses = self.budget_service.get_all_budgets_status()
        print(format_budget_status_table(statuses))

    def view_summary(self) -> None:
        """View financial summary."""
        print(header("Financial Summary"))

        totals = self.txn_service.get_totals()
        income_str = f"${totals['income']:,.2f}"
        expense_str = f"${totals['expense']:,.2f}"
        print(f"  Total Income:   {green(income_str)}")
        print(f"  Total Expenses: {red(expense_str)}")

        net = totals["net"]
        net_color = green if net >= 0 else red
        net_str = f"${net:,.2f}"
        print(f"  Net Balance:    {net_color(net_str)}")

        print("\n" + bold("Budget Overview:"))
        statuses = self.budget_service.get_all_budgets_status()
        if statuses:
            print(format_budget_status_table(statuses))
        else:
            print(yellow("  No budgets set."))

    def show_help(self) -> None:
        """Display help information."""
        print(header("Help"))
        print(bold("AI Wealth & Spending Companion - Phase I CLI"))
        print()
        print("This is an in-memory finance tracker. All data resets when you exit.")
        print()
        print(bold("Features:"))
        print("  • Add, edit, and delete income/expense transactions")
        print("  • Filter transactions by category or date range")
        print("  • Sort transactions by amount")
        print("  • Set and track budgets per category")
        print("  • View financial summary with totals")
        print()
        print(bold("Transaction Types:"))
        print("  💚 Income  - Money coming in (salary, investments)")
        print("  ❤️  Expense - Money going out (food, rent, utilities)")
        print("  💛 Recurring - Marks repeating transactions")
        print()
        print(bold("Default Categories:"))
        categories = self.cat_service.get_all_categories()
        print(format_categories_table(categories))
        print()
        print(bold("Tips:"))
        print("  • Set budgets to track spending limits")
        print("  • Use the summary view for a quick overview")
        print("  • Filter by date to see monthly spending")
