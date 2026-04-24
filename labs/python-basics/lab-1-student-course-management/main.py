#!/usr/bin/env python3
"""
Student Course Management System
Main entry point for the console application.
"""

import logging

from colorama import Fore

from app import StudentCourseManagementSystem
from menu_handlers import MenuHandlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Initialise and run the Student Course Management System."""
    try:
        system = StudentCourseManagementSystem()
        menu_handler = MenuHandlers(system)
        menu_handler.run_main_menu()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\n⚠️  Program interrupted by user.")
        logger.info("Application interrupted by user (KeyboardInterrupt)")
    except Exception as e:
        logger.exception("Unhandled exception: %s", e)
        print(Fore.RED + f"\n❌ An error occurred: {e}")
    finally:
        print(Fore.GREEN + "\nGoodbye!")


if __name__ == "__main__":
    main()
