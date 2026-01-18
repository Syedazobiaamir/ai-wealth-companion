"""Budget service for business logic."""
from typing import List

from src.models import Budget, BudgetStatus, Result
from src.repositories.base import BudgetRepository, TransactionRepository, CategoryRepository


class BudgetService:
    """Business logic for budget operations."""

    def __init__(
        self,
        budget_repo: BudgetRepository,
        transaction_repo: TransactionRepository,
        category_repo: CategoryRepository,
    ):
        self._budget_repo = budget_repo
        self._txn_repo = transaction_repo
        self._cat_repo = category_repo

    def set_budget(self, category: str, limit: float) -> Result[Budget, str]:
        """
        Set monthly budget for a category.

        Args:
            category: Category name (must exist)
            limit: Budget limit (must be > 0)

        Returns:
            Result with Budget on success, error message on failure
        """
        # Validate category exists
        if not self._cat_repo.exists(category):
            return Result.err(f"Category '{category}' not found.")

        # Validate limit
        if limit <= 0:
            return Result.err(f"Invalid limit {limit}. Limit must be greater than 0.")

        budget = Budget(category=category, limit=limit)
        created = self._budget_repo.set(budget)
        return Result.ok(created)

    def get_budget_status(self, category: str) -> Result[BudgetStatus, str]:
        """
        Get budget status for a category.

        Args:
            category: Category name

        Returns:
            Result with BudgetStatus on success, error message on failure
        """
        # Check category exists
        if not self._cat_repo.exists(category):
            return Result.err(f"Category '{category}' not found.")

        # Check budget is set
        budget = self._budget_repo.get_by_category(category)
        if budget is None:
            return Result.err(f"No budget set for category '{category}'.")

        # Calculate spent from expense transactions
        spent = self._calculate_spent(category)

        # Calculate status
        remaining = budget.limit - spent
        percentage = (spent / budget.limit) * 100 if budget.limit > 0 else 0
        exceeded = spent > budget.limit

        status = BudgetStatus(
            category=category,
            limit=budget.limit,
            spent=spent,
            remaining=remaining,
            percentage=percentage,
            exceeded=exceeded,
        )

        return Result.ok(status)

    def get_all_budgets_status(self) -> List[BudgetStatus]:
        """Get status for all budgets."""
        statuses = []
        for budget in self._budget_repo.get_all():
            result = self.get_budget_status(budget.category)
            if result.is_ok():
                statuses.append(result.unwrap())
        return statuses

    def _calculate_spent(self, category: str) -> float:
        """Calculate total expense amount for a category."""
        transactions = self._txn_repo.filter_by_category(category)
        return sum(t.amount for t in transactions if t.is_expense())
