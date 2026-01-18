"""Main CLI entry point for AI Wealth & Spending Companion."""
import sys

from src.repositories.memory import (
    InMemoryTransactionRepository,
    InMemoryCategoryRepository,
    InMemoryBudgetRepository,
)
from src.services import TransactionService, BudgetService, CategoryService
from src.cli.menus import MenuHandler
from src.cli.formatters import (
    header, success_message, info_message, warning_message, cyan, bold
)


def initialize_services():
    """Initialize all repositories and services."""
    # Create repositories
    txn_repo = InMemoryTransactionRepository()
    cat_repo = InMemoryCategoryRepository()
    budget_repo = InMemoryBudgetRepository()

    # Create services
    cat_service = CategoryService(cat_repo)
    cat_service.load_default_categories()

    txn_service = TransactionService(txn_repo, cat_repo)
    budget_service = BudgetService(budget_repo, txn_repo, cat_repo)

    return txn_service, budget_service, cat_service


def main():
    """Main CLI loop."""
    print(header("Welcome to AI Wealth & Spending Companion"))
    print(info_message("Phase I - CLI Finance Tracker"))
    print(warning_message("All data is stored in memory and will be lost on exit."))
    print()

    # Initialize services
    txn_service, budget_service, cat_service = initialize_services()

    # Create menu handler
    menu = MenuHandler(txn_service, budget_service, cat_service)

    while True:
        try:
            menu.show_main_menu()
            choice = input("Select option (0-8): ").strip()

            if choice == "0":
                print(success_message("Goodbye! Thanks for using AI Wealth & Spending Companion."))
                break
            elif choice == "1":
                menu.add_transaction()
            elif choice == "2":
                menu.list_transactions()
            elif choice == "3":
                menu.edit_transaction()
            elif choice == "4":
                menu.delete_transaction()
            elif choice == "5":
                menu.search_filter_menu()
            elif choice == "6":
                menu.budget_menu()
            elif choice == "7":
                menu.view_summary()
            elif choice == "8":
                menu.show_help()
            else:
                print(warning_message("Invalid option. Please select 0-8."))

            input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            print("\n" + success_message("Goodbye!"))
            break
        except EOFError:
            print("\n" + success_message("Goodbye!"))
            break


if __name__ == "__main__":
    main()
