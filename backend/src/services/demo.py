"""Demo service for generating sample data."""

import random
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.budget import Budget
from src.models.category import Category
from src.models.goal import Goal, GoalStatus
from src.models.transaction import Transaction, TransactionType
from src.models.user import User
from src.models.wallet import Wallet, WalletType


class DemoService:
    """Service for demo data generation."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def seed_demo_data(
        self,
        user_id: UUID,
        months: int = 6,
    ) -> Dict[str, Any]:
        """Generate comprehensive demo data for a user."""
        # Clear existing data for user
        await self._clear_user_data(user_id)

        # Create wallets
        wallets = await self._create_demo_wallets(user_id)

        # Get or create categories
        categories = await self._get_or_create_categories()

        # Create transactions
        transactions = await self._create_demo_transactions(
            user_id, wallets, categories, months
        )

        # Create budgets
        budgets = await self._create_demo_budgets(user_id, categories)

        # Create goals
        goals = await self._create_demo_goals(user_id)

        # Mark user as demo user
        await self._mark_demo_user(user_id)

        return {
            "success": True,
            "data": {
                "wallets_created": len(wallets),
                "transactions_created": len(transactions),
                "budgets_created": len(budgets),
                "goals_created": len(goals),
                "period_months": months,
            },
            "meta": {
                "generated_at": datetime.utcnow().isoformat() + "Z",
            },
        }

    async def reset_demo_data(self, user_id: UUID) -> Dict[str, Any]:
        """Reset demo data for a user."""
        await self._clear_user_data(user_id)
        return {
            "success": True,
            "data": {
                "message": "Demo data has been reset",
            },
        }

    async def _clear_user_data(self, user_id: UUID) -> None:
        """Clear all user data."""
        # Delete in order due to foreign keys
        await self.session.execute(
            delete(Transaction).where(Transaction.user_id == user_id)
        )
        await self.session.execute(
            delete(Budget).where(Budget.user_id == user_id)
        )
        await self.session.execute(
            delete(Goal).where(Goal.user_id == user_id)
        )
        await self.session.execute(
            delete(Wallet).where(Wallet.user_id == user_id)
        )
        await self.session.flush()

    async def _mark_demo_user(self, user_id: UUID) -> None:
        """Mark user as demo user."""
        statement = select(User).where(User.id == user_id)
        result = await self.session.execute(statement)
        user = result.scalar_one_or_none()
        if user:
            user.is_demo_user = True
            await self.session.flush()

    async def _create_demo_wallets(self, user_id: UUID) -> List[Wallet]:
        """Create demo wallets."""
        wallet_configs = [
            {
                "name": "Main Account",
                "type": WalletType.bank,
                "initial_balance": Decimal("125000.00"),
                "color": "#4CAF50",
                "icon": "bank",
                "is_default": True,
            },
            {
                "name": "Cash",
                "type": WalletType.cash,
                "initial_balance": Decimal("15000.00"),
                "color": "#8BC34A",
                "icon": "cash",
                "is_default": False,
            },
            {
                "name": "Savings",
                "type": WalletType.savings,
                "initial_balance": Decimal("250000.00"),
                "color": "#2196F3",
                "icon": "piggy-bank",
                "is_default": False,
            },
        ]

        wallets = []
        for config in wallet_configs:
            wallet = Wallet(
                user_id=user_id,
                name=config["name"],
                type=config["type"],
                currency="PKR",
                initial_balance=config["initial_balance"],
                current_balance=config["initial_balance"],
                color=config["color"],
                icon=config["icon"],
                is_default=config["is_default"],
            )
            self.session.add(wallet)
            wallets.append(wallet)

        await self.session.flush()
        for w in wallets:
            await self.session.refresh(w)
        return wallets

    async def _get_or_create_categories(self) -> Dict[str, Category]:
        """Get or create system categories."""
        # Check if categories exist
        statement = select(Category)
        result = await self.session.execute(statement)
        existing = {c.name: c for c in result.scalars().all()}

        if existing:
            return existing

        # Create default categories
        category_configs = [
            # Expenses
            {"name": "Food & Dining", "name_ur": "کھانا", "type": TransactionType.expense, "emoji": "🍔", "color": "#FF6B6B", "is_system": True},
            {"name": "Transportation", "name_ur": "نقل و حمل", "type": TransactionType.expense, "emoji": "🚗", "color": "#4ECDC4", "is_system": True},
            {"name": "Shopping", "name_ur": "خریداری", "type": TransactionType.expense, "emoji": "🛍️", "color": "#9B59B6", "is_system": True},
            {"name": "Utilities", "name_ur": "یوٹیلیٹیز", "type": TransactionType.expense, "emoji": "💡", "color": "#F39C12", "is_system": True},
            {"name": "Healthcare", "name_ur": "صحت", "type": TransactionType.expense, "emoji": "🏥", "color": "#E74C3C", "is_system": True},
            {"name": "Entertainment", "name_ur": "تفریح", "type": TransactionType.expense, "emoji": "🎬", "color": "#3498DB", "is_system": True},
            {"name": "Education", "name_ur": "تعلیم", "type": TransactionType.expense, "emoji": "📚", "color": "#1ABC9C", "is_system": True},
            {"name": "Rent", "name_ur": "کرایہ", "type": TransactionType.expense, "emoji": "🏠", "color": "#95A5A6", "is_system": True},
            # Income
            {"name": "Salary", "name_ur": "تنخواہ", "type": TransactionType.income, "emoji": "💵", "color": "#27AE60", "is_system": True},
            {"name": "Freelance", "name_ur": "فری لانس", "type": TransactionType.income, "emoji": "💼", "color": "#2ECC71", "is_system": True},
            {"name": "Investment", "name_ur": "سرمایہ کاری", "type": TransactionType.income, "emoji": "📈", "color": "#16A085", "is_system": True},
            {"name": "Gift", "name_ur": "تحفہ", "type": TransactionType.income, "emoji": "🎁", "color": "#E91E63", "is_system": True},
        ]

        categories = {}
        for config in category_configs:
            category = Category(
                name=config["name"],
                name_ur=config["name_ur"],
                type=config["type"],
                emoji=config["emoji"],
                color=config["color"],
                is_system=config["is_system"],
            )
            self.session.add(category)
            categories[config["name"]] = category

        await self.session.flush()
        for c in categories.values():
            await self.session.refresh(c)
        return categories

    async def _create_demo_transactions(
        self,
        user_id: UUID,
        wallets: List[Wallet],
        categories: Dict[str, Category],
        months: int,
    ) -> List[Transaction]:
        """Create demo transactions over specified months."""
        transactions = []
        today = date.today()
        main_wallet = wallets[0]  # Use main wallet for most transactions

        # Expense patterns (category, min_amount, max_amount, frequency_per_month)
        expense_patterns = [
            ("Food & Dining", 200, 2000, 20),
            ("Transportation", 500, 3000, 8),
            ("Shopping", 1000, 15000, 4),
            ("Utilities", 5000, 15000, 1),
            ("Healthcare", 500, 5000, 1),
            ("Entertainment", 500, 3000, 4),
            ("Education", 2000, 10000, 1),
            ("Rent", 25000, 35000, 1),
        ]

        # Income patterns
        income_patterns = [
            ("Salary", 70000, 80000, 1),
            ("Freelance", 5000, 20000, 2),
        ]

        notes_expense = [
            "Weekly groceries",
            "Lunch with colleagues",
            "Dinner out",
            "Coffee shop",
            "Uber ride",
            "Petrol fill-up",
            "Online shopping",
            "Electricity bill",
            "Gas bill",
            "Internet bill",
            "Doctor visit",
            "Medicine",
            "Movie tickets",
            "Netflix subscription",
            "Tuition fee",
            "Books purchase",
        ]

        notes_income = [
            "Monthly salary",
            "Bonus payment",
            "Freelance project",
            "Client payment",
            "Investment return",
            "Dividend",
        ]

        for month_offset in range(months):
            # Calculate month
            target_month = today.month - month_offset
            target_year = today.year
            while target_month <= 0:
                target_month += 12
                target_year -= 1

            month_start = date(target_year, target_month, 1)
            if target_month == 12:
                month_end = date(target_year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = date(target_year, target_month + 1, 1) - timedelta(days=1)

            # Generate expenses
            for cat_name, min_amt, max_amt, freq in expense_patterns:
                category = categories.get(cat_name)
                if not category:
                    continue

                for _ in range(freq):
                    amount = Decimal(str(random.randint(min_amt, max_amt)))
                    tx_date = month_start + timedelta(
                        days=random.randint(0, (month_end - month_start).days)
                    )

                    # Don't create future transactions
                    if tx_date > today:
                        continue

                    tx = Transaction(
                        user_id=user_id,
                        wallet_id=main_wallet.id,
                        category_id=category.id,
                        type=TransactionType.expense,
                        amount=amount,
                        transaction_date=tx_date,
                        note=random.choice(notes_expense),
                    )
                    self.session.add(tx)
                    transactions.append(tx)

            # Generate income
            for cat_name, min_amt, max_amt, freq in income_patterns:
                category = categories.get(cat_name)
                if not category:
                    continue

                for _ in range(freq):
                    amount = Decimal(str(random.randint(min_amt, max_amt)))
                    # Income typically comes at specific times
                    if cat_name == "Salary":
                        tx_date = date(target_year, target_month, 1)
                    else:
                        tx_date = month_start + timedelta(
                            days=random.randint(0, (month_end - month_start).days)
                        )

                    if tx_date > today:
                        continue

                    tx = Transaction(
                        user_id=user_id,
                        wallet_id=main_wallet.id,
                        category_id=category.id,
                        type=TransactionType.income,
                        amount=amount,
                        transaction_date=tx_date,
                        note=random.choice(notes_income),
                    )
                    self.session.add(tx)
                    transactions.append(tx)

        await self.session.flush()
        return transactions

    async def _create_demo_budgets(
        self,
        user_id: UUID,
        categories: Dict[str, Category],
    ) -> List[Budget]:
        """Create demo budgets for current month."""
        today = date.today()
        budgets = []

        budget_configs = [
            ("Food & Dining", 15000),
            ("Transportation", 10000),
            ("Shopping", 20000),
            ("Entertainment", 5000),
            ("Utilities", 15000),
        ]

        for cat_name, limit in budget_configs:
            category = categories.get(cat_name)
            if not category:
                continue

            budget = Budget(
                user_id=user_id,
                category_id=category.id,
                limit_amount=Decimal(str(limit)),
                month=today.month,
                year=today.year,
                alert_threshold=80,
            )
            self.session.add(budget)
            budgets.append(budget)

        await self.session.flush()
        return budgets

    async def _create_demo_goals(self, user_id: UUID) -> List[Goal]:
        """Create demo financial goals."""
        goals = []
        today = date.today()

        goal_configs = [
            {
                "name": "Emergency Fund",
                "description": "6 months of expenses saved",
                "target_amount": Decimal("300000"),
                "current_amount": Decimal("180000"),
                "emoji": "🛡️",
                "color": "#FF6B6B",
                "priority": 10,
                "target_date": date(today.year + 1, 6, 1),
            },
            {
                "name": "New Laptop",
                "description": "MacBook Pro for work",
                "target_amount": Decimal("350000"),
                "current_amount": Decimal("150000"),
                "emoji": "💻",
                "color": "#4ECDC4",
                "priority": 7,
                "target_date": date(today.year, 12, 31),
            },
            {
                "name": "Vacation Fund",
                "description": "Trip to Turkey",
                "target_amount": Decimal("200000"),
                "current_amount": Decimal("50000"),
                "emoji": "✈️",
                "color": "#9B59B6",
                "priority": 5,
                "target_date": date(today.year + 1, 3, 1),
            },
        ]

        for config in goal_configs:
            goal = Goal(
                user_id=user_id,
                name=config["name"],
                description=config["description"],
                target_amount=config["target_amount"],
                current_amount=config["current_amount"],
                currency="PKR",
                target_date=config["target_date"],
                emoji=config["emoji"],
                color=config["color"],
                priority=config["priority"],
                status=GoalStatus.active,
            )
            self.session.add(goal)
            goals.append(goal)

        await self.session.flush()
        return goals
