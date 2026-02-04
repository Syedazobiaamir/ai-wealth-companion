"""Official MCP Server using the mcp SDK.

This module creates an MCP server with financial tools using the official
Model Context Protocol SDK.
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import UUID

from mcp.server import FastMCP
from mcp.types import TextContent

# Create MCP server instance
mcp = FastMCP("ai-wealth-companion")


# ── Financial Summary Tool ─────────────────────────────────────────────

@mcp.tool()
async def get_financial_summary(
    period: str = "month",
    user_id: str = "",
) -> Dict[str, Any]:
    """
    Get the user's financial overview including income, expenses, and savings.

    Args:
        period: Time period - 'week', 'month', or 'year'
        user_id: User ID (injected by system)

    Returns:
        Financial summary with income, expenses, net balance, and savings rate
    """
    # This will be called with actual DB session in production
    return {
        "period": period,
        "income": 0,
        "expenses": 0,
        "net_balance": 0,
        "savings_rate": 0,
        "message": "Use with database session for real data"
    }


# ── Budget Tool ────────────────────────────────────────────────────────

@mcp.tool()
async def create_budget(
    category: str,
    amount: float,
    month: Optional[int] = None,
    year: Optional[int] = None,
    user_id: str = "",
) -> Dict[str, Any]:
    """
    Create a monthly budget for a specific category.

    Args:
        category: Budget category name (e.g., 'Food', 'Entertainment')
        amount: Monthly spending limit
        month: Month number (1-12), defaults to current month
        year: Year, defaults to current year
        user_id: User ID (injected by system)

    Returns:
        Created budget details
    """
    today = date.today()
    return {
        "category": category,
        "limit": amount,
        "month": month or today.month,
        "year": year or today.year,
        "status": "created",
        "message": f"Budget of {amount} set for {category}"
    }


# ── Transaction Tool ───────────────────────────────────────────────────

@mcp.tool()
async def add_transaction(
    type: str,
    amount: float,
    category: str,
    note: Optional[str] = None,
    date: Optional[str] = None,
    user_id: str = "",
) -> Dict[str, Any]:
    """
    Record a financial transaction (income or expense).

    Args:
        type: Transaction type - 'income' or 'expense'
        amount: Transaction amount
        category: Category name
        note: Optional description
        date: Transaction date (YYYY-MM-DD), defaults to today
        user_id: User ID (injected by system)

    Returns:
        Recorded transaction details
    """
    return {
        "type": type,
        "amount": amount,
        "category": category,
        "note": note,
        "date": date or str(date.today()),
        "status": "recorded",
        "message": f"Recorded {type} of {amount} in {category}"
    }


# ── Spending Analysis Tool ─────────────────────────────────────────────

@mcp.tool()
async def analyze_spending(
    period: str = "month",
    category: Optional[str] = None,
    user_id: str = "",
) -> Dict[str, Any]:
    """
    Analyze spending patterns including trends and category breakdown.

    Args:
        period: Time period - 'week', 'month', or 'year'
        category: Optional specific category to analyze
        user_id: User ID (injected by system)

    Returns:
        Spending analysis with trends and recommendations
    """
    return {
        "period": period,
        "category": category,
        "total_spent": 0,
        "top_categories": [],
        "trend": "stable",
        "recommendations": []
    }


# ── Investment Simulation Tool ─────────────────────────────────────────

@mcp.tool()
async def simulate_investment(
    amount: float,
    months: int,
    user_id: str = "",
) -> Dict[str, Any]:
    """
    Run investment projection with conservative, moderate, and aggressive scenarios.

    Args:
        amount: Investment amount
        months: Investment duration in months
        user_id: User ID (injected by system)

    Returns:
        Investment projections with disclaimer
    """
    # Simple compound interest calculation
    rates = {"conservative": 0.06, "moderate": 0.10, "aggressive": 0.15}
    projections = {}

    for scenario, annual_rate in rates.items():
        monthly_rate = annual_rate / 12
        final_value = amount * ((1 + monthly_rate) ** months)
        projections[scenario] = {
            "final_value": round(final_value, 2),
            "total_return": round(final_value - amount, 2),
            "return_percentage": round((final_value - amount) / amount * 100, 2)
        }

    return {
        "initial_amount": amount,
        "duration_months": months,
        "projections": projections,
        "disclaimer": "This is a simulation only. Past performance does not guarantee future results. Consult a licensed financial advisor."
    }


# ── Task Management Tools ──────────────────────────────────────────────

@mcp.tool()
async def create_task(
    title: str,
    priority: str = "medium",
    category: str = "other",
    due_date: Optional[str] = None,
    user_id: str = "",
) -> Dict[str, Any]:
    """
    Create a task or reminder for the user.

    Args:
        title: Task title/description
        priority: Priority level - 'high', 'medium', or 'low'
        category: Task category - 'bills', 'savings', 'review', 'investment', 'budget', 'other'
        due_date: Due date in YYYY-MM-DD format
        user_id: User ID (injected by system)

    Returns:
        Created task details
    """
    return {
        "title": title,
        "priority": priority,
        "category": category,
        "due_date": due_date,
        "status": "created",
        "message": f"Task '{title}' created with {priority} priority"
    }


@mcp.tool()
async def list_tasks(
    status: str = "active",
    user_id: str = "",
) -> Dict[str, Any]:
    """
    List user's tasks filtered by status.

    Args:
        status: Filter - 'active', 'overdue', or 'all'
        user_id: User ID (injected by system)

    Returns:
        List of tasks matching the filter
    """
    return {
        "status": status,
        "tasks": [],
        "count": 0
    }


@mcp.tool()
async def get_task_summary(user_id: str = "") -> Dict[str, Any]:
    """
    Get overview of user's tasks including counts by status.

    Args:
        user_id: User ID (injected by system)

    Returns:
        Task summary with counts
    """
    return {
        "total": 0,
        "active": 0,
        "completed": 0,
        "overdue": 0,
        "due_soon": 0
    }


@mcp.tool()
async def complete_task(
    task_id: str,
    user_id: str = "",
) -> Dict[str, Any]:
    """
    Mark a task as completed.

    Args:
        task_id: The ID of the task to complete
        user_id: User ID (injected by system)

    Returns:
        Updated task status
    """
    return {
        "task_id": task_id,
        "status": "completed",
        "message": "Task marked as complete"
    }


@mcp.tool()
async def update_task(
    task_id: str,
    title: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    user_id: str = "",
) -> Dict[str, Any]:
    """
    Update an existing task's properties.

    Args:
        task_id: The ID of the task to update
        title: New task title (optional)
        priority: New priority level (optional)
        due_date: New due date (optional)
        user_id: User ID (injected by system)

    Returns:
        Updated task details
    """
    updates = {}
    if title:
        updates["title"] = title
    if priority:
        updates["priority"] = priority
    if due_date:
        updates["due_date"] = due_date

    return {
        "task_id": task_id,
        "updates": updates,
        "status": "updated",
        "message": "Task updated successfully"
    }


# ── Health Score Tool ─────────────────────────────────────────────────

@mcp.tool()
async def get_health_score(user_id: str = "") -> Dict[str, Any]:
    """
    Calculate the user's financial health score (0-100).

    The score is based on:
    - Budget adherence (40%)
    - Savings rate (30%)
    - Spending consistency (20%)
    - Goal progress (10%)

    Args:
        user_id: User ID (injected by system)

    Returns:
        Health score with breakdown and recommendations
    """
    return {
        "score": 0,
        "grade": "Needs Assessment",
        "breakdown": {
            "budget_adherence": 0,
            "savings_rate": 0,
            "spending_consistency": 0,
            "goal_progress": 0
        },
        "recommendations": [
            "Start tracking your expenses to get your health score"
        ]
    }


# ── Dashboard Metrics Tool ─────────────────────────────────────────────

@mcp.tool()
async def get_dashboard_metrics(user_id: str = "") -> Dict[str, Any]:
    """
    Get dashboard data including health scores and recommendations.

    Args:
        user_id: User ID (injected by system)

    Returns:
        Dashboard metrics for AI insight cards
    """
    return {
        "health_score": 0,
        "income": 0,
        "expenses": 0,
        "budgets_on_track": 0,
        "budgets_exceeded": 0,
        "alerts": [],
        "recommendations": []
    }


# Export the MCP server
def get_mcp_server() -> FastMCP:
    """Return the configured MCP server instance."""
    return mcp


# Get tool definitions for OpenAI function calling format
def get_openai_tools() -> list:
    """Convert MCP tools to OpenAI function calling format."""
    tools = []
    for name, tool in mcp._tools.items():
        tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": tool.description or "",
                "parameters": tool.parameters or {"type": "object", "properties": {}}
            }
        })
    return tools
