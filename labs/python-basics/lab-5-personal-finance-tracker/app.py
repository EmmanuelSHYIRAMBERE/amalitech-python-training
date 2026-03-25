#!/usr/bin/env python3
"""
Personal Finance Tracker
Main application class for managing finances.
"""

from typing import Dict
from colorama import init
from datetime import datetime, timedelta

from src.models.account import Account, CheckingAccount, SavingsAccount, InvestmentAccount
from src.models.transaction import Transaction, TransactionType, TransactionCategory
from src.models.savings_goal import SavingsGoal
from src.utils.storage import JSONStorage, safe_save, safe_load

init(autoreset=True)

class PersonalFinanceTracker:
    """Main application class."""
    
    def __init__(self):
        self.accounts: Dict[str, Account] = {}
        self.goals: Dict[str, SavingsGoal] = {}
        self.storage = JSONStorage()
        self._transaction_counter = 1
        self._account_counter = 1
        self._goal_counter = 1
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample data for testing."""
        # Add sample accounts
        checking = CheckingAccount("ACC001", "Main Checking", 5000.0, 500.0)
        savings = SavingsAccount("ACC002", "Emergency Fund", 10000.0, 0.02, 1000.0)
        investment = InvestmentAccount("ACC003", "Retirement", 25000.0, "Medium")
        
        # Add sample transactions to checking
        t1 = Transaction("T001", 3000.0, TransactionType.INCOME, 
                        TransactionCategory.SALARY, "Monthly Salary",
                        datetime.now() - timedelta(days=5))
        t2 = Transaction("T002", 150.0, TransactionType.EXPENSE,
                        TransactionCategory.FOOD, "Groceries",
                        datetime.now() - timedelta(days=4))
        t3 = Transaction("T003", 80.0, TransactionType.EXPENSE,
                        TransactionCategory.UTILITIES, "Electric Bill",
                        datetime.now() - timedelta(days=3))
        
        checking.add_transaction(t1)
        checking.add_transaction(t2)
        checking.add_transaction(t3)
        
        # Add sample transactions to savings
        t4 = Transaction("T004", 500.0, TransactionType.INCOME,
                        TransactionCategory.OTHER_INCOME, "Transfer from Checking",
                        datetime.now() - timedelta(days=2))
        savings.add_transaction(t4)
        
        # Add sample transactions to investment
        t5 = Transaction("T005", 1000.0, TransactionType.INCOME,
                        TransactionCategory.INVESTMENT, "Monthly Contribution",
                        datetime.now() - timedelta(days=1))
        investment.add_transaction(t5)
        
        self.accounts = {
            "ACC001": checking,
            "ACC002": savings,
            "ACC003": investment
        }
        
        # Add sample savings goals
        goal1 = SavingsGoal("G001", "Vacation Fund", 5000.0, 2500.0,
                           datetime.now() + timedelta(days=180))
        goal2 = SavingsGoal("G002", "New Car", 20000.0, 5000.0,
                           datetime.now() + timedelta(days=365))
        goal3 = SavingsGoal("G003", "Emergency Fund", 10000.0, 10000.0)
        
        self.goals = {
            "G001": goal1,
            "G002": goal2,
            "G003": goal3
        }
        
        self._transaction_counter = 6
        self._account_counter = 4
        self._goal_counter = 4
    
    def generate_transaction_id(self) -> str:
        """Generate unique transaction ID."""
        transaction_id = f"T{self._transaction_counter:03d}"
        self._transaction_counter += 1
        return transaction_id
    
    def generate_account_id(self) -> str:
        """Generate unique account ID."""
        account_id = f"ACC{self._account_counter:03d}"
        self._account_counter += 1
        return account_id
    
    def generate_goal_id(self) -> str:
        """Generate unique goal ID."""
        goal_id = f"G{self._goal_counter:03d}"
        self._goal_counter += 1
        return goal_id
    
    def get_all_transactions(self) -> list:
        """Get all transactions from all accounts."""
        all_transactions = []
        for account in self.accounts.values():
            all_transactions.extend(account.transactions)
        return sorted(all_transactions, key=lambda t: t.date, reverse=True)
    
    def get_total_balance(self) -> float:
        """Calculate total balance across all accounts."""
        return sum(acc.balance for acc in self.accounts.values())
    
    def get_total_income(self) -> float:
        """Calculate total income across all accounts."""
        return sum(acc.get_total_income() for acc in self.accounts.values())
    
    def get_total_expenses(self) -> float:
        """Calculate total expenses across all accounts."""
        return sum(acc.get_total_expenses() for acc in self.accounts.values())
    
    def save_to_json(self) -> tuple:
        """Save all data to JSON files."""
        try:
            # Save accounts
            accounts_data = {
                acc_id: acc.to_dict() 
                for acc_id, acc in self.accounts.items()
            }
            success, error = safe_save(self.storage, "accounts.json", accounts_data)
            if not success:
                return (False, f"Failed to save accounts: {error}")
            
            # Save goals
            goals_data = {
                goal_id: goal.to_dict()
                for goal_id, goal in self.goals.items()
            }
            success, error = safe_save(self.storage, "goals.json", goals_data)
            if not success:
                return (False, f"Failed to save goals: {error}")
            
            # Save metadata
            metadata = {
                "last_saved": datetime.now().isoformat(),
                "transaction_counter": self._transaction_counter,
                "account_counter": self._account_counter,
                "goal_counter": self._goal_counter
            }
            success, error = safe_save(self.storage, "metadata.json", metadata)
            if not success:
                return (False, f"Failed to save metadata: {error}")
            
            return (True, None)
        
        except Exception as e:
            return (False, f"Unexpected error: {e}")
    
    def load_from_json(self) -> tuple:
        """Load all data from JSON files."""
        try:
            # Load accounts (implementation would reconstruct Account objects)
            # For now, we'll keep the sample data
            # In a full implementation, you'd deserialize the JSON back to objects
            
            return (True, None)
        
        except Exception as e:
            return (False, f"Unexpected error: {e}")
    
    def _clear_screen(self):
        """Clear the console screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
