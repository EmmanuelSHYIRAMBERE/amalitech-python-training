"""Helper functions and utilities."""

from typing import List, Dict, Any
from datetime import datetime
import re

def validate_email(email: str) -> bool:
    """Validate email format using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    pattern = r'^\+?[\d\s\-()]{10,}$'
    return re.match(pattern, phone) is not None

def create_menu(options: List[str]) -> None:
    """Create a formatted menu from options list."""
    print("\n" + "="*60)
    print("🚗 VEHICLE RENTAL SYSTEM")
    print("="*60)
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    print("0. Exit")
    print("-"*60)

def get_user_input(prompt: str, validator=None, error_msg="Invalid input."):
    """Get user input with optional validation."""
    while True:
        value = input(prompt).strip()
        if not validator or validator(value):
            return value
        print(f"❌ {error_msg}")

def format_currency(amount: float) -> str:
    """Format amount as currency."""
    return f"${amount:.2f}"

def calculate_discount(base_cost: float, days: int) -> float:
    """Calculate discount based on rental duration."""
    if days >= 30:
        return base_cost * 0.20  # 20% discount
    elif days >= 14:
        return base_cost * 0.15  # 15% discount
    elif days >= 7:
        return base_cost * 0.10  # 10% discount
    return 0.0

def generate_rental_summary(*rentals, **kwargs) -> Dict[str, Any]:
    """
    Generate rental summary using *args and **kwargs.
    Args: variable number of rental objects
    Kwargs: additional summary options
    """
    total_revenue = sum(r.total_cost for r in rentals)
    active_rentals = sum(1 for r in rentals if not r.is_returned)
    
    summary = {
        "total_rentals": len(rentals),
        "active_rentals": active_rentals,
        "completed_rentals": len(rentals) - active_rentals,
        "total_revenue": total_revenue,
        "summary_type": kwargs.get("type", "basic"),
        "generated_at": datetime.now().isoformat(),
        "include_details": kwargs.get("details", False)
    }
    return summary
