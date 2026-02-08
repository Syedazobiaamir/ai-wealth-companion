"""Finance CRUD skill — parses natural language into financial operations."""

import re
from datetime import date
from typing import Any, Dict, List, Optional, Tuple


# Common Urdu/Roman-Urdu financial terms mapped to categories
CATEGORY_ALIASES = {
    "kirana": "Groceries", "grocery": "Groceries", "groceries": "Groceries",
    "khana": "Food", "food": "Food", "restaurant": "Food", "dining": "Food",
    "petrol": "Transportation", "transport": "Transportation", "uber": "Transportation", "careem": "Transportation",
    "rent": "Housing", "kiraya": "Housing", "ghar": "Housing",
    "bijli": "Utilities", "electricity": "Utilities", "gas": "Utilities", "pani": "Utilities", "water": "Utilities",
    "entertainment": "Entertainment", "movie": "Entertainment", "fun": "Entertainment",
    "shopping": "Shopping", "kapray": "Shopping", "clothes": "Shopping",
    "health": "Healthcare", "doctor": "Healthcare", "dawai": "Healthcare", "medicine": "Healthcare",
    "education": "Education", "school": "Education", "tuition": "Education", "fees": "Education",
    "savings": "Savings", "bachat": "Savings",
    "salary": "Salary", "tankhwa": "Salary", "income": "Salary",
    "freelance": "Freelance", "side": "Freelance",
    "investment": "Investment", "invest": "Investment",
}

# Amount patterns
AMOUNT_PATTERN = re.compile(
    r'(?:PKR|Rs\.?|₨)?\s*(\d[\d,]*(?:\.\d+)?)\s*(?:PKR|Rs\.?|₨|rupees?)?',
    re.IGNORECASE,
)


def extract_amount(text: str) -> Optional[float]:
    """Extract monetary amount from text.

    Supports:
    - PKR, Rs., ₨ formats
    - Numbers with commas (15,000)
    - "15k", "15 thousand", "15 hazar" (thousand)
    - "2 lakh", "2 lac" (100,000)
    - Urdu: "pachees hazar" (25,000), "das hazar" (10,000)
    """
    # First check for lakh/lac (100,000)
    lakh_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakh|lac|لاکھ)', text, re.IGNORECASE)
    if lakh_match:
        return float(lakh_match.group(1)) * 100000

    # Check for words like "15 thousand" or "15k" or "15 hazar"
    k_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:k|thousand|hazar|ہزار)', text, re.IGNORECASE)
    if k_match:
        return float(k_match.group(1)) * 1000

    # Standard numeric patterns
    match = AMOUNT_PATTERN.search(text)
    if match:
        raw = match.group(1).replace(",", "")
        return float(raw)

    # Urdu number words (common ones)
    urdu_numbers = {
        "ek": 1, "do": 2, "teen": 3, "char": 4, "panch": 5,
        "che": 6, "saat": 7, "aath": 8, "nau": 9, "das": 10,
        "gyara": 11, "bara": 12, "tera": 13, "chauda": 14, "pandra": 15,
        "sola": 16, "satra": 17, "athra": 18, "unees": 19, "bees": 20,
        "pachees": 25, "tees": 30, "chalees": 40, "pachas": 50,
        "sath": 60, "sattar": 70, "assi": 80, "nabbe": 90, "sau": 100,
    }
    lower = text.lower()
    for word, value in urdu_numbers.items():
        if word in lower:
            # Check if followed by hazar/lakh
            if "hazar" in lower or "ہزار" in lower:
                return float(value) * 1000
            elif "lakh" in lower or "lac" in lower or "لاکھ" in lower:
                return float(value) * 100000
            elif "sau" in lower and word != "sau":
                return float(value) * 100
            else:
                return float(value)

    return None


def extract_category(text: str) -> Optional[str]:
    """Extract category name from text using alias mapping."""
    lower = text.lower()
    for alias, category in CATEGORY_ALIASES.items():
        if alias in lower:
            return category
    return None


def extract_date(text: str) -> Optional[date]:
    """Extract date from text. Supports 'today', 'yesterday', 'kal', YYYY-MM-DD."""
    lower = text.lower()
    today = date.today()
    if "today" in lower or "aaj" in lower:
        return today
    if "yesterday" in lower or "kal" in lower:
        from datetime import timedelta
        return today - timedelta(days=1)
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
    if date_match:
        try:
            return date.fromisoformat(date_match.group(1))
        except ValueError:
            pass
    return None


def classify_intent(text: str) -> Tuple[str, float]:
    """Classify the financial intent of a message.
    Returns (intent, confidence).
    """
    lower = text.lower()

    # Wallet-related patterns (check first, as they have specific handling)
    wallet_words = ["wallet", "wallets", "account", "paisa", "paisay"]
    wallet_create = ["create", "add", "new", "make", "open", "banao"]
    wallet_query = ["show", "list", "my", "all", "balance", "dikhao", "kitna"]

    has_wallet = any(w in lower for w in wallet_words)
    if has_wallet:
        if any(w in lower for w in wallet_create):
            return ("create_wallet", 0.9)
        if any(w in lower for w in wallet_query):
            return ("list_wallets", 0.9)

    # Create/add patterns
    create_patterns = [
        "add", "create", "set", "new", "record", "log", "make",
        "spent", "paid", "bought", "earned", "received",
        "daalo", "likho", "banao", "jama",
    ]
    # Query patterns
    query_patterns = [
        "show", "get", "what", "how much", "how is", "list", "balance",
        "expenses", "income", "budget", "summary", "status",
        "dikhao", "batao", "kitna", "kya",
    ]
    # Analysis patterns
    analysis_patterns = [
        "analyze", "analyse", "why", "compare", "trend", "pattern",
        "predict", "forecast", "insight", "health", "score",
    ]
    # Update patterns
    update_patterns = [
        "update", "change", "modify", "edit", "increase", "decrease",
    ]
    # Delete patterns
    delete_patterns = [
        "delete", "remove", "cancel",
    ]

    for p in create_patterns:
        if p in lower:
            return ("create", 0.85)
    for p in query_patterns:
        if p in lower:
            return ("query", 0.85)
    for p in analysis_patterns:
        if p in lower:
            return ("analyze", 0.85)
    for p in update_patterns:
        if p in lower:
            return ("update", 0.8)
    for p in delete_patterns:
        if p in lower:
            return ("delete", 0.8)

    # Check if it contains an amount (likely a transaction)
    if extract_amount(text):
        return ("create", 0.6)

    return ("query", 0.5)


def extract_transaction_type(text: str) -> str:
    """Determine if this is income or expense."""
    lower = text.lower()
    income_words = ["income", "salary", "earned", "received", "tankhwa", "aaya", "mila", "freelance"]
    for w in income_words:
        if w in lower:
            return "income"
    return "expense"


def parse_financial_command(text: str) -> Dict[str, Any]:
    """Parse a natural language financial command into structured data."""
    intent, confidence = classify_intent(text)
    amount = extract_amount(text)
    category = extract_category(text)
    txn_date = extract_date(text)
    txn_type = extract_transaction_type(text)

    return {
        "intent": intent,
        "confidence": confidence,
        "amount": amount,
        "category": category,
        "transaction_type": txn_type,
        "date": txn_date.isoformat() if txn_date else None,
        "raw_text": text,
    }
