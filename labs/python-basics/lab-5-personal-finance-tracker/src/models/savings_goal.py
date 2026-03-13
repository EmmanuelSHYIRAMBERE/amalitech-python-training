"""Savings goal tracking."""

from datetime import datetime
from typing import Optional

class SavingsGoal:
    """Savings goal with progress tracking."""
    
    def __init__(self, goal_id: str, name: str, target_amount: float,
                 current_amount: float = 0.0, deadline: Optional[datetime] = None):
        self._goal_id = goal_id
        self._name = name
        self._target_amount = target_amount
        self._current_amount = current_amount
        self._deadline = deadline
        self._created_at = datetime.now()
    
    @property
    def goal_id(self) -> str:
        """Get goal ID."""
        return self._goal_id
    
    @property
    def name(self) -> str:
        """Get goal name."""
        return self._name
    
    @property
    def target_amount(self) -> float:
        """Get target amount."""
        return self._target_amount
    
    @property
    def current_amount(self) -> float:
        """Get current amount."""
        return self._current_amount
    
    @property
    def deadline(self) -> Optional[datetime]:
        """Get deadline."""
        return self._deadline
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self._target_amount == 0:
            return 0.0
        return min((self._current_amount / self._target_amount) * 100, 100.0)
    
    @property
    def remaining_amount(self) -> float:
        """Calculate remaining amount to reach goal."""
        return max(self._target_amount - self._current_amount, 0.0)
    
    @property
    def is_achieved(self) -> bool:
        """Check if goal is achieved."""
        return self._current_amount >= self._target_amount
    
    @property
    def is_overdue(self) -> bool:
        """Check if goal is overdue."""
        if not self._deadline or self.is_achieved:
            return False
        return datetime.now() > self._deadline
    
    def add_contribution(self, amount: float) -> None:
        """Add contribution to goal."""
        if amount < 0:
            raise ValueError("Contribution amount must be positive")
        self._current_amount += amount
    
    def withdraw(self, amount: float) -> bool:
        """Withdraw from goal."""
        if amount < 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self._current_amount:
            return False
        self._current_amount -= amount
        return True
    
    def days_remaining(self) -> Optional[int]:
        """Calculate days remaining until deadline."""
        if not self._deadline:
            return None
        delta = self._deadline - datetime.now()
        return max(delta.days, 0)
    
    def to_dict(self) -> dict:
        """Convert goal to dictionary for JSON serialization."""
        return {
            "goal_id": self._goal_id,
            "name": self._name,
            "target_amount": self._target_amount,
            "current_amount": self._current_amount,
            "deadline": self._deadline.isoformat() if self._deadline else None,
            "created_at": self._created_at.isoformat(),
            "progress_percentage": self.progress_percentage,
            "is_achieved": self.is_achieved
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SavingsGoal':
        """Create goal from dictionary."""
        deadline = datetime.fromisoformat(data["deadline"]) if data.get("deadline") else None
        return cls(
            goal_id=data["goal_id"],
            name=data["name"],
            target_amount=data["target_amount"],
            current_amount=data["current_amount"],
            deadline=deadline
        )
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        status = "✅ Achieved" if self.is_achieved else f"{self.progress_percentage:.1f}% Complete"
        return f"{self._name}: ${self._current_amount:.2f} / ${self._target_amount:.2f} ({status})"
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"SavingsGoal(id='{self._goal_id}', name='{self._name}', progress={self.progress_percentage:.1f}%)"
    
    def __eq__(self, other) -> bool:
        """Check equality based on goal ID."""
        if not isinstance(other, SavingsGoal):
            return False
        return self._goal_id == other._goal_id
    
    def __lt__(self, other) -> bool:
        """Compare goals by progress percentage."""
        if isinstance(other, SavingsGoal):
            return self.progress_percentage < other.progress_percentage
        raise TypeError(f"Cannot compare SavingsGoal with {type(other)}")
