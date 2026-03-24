"""Helper functions and utilities."""

from typing import List, Dict
from datetime import datetime
import re


def validate_email(email: str) -> bool:
    """Validate email format using regex."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def calculate_grade_percentage(score: float, total: float) -> float:
    """Calculate grade percentage."""
    return (score / total) * 100 if total > 0 else 0


def filter_students_by_course(
    students: Dict, course_code: str, enrollments: Dict
) -> List[str]:
    """Filter students enrolled in a specific course."""
    return [
        students[sid]["name"]
        for sid, courses in enrollments.items()
        if course_code in courses
    ]


def create_menu(options: List[str]) -> None:
    """Create a formatted menu from options list."""
    print("\n" + "=" * 50)
    print("📚 STUDENT COURSE MANAGEMENT SYSTEM")
    print("=" * 50)
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    print("0. Exit")
    print("-" * 50)


def get_user_input(prompt: str, validator=None, error_msg="Invalid input."):
    """Get user input with optional validation."""
    while True:
        value = input(prompt).strip()
        if not validator or validator(value):
            return value
        print(f"❌ {error_msg}")


def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """Safe division with default value."""
    try:
        return a / b
    except ZeroDivisionError:
        return default


# def *args, **kwargs demonstration
def flexible_summary(*args, **kwargs) -> Dict:
    """
    Demonstrate *args and **kwargs usage.
    Args: variable number of student names
    Kwargs: additional information about the summary
    """
    summary = {
        "students_count": len(args),
        "students": list(args),
        "summary_type": kwargs.get("type", "basic"),
        "generated_at": datetime.now().isoformat(),
        "additional_info": kwargs.get("info", "No additional info"),
    }
    return summary
