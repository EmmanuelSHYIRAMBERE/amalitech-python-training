#!/usr/bin/env python3
"""
Personal Finance Tracker
Menu handlers and user interface logic.
"""

import os
from datetime import datetime, timedelta
from colorama import Fore, Style

from src.models.account import CheckingAccount, SavingsAccount, InvestmentAccount
from src.models.transaction import Transaction, TransactionType, TransactionCategory
from src.models.savings_goal import SavingsGoal
from src.utils.helpers import (create_menu, get_user_input, validate_amount,
                               format_currency, generate_financial_summary)
from src.reports.report_generator import (AccountReport, TransactionReport,
                                          CategoryReport, SavingsGoalReport,
                                          FinancialSummaryReport)

class MenuHandlers:
    """Handles all menu operations and user interactions."""
    
    def __init__(self, system):
        self.system = system
    
    def run_main_menu(self):
        """Main application loop."""
        while True:
            self.system._clear_screen()
            
            print(Fore.YELLOW + "="*60)
            print("Welcome to Personal Finance Tracker")
            print("="*60 + Style.RESET_ALL)
            
            options = [
                "Account Management",
                "Transaction Management",
                "Savings Goals",
                "View Reports",
                "Financial Summary",
                "Save Data to JSON"
            ]
            
            create_menu(options)
            
            choice = get_user_input("Enter your choice: ",
                                   lambda x: x.isdigit() and 0 <= int(x) <= len(options))
            choice = int(choice)
            
            if choice == 0:
                # Save before exit
                print("\nSaving data...")
                success, error = self.system.save_to_json()
                if success:
                    print(Fore.GREEN + "✅ Data saved successfully!")
                else:
                    print(Fore.RED + f"❌ Save failed: {error}")
                print(Fore.GREEN + "\nThank you for using Personal Finance Tracker. Goodbye!")
                break
            elif choice == 1:
                self._account_management_menu()
            elif choice == 2:
                self._transaction_management_menu()
            elif choice == 3:
                self._savings_goals_menu()
            elif choice == 4:
                self._reports_menu()
            elif choice == 5:
                self._financial_summary()
                input("\nPress Enter to continue...")
            elif choice == 6:
                self._save_data()
                input("\nPress Enter to continue...")
    
    def _account_management_menu(self):
        """Account management submenu."""
        while True:
            self.system._clear_screen()
            print(Fore.CYAN + "\n🏦 ACCOUNT MANAGEMENT")
            print("="*40)
            
            options = [
                "Add Checking Account",
                "Add Savings Account",
                "Add Investment Account",
                "View All Accounts",
                "View Account Details",
                "Delete Account",
                "Back to Main Menu"
            ]
            
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")
            print("0. Back")
            
            choice = get_user_input("Enter your choice: ",
                                   lambda x: x.isdigit() and 0 <= int(x) <= len(options))
            choice = int(choice)
            
            if choice == 0:
                break
            elif choice == 1:
                self._add_checking_account()
            elif choice == 2:
                self._add_savings_account()
            elif choice == 3:
                self._add_investment_account()
            elif choice == 4:
                self._view_all_accounts()
            elif choice == 5:
                self._view_account_details()
            elif choice == 6:
                self._delete_account()
            
            input("\nPress Enter to continue...")
    
    def _add_checking_account(self):
        """Add a new checking account."""
        print(Fore.CYAN + "\n➕ ADD CHECKING ACCOUNT")
        print("-"*30)
        
        name = get_user_input("Account Name: ",
                            lambda x: len(x.strip()) >= 2,
                            "Name must be at least 2 characters!")
        
        initial_balance = float(get_user_input("Initial Balance: $",
                                              validate_amount,
                                              "Amount must be positive!") or "0")
        
        overdraft = float(get_user_input("Overdraft Limit: $",
                                        lambda x: validate_amount(x) or x == "0",
                                        "Amount must be non-negative!") or "0")
        
        account_id = self.system.generate_account_id()
        account = CheckingAccount(account_id, name, initial_balance, overdraft)
        self.system.accounts[account_id] = account
        
        print(Fore.GREEN + f"✅ Checking account '{name}' created successfully!")
        print(f"Account ID: {account_id}")
    
    def _add_savings_account(self):
        """Add a new savings account."""
        print(Fore.CYAN + "\n➕ ADD SAVINGS ACCOUNT")
        print("-"*30)
        
        name = get_user_input("Account Name: ",
                            lambda x: len(x.strip()) >= 2,
                            "Name must be at least 2 characters!")
        
        initial_balance = float(get_user_input("Initial Balance: $",
                                              validate_amount,
                                              "Amount must be positive!") or "0")
        
        interest_rate = float(get_user_input("Interest Rate (e.g., 0.02 for 2%): ",
                                            lambda x: x.replace('.', '').isdigit(),
                                            "Invalid rate!") or "0.01")
        
        min_balance = float(get_user_input("Minimum Balance: $",
                                          lambda x: validate_amount(x) or x == "0",
                                          "Amount must be non-negative!") or "0")
        
        account_id = self.system.generate_account_id()
        account = SavingsAccount(account_id, name, initial_balance, interest_rate, min_balance)
        self.system.accounts[account_id] = account
        
        print(Fore.GREEN + f"✅ Savings account '{name}' created successfully!")
        print(f"Account ID: {account_id}")
        print(f"Interest Rate: {interest_rate*100:.2f}%")
    
    def _add_investment_account(self):
        """Add a new investment account."""
        print(Fore.CYAN + "\n➕ ADD INVESTMENT ACCOUNT")
        print("-"*30)
        
        name = get_user_input("Account Name: ",
                            lambda x: len(x.strip()) >= 2,
                            "Name must be at least 2 characters!")
        
        initial_balance = float(get_user_input("Initial Balance: $",
                                              validate_amount,
                                              "Amount must be positive!") or "0")
        
        print("\nRisk Levels: Low, Medium, High")
        risk = get_user_input("Risk Level: ",
                            lambda x: x.capitalize() in ["Low", "Medium", "High"],
                            "Must be Low, Medium, or High!")
        
        account_id = self.system.generate_account_id()
        account = InvestmentAccount(account_id, name, initial_balance, risk.capitalize())
        self.system.accounts[account_id] = account
        
        print(Fore.GREEN + f"✅ Investment account '{name}' created successfully!")
        print(f"Account ID: {account_id}")
    
    def _view_all_accounts(self):
        """View all accounts."""
        if not self.system.accounts:
            print(Fore.YELLOW + "No accounts in the system.")
            return
        
        print(Fore.CYAN + "\n🏦 ALL ACCOUNTS")
        print("-"*60)
        
        for account_id, account in sorted(self.system.accounts.items()):
            print(f"\n{account}")
            print(f"  ID: {account.account_id}")
            print(f"  Transactions: {len(account.transactions)}")
            print(f"  Total Income: {format_currency(account.get_total_income())}")
            print(f"  Total Expenses: {format_currency(account.get_total_expenses())}")
    
    def _view_account_details(self):
        """View detailed account information."""
        if not self.system.accounts:
            print(Fore.YELLOW + "No accounts in the system.")
            return
        
        print(Fore.CYAN + "\n🔍 ACCOUNT DETAILS")
        print("-"*30)
        
        for account_id, account in self.system.accounts.items():
            print(f"{account_id}: {account.account_name}")
        
        account_id = get_user_input("\nEnter Account ID: ",
                                   lambda x: x in self.system.accounts,
                                   "Account not found!")
        
        account = self.system.accounts[account_id]
        
        print(Fore.CYAN + "\n" + "="*50)
        print(f"ACCOUNT DETAILS: {account.account_name}")
        print("="*50)
        print(f"ID: {account.account_id}")
        print(f"Type: {account.get_account_type()}")
        print(f"Balance: {format_currency(account.balance)}")
        print(f"Created: {account.created_at.strftime('%Y-%m-%d')}")
        
        # Type-specific details
        if isinstance(account, CheckingAccount):
            print(f"Overdraft Limit: {format_currency(account.overdraft_limit)}")
            print(f"Available Balance: {format_currency(account.get_available_balance())}")
        elif isinstance(account, SavingsAccount):
            print(f"Interest Rate: {account.interest_rate*100:.2f}%")
            print(f"Minimum Balance: {format_currency(account.minimum_balance)}")
            print(f"Projected Interest: {format_currency(account.calculate_interest())}")
        elif isinstance(account, InvestmentAccount):
            print(f"Risk Level: {account.risk_level}")
        
        print(f"\nTotal Income: {format_currency(account.get_total_income())}")
        print(f"Total Expenses: {format_currency(account.get_total_expenses())}")
        print(f"Number of Transactions: {len(account.transactions)}")
    
    def _delete_account(self):
        """Delete an account."""
        if not self.system.accounts:
            print(Fore.YELLOW + "No accounts in the system.")
            return
        
        print(Fore.CYAN + "\n🗑️ DELETE ACCOUNT")
        print("-"*30)
        
        account_id = get_user_input("Enter Account ID: ",
                                   lambda x: x in self.system.accounts,
                                   "Account not found!")
        
        account = self.system.accounts[account_id]
        
        confirm = get_user_input(f"Delete '{account.account_name}'? (yes/no): ",
                               lambda x: x.lower() in ['yes', 'no'])
        
        if confirm.lower() == 'yes':
            del self.system.accounts[account_id]
            print(Fore.GREEN + "✅ Account deleted successfully!")
    
    def _transaction_management_menu(self):
        """Transaction management submenu."""
        while True:
            self.system._clear_screen()
            print(Fore.CYAN + "\n💳 TRANSACTION MANAGEMENT")
            print("="*40)
            
            options = [
                "Add Income",
                "Add Expense",
                "View All Transactions",
                "View Transactions by Account",
                "View Transactions by Category",
                "Back to Main Menu"
            ]
            
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")
            print("0. Back")
            
            choice = get_user_input("Enter your choice: ",
                                   lambda x: x.isdigit() and 0 <= int(x) <= len(options))
            choice = int(choice)
            
            if choice == 0:
                break
            elif choice == 1:
                self._add_income()
            elif choice == 2:
                self._add_expense()
            elif choice == 3:
                self._view_all_transactions()
            elif choice == 4:
                self._view_transactions_by_account()
            elif choice == 5:
                self._view_transactions_by_category()
            
            input("\nPress Enter to continue...")
    
    def _add_income(self):
        """Add income transaction."""
        print(Fore.CYAN + "\n➕ ADD INCOME")
        print("-"*30)
        
        if not self.system.accounts:
            print(Fore.YELLOW + "No accounts available. Create an account first.")
            return
        
        # Select account
        print("\nAvailable Accounts:")
        for account_id, account in self.system.accounts.items():
            print(f"  {account_id}: {account.account_name}")
        
        account_id = get_user_input("\nSelect Account ID: ",
                                   lambda x: x in self.system.accounts,
                                   "Account not found!")
        
        # Select category
        print("\nIncome Categories:")
        income_categories = [cat for cat in TransactionCategory 
                           if cat.value in ["Salary", "Freelance", "Investment", "Other Income"]]
        for i, cat in enumerate(income_categories, 1):
            print(f"  {i}. {cat.value}")
        
        cat_choice = int(get_user_input("Select Category: ",
                                       lambda x: x.isdigit() and 1 <= int(x) <= len(income_categories)))
        category = income_categories[cat_choice - 1]
        
        amount = float(get_user_input("Amount: $", validate_amount))
        description = get_user_input("Description: ")
        
        transaction_id = self.system.generate_transaction_id()
        transaction = Transaction(transaction_id, amount, TransactionType.INCOME,
                                 category, description)
        
        account = self.system.accounts[account_id]
        if account.add_transaction(transaction):
            print(Fore.GREEN + f"✅ Income of {format_currency(amount)} added successfully!")
            print(f"New balance: {format_currency(account.balance)}")
        else:
            print(Fore.RED + "❌ Failed to add transaction!")
    
    def _add_expense(self):
        """Add expense transaction."""
        print(Fore.CYAN + "\n➕ ADD EXPENSE")
        print("-"*30)
        
        if not self.system.accounts:
            print(Fore.YELLOW + "No accounts available. Create an account first.")
            return
        
        # Select account
        print("\nAvailable Accounts:")
        for account_id, account in self.system.accounts.items():
            print(f"  {account_id}: {account.account_name} - {format_currency(account.balance)}")
        
        account_id = get_user_input("\nSelect Account ID: ",
                                   lambda x: x in self.system.accounts,
                                   "Account not found!")
        
        # Select category
        print("\nExpense Categories:")
        expense_categories = [cat for cat in TransactionCategory 
                            if cat.value not in ["Salary", "Freelance", "Investment", "Other Income"]]
        for i, cat in enumerate(expense_categories, 1):
            print(f"  {i}. {cat.value}")
        
        cat_choice = int(get_user_input("Select Category: ",
                                       lambda x: x.isdigit() and 1 <= int(x) <= len(expense_categories)))
        category = expense_categories[cat_choice - 1]
        
        amount = float(get_user_input("Amount: $", validate_amount))
        description = get_user_input("Description: ")
        
        account = self.system.accounts[account_id]
        
        # Check if withdrawal is allowed
        if not account.can_withdraw(amount):
            print(Fore.RED + "❌ Insufficient funds for this transaction!")
            return
        
        transaction_id = self.system.generate_transaction_id()
        transaction = Transaction(transaction_id, amount, TransactionType.EXPENSE,
                                 category, description)
        
        if account.add_transaction(transaction):
            print(Fore.GREEN + f"✅ Expense of {format_currency(amount)} recorded successfully!")
            print(f"New balance: {format_currency(account.balance)}")
        else:
            print(Fore.RED + "❌ Failed to add transaction!")
    
    def _view_all_transactions(self):
        """View all transactions."""
        transactions = self.system.get_all_transactions()
        
        if not transactions:
            print(Fore.YELLOW + "No transactions found.")
            return
        
        print(Fore.CYAN + "\n💳 ALL TRANSACTIONS")
        print("-"*60)
        
        for transaction in transactions[:20]:  # Show last 20
            print(f"\n{transaction}")
            print(f"  ID: {transaction.transaction_id}")
        
        if len(transactions) > 20:
            print(f"\n... and {len(transactions) - 20} more transactions")
    
    def _view_transactions_by_account(self):
        """View transactions for a specific account."""
        if not self.system.accounts:
            print(Fore.YELLOW + "No accounts in the system.")
            return
        
        print(Fore.CYAN + "\n🔍 TRANSACTIONS BY ACCOUNT")
        print("-"*30)
        
        for account_id, account in self.system.accounts.items():
            print(f"{account_id}: {account.account_name}")
        
        account_id = get_user_input("\nEnter Account ID: ",
                                   lambda x: x in self.system.accounts,
                                   "Account not found!")
        
        account = self.system.accounts[account_id]
        transactions = account.transactions
        
        if not transactions:
            print(Fore.YELLOW + f"No transactions in {account.account_name}.")
            return
        
        print(Fore.CYAN + f"\n💳 TRANSACTIONS: {account.account_name}")
        print("-"*60)
        
        for transaction in transactions:
            print(f"\n{transaction}")
    
    def _view_transactions_by_category(self):
        """View transactions grouped by category."""
        transactions = self.system.get_all_transactions()
        
        if not transactions:
            print(Fore.YELLOW + "No transactions found.")
            return
        
        # Group by category
        by_category = {}
        for t in transactions:
            cat = t.category.value
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(t)
        
        print(Fore.CYAN + "\n📊 TRANSACTIONS BY CATEGORY")
        print("-"*60)
        
        for category, trans_list in sorted(by_category.items()):
            total = sum(t.amount for t in trans_list)
            print(f"\n{category}: {len(trans_list)} transactions, {format_currency(total)}")
            for t in trans_list[:5]:  # Show first 5
                print(f"  • {t.date.strftime('%Y-%m-%d')}: {format_currency(t.amount)} - {t.description}")
    
    def _savings_goals_menu(self):
        """Savings goals submenu."""
        while True:
            self.system._clear_screen()
            print(Fore.CYAN + "\n🎯 SAVINGS GOALS")
            print("="*40)
            
            options = [
                "Add Savings Goal",
                "View All Goals",
                "Add Contribution to Goal",
                "Withdraw from Goal",
                "Delete Goal",
                "Back to Main Menu"
            ]
            
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")
            print("0. Back")
            
            choice = get_user_input("Enter your choice: ",
                                   lambda x: x.isdigit() and 0 <= int(x) <= len(options))
            choice = int(choice)
            
            if choice == 0:
                break
            elif choice == 1:
                self._add_savings_goal()
            elif choice == 2:
                self._view_all_goals()
            elif choice == 3:
                self._add_goal_contribution()
            elif choice == 4:
                self._withdraw_from_goal()
            elif choice == 5:
                self._delete_goal()
            
            input("\nPress Enter to continue...")
    
    def _add_savings_goal(self):
        """Add a new savings goal."""
        print(Fore.CYAN + "\n➕ ADD SAVINGS GOAL")
        print("-"*30)
        
        name = get_user_input("Goal Name: ",
                            lambda x: len(x.strip()) >= 2,
                            "Name must be at least 2 characters!")
        
        target = float(get_user_input("Target Amount: $", validate_amount))
        
        current = float(get_user_input("Current Amount: $",
                                      lambda x: validate_amount(x) or x == "0") or "0")
        
        has_deadline = get_user_input("Set deadline? (y/n): ",
                                     lambda x: x.lower() in ['y', 'n'])
        
        deadline = None
        if has_deadline.lower() == 'y':
            days = int(get_user_input("Days until deadline: ",
                                     lambda x: x.isdigit() and int(x) > 0))
            deadline = datetime.now() + timedelta(days=days)
        
        goal_id = self.system.generate_goal_id()
        goal = SavingsGoal(goal_id, name, target, current, deadline)
        self.system.goals[goal_id] = goal
        
        print(Fore.GREEN + f"✅ Savings goal '{name}' created successfully!")
        print(f"Goal ID: {goal_id}")
        print(f"Progress: {goal.progress_percentage:.1f}%")
    
    def _view_all_goals(self):
        """View all savings goals."""
        if not self.system.goals:
            print(Fore.YELLOW + "No savings goals found.")
            return
        
        print(Fore.CYAN + "\n🎯 ALL SAVINGS GOALS")
        print("-"*60)
        
        for goal_id, goal in sorted(self.system.goals.items()):
            print(f"\n{goal}")
            print(f"  ID: {goal.goal_id}")
            print(f"  Remaining: {format_currency(goal.remaining_amount)}")
            if goal.deadline:
                days = goal.days_remaining()
                print(f"  Days Remaining: {days}")
                if goal.is_overdue:
                    print(Fore.RED + "  ⚠️ OVERDUE!")
    
    def _add_goal_contribution(self):
        """Add contribution to a goal."""
        if not self.system.goals:
            print(Fore.YELLOW + "No savings goals found.")
            return
        
        print(Fore.CYAN + "\n➕ ADD CONTRIBUTION")
        print("-"*30)
        
        for goal_id, goal in self.system.goals.items():
            print(f"{goal_id}: {goal.name} - {goal.progress_percentage:.1f}%")
        
        goal_id = get_user_input("\nSelect Goal ID: ",
                                lambda x: x in self.system.goals,
                                "Goal not found!")
        
        amount = float(get_user_input("Contribution Amount: $", validate_amount))
        
        goal = self.system.goals[goal_id]
        goal.add_contribution(amount)
        
        print(Fore.GREEN + f"✅ Contribution of {format_currency(amount)} added!")
        print(f"New progress: {goal.progress_percentage:.1f}%")
        
        if goal.is_achieved:
            print(Fore.GREEN + "🎉 Goal achieved!")
    
    def _withdraw_from_goal(self):
        """Withdraw from a goal."""
        if not self.system.goals:
            print(Fore.YELLOW + "No savings goals found.")
            return
        
        print(Fore.CYAN + "\n💸 WITHDRAW FROM GOAL")
        print("-"*30)
        
        for goal_id, goal in self.system.goals.items():
            print(f"{goal_id}: {goal.name} - {format_currency(goal.current_amount)}")
        
        goal_id = get_user_input("\nSelect Goal ID: ",
                                lambda x: x in self.system.goals,
                                "Goal not found!")
        
        amount = float(get_user_input("Withdrawal Amount: $", validate_amount))
        
        goal = self.system.goals[goal_id]
        if goal.withdraw(amount):
            print(Fore.GREEN + f"✅ Withdrawal of {format_currency(amount)} successful!")
            print(f"New progress: {goal.progress_percentage:.1f}%")
        else:
            print(Fore.RED + "❌ Insufficient funds in goal!")
    
    def _delete_goal(self):
        """Delete a savings goal."""
        if not self.system.goals:
            print(Fore.YELLOW + "No savings goals found.")
            return
        
        print(Fore.CYAN + "\n🗑️ DELETE GOAL")
        print("-"*30)
        
        goal_id = get_user_input("Enter Goal ID: ",
                                lambda x: x in self.system.goals,
                                "Goal not found!")
        
        goal = self.system.goals[goal_id]
        
        confirm = get_user_input(f"Delete '{goal.name}'? (yes/no): ",
                               lambda x: x.lower() in ['yes', 'no'])
        
        if confirm.lower() == 'yes':
            del self.system.goals[goal_id]
            print(Fore.GREEN + "✅ Goal deleted successfully!")
    
    def _reports_menu(self):
        """Reports generation submenu."""
        while True:
            self.system._clear_screen()
            print(Fore.CYAN + "\n📊 REPORTS")
            print("="*40)
            
            options = [
                "Account Summary Report",
                "Transaction Report",
                "Category Breakdown Report",
                "Savings Goals Report",
                "Generate All Reports",
                "Back to Main Menu"
            ]
            
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")
            print("0. Back")
            
            choice = get_user_input("Enter your choice: ",
                                   lambda x: x.isdigit() and 0 <= int(x) <= len(options))
            choice = int(choice)
            
            if choice == 0:
                break
            elif choice == 1:
                self._generate_account_report()
            elif choice == 2:
                self._generate_transaction_report()
            elif choice == 3:
                self._generate_category_report()
            elif choice == 4:
                self._generate_goals_report()
            elif choice == 5:
                self._generate_all_reports()
            
            input("\nPress Enter to continue...")
    
    def _generate_account_report(self):
        """Generate account summary report."""
        report = AccountReport(list(self.system.accounts.values()))
        print(report.generate())
    
    def _generate_transaction_report(self):
        """Generate transaction report."""
        transactions = self.system.get_all_transactions()
        report = TransactionReport(transactions)
        print(report.generate())
    
    def _generate_category_report(self):
        """Generate category breakdown report."""
        transactions = self.system.get_all_transactions()
        report = CategoryReport(transactions)
        print(report.generate())
    
    def _generate_goals_report(self):
        """Generate savings goals report."""
        report = SavingsGoalReport(list(self.system.goals.values()))
        print(report.generate())
    
    def _generate_all_reports(self):
        """Generate all reports."""
        self._generate_account_report()
        print("\n" + "="*70)
        self._generate_transaction_report()
        print("\n" + "="*70)
        self._generate_category_report()
        print("\n" + "="*70)
        self._generate_goals_report()
    
    def _financial_summary(self):
        """Display financial summary."""
        summary_report = FinancialSummaryReport(
            list(self.system.accounts.values()),
            list(self.system.goals.values())
        )
        print(summary_report.generate())
        
        # Additional summary using *args/**kwargs
        summary = generate_financial_summary(
            *self.system.accounts.values(),
            include_details=True,
            period="All Time"
        )
        
        print(Fore.CYAN + "\n📈 ADDITIONAL METRICS")
        print("="*50)
        print(f"Savings Rate: {summary['savings_rate']:.1f}%")
        print(f"Net Savings: {format_currency(summary['net_savings'])}")
    
    def _save_data(self):
        """Save data to JSON."""
        print(Fore.CYAN + "\n💾 SAVING DATA")
        print("-"*30)
        
        success, error = self.system.save_to_json()
        
        if success:
            print(Fore.GREEN + "✅ Data saved successfully to JSON files!")
            print("Files saved:")
            print("  • data/accounts.json")
            print("  • data/goals.json")
            print("  • data/metadata.json")
        else:
            print(Fore.RED + f"❌ Save failed: {error}")
