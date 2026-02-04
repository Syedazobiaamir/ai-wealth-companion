#!/usr/bin/env python3
"""Seed demo data for AI Wealth Companion.

Usage:
    cd backend
    python scripts/seed_demo_data.py

This creates a demo user with realistic financial data including:
- Wallets (cash, bank, savings)
- Categories (food, transport, utilities, etc.)
- Transactions (income & expenses over 3 months)
- Budgets for current month
- Sample tasks
"""

import asyncio
import random
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Import models
import sys
sys.path.insert(0, '/home/ibek34578921/hackathone2/backend')

from src.models.user import User
from src.models.wallet import Wallet, WalletType
from src.models.category import Category
from src.models.transaction import Transaction, TransactionType
from src.models.budget import Budget
from src.models.task import Task, TaskPriority, TaskCategory
from src.core.config import get_settings
from src.core.security import hash_password

settings = get_settings()

# Demo user credentials
DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "demo1234"

# Categories with realistic spending patterns
CATEGORIES = [
    {"name": "Salary", "emoji": "💰", "type": "income", "monthly_range": (80000, 120000)},
    {"name": "Freelance", "emoji": "💻", "type": "income", "monthly_range": (10000, 30000)},
    {"name": "Food & Dining", "emoji": "🍔", "type": "expense", "monthly_range": (15000, 25000)},
    {"name": "Transport", "emoji": "🚗", "type": "expense", "monthly_range": (8000, 15000)},
    {"name": "Utilities", "emoji": "💡", "type": "expense", "monthly_range": (5000, 10000)},
    {"name": "Shopping", "emoji": "🛒", "type": "expense", "monthly_range": (5000, 15000)},
    {"name": "Entertainment", "emoji": "🎬", "type": "expense", "monthly_range": (3000, 8000)},
    {"name": "Healthcare", "emoji": "🏥", "type": "expense", "monthly_range": (2000, 6000)},
    {"name": "Education", "emoji": "📚", "type": "expense", "monthly_range": (3000, 10000)},
    {"name": "Groceries", "emoji": "🥬", "type": "expense", "monthly_range": (10000, 18000)},
    {"name": "Rent", "emoji": "🏠", "type": "expense", "monthly_range": (25000, 35000)},
    {"name": "Internet & Phone", "emoji": "📱", "type": "expense", "monthly_range": (2000, 4000)},
]

# Wallets
WALLETS = [
    {"name": "Cash Wallet", "type": WalletType.cash, "initial": 15000, "color": "#22c55e"},
    {"name": "HBL Bank", "type": WalletType.bank, "initial": 85000, "color": "#3b82f6"},
    {"name": "Emergency Fund", "type": WalletType.savings, "initial": 50000, "color": "#f59e0b"},
]

# Tasks
TASKS = [
    {"title": "Pay electricity bill", "priority": TaskPriority.high, "category": TaskCategory.bills, "due_days": 3},
    {"title": "Review monthly budget", "priority": TaskPriority.medium, "category": TaskCategory.review, "due_days": 7},
    {"title": "Transfer to savings", "priority": TaskPriority.medium, "category": TaskCategory.savings, "due_days": 5},
    {"title": "Check investment portfolio", "priority": TaskPriority.low, "category": TaskCategory.investment, "due_days": 14},
]


async def seed_demo_data():
    """Main seeding function."""
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if demo user exists
        result = await session.execute(select(User).where(User.email == DEMO_EMAIL))
        existing_user = result.scalars().first()

        if existing_user:
            print(f"Demo user already exists: {DEMO_EMAIL}")
            user_id = existing_user.id
        else:
            # Create demo user
            user = User(
                id=uuid4(),
                email=DEMO_EMAIL,
                password_hash=hash_password(DEMO_PASSWORD),
                display_name="Demo User",
                preferred_currency="PKR",
                preferred_locale="en",
                is_active=True,
                is_demo_user=True,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            user_id = user.id
            print(f"Created demo user: {DEMO_EMAIL} / {DEMO_PASSWORD}")

        # Create or get categories
        category_map = {}
        for cat_data in CATEGORIES:
            result = await session.execute(select(Category).where(Category.name == cat_data["name"]))
            existing_cat = result.scalars().first()
            if existing_cat:
                category_map[cat_data["name"]] = existing_cat.id
            else:
                cat = Category(id=uuid4(), name=cat_data["name"], emoji=cat_data["emoji"])
                session.add(cat)
                await session.flush()
                category_map[cat_data["name"]] = cat.id
        await session.commit()
        print(f"Categories ready: {len(category_map)}")

        # Create wallets
        result = await session.execute(select(Wallet).where(Wallet.user_id == user_id))
        existing_wallets = result.scalars().all()
        if not existing_wallets:
            for i, w_data in enumerate(WALLETS):
                wallet = Wallet(
                    id=uuid4(),
                    user_id=user_id,
                    name=w_data["name"],
                    type=w_data["type"],
                    currency="PKR",
                    initial_balance=Decimal(str(w_data["initial"])),
                    current_balance=Decimal(str(w_data["initial"])),
                    color=w_data["color"],
                    is_default=(i == 1),  # Bank is default
                )
                session.add(wallet)
            await session.commit()
            print(f"Created {len(WALLETS)} wallets")
        else:
            print(f"Wallets already exist: {len(existing_wallets)}")

        # Get default wallet
        result = await session.execute(select(Wallet).where(Wallet.user_id == user_id, Wallet.is_default == True))
        default_wallet = result.scalars().first()
        wallet_id = default_wallet.id if default_wallet else None

        # Create transactions for last 3 months (delete existing first)
        from sqlalchemy import delete
        await session.execute(delete(Transaction).where(Transaction.user_id == user_id))
        await session.commit()
        print("Cleared existing transactions...")

        if True:
            today = date.today()
            transactions_created = 0

            for month_offset in range(3):
                # Calculate month
                month_date = today - timedelta(days=30 * month_offset)
                month = month_date.month
                year = month_date.year
                days_in_month = 28 if month == 2 else 30

                for cat_data in CATEGORIES:
                    cat_id = category_map[cat_data["name"]]
                    tx_type = TransactionType.income if cat_data["type"] == "income" else TransactionType.expense
                    min_amt, max_amt = cat_data["monthly_range"]

                    # Number of transactions per category per month
                    if cat_data["name"] in ["Salary"]:
                        num_transactions = 1  # Monthly salary
                    elif cat_data["name"] in ["Rent", "Internet & Phone", "Utilities"]:
                        num_transactions = 1  # Monthly bills
                    elif cat_data["name"] in ["Food & Dining", "Groceries"]:
                        num_transactions = random.randint(8, 15)  # Frequent
                    else:
                        num_transactions = random.randint(2, 6)

                    # Total amount for the month
                    total_monthly = random.randint(min_amt, max_amt)

                    for i in range(num_transactions):
                        # Distribute amount
                        if num_transactions == 1:
                            amount = total_monthly
                        else:
                            # Random portion of remaining
                            remaining = total_monthly // (num_transactions - i) if i < num_transactions - 1 else total_monthly
                            amount = random.randint(remaining // 2, remaining) if remaining > 0 else 100
                            total_monthly -= amount

                        # Set day: Salary on 1st, bills on 5th, others random
                        if cat_data["name"] == "Salary":
                            day = 1  # Salary always on 1st
                        elif cat_data["name"] in ["Rent", "Internet & Phone", "Utilities"]:
                            day = 5  # Bills on 5th
                        else:
                            day = random.randint(1, min(days_in_month, 28))
                        tx_date = date(year, month, day)

                        # Don't create future transactions
                        if tx_date > today:
                            continue

                        tx = Transaction(
                            id=uuid4(),
                            user_id=user_id,
                            wallet_id=wallet_id,
                            type=tx_type,
                            amount=Decimal(str(max(100, amount))),
                            category_id=cat_id,
                            transaction_date=tx_date,
                            note=f"Demo {cat_data['name'].lower()} transaction",
                            is_recurring=cat_data["name"] in ["Salary", "Rent", "Utilities", "Internet & Phone"],
                        )
                        session.add(tx)
                        transactions_created += 1

            await session.commit()
            print(f"Created {transactions_created} transactions")

        # Create budgets for current month
        result = await session.execute(select(Budget).where(Budget.user_id == user_id).limit(1))
        if result.scalars().first():
            print("Budgets already exist, skipping...")
        else:
            current_month = today.month
            current_year = today.year
            budgets_created = 0

            for cat_data in CATEGORIES:
                if cat_data["type"] == "expense":
                    cat_id = category_map[cat_data["name"]]
                    _, max_amt = cat_data["monthly_range"]
                    # Budget slightly higher than max to show realistic usage
                    limit = Decimal(str(int(max_amt * 1.1)))

                    budget = Budget(
                        id=uuid4(),
                        user_id=user_id,
                        category_id=cat_id,
                        limit_amount=limit,
                        month=current_month,
                        year=current_year,
                        alert_threshold=80,
                    )
                    session.add(budget)
                    budgets_created += 1

            await session.commit()
            print(f"Created {budgets_created} budgets")

        # Create tasks
        result = await session.execute(select(Task).where(Task.user_id == user_id).limit(1))
        if result.scalars().first():
            print("Tasks already exist, skipping...")
        else:
            for task_data in TASKS:
                task = Task(
                    id=uuid4(),
                    user_id=user_id,
                    title=task_data["title"],
                    priority=task_data["priority"],
                    category=task_data["category"],
                    due_date=today + timedelta(days=task_data["due_days"]),
                    is_completed=False,
                )
                session.add(task)
            await session.commit()
            print(f"Created {len(TASKS)} tasks")

        print("\n" + "=" * 50)
        print("Demo data seeding complete!")
        print("=" * 50)
        print(f"\nLogin credentials:")
        print(f"  Email: {DEMO_EMAIL}")
        print(f"  Password: {DEMO_PASSWORD}")
        print(f"\nGo to: http://localhost:3000/login")


if __name__ == "__main__":
    asyncio.run(seed_demo_data())
