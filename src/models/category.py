"""Category model for transaction classification."""
from dataclasses import dataclass, field


@dataclass
class Category:
    """
    Represents a classification for transactions.

    Attributes:
        name: Unique category identifier (e.g., "Food", "Rent")
        emoji: Optional display icon (e.g., "🍔", "🏠")
    """
    name: str
    emoji: str = field(default="")

    def display(self) -> str:
        """Return display string with emoji if present."""
        if self.emoji:
            return f"{self.emoji} {self.name}"
        return self.name

    def __hash__(self):
        return hash(self.name)
