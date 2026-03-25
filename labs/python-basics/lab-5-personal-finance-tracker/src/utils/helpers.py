"""Helper functions and utilities."""

from typing import List, Dict, Any, Callable
from datetime import datetime, timedelta
import re

def validate_email(email: str) -> bool:
    """Validate email format using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_amount(amount: str) -> bool:
    """Validate amount format."""
    try:
        value = float(amount)
        return value > 0
    except ValueError:
        return False

def format_currency(amount: float) -> str:
    """Format amount as currency."""
    return f"${amount:,.2f}"

def format_percentage(value: float) -> str:
    """Format value as percentage."""
    return f"{value:.2f}%"

def create_menu(options: List[str]) -> None:
    """Create a formatted menu from options list."""
    print("\n" + "="*60)
    print("💰 PERSONAL FINANCE TRACKER")
    print("="*60)
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    print("0. Exit")
    print("-"*60)

def get_user_input(prompt: str, validator: Callable = None, 
                   error_msg: str = "Invalid input.") -> str:
    """Get user input with optional validation."""
    while True:
        value = input(prompt).strip()
        if not validator or validator(value):
            return value
        print(f"❌ {error_msg}")

def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """Calculate statistics using comprehensions."""
    if not values:
        return {
            "total": 0.0,
            "average": 0.0,
            "min": 0.0,
            "max": 0.0,
            "count": 0
        }
    
    return {
        "total": sum(values),
        "average": sum(values) / len(values),
        "min": min(values),
        "max": max(values),
        "count": len(values)
    }

def filter_by_date_range(items: List[Any], start_date: datetime, 
                        end_date: datetime, date_attr: str = 'date') -> List[Any]:
    """Filter items by date range using comprehension."""
    return [item for item in items 
            if start_date <= getattr(item, date_attr) <= end_date]

def group_by_attribute(items: List[Any], attr: str) -> Dict[Any, List[Any]]:
    """Group items by attribute using comprehension."""
    groups = {}
    for item in items:
        key = getattr(item, attr)
        if key not in groups:
            groups[key] = []
        groups[key].append(item)
    return groups

def calculate_monthly_average(transactions: List[Any], months: int = 12) -> float:
    """Calculate monthly average from transactions."""
    if not transactions or months <= 0:
        return 0.0
    
    total = sum(t.amount for t in transactions)
    return total / months

def get_date_range_options() -> Dict[str, tuple]:
    """Get predefined date range options."""
    today = datetime.now()
    return {
        "This Month": (today.replace(day=1), today),
        "Last Month": (
            (today.replace(day=1) - timedelta(days=1)).replace(day=1),
            today.replace(day=1) - timedelta(days=1)
        ),
        "Last 3 Months": (today - timedelta(days=90), today),
        "Last 6 Months": (today - timedelta(days=180), today),
        "This Year": (today.replace(month=1, day=1), today),
        "Last Year": (
            today.replace(year=today.year-1, month=1, day=1),
            today.replace(year=today.year-1, month=12, day=31)
        )
    }

def calculate_budget_variance(actual: float, budgeted: float) -> Dict[str, Any]:
    """Calculate budget variance."""
    variance = actual - budgeted
    variance_percentage = (variance / budgeted * 100) if budgeted != 0 else 0
    
    return {
        "actual": actual,
        "budgeted": budgeted,
        "variance": variance,
        "variance_percentage": variance_percentage,
        "status": "Over Budget" if variance > 0 else "Under Budget" if variance < 0 else "On Budget"
    }

def generate_financial_summary(*accounts, **options) -> Dict[str, Any]:
    """
    Generate financial summary using *args and **kwargs.
    
    Args:
        *accounts: Variable number of account objects
        **options: Additional options
            - include_details: bool
            - period: str
    
    Returns:
        Dictionary with financial summary
    """
    total_balance = sum(acc.balance for acc in accounts)
    total_income = sum(acc.get_total_income() for acc in accounts)
    total_expenses = sum(acc.get_total_expenses() for acc in accounts)
    
    summary = {
        "total_accounts": len(accounts),
        "total_balance": total_balance,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_savings": total_income - total_expenses,
        "savings_rate": (total_income - total_expenses) / total_income * 100 if total_income > 0 else 0,
        "period": options.get("period", "All Time"),
        "generated_at": datetime.now().isoformat()
    }
    
    if options.get("include_details", False):
        summary["accounts"] = [
            {
                "name": acc.account_name,
                "type": acc.get_account_type(),
                "balance": acc.balance
            }
            for acc in accounts
        ]
    
    return summary

def calculate_expense_breakdown(transactions: List[Any]) -> Dict[str, float]:
    """Calculate expense breakdown by category using comprehension."""
    breakdown = {}
    for transaction in transactions:
        if hasattr(transaction, 'category'):
            category = transaction.category.value
            if category not in breakdown:
                breakdown[category] = 0.0
            breakdown[category] += transaction.amount
    return breakdown

def find_largest_transactions(transactions: List[Any], n: int = 5) -> List[Any]:
    """Find N largest transactions using sorted comprehension."""
    return sorted(transactions, key=lambda t: t.amount, reverse=True)[:n]

def calculate_spending_trend(transactions: List[Any], days: int = 30) -> Dict[str, float]:
    """Calculate spending trend over specified days."""
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_transactions = [t for t in transactions 
                          if t.date >= cutoff_date]
    
    if not recent_transactions:
        return {"daily_average": 0.0, "total": 0.0, "days": days}
    
    total = sum(t.amount for t in recent_transactions)
    return {
        "daily_average": total / days,
        "total": total,
        "days": days
    }
