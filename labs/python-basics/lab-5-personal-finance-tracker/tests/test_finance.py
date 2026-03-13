import pytest
from datetime import datetime, timedelta
from src.models.transaction import Transaction, TransactionType, TransactionCategory
from src.models.account import CheckingAccount, SavingsAccount, InvestmentAccount
from src.models.savings_goal import SavingsGoal

# Transaction Tests
def test_transaction_creation():
    """Test transaction creation and properties."""
    transaction = Transaction("T001", 100.0, TransactionType.INCOME,
                             TransactionCategory.SALARY, "Test salary")
    assert transaction.transaction_id == "T001"
    assert transaction.amount == 100.0
    assert transaction.transaction_type == TransactionType.INCOME
    assert transaction.get_signed_amount() == 100.0

def test_transaction_expense_sign():
    """Test expense transactions have negative sign."""
    transaction = Transaction("T002", 50.0, TransactionType.EXPENSE,
                             TransactionCategory.FOOD, "Groceries")
    assert transaction.get_signed_amount() == -50.0

def test_transaction_equality():
    """Test transaction equality operator."""
    t1 = Transaction("T001", 100.0, TransactionType.INCOME,
                    TransactionCategory.SALARY, "Salary")
    t2 = Transaction("T001", 200.0, TransactionType.EXPENSE,
                    TransactionCategory.FOOD, "Food")
    t3 = Transaction("T002", 100.0, TransactionType.INCOME,
                    TransactionCategory.SALARY, "Salary")
    assert t1 == t2  # Same ID
    assert t1 != t3  # Different ID

def test_transaction_addition():
    """Test transaction addition operator."""
    t1 = Transaction("T001", 100.0, TransactionType.INCOME,
                    TransactionCategory.SALARY, "Salary")
    t2 = Transaction("T002", 50.0, TransactionType.EXPENSE,
                    TransactionCategory.FOOD, "Food")
    result = t1 + t2
    assert result == 50.0  # 100 - 50

# Account Tests
def test_checking_account_creation():
    """Test checking account creation."""
    account = CheckingAccount("ACC001", "Main Checking", 1000.0, 500.0)
    assert account.account_id == "ACC001"
    assert account.account_name == "Main Checking"
    assert account.balance == 1000.0
    assert account.overdraft_limit == 500.0

def test_checking_account_overdraft():
    """Test checking account overdraft protection."""
    account = CheckingAccount("ACC001", "Main Checking", 1000.0, 500.0)
    assert account.can_withdraw(1400.0) == True  # Within overdraft
    assert account.can_withdraw(1600.0) == False  # Exceeds overdraft

def test_savings_account_interest():
    """Test savings account interest calculation."""
    account = SavingsAccount("ACC002", "Savings", 10000.0, 0.02)
    interest = account.calculate_interest()
    assert interest == 200.0  # 10000 * 0.02

def test_savings_account_minimum_balance():
    """Test savings account minimum balance requirement."""
    account = SavingsAccount("ACC003", "Savings", 5000.0, 0.01, 1000.0)
    assert account.can_withdraw(3000.0) == False  # Would go below minimum
    assert account.can_withdraw(4000.0) == True  # Stays above minimum

def test_investment_account_holdings():
    """Test investment account holdings management."""
    account = InvestmentAccount("ACC004", "Investment", 10000.0, "Medium")
    account.add_holding("AAPL", 10.0)
    account.add_holding("GOOGL", 5.0)
    assert "AAPL" in account.holdings
    assert account.holdings["AAPL"] == 10.0
    assert account.remove_holding("AAPL", 5.0) == True
    assert account.holdings["AAPL"] == 5.0

def test_account_balance_calculation():
    """Test account balance calculation with transactions."""
    account = CheckingAccount("ACC001", "Checking", 1000.0)
    
    t1 = Transaction("T001", 500.0, TransactionType.INCOME,
                    TransactionCategory.SALARY, "Salary")
    t2 = Transaction("T002", 200.0, TransactionType.EXPENSE,
                    TransactionCategory.FOOD, "Groceries")
    
    account.add_transaction(t1)
    account.add_transaction(t2)
    
    assert account.balance == 1300.0  # 1000 + 500 - 200

def test_account_transaction_filtering():
    """Test filtering transactions by type."""
    account = CheckingAccount("ACC001", "Checking", 1000.0)
    
    t1 = Transaction("T001", 500.0, TransactionType.INCOME,
                    TransactionCategory.SALARY, "Salary")
    t2 = Transaction("T002", 200.0, TransactionType.EXPENSE,
                    TransactionCategory.FOOD, "Groceries")
    t3 = Transaction("T003", 100.0, TransactionType.EXPENSE,
                    TransactionCategory.TRANSPORT, "Gas")
    
    account.add_transaction(t1)
    account.add_transaction(t2)
    account.add_transaction(t3)
    
    income_transactions = account.get_transactions_by_type(TransactionType.INCOME)
    expense_transactions = account.get_transactions_by_type(TransactionType.EXPENSE)
    
    assert len(income_transactions) == 1
    assert len(expense_transactions) == 2

def test_account_totals():
    """Test account income and expense totals."""
    account = CheckingAccount("ACC001", "Checking", 1000.0)
    
    t1 = Transaction("T001", 500.0, TransactionType.INCOME,
                    TransactionCategory.SALARY, "Salary")
    t2 = Transaction("T002", 200.0, TransactionType.EXPENSE,
                    TransactionCategory.FOOD, "Groceries")
    t3 = Transaction("T003", 300.0, TransactionType.INCOME,
                    TransactionCategory.FREELANCE, "Freelance")
    
    account.add_transaction(t1)
    account.add_transaction(t2)
    account.add_transaction(t3)
    
    assert account.get_total_income() == 800.0
    assert account.get_total_expenses() == 200.0

def test_account_equality():
    """Test account equality operator."""
    acc1 = CheckingAccount("ACC001", "Checking", 1000.0)
    acc2 = CheckingAccount("ACC001", "Different Name", 2000.0)
    acc3 = CheckingAccount("ACC002", "Checking", 1000.0)
    
    assert acc1 == acc2  # Same ID
    assert acc1 != acc3  # Different ID

def test_account_addition():
    """Test account addition operator."""
    acc1 = CheckingAccount("ACC001", "Checking", 1000.0)
    acc2 = SavingsAccount("ACC002", "Savings", 5000.0)
    
    total = acc1 + acc2
    assert total == 6000.0

# Savings Goal Tests
def test_savings_goal_creation():
    """Test savings goal creation."""
    goal = SavingsGoal("G001", "Vacation", 5000.0, 2000.0)
    assert goal.goal_id == "G001"
    assert goal.name == "Vacation"
    assert goal.target_amount == 5000.0
    assert goal.current_amount == 2000.0

def test_savings_goal_progress():
    """Test savings goal progress calculation."""
    goal = SavingsGoal("G001", "Vacation", 5000.0, 2500.0)
    assert goal.progress_percentage == 50.0
    assert goal.remaining_amount == 2500.0
    assert goal.is_achieved == False

def test_savings_goal_achieved():
    """Test savings goal achievement."""
    goal = SavingsGoal("G001", "Vacation", 5000.0, 5000.0)
    assert goal.is_achieved == True
    assert goal.progress_percentage == 100.0
    assert goal.remaining_amount == 0.0

def test_savings_goal_contribution():
    """Test adding contribution to goal."""
    goal = SavingsGoal("G001", "Vacation", 5000.0, 2000.0)
    goal.add_contribution(1000.0)
    assert goal.current_amount == 3000.0
    assert goal.progress_percentage == 60.0

def test_savings_goal_withdrawal():
    """Test withdrawing from goal."""
    goal = SavingsGoal("G001", "Vacation", 5000.0, 2000.0)
    assert goal.withdraw(500.0) == True
    assert goal.current_amount == 1500.0
    assert goal.withdraw(2000.0) == False  # Insufficient funds

def test_savings_goal_deadline():
    """Test savings goal deadline tracking."""
    future_date = datetime.now() + timedelta(days=30)
    goal = SavingsGoal("G001", "Vacation", 5000.0, 2000.0, future_date)
    assert goal.days_remaining() == 30
    assert goal.is_overdue == False

def test_savings_goal_overdue():
    """Test overdue goal detection."""
    past_date = datetime.now() - timedelta(days=10)
    goal = SavingsGoal("G001", "Vacation", 5000.0, 2000.0, past_date)
    assert goal.is_overdue == True

def test_savings_goal_comparison():
    """Test savings goal comparison operator."""
    goal1 = SavingsGoal("G001", "Vacation", 5000.0, 2500.0)  # 50%
    goal2 = SavingsGoal("G002", "Car", 10000.0, 7500.0)  # 75%
    assert goal1 < goal2
