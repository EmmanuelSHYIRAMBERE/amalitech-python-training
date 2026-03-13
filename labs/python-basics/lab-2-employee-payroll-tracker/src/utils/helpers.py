#!/usr/bin/env python3
"""
Helper utilities for validation and formatting.
"""

import re
from typing import Callable


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email string to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def format_currency(amount: float) -> str:
    """
    Format amount as currency.
    
    Args:
        amount: Amount to format
        
    Returns:
        Formatted currency string
    """
    return f"${amount:,.2f}"


def get_user_input(prompt: str, validator: Callable = None, error_msg: str = None) -> str:
    """
    Get validated user input.
    
    Args:
        prompt: Input prompt message
        validator: Optional validation function
        error_msg: Optional error message for validation failure
        
    Returns:
        Validated user input
    """
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
    """
    Display a numbered menu.
    
    Args:
        options: List of menu option strings
    """
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    print("0. Exit")
