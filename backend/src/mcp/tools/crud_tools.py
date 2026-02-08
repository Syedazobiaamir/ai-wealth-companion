"""Comprehensive CRUD tools for all app features via chatbot."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.category import Category
from src.models.budget import Budget
from src.models.transaction import Transaction, TransactionType
from src.models.wallet import Wallet
from src.models.task import Task, TaskStatus, TaskPriority, TaskCategory


# ============== CATEGORY CRUD ==============

async def create_category(
    user_id: UUID,
    session: AsyncSession,
    name: str,
    category_type: str = "expense",
    icon: str = None,
    color: str = None,
    **kwargs,
) -> Dict[str, Any]:
    """Create a new spending category."""
    # Check if category already exists
    stmt = select(Category).where(
        Category.user_id == user_id,
        Category.name.ilike(name)
    )
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        return {"error": f"Category '{name}' already exists."}

    cat_type = "income" if category_type.lower() == "income" else "expense"
    category = Category(
        user_id=user_id,
        name=name.title(),
        type=cat_type,
        icon=icon or "tag",
        color=color or "#6B7280",
        is_active=True,
    )
    session.add(category)
    await session.commit()
    await session.refresh(category)

    return {
        "category_id": str(category.id),
        "name": category.name,
        "type": cat_type,
        "message": f"Category '{category.name}' created successfully!",
    }


async def list_categories(
    user_id: UUID,
    session: AsyncSession,
    category_type: str = None,
    **kwargs,
) -> Dict[str, Any]:
    """List all categories for the user."""
    stmt = select(Category).where(
        Category.user_id == user_id,
        Category.is_active == True
    )
    if category_type:
        stmt = stmt.where(Category.type == category_type.lower())

    result = await session.execute(stmt)
    categories = result.scalars().all()

    if not categories:
        return {
            "categories": [],
            "total": 0,
            "message": "No categories found. Say 'create category Groceries' to add one!",
        }

    cat_list = [{"id": str(c.id), "name": c.name, "type": c.type} for c in categories]
    expense_cats = [c for c in cat_list if c["type"] == "expense"]
    income_cats = [c for c in cat_list if c["type"] == "income"]

    lines = [f"You have {len(cat_list)} categories:"]
    if expense_cats:
        lines.append(f"  Expense: {', '.join(c['name'] for c in expense_cats)}")
    if income_cats:
        lines.append(f"  Income: {', '.join(c['name'] for c in income_cats)}")

    return {
        "categories": cat_list,
        "total": len(cat_list),
        "message": "\n".join(lines),
    }


async def delete_category(
    user_id: UUID,
    session: AsyncSession,
    name: str,
    **kwargs,
) -> Dict[str, Any]:
    """Delete a category by name."""
    stmt = select(Category).where(
        Category.user_id == user_id,
        Category.name.ilike(f"%{name}%")
    )
    result = await session.execute(stmt)
    category = result.scalar_one_or_none()

    if not category:
        return {"error": f"Category '{name}' not found."}

    category.is_active = False
    await session.commit()

    return {
        "message": f"Category '{category.name}' deleted successfully!",
    }


# ============== BUDGET CRUD ==============

async def list_budgets(
    user_id: UUID,
    session: AsyncSession,
    **kwargs,
) -> Dict[str, Any]:
    """List all budgets for the user."""
    current_month = date.today().month
    current_year = date.today().year

    stmt = select(Budget).where(
        Budget.user_id == user_id,
        Budget.month == current_month,
        Budget.year == current_year,
    )
    result = await session.execute(stmt)
    budgets = result.scalars().all()

    if not budgets:
        return {
            "budgets": [],
            "total": 0,
            "message": "No budgets set for this month. Say 'set budget 5000 for Food' to create one!",
        }

    budget_list = []
    for b in budgets:
        # Get category name
        cat_stmt = select(Category).where(Category.id == b.category_id)
        cat_result = await session.execute(cat_stmt)
        cat = cat_result.scalar_one_or_none()
        cat_name = cat.name if cat else "Unknown"

        budget_list.append({
            "id": str(b.id),
            "category": cat_name,
            "limit": float(b.amount),
            "spent": float(b.spent_amount),
            "remaining": float(b.amount - b.spent_amount),
        })

    lines = [f"Your budgets for {date.today().strftime('%B %Y')}:"]
    for b in budget_list:
        pct = (b["spent"] / b["limit"] * 100) if b["limit"] > 0 else 0
        status = "⚠️" if pct > 80 else "✓"
        lines.append(f"  {status} {b['category']}: {b['spent']:,.0f}/{b['limit']:,.0f} ({pct:.0f}%)")

    return {
        "budgets": budget_list,
        "total": len(budget_list),
        "message": "\n".join(lines),
    }


async def update_budget(
    user_id: UUID,
    session: AsyncSession,
    category: str,
    amount: float,
    **kwargs,
) -> Dict[str, Any]:
    """Update or create a budget for a category."""
    # Find category
    cat_stmt = select(Category).where(
        Category.user_id == user_id,
        Category.name.ilike(f"%{category}%")
    )
    cat_result = await session.execute(cat_stmt)
    cat = cat_result.scalar_one_or_none()

    if not cat:
        return {"error": f"Category '{category}' not found. Create it first!"}

    current_month = date.today().month
    current_year = date.today().year

    # Check if budget exists
    budget_stmt = select(Budget).where(
        Budget.user_id == user_id,
        Budget.category_id == cat.id,
        Budget.month == current_month,
        Budget.year == current_year,
    )
    budget_result = await session.execute(budget_stmt)
    budget = budget_result.scalar_one_or_none()

    if budget:
        budget.amount = Decimal(str(amount))
        await session.commit()
        return {"message": f"Budget for '{cat.name}' updated to PKR {amount:,.0f}!"}
    else:
        new_budget = Budget(
            user_id=user_id,
            category_id=cat.id,
            amount=Decimal(str(amount)),
            spent_amount=Decimal("0"),
            month=current_month,
            year=current_year,
        )
        session.add(new_budget)
        await session.commit()
        return {"message": f"Budget of PKR {amount:,.0f} set for '{cat.name}'!"}


async def delete_budget(
    user_id: UUID,
    session: AsyncSession,
    category: str,
    **kwargs,
) -> Dict[str, Any]:
    """Delete a budget for a category."""
    # Find category
    cat_stmt = select(Category).where(
        Category.user_id == user_id,
        Category.name.ilike(f"%{category}%")
    )
    cat_result = await session.execute(cat_stmt)
    cat = cat_result.scalar_one_or_none()

    if not cat:
        return {"error": f"Category '{category}' not found."}

    current_month = date.today().month
    current_year = date.today().year

    stmt = delete(Budget).where(
        Budget.user_id == user_id,
        Budget.category_id == cat.id,
        Budget.month == current_month,
        Budget.year == current_year,
    )
    await session.execute(stmt)
    await session.commit()

    return {"message": f"Budget for '{cat.name}' deleted!"}


# ============== TRANSACTION CRUD ==============

async def list_transactions(
    user_id: UUID,
    session: AsyncSession,
    limit: int = 10,
    transaction_type: str = None,
    **kwargs,
) -> Dict[str, Any]:
    """List recent transactions."""
    stmt = select(Transaction).where(
        Transaction.user_id == user_id
    ).order_by(Transaction.transaction_date.desc()).limit(limit)

    if transaction_type:
        txn_type = TransactionType.income if transaction_type.lower() == "income" else TransactionType.expense
        stmt = stmt.where(Transaction.type == txn_type)

    result = await session.execute(stmt)
    transactions = result.scalars().all()

    if not transactions:
        return {
            "transactions": [],
            "total": 0,
            "message": "No transactions found. Say 'spent 500 on groceries' to add one!",
        }

    txn_list = []
    for t in transactions:
        # Get category name
        cat_stmt = select(Category).where(Category.id == t.category_id)
        cat_result = await session.execute(cat_stmt)
        cat = cat_result.scalar_one_or_none()
        cat_name = cat.name if cat else "Unknown"

        txn_list.append({
            "id": str(t.id),
            "type": t.type.value,
            "amount": float(t.amount),
            "category": cat_name,
            "date": t.transaction_date.isoformat(),
            "note": t.note,
        })

    lines = [f"Recent transactions ({len(txn_list)}):"]
    for t in txn_list:
        sign = "+" if t["type"] == "income" else "-"
        lines.append(f"  {sign}{t['amount']:,.0f} {t['category']} ({t['date']})")

    return {
        "transactions": txn_list,
        "total": len(txn_list),
        "message": "\n".join(lines),
    }


async def delete_transaction(
    user_id: UUID,
    session: AsyncSession,
    transaction_id: str = None,
    last: bool = False,
    **kwargs,
) -> Dict[str, Any]:
    """Delete a transaction by ID or delete the last one."""
    if last:
        stmt = select(Transaction).where(
            Transaction.user_id == user_id
        ).order_by(Transaction.created_at.desc()).limit(1)
        result = await session.execute(stmt)
        txn = result.scalar_one_or_none()
    elif transaction_id:
        try:
            txn_uuid = UUID(transaction_id)
            stmt = select(Transaction).where(
                Transaction.id == txn_uuid,
                Transaction.user_id == user_id
            )
            result = await session.execute(stmt)
            txn = result.scalar_one_or_none()
        except ValueError:
            return {"error": "Invalid transaction ID."}
    else:
        return {"error": "Please specify which transaction to delete or say 'delete last transaction'."}

    if not txn:
        return {"error": "Transaction not found."}

    # Get category name for confirmation
    cat_stmt = select(Category).where(Category.id == txn.category_id)
    cat_result = await session.execute(cat_stmt)
    cat = cat_result.scalar_one_or_none()
    cat_name = cat.name if cat else "Unknown"

    await session.delete(txn)
    await session.commit()

    return {
        "message": f"Deleted {txn.type.value}: {float(txn.amount):,.0f} ({cat_name})",
    }


# ============== TASK CRUD (update/delete) ==============

async def update_task(
    user_id: UUID,
    session: AsyncSession,
    task_title: str,
    new_title: str = None,
    new_priority: str = None,
    new_due_date: str = None,
    mark_complete: bool = False,
    **kwargs,
) -> Dict[str, Any]:
    """Update a task by title."""
    stmt = select(Task).where(
        Task.user_id == user_id,
        Task.title.ilike(f"%{task_title}%")
    )
    result = await session.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        return {"error": f"Task '{task_title}' not found."}

    if new_title:
        task.title = new_title
    if new_priority:
        try:
            task.priority = TaskPriority(new_priority.lower())
        except ValueError:
            pass
    if new_due_date:
        try:
            task.due_date = date.fromisoformat(new_due_date)
        except ValueError:
            pass
    if mark_complete:
        task.status = TaskStatus.completed
        task.completed_at = datetime.utcnow()

    task.updated_at = datetime.utcnow()
    await session.commit()

    status_msg = "completed" if mark_complete else "updated"
    return {
        "message": f"Task '{task.title}' {status_msg}!",
    }


async def delete_task(
    user_id: UUID,
    session: AsyncSession,
    task_title: str,
    **kwargs,
) -> Dict[str, Any]:
    """Delete a task by title."""
    stmt = select(Task).where(
        Task.user_id == user_id,
        Task.title.ilike(f"%{task_title}%")
    )
    result = await session.execute(stmt)
    task = result.scalar_one_or_none()

    if not task:
        return {"error": f"Task '{task_title}' not found."}

    title = task.title
    await session.delete(task)
    await session.commit()

    return {
        "message": f"Task '{title}' deleted!",
    }


# ============== GOAL CRUD ==============

async def create_goal(
    user_id: UUID,
    session: AsyncSession,
    name: str,
    target_amount: float,
    target_date: str = None,
    **kwargs,
) -> Dict[str, Any]:
    """Create a savings goal."""
    from src.models.goal import Goal

    goal = Goal(
        user_id=user_id,
        name=name,
        target_amount=Decimal(str(target_amount)),
        current_amount=Decimal("0"),
        target_date=date.fromisoformat(target_date) if target_date else None,
        is_active=True,
    )
    session.add(goal)
    await session.commit()
    await session.refresh(goal)

    return {
        "goal_id": str(goal.id),
        "name": goal.name,
        "target": float(goal.target_amount),
        "message": f"Goal '{name}' created! Target: PKR {target_amount:,.0f}",
    }


async def list_goals(
    user_id: UUID,
    session: AsyncSession,
    **kwargs,
) -> Dict[str, Any]:
    """List all savings goals."""
    from src.models.goal import Goal

    stmt = select(Goal).where(
        Goal.user_id == user_id,
        Goal.is_active == True
    )
    result = await session.execute(stmt)
    goals = result.scalars().all()

    if not goals:
        return {
            "goals": [],
            "total": 0,
            "message": "No goals set. Say 'create goal Emergency Fund 100000' to add one!",
        }

    goal_list = []
    lines = ["Your savings goals:"]
    for g in goals:
        pct = (float(g.current_amount) / float(g.target_amount) * 100) if g.target_amount > 0 else 0
        goal_list.append({
            "id": str(g.id),
            "name": g.name,
            "target": float(g.target_amount),
            "current": float(g.current_amount),
            "progress": pct,
        })
        lines.append(f"  • {g.name}: {float(g.current_amount):,.0f}/{float(g.target_amount):,.0f} ({pct:.0f}%)")

    return {
        "goals": goal_list,
        "total": len(goal_list),
        "message": "\n".join(lines),
    }


async def update_goal(
    user_id: UUID,
    session: AsyncSession,
    name: str,
    add_amount: float = None,
    new_target: float = None,
    **kwargs,
) -> Dict[str, Any]:
    """Update a goal - add savings or change target."""
    from src.models.goal import Goal

    stmt = select(Goal).where(
        Goal.user_id == user_id,
        Goal.name.ilike(f"%{name}%"),
        Goal.is_active == True
    )
    result = await session.execute(stmt)
    goal = result.scalar_one_or_none()

    if not goal:
        return {"error": f"Goal '{name}' not found."}

    if add_amount:
        goal.current_amount = goal.current_amount + Decimal(str(add_amount))
        pct = (float(goal.current_amount) / float(goal.target_amount) * 100)
        await session.commit()
        return {
            "message": f"Added PKR {add_amount:,.0f} to '{goal.name}'! Progress: {pct:.0f}%",
        }

    if new_target:
        goal.target_amount = Decimal(str(new_target))
        await session.commit()
        return {
            "message": f"Goal '{goal.name}' target updated to PKR {new_target:,.0f}!",
        }

    return {"error": "Please specify what to update."}


async def delete_goal(
    user_id: UUID,
    session: AsyncSession,
    name: str,
    **kwargs,
) -> Dict[str, Any]:
    """Delete a savings goal."""
    from src.models.goal import Goal

    stmt = select(Goal).where(
        Goal.user_id == user_id,
        Goal.name.ilike(f"%{name}%")
    )
    result = await session.execute(stmt)
    goal = result.scalar_one_or_none()

    if not goal:
        return {"error": f"Goal '{name}' not found."}

    goal_name = goal.name
    goal.is_active = False
    await session.commit()

    return {
        "message": f"Goal '{goal_name}' deleted!",
    }


# ============== WALLET UPDATE/DELETE ==============

async def update_wallet(
    user_id: UUID,
    session: AsyncSession,
    name: str,
    new_name: str = None,
    set_default: bool = False,
    **kwargs,
) -> Dict[str, Any]:
    """Update a wallet."""
    stmt = select(Wallet).where(
        Wallet.user_id == user_id,
        Wallet.name.ilike(f"%{name}%"),
        Wallet.is_active == True
    )
    result = await session.execute(stmt)
    wallet = result.scalar_one_or_none()

    if not wallet:
        return {"error": f"Wallet '{name}' not found."}

    if new_name:
        wallet.name = new_name

    if set_default:
        # Clear other defaults
        clear_stmt = update(Wallet).where(
            Wallet.user_id == user_id,
            Wallet.is_default == True
        ).values(is_default=False)
        await session.execute(clear_stmt)
        wallet.is_default = True

    wallet.updated_at = datetime.utcnow()
    await session.commit()

    msg = f"Wallet '{wallet.name}'"
    if set_default:
        msg += " set as default"
    if new_name:
        msg += f" renamed to '{new_name}'"
    msg += "!"

    return {"message": msg}


async def delete_wallet(
    user_id: UUID,
    session: AsyncSession,
    name: str,
    **kwargs,
) -> Dict[str, Any]:
    """Delete a wallet."""
    stmt = select(Wallet).where(
        Wallet.user_id == user_id,
        Wallet.name.ilike(f"%{name}%"),
        Wallet.is_active == True
    )
    result = await session.execute(stmt)
    wallet = result.scalar_one_or_none()

    if not wallet:
        return {"error": f"Wallet '{name}' not found."}

    wallet_name = wallet.name
    wallet.is_active = False
    await session.commit()

    return {
        "message": f"Wallet '{wallet_name}' deleted!",
    }
