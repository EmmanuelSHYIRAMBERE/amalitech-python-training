"""Account classes with inheritance and polymorphism."""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
from src.models.transaction import Transaction, TransactionType, TransactionCategory

class Account(ABC):
    """Abstract base class for all account types."""
    
    def __init__(self, account_id: str, account_name: str, 
                 initial_balance: float = 0.0):
        self._account_id = account_id
        self._account_name = account_name
        self._initial_balance = initial_balance
        self._transactions: List[Transaction] = []
        self._created_at = datetime.now()
    
    @property
    def account_id(self) -> str:
        """Get account ID."""
        return self._account_id
    
    @property
    def account_name(self) -> str:
        """Get account name."""
        return self._account_name
    
    @account_name.setter
    def account_name(self, value: str) -> None:
        """Set account name with validation."""
        if not value or len(value.strip()) < 2:
            raise ValueError("Account name must be at least 2 characters")
        self._account_name = value.strip()
    
    @property
    def balance(self) -> float:
        """Calculate current balance using comprehension."""
        transaction_sum = sum(t.get_signed_amount() for t in self._transactions)
        return self._initial_balance + transaction_sum
    
    @property
    def transactions(self) -> List[Transaction]:
        """Get list of transactions."""
        return self._transactions.copy()
    
    @property
    def created_at(self) -> datetime:
        """Get account creation date."""
        return self._created_at
    
    @abstractmethod
    def get_account_type(self) -> str:
        """Get account type description."""
        pass
    
    @abstractmethod
    def can_withdraw(self, amount: float) -> bool:
        """Check if withdrawal is allowed."""
        pass
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """Add a transaction to the account."""
        # Check if withdrawal is allowed
        if transaction.transaction_type == TransactionType.EXPENSE:
            if not self.can_withdraw(transaction.amount):
                return False
        
        self._transactions.append(transaction)
        return True
    
    def get_transactions_by_type(self, transaction_type: TransactionType) -> List[Transaction]:
        """Get transactions filtered by type using comprehension."""
        return [t for t in self._transactions if t.transaction_type == transaction_type]
    
    def get_transactions_by_category(self, category: TransactionCategory) -> List[Transaction]:
        """Get transactions filtered by category using comprehension."""
        return [t for t in self._transactions if t.category == category]
    
    def get_total_income(self) -> float:
        """Calculate total income using comprehension."""
        return sum(t.amount for t in self._transactions 
                  if t.transaction_type == TransactionType.INCOME)
    
    def get_total_expenses(self) -> float:
        """Calculate total expenses using comprehension."""
        return sum(t.amount for t in self._transactions 
                  if t.transaction_type == TransactionType.EXPENSE)
    
    def get_transactions_summary(self) -> Dict[str, float]:
        """Get summary of transactions by category using comprehension."""
        summary = {}
        for transaction in self._transactions:
            category = transaction.category.value
            if category not in summary:
                summary[category] = 0.0
            summary[category] += transaction.get_signed_amount()
        return summary
    
    def to_dict(self) -> dict:
        """Convert account to dictionary for JSON serialization."""
        return {
            "account_id": self._account_id,
            "account_name": self._account_name,
            "account_type": self.get_account_type(),
            "initial_balance": self._initial_balance,
            "current_balance": self.balance,
            "created_at": self._created_at.isoformat(),
            "transactions": [t.to_dict() for t in self._transactions]
        }
    
    # Operator overloading
    def __eq__(self, other) -> bool:
        """Check equality based on account ID."""
        if not isinstance(other, Account):
            return False
        return self._account_id == other._account_id
    
    def __add__(self, other) -> float:
        """Add account balances."""
        if isinstance(other, Account):
            return self.balance + other.balance
        elif isinstance(other, (int, float)):
            return self.balance + other
        raise TypeError(f"Cannot add Account with {type(other)}")
    
    def __radd__(self, other) -> float:
        """Right-side addition."""
        return self.__add__(other)
    
    def __lt__(self, other) -> bool:
        """Compare accounts by balance."""
        if isinstance(other, Account):
            return self.balance < other.balance
        raise TypeError(f"Cannot compare Account with {type(other)}")
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        return (f"{self.get_account_type()}: {self._account_name} "
                f"(Balance: ${self.balance:.2f})")
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (f"{self.__class__.__name__}(id='{self._account_id}', "
                f"name='{self._account_name}', balance={self.balance:.2f})")

class CheckingAccount(Account):
    """Checking account with overdraft protection."""
    
    def __init__(self, account_id: str, account_name: str, 
                 initial_balance: float = 0.0, overdraft_limit: float = 0.0):
        super().__init__(account_id, account_name, initial_balance)
        self._overdraft_limit = overdraft_limit
    
    @property
    def overdraft_limit(self) -> float:
        """Get overdraft limit."""
        return self._overdraft_limit
    
    @overdraft_limit.setter
    def overdraft_limit(self, value: float) -> None:
        """Set overdraft limit."""
        if value < 0:
            raise ValueError("Overdraft limit cannot be negative")
        self._overdraft_limit = value
    
    def get_account_type(self) -> str:
        """Get account type."""
        return "Checking Account"
    
    def can_withdraw(self, amount: float) -> bool:
        """Check if withdrawal is allowed (including overdraft)."""
        return (self.balance - amount) >= -self._overdraft_limit
    
    def get_available_balance(self) -> float:
        """Get available balance including overdraft."""
        return self.balance + self._overdraft_limit

class SavingsAccount(Account):
    """Savings account with interest rate."""
    
    def __init__(self, account_id: str, account_name: str, 
                 initial_balance: float = 0.0, interest_rate: float = 0.01,
                 minimum_balance: float = 0.0):
        super().__init__(account_id, account_name, initial_balance)
        self._interest_rate = interest_rate
        self._minimum_balance = minimum_balance
    
    @property
    def interest_rate(self) -> float:
        """Get interest rate."""
        return self._interest_rate
    
    @interest_rate.setter
    def interest_rate(self, value: float) -> None:
        """Set interest rate."""
        if value < 0 or value > 1:
            raise ValueError("Interest rate must be between 0 and 1")
        self._interest_rate = value
    
    @property
    def minimum_balance(self) -> float:
        """Get minimum balance requirement."""
        return self._minimum_balance
    
    def get_account_type(self) -> str:
        """Get account type."""
        return f"Savings Account ({self._interest_rate*100:.2f}% APY)"
    
    def can_withdraw(self, amount: float) -> bool:
        """Check if withdrawal maintains minimum balance."""
        return (self.balance - amount) >= self._minimum_balance
    
    def calculate_interest(self) -> float:
        """Calculate interest on current balance."""
        return self.balance * self._interest_rate
    
    def apply_interest(self, transaction_id: str) -> Transaction:
        """Apply interest to account."""
        interest = self.calculate_interest()
        transaction = Transaction(
            transaction_id=transaction_id,
            amount=interest,
            transaction_type=TransactionType.INCOME,
            category=TransactionCategory.INVESTMENT,
            description="Interest earned"
        )
        self.add_transaction(transaction)
        return transaction

class InvestmentAccount(Account):
    """Investment account for stocks, bonds, etc."""
    
    def __init__(self, account_id: str, account_name: str, 
                 initial_balance: float = 0.0, risk_level: str = "Medium"):
        super().__init__(account_id, account_name, initial_balance)
        self._risk_level = risk_level
        self._holdings: Dict[str, float] = {}  # symbol: quantity
    
    @property
    def risk_level(self) -> str:
        """Get risk level."""
        return self._risk_level
    
    @risk_level.setter
    def risk_level(self, value: str) -> None:
        """Set risk level."""
        valid_levels = ["Low", "Medium", "High"]
        if value not in valid_levels:
            raise ValueError(f"Risk level must be one of {valid_levels}")
        self._risk_level = value
    
    @property
    def holdings(self) -> Dict[str, float]:
        """Get investment holdings."""
        return self._holdings.copy()
    
    def get_account_type(self) -> str:
        """Get account type."""
        return f"Investment Account (Risk: {self._risk_level})"
    
    def can_withdraw(self, amount: float) -> bool:
        """Check if withdrawal is allowed (must have sufficient balance)."""
        return self.balance >= amount
    
    def add_holding(self, symbol: str, quantity: float) -> None:
        """Add investment holding."""
        if symbol in self._holdings:
            self._holdings[symbol] += quantity
        else:
            self._holdings[symbol] = quantity
    
    def remove_holding(self, symbol: str, quantity: float) -> bool:
        """Remove investment holding."""
        if symbol not in self._holdings:
            return False
        if self._holdings[symbol] < quantity:
            return False
        self._holdings[symbol] -= quantity
        if self._holdings[symbol] == 0:
            del self._holdings[symbol]
        return True
