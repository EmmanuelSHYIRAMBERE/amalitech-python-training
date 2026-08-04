#!/usr/bin/env python3
"""
Employee Payroll Tracker
Main entry point for the console application.
"""

from colorama import Fore
from app import PayrollSystem
from menu_handlers import MenuHandlers


def main():
    """Main entry point."""
    try:
        system = PayrollSystem()
        menu_handler = MenuHandlers(system)
        menu_handler.run_main_menu()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\n⚠️ Program interrupted by user.")
    except Exception as e:
        print(Fore.RED + f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print(Fore.GREEN + "\nGoodbye!")


if __name__ == "__main__":
    main()
