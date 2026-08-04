#!/usr/bin/env python3
"""
Helper utilities for validation and formatting.
"""

import re
from typing import Callable


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_isbn(isbn: str) -> bool:
    """Validate ISBN format (ISBN-10 or ISBN-13)."""
    isbn = isbn.replace('-', '').replace(' ', '')
    return len(isbn) in [10, 13] and isbn.isdigit()


def get_user_input(prompt: str, validator: Callable = None, error_msg: str = None) -> str:
    """Get validated user input."""
    while True:
        try:
            user_input = input(prompt).strip()
            if validator is None or validator(user_input):
                return user_input
            if error_msg:
                print(f"❌ {error_msg}")
        except (KeyboardInterrupt, EOFError):
            raise
        except Exception as e:
            print(f"❌ Invalid input: {e}")


def create_menu(options: list):
    """Display a numbered menu."""
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    print("0. Back/Exit")


def format_date(dt) -> str:
    """Format datetime object."""
    if dt is None:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M")
