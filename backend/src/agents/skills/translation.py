"""Translation skill — language detection and Urdu formatting."""

import re
from typing import Any, Dict, Optional, Tuple

# Urdu script range
URDU_RANGE = re.compile(r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]')

# Common Roman Urdu words
ROMAN_URDU_WORDS = {
    "kya", "hai", "mera", "meri", "mere", "kitna", "kitni", "batao",
    "dikhao", "aaj", "kal", "mahina", "saal", "paisa", "paise",
    "budget", "kharcha", "kharch", "kamai", "tankhwa", "bachat",
    "hisab", "kitab", "ghar", "kiraya", "bijli", "kirana",
    "khana", "dawai", "kapray", "petrol", "masla", "shukriya",
    "theek", "acha", "nahi", "haan", "ji", "karo", "karna",
    "daalo", "likho", "banao", "jama", "raqam",
}


def detect_language(text: str) -> str:
    """Detect if text is English, Urdu script, or Roman Urdu.
    Returns 'en', 'ur', or 'ur-roman'.
    """
    # Check for Urdu script characters
    if URDU_RANGE.search(text):
        return "ur"

    # Check for Roman Urdu words
    words = set(text.lower().split())
    urdu_count = len(words & ROMAN_URDU_WORDS)
    total = len(words)

    if total > 0 and urdu_count / total >= 0.3:
        return "ur-roman"

    return "en"


def format_currency_urdu(amount: float, currency: str = "PKR") -> str:
    """Format currency in Urdu style."""
    formatted = f"{amount:,.0f}"
    if currency == "PKR":
        return f"₨ {formatted}"
    return f"{formatted} {currency}"


def format_date_urdu(date_str: str) -> str:
    """Format date in Urdu-friendly way."""
    URDU_MONTHS = {
        "01": "جنوری", "02": "فروری", "03": "مارچ",
        "04": "اپریل", "05": "مئی", "06": "جون",
        "07": "جولائی", "08": "اگست", "09": "ستمبر",
        "10": "اکتوبر", "11": "نومبر", "12": "دسمبر",
    }
    try:
        parts = date_str.split("-")
        month = URDU_MONTHS.get(parts[1], parts[1])
        return f"{parts[2]} {month} {parts[0]}"
    except (IndexError, ValueError):
        return date_str


def translate_response_hint(text: str, language: str) -> Optional[str]:
    """Provide Urdu translation hints for common phrases.
    Full translation requires LLM; this handles key financial terms.
    """
    if language == "en":
        return None

    # Common financial response translations
    TRANSLATIONS = {
        "Your balance is": "آپ کا بیلنس ہے",
        "Budget exceeded": "بجٹ سے زیادہ خرچ",
        "Budget warning": "بجٹ کی وارننگ",
        "Transaction recorded": "لین دین درج ہو گیا",
        "income": "آمدنی",
        "expense": "خرچ",
        "savings": "بچت",
        "budget": "بجٹ",
        "goal": "ہدف",
        "category": "زمرہ",
        "total": "کل",
    }

    result = text
    for en, ur in TRANSLATIONS.items():
        if en.lower() in text.lower():
            result = result + f"\n\n({ur})"
            break

    return result if result != text else None
