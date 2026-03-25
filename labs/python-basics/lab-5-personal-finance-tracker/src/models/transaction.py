"""Transaction class for financial operations."""

from datetime import datetime
from typing import Optional
from enum import Enum

class TransactionType(Enum):
    """Transaction type enumeration."""
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"

class TransactionCategory(Enum):
    """Transaction category enumeration."""
    # Income categories
    SALARY = "Salary"
    FREELANCE = "Freelance"
    INVESTMENT = "Investment"
    OTHER_INCOME = "Other Income"
    
    # Expense categories
    FOOD = "Food"
    TRANSPORT = "Transport"
    UTILITIES = "Utilities"
    ENTERTAINMENT = "Entertainment"
    HEALTHCARE = "Healthcare"
    SHOPPING = "Shopping"
    EDUCATION = "Education"
    OTHER_EXPENSE = "Other Expense"

class Transaction:
    """Transaction class with operator overloading."""
    
    def __init__(self, transaction_id: str, amount: float, 
                 transaction_type: TransactionType, category: TransactionCategory,
                 description: str = "", date: Optional[datetime] = None):
        self._transaction_id = transaction_id
        self._amount = abs(amount)  # Always store positive
        self._transaction_type = transaction_type
        self._category = category
        self._description = description
        self._date = date or datetime.now()
    
    @property
    def transaction_id(self) -> str:
        """Get transaction ID."""
        return self._transaction_id
    
    @property
    def amount(self) -> float:
        """Get transaction amount."""
        return self._amount
    
    @property
    def transaction_type(self) -> TransactionType:
        """Get transaction type."""
        return self._transaction_type
    
    @property
    def category(self) -> TransactionCategory:
        """Get transaction category."""
        return self._category
    
    @property
    def description(self) -> str:
        """Get transaction description."""
        return self._description
    
    @property
    def date(self) -> datetime:
        """Get transaction date."""
        return self._date
    
    def get_signed_amount(self) -> float:
        """Get amount with sign based on transaction type."""
        if self._transaction_type == TransactionType.EXPENSE:
            return -self._amount
        return self._amount
    
    def to_dict(self) -> dict:
        """Convert transaction to dictionary for JSON serialization."""
        return {
            "transaction_id": self._transaction_id,
            "amount": self._amount,
            "transaction_type": self._transaction_type.value,
            "category": self._category.value,
            "description": self._description,
            "date": self._date.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """Create transaction from dictionary."""
        return cls(
            transaction_id=data["transaction_id"],
            amount=data["amount"],
            transaction_type=TransactionType(data["transaction_type"]),
            category=TransactionCategory(data["category"]),
            description=data.get("description", ""),
            date=datetime.fromisoformat(data["date"])
        )
    
    # Operator overloading
    def __eq__(self, other) -> bool:
        """Check equality based on transaction ID."""
        if not isinstance(other, Transaction):
            return False
        return self._transaction_id == other._transaction_id
    
    def __add__(self, other) -> float:
        """Add transaction amounts (considering signs)."""
        if isinstance(other, Transaction):
            return self.get_signed_amount() + other.get_signed_amount()
        elif isinstance(other, (int, float)):
            return self.get_signed_amount() + other
        raise TypeError(f"Cannot add Transaction with {type(other)}")
    
    def __radd__(self, other) -> float:
        """Right-side addition."""
        return self.__add__(other)
    
    def __lt__(self, other) -> bool:
        """Compare transactions by date."""
        if isinstance(other, Transaction):
            return self._date < other._date
        raise TypeError(f"Cannot compare Transaction with {type(other)}")
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        sign = "-" if self._transaction_type == TransactionType.EXPENSE else "+"
        return (f"{self._date.strftime('%Y-%m-%d')} | {sign}${self._amount:.2f} | "
                f"{self._category.value} | {self._description}")
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (f"Transaction(id='{self._transaction_id}', "
                f"amount={self._amount}, type={self._transaction_type.value})")
