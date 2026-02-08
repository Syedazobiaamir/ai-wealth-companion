"""MCP server setup — exposes financial tools for agent consumption."""

from typing import Any, Callable, Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.mcp.tools.financial_summary import get_financial_summary
from src.mcp.tools.budget_tools import create_budget
from src.mcp.tools.transaction_tools import add_transaction
from src.mcp.tools.spending_analysis import analyze_spending
from src.mcp.tools.investment_tools import simulate_investment
from src.mcp.tools.dashboard_metrics import generate_dashboard_metrics
from src.mcp.tools.task_tools import create_task, list_tasks, get_task_summary
from src.mcp.tools.wallet_tools import create_wallet, list_wallets, get_wallet_balance


# Tool registry with JSON schema descriptions
TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "get_financial_summary": {
        "description": "Get the user's financial overview including income, expenses, savings, and category breakdown for a given period.",
        "parameters": {
            "type": "object",
            "properties": {
                "period": {
                    "type": "string",
                    "enum": ["week", "month", "year"],
                    "default": "month",
                    "description": "Time period for the summary.",
                },
            },
            "required": [],
        },
        "handler": get_financial_summary,
    },
    "create_budget": {
        "description": "Create a monthly budget for a specific category with a spending limit.",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Budget category name (e.g. Food, Entertainment).",
                },
                "amount": {
                    "type": "number",
                    "description": "Monthly spending limit.",
                },
                "month": {"type": "integer", "description": "Month number (1-12)."},
                "year": {"type": "integer", "description": "Year."},
            },
            "required": ["category", "amount"],
        },
        "handler": create_budget,
    },
    "add_transaction": {
        "description": "Record a financial transaction (income or expense).",
        "parameters": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["income", "expense"],
                    "description": "Transaction type.",
                },
                "amount": {"type": "number", "description": "Transaction amount."},
                "category": {"type": "string", "description": "Category name."},
                "note": {"type": "string", "description": "Optional description."},
                "date": {"type": "string", "description": "Transaction date (YYYY-MM-DD). Defaults to today."},
            },
            "required": ["type", "amount", "category"],
        },
        "handler": add_transaction,
    },
    "analyze_spending": {
        "description": "Analyze spending patterns including trends, anomalies, and category comparisons.",
        "parameters": {
            "type": "object",
            "properties": {
                "period": {
                    "type": "string",
                    "enum": ["week", "month", "year"],
                    "default": "month",
                },
                "category": {
                    "type": "string",
                    "description": "Optional category to focus analysis on.",
                },
            },
            "required": [],
        },
        "handler": analyze_spending,
    },
    "simulate_investment": {
        "description": "Run an investment projection showing conservative, moderate, and aggressive return scenarios. Includes mandatory disclaimer.",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Investment amount."},
                "months": {"type": "integer", "description": "Investment duration in months."},
            },
            "required": ["amount", "months"],
        },
        "handler": simulate_investment,
    },
    "generate_dashboard_metrics": {
        "description": "Get dashboard data including health scores, alerts, and recommendations for AI insight cards.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
        "handler": generate_dashboard_metrics,
    },
    "create_task": {
        "description": "Create a task or reminder for the user.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Task title."},
                "priority": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                    "default": "medium",
                    "description": "Task priority.",
                },
                "category": {
                    "type": "string",
                    "enum": ["bills", "savings", "review", "investment", "budget", "other"],
                    "default": "other",
                    "description": "Task category.",
                },
                "due_date": {
                    "type": "string",
                    "description": "Due date in YYYY-MM-DD format.",
                },
            },
            "required": ["title"],
        },
        "handler": create_task,
    },
    "list_tasks": {
        "description": "List the user's tasks filtered by status.",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["active", "overdue", "all"],
                    "default": "active",
                    "description": "Filter: active, overdue, or all.",
                },
            },
            "required": [],
        },
        "handler": list_tasks,
    },
    "get_task_summary": {
        "description": "Get an overview of the user's tasks including active, completed, overdue, and due-soon counts.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
        "handler": get_task_summary,
    },
    "create_wallet": {
        "description": "Create a new wallet for storing money (cash, bank account, credit card, savings, or investment account).",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Wallet name (e.g., 'My Cash', 'Bank Account', 'Savings').",
                },
                "wallet_type": {
                    "type": "string",
                    "enum": ["cash", "bank", "credit", "savings", "investment"],
                    "default": "cash",
                    "description": "Type of wallet.",
                },
                "initial_balance": {
                    "type": "number",
                    "default": 0,
                    "description": "Starting balance.",
                },
                "currency": {
                    "type": "string",
                    "default": "PKR",
                    "description": "Currency code.",
                },
            },
            "required": ["name"],
        },
        "handler": create_wallet,
    },
    "list_wallets": {
        "description": "List all wallets and their balances.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
        "handler": list_wallets,
    },
    "get_wallet_balance": {
        "description": "Get total balance across all wallets.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
        "handler": get_wallet_balance,
    },
}


def get_tool_definitions() -> List[Dict[str, Any]]:
    """Return OpenAI-compatible tool definitions for agent registration."""
    tools = []
    for name, config in TOOL_REGISTRY.items():
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": config["description"],
                    "parameters": config["parameters"],
                },
            }
        )
    return tools


def _validate_tool_args(tool_name: str, arguments: Dict[str, Any]) -> Optional[str]:
    """Validate tool arguments against JSON schema. Returns error message or None."""
    schema = TOOL_REGISTRY[tool_name]["parameters"]
    required = schema.get("required", [])
    properties = schema.get("properties", {})

    # Check required fields
    for field in required:
        if field not in arguments:
            return f"Missing required parameter: {field}"

    # Check types
    for key, value in arguments.items():
        if key not in properties:
            continue
        expected = properties[key].get("type")
        if expected == "string" and not isinstance(value, str):
            return f"Parameter '{key}' must be a string"
        if expected == "number" and not isinstance(value, (int, float)):
            return f"Parameter '{key}' must be a number"
        if expected == "integer" and not isinstance(value, int):
            return f"Parameter '{key}' must be an integer"
        # Check enum constraints
        if "enum" in properties[key] and value not in properties[key]["enum"]:
            return f"Parameter '{key}' must be one of: {properties[key]['enum']}"

    return None


async def execute_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    user_id: UUID,
    session: AsyncSession,
) -> Dict[str, Any]:
    """Execute a registered MCP tool by name with validation."""
    import logging

    logger = logging.getLogger("mcp.tools")

    if tool_name not in TOOL_REGISTRY:
        return {"error": f"Unknown tool: {tool_name}", "status": "error"}

    # Validate arguments against schema
    validation_error = _validate_tool_args(tool_name, arguments)
    if validation_error:
        logger.warning("Tool %s validation failed: %s", tool_name, validation_error)
        return {"error": validation_error, "status": "validation_error", "tool": tool_name}

    handler = TOOL_REGISTRY[tool_name]["handler"]
    try:
        logger.info("Executing tool=%s user=%s", tool_name, user_id)
        result = await handler(user_id=user_id, session=session, **arguments)
        logger.info("Tool %s completed successfully", tool_name)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error("Tool %s failed: %s", tool_name, str(e), exc_info=True)
        return {"error": str(e), "status": "error", "tool": tool_name}
