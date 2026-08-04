# Personal Finance Tracker

A comprehensive console-based application for managing personal finances including accounts, transactions, and savings goals with advanced OOP principles.

## Features

- **Account Management**: Create and manage Checking, Savings, and Investment accounts
- **Transaction Tracking**: Record income and expenses with categorization
- **Savings Goals**: Set and track progress toward financial goals
- **Dynamic Calculations**: Real-time balance updates and aggregations
- **JSON Storage**: Persist data with exception handling
- **Comprehensive Reports**: Generate detailed financial reports
- **Operator Overloading**: Natural mathematical operations on financial objects

## Technical Highlights

- Python 3.10+ with type hints
- Object-Oriented Design with inheritance and polymorphism
- Abstract Base Classes for uniform operations
- Property decorators for encapsulation
- Operator overloading (**eq**, **add**, **lt**, **str**, **repr**)
- List comprehensions for aggregations
- JSON serialization with exception handling
- Comprehensive error handling
- Colorful console output using colorama
- Tabulated reports using tabulate

## Prerequisites

- Python 3.10 or higher
- Poetry (Python dependency management tool)

## Installation

### 1. Clone the Repository and Navigate to Project

```bash
git clone https://github.com/EmmanuelSHYIRAMBERE/Lab-5-Personal-Finance-Tracker.git
cd Lab-5-Personal-Finance-Tracker
```

### 2. Install Dependencies with Poetry

```bash
poetry install
```

## Usage

### Running the Application

```bash
poetry run python main.py
```

## 🧪 Run Tests

```bash
poetry run pytest tests/ -v
```

### Main Menu Options

The application provides an interactive menu system with the following main options:

1. **Account Management**
   - Add Checking Account (with overdraft protection)
   - Add Savings Account (with interest calculation)
   - Add Investment Account (with risk levels)
   - View All Accounts
   - View Account Details
   - Delete Account

2. **Transaction Management**
   - Add Income (Salary, Freelance, Investment, Other)
   - Add Expense (Food, Transport, Utilities, etc.)
   - View All Transactions
   - View Transactions by Account
   - View Transactions by Category

3. **Savings Goals**
   - Add Savings Goal
   - View All Goals
   - Add Contribution to Goal
   - Withdraw from Goal
   - Delete Goal

4. **View Reports**
   - Account Summary Report
   - Transaction Report
   - Category Breakdown Report
   - Savings Goals Report
   - Generate All Reports

5. **Financial Summary**
   - Comprehensive financial overview
   - Savings rate calculation
   - Account type breakdown

6. **Save Data to JSON**
   - Persist all data to JSON files
   - Exception handling for file operations

## Example Output

### Main Menu

```
============================================================
Welcome to Personal Finance Tracker
============================================================

1. Account Management
2. Transaction Management
3. Savings Goals
4. View Reports
5. Financial Summary
6. Save Data to JSON
0. Exit

Enter your choice:
```

### Account Summary

```
🏦 ALL ACCOUNTS
------------------------------------------------------------

Checking Account: Main Checking (Balance: $7,770.00)
  ID: ACC001
  Transactions: 3
  Total Income: $3,000.00
  Total Expenses: $230.00

Savings Account (2.00% APY): Emergency Fund (Balance: $10,500.00)
  ID: ACC002
  Transactions: 1
  Total Income: $500.00
  Total Expenses: $0.00

Investment Account (Risk: Medium): Retirement (Balance: $26,000.00)
  ID: ACC003
  Transactions: 1
  Total Income: $1,000.00
  Total Expenses: $0.00
```

### Financial Summary

```
======================================================================
                    FINANCIAL SUMMARY REPORT
======================================================================
Generated: 2024-03-09 15:30:45

💰 ACCOUNT SUMMARY
Total Balance: $44,270.00
Number of Accounts: 3

📊 INCOME & EXPENSES
Total Income: $4,500.00
Total Expenses: $230.00
Net Savings: $4,270.00
Savings Rate: 94.9%

🎯 SAVINGS GOALS
Goals Achieved: 1/3
Total Saved: $17,500.00
Total Target: $35,000.00
Overall Progress: 50.0%

🏦 ACCOUNT TYPE BREAKDOWN
  • Checking Account: 1 account(s), $7,770.00
  • Savings Account (2.00% APY): 1 account(s), $10,500.00
  • Investment Account (Risk: Medium): 1 account(s), $26,000.00
```

### Savings Goals

```
🎯 ALL SAVINGS GOALS
------------------------------------------------------------

Vacation Fund: $2,500.00 / $5,000.00 (50.0% Complete)
  ID: G001
  Remaining: $2,500.00
  Days Remaining: 180

New Car: $5,000.00 / $20,000.00 (25.0% Complete)
  ID: G002
  Remaining: $15,000.00
  Days Remaining: 365

Emergency Fund: $10,000.00 / $10,000.00 (✅ Achieved)
  ID: G003
  Remaining: $0.00
```

## Project Structure

```
personal-finance-tracker/
├── src/
│   ├── models/
│   │   ├── transaction.py      # Transaction class with operator overloading
│   │   ├── account.py          # Account ABC and subclasses
│   │   └── savings_goal.py     # Savings goal tracking
│   ├── reports/
│   │   └── report_generator.py # Report generation classes
│   └── utils/
│       ├── helpers.py          # Utility functions with comprehensions
│       └── storage.py          # JSON storage with exception handling
├── data/                       # JSON data files
├── tests/
│   └── test_finance.py         # Unit tests
├── main.py                     # Application entry point
├── app.py                      # Main application class
├── menu_handlers.py            # Menu and UI logic
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

## Sample Data

The application comes pre-loaded with sample data:

**Accounts:**

- Main Checking (ACC001) - $5,000 initial balance, $500 overdraft
- Emergency Fund (ACC002) - $10,000 initial balance, 2% interest
- Retirement (ACC003) - $25,000 initial balance, Medium risk

**Transactions:**

- Monthly Salary: +$3,000
- Groceries: -$150
- Electric Bill: -$80
- Transfer to Savings: +$500
- Investment Contribution: +$1,000

**Savings Goals:**

- Vacation Fund: $2,500 / $5,000 (50%)
- New Car: $5,000 / $20,000 (25%)
- Emergency Fund: $10,000 / $10,000 (100% ✅)

## Features in Detail

### Account Types

1. **Checking Account**
   - Overdraft protection
   - Available balance calculation
   - No minimum balance requirement

2. **Savings Account**
   - Interest rate (APY)
   - Minimum balance requirement
   - Interest calculation and application

3. **Investment Account**
   - Risk level (Low, Medium, High)
   - Holdings tracking (stocks, bonds, etc.)
   - Portfolio management

### Transaction Features

- **Types**: Income, Expense, Transfer
- **Categories**:
  - Income: Salary, Freelance, Investment, Other
  - Expense: Food, Transport, Utilities, Entertainment, Healthcare, Shopping, Education, Other
- **Automatic balance updates**
- **Signed amounts** (positive for income, negative for expenses)
- **Date tracking**

### Operator Overloading

```python
# Transaction addition
t1 + t2  # Returns combined signed amount

# Account addition
acc1 + acc2  # Returns total balance

# Equality comparison
t1 == t2  # Compares by ID
acc1 == acc2  # Compares by ID

# Less than comparison
t1 < t2  # Compares by date
goal1 < goal2  # Compares by progress percentage
```

### Property Decorators

```python
@property
def balance(self) -> float:
    """Calculate current balance using comprehension."""
    transaction_sum = sum(t.get_signed_amount() for t in self._transactions)
    return self._initial_balance + transaction_sum

@property
def progress_percentage(self) -> float:
    """Calculate progress percentage."""
    return (self._current_amount / self._target_amount) * 100
```

### List Comprehensions

```python
# Filter transactions by type
income_transactions = [t for t in transactions
                      if t.transaction_type == TransactionType.INCOME]

# Calculate total using comprehension
total_income = sum(t.amount for t in transactions
                  if t.transaction_type == TransactionType.INCOME)

# Group by category
summary = {cat: sum(t.amount for t in transactions if t.category == cat)
          for cat in categories}
```

### Exception Handling

```python
try:
    storage.save_data("accounts.json", data)
except StorageException as e:
    print(f"Storage error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Lab 5 Requirements

### ✅ Numeric Data Types and Operators

- Extensive use of float for monetary values
- Arithmetic operators (+, -, \*, /)
- Comparison operators (<, >, ==)
- Operator overloading (**add**, **eq**, **lt**)

### ✅ Control Structures

- Transaction validation (if/else)
- Balance checking before withdrawals
- Menu navigation (while loops)
- Input validation loops

### ✅ Functions and Modules

- Modular organization (models, utils, reports)
- Helper functions with comprehensions
- \*args/\*\*kwargs usage
- Functional decomposition

### ✅ OOP Implementation

- Account ABC with subclasses
- Transaction class with operator overloading
- SavingsGoal class
- Inheritance and polymorphism

### ✅ Encapsulation

- Private attributes (\_attribute)
- @property decorators
- Controlled access through methods

### ✅ JSON Storage

- Save/load functionality
- Exception handling
- Data serialization/deserialization

### ✅ Special Methods

- **str** for user-friendly output
- **repr** for developer output
- **eq** for equality comparison
- **add** for addition operations
- **lt** for less-than comparison

## Testing

### Run Unit Tests

```bash
poetry run pytest tests/ -v
```

### Test Coverage

- Transaction creation and operations
- Account balance calculations
- Savings goal progress tracking
- Operator overloading
- Property decorators
- Exception handling

## Error Handling

The application includes comprehensive error handling:

- Input validation for all user entries
- Amount validation (positive numbers)
- Account existence checking
- Insufficient funds detection
- JSON file operation errors
- Graceful handling of keyboard interrupts

## Tips

- Use `Ctrl+C` to safely exit the application at any time
- Data is automatically saved on exit
- Sample data is loaded automatically for testing
- All monetary values are displayed with 2 decimal places
- Reports can be generated at any time

## Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'colorama'`

- **Solution**: Install dependencies using `poetry install`

**Issue**: Colors not displaying correctly on Windows

- **Solution**: The application uses colorama which automatically handles Windows console colors

**Issue**: Application crashes on startup

- **Solution**: Ensure Python 3.10+ is installed: `python --version`

**Issue**: JSON save fails

- **Solution**: Ensure the `data/` directory exists and has write permissions

## Contributing

Contributions are welcome! Please ensure:

- Code follows PEP 8 style guidelines
- Type hints are included
- Error handling is comprehensive
- Documentation is updated

## License

This project is available for educational purposes.

## Author

EmmanuelSHYIRAMBERE (emashyirambere1@gmail.com)
