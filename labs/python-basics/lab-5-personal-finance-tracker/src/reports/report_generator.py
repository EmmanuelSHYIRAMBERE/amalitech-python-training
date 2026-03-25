"""Report generation using ABC and polymorphism."""

from abc import ABC, abstractmethod
from typing import List, Any, Dict
from datetime import datetime
from tabulate import tabulate
from colorama import Fore, Style, init

init(autoreset=True)

class ReportGenerator(ABC):
    """Abstract base class for report generators."""
    
    def __init__(self, title: str):
        self.title = title
        self.generated_at = datetime.now()
    
    @abstractmethod
    def generate(self) -> str:
        """Generate the report content."""
        pass
    
    @abstractmethod
    def get_data(self) -> List[Any]:
        """Get the data for the report."""
        pass
    
    def _format_header(self) -> str:
        """Format report header."""
        header = f"\n{Fore.CYAN}{'='*70}\n"
        header += f"{self.title.center(70)}\n"
        header += f"{'='*70}{Style.RESET_ALL}\n"
        header += f"Generated: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        return header

class AccountReport(ReportGenerator):
    """Account summary report generator."""
    
    def __init__(self, accounts: List):
        super().__init__("ACCOUNT SUMMARY REPORT")
        self._accounts = accounts
    
    def get_data(self) -> List[Any]:
        return self._accounts
    
    def generate(self) -> str:
        """Generate account report."""
        report = self._format_header()
        
        if not self._accounts:
            report += f"{Fore.YELLOW}No accounts found.{Style.RESET_ALL}\n"
            return report
        
        table_data = []
        for account in self._accounts:
            table_data.append([
                account.account_id,
                account.account_name,
                account.get_account_type(),
                f"${account.balance:,.2f}",
                len(account.transactions)
            ])
        
        headers = ["ID", "Name", "Type", "Balance", "Transactions"]
        report += tabulate(table_data, headers=headers, tablefmt="grid")
        
        total_balance = sum(acc.balance for acc in self._accounts)
        report += f"\n\n{Fore.GREEN}Total Balance: ${total_balance:,.2f}{Style.RESET_ALL}\n"
        report += f"Total Accounts: {len(self._accounts)}\n"
        
        return report

class TransactionReport(ReportGenerator):
    """Transaction history report generator."""
    
    def __init__(self, transactions: List, title: str = "TRANSACTION REPORT"):
        super().__init__(title)
        self._transactions = transactions
    
    def get_data(self) -> List[Any]:
        return self._transactions
    
    def generate(self) -> str:
        """Generate transaction report."""
        report = self._format_header()
        
        if not self._transactions:
            report += f"{Fore.YELLOW}No transactions found.{Style.RESET_ALL}\n"
            return report
        
        table_data = []
        for transaction in sorted(self._transactions, key=lambda t: t.date, reverse=True):
            sign = "+" if transaction.transaction_type.value == "income" else "-"
            table_data.append([
                transaction.date.strftime('%Y-%m-%d'),
                transaction.transaction_type.value.capitalize(),
                transaction.category.value,
                f"{sign}${transaction.amount:,.2f}",
                transaction.description[:30]
            ])
        
        headers = ["Date", "Type", "Category", "Amount", "Description"]
        report += tabulate(table_data, headers=headers, tablefmt="grid")
        
        total_income = sum(t.amount for t in self._transactions 
                          if t.transaction_type.value == "income")
        total_expenses = sum(t.amount for t in self._transactions 
                            if t.transaction_type.value == "expense")
        
        report += f"\n\n{Fore.GREEN}Total Income: ${total_income:,.2f}{Style.RESET_ALL}\n"
        report += f"{Fore.RED}Total Expenses: ${total_expenses:,.2f}{Style.RESET_ALL}\n"
        report += f"{Fore.CYAN}Net: ${total_income - total_expenses:,.2f}{Style.RESET_ALL}\n"
        
        return report

class CategoryReport(ReportGenerator):
    """Expense breakdown by category report."""
    
    def __init__(self, transactions: List):
        super().__init__("EXPENSE BREAKDOWN BY CATEGORY")
        self._transactions = transactions
    
    def get_data(self) -> List[Any]:
        return self._transactions
    
    def generate(self) -> str:
        """Generate category breakdown report."""
        report = self._format_header()
        
        if not self._transactions:
            report += f"{Fore.YELLOW}No transactions found.{Style.RESET_ALL}\n"
            return report
        
        # Calculate category totals using comprehension
        category_totals = {}
        for transaction in self._transactions:
            category = transaction.category.value
            if category not in category_totals:
                category_totals[category] = 0.0
            category_totals[category] += transaction.amount
        
        # Sort by amount descending
        sorted_categories = sorted(category_totals.items(), 
                                  key=lambda x: x[1], reverse=True)
        
        total = sum(category_totals.values())
        
        table_data = []
        for category, amount in sorted_categories:
            percentage = (amount / total * 100) if total > 0 else 0
            table_data.append([
                category,
                f"${amount:,.2f}",
                f"{percentage:.1f}%"
            ])
        
        headers = ["Category", "Amount", "Percentage"]
        report += tabulate(table_data, headers=headers, tablefmt="grid")
        
        report += f"\n\n{Fore.GREEN}Total: ${total:,.2f}{Style.RESET_ALL}\n"
        
        return report

class SavingsGoalReport(ReportGenerator):
    """Savings goals progress report."""
    
    def __init__(self, goals: List):
        super().__init__("SAVINGS GOALS REPORT")
        self._goals = goals
    
    def get_data(self) -> List[Any]:
        return self._goals
    
    def generate(self) -> str:
        """Generate savings goals report."""
        report = self._format_header()
        
        if not self._goals:
            report += f"{Fore.YELLOW}No savings goals found.{Style.RESET_ALL}\n"
            return report
        
        table_data = []
        for goal in self._goals:
            status = "✅" if goal.is_achieved else "🔄"
            deadline_str = goal.deadline.strftime('%Y-%m-%d') if goal.deadline else "No deadline"
            
            table_data.append([
                status,
                goal.name,
                f"${goal.current_amount:,.2f}",
                f"${goal.target_amount:,.2f}",
                f"{goal.progress_percentage:.1f}%",
                deadline_str
            ])
        
        headers = ["Status", "Goal", "Current", "Target", "Progress", "Deadline"]
        report += tabulate(table_data, headers=headers, tablefmt="grid")
        
        achieved = sum(1 for g in self._goals if g.is_achieved)
        total_saved = sum(g.current_amount for g in self._goals)
        total_target = sum(g.target_amount for g in self._goals)
        
        report += f"\n\n{Fore.GREEN}Goals Achieved: {achieved}/{len(self._goals)}{Style.RESET_ALL}\n"
        report += f"Total Saved: ${total_saved:,.2f}\n"
        report += f"Total Target: ${total_target:,.2f}\n"
        
        return report

class FinancialSummaryReport(ReportGenerator):
    """Comprehensive financial summary report."""
    
    def __init__(self, accounts: List, goals: List):
        super().__init__("FINANCIAL SUMMARY REPORT")
        self._accounts = accounts
        self._goals = goals
    
    def get_data(self) -> List[Any]:
        return self._accounts
    
    def generate(self) -> str:
        """Generate financial summary report."""
        report = self._format_header()
        
        # Account Summary
        total_balance = sum(acc.balance for acc in self._accounts)
        total_income = sum(acc.get_total_income() for acc in self._accounts)
        total_expenses = sum(acc.get_total_expenses() for acc in self._accounts)
        net_savings = total_income - total_expenses
        
        report += f"\n{Fore.CYAN}💰 ACCOUNT SUMMARY{Style.RESET_ALL}\n"
        report += f"Total Balance: ${total_balance:,.2f}\n"
        report += f"Number of Accounts: {len(self._accounts)}\n"
        
        # Income & Expenses
        report += f"\n{Fore.CYAN}📊 INCOME & EXPENSES{Style.RESET_ALL}\n"
        report += f"Total Income: {Fore.GREEN}${total_income:,.2f}{Style.RESET_ALL}\n"
        report += f"Total Expenses: {Fore.RED}${total_expenses:,.2f}{Style.RESET_ALL}\n"
        report += f"Net Savings: ${net_savings:,.2f}\n"
        
        if total_income > 0:
            savings_rate = (net_savings / total_income) * 100
            report += f"Savings Rate: {savings_rate:.1f}%\n"
        
        # Savings Goals
        if self._goals:
            report += f"\n{Fore.CYAN}🎯 SAVINGS GOALS{Style.RESET_ALL}\n"
            achieved = sum(1 for g in self._goals if g.is_achieved)
            total_saved = sum(g.current_amount for g in self._goals)
            total_target = sum(g.target_amount for g in self._goals)
            
            report += f"Goals Achieved: {achieved}/{len(self._goals)}\n"
            report += f"Total Saved: ${total_saved:,.2f}\n"
            report += f"Total Target: ${total_target:,.2f}\n"
            
            if total_target > 0:
                overall_progress = (total_saved / total_target) * 100
                report += f"Overall Progress: {overall_progress:.1f}%\n"
        
        # Account Type Breakdown
        account_types = {}
        for account in self._accounts:
            acc_type = account.get_account_type()
            if acc_type not in account_types:
                account_types[acc_type] = {"count": 0, "balance": 0.0}
            account_types[acc_type]["count"] += 1
            account_types[acc_type]["balance"] += account.balance
        
        report += f"\n{Fore.CYAN}🏦 ACCOUNT TYPE BREAKDOWN{Style.RESET_ALL}\n"
        for acc_type, data in account_types.items():
            report += f"  • {acc_type}: {data['count']} account(s), ${data['balance']:,.2f}\n"
        
        return report
