# Employee Payroll Tracker

A comprehensive console-based payroll management system for computing pay slips across multiple employee categories (Full-time, Contract, Intern). This system demonstrates OOP principles, inheritance, polymorphism, and property decorators.

## Features

- **Employee Management**: Add and manage full-time, contract, and intern employees
- **Payroll Operations**: Calculate salaries, bonuses, taxes, and net pay
- **Reporting**: Generate detailed payroll reports with tabular formatting
- **Statistics**: View system-wide payroll statistics and analytics
- **Property Decorators**: Safe data validation and encapsulation
- **Polymorphism**: Role-based salary calculations

## Technical Highlights

- Python 3.10+ with type hints
- Object-Oriented Design with inheritance and polymorphism
- Abstract Base Classes for extensibility
- Property decorators for data validation
- Modular functions for salary computation
- Comprehensive error handling
- Colorful console output using colorama
- Tabulated reports using tabulate

## Prerequisites

- Python 3.10 or higher
- Poetry (Python dependency management tool)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/EmmanuelSHYIRAMBERE/Lab-2-Employee-Payroll-Tracker.git
cd Lab-2-Employee-Payroll-Tracker
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

### Main Menu Options

1. **Employee Management**
   - Add Full-Time Employee
   - Add Contract Employee
   - Add Intern
   - View All Employees
   - View Employee Details
   - Remove Employee

2. **Payroll Operations**
   - Update Employee Bonus
   - Update Tax Rate
   - Update Contract Hours
   - Calculate Total Payroll

3. **Generate Reports**
   - Employee List Report
   - Payslip Report
   - Employee Type Report
   - Tax Report
   - Generate All Reports

4. **View Statistics**
   - Total payroll summary
   - Employee type breakdown
   - Highest/lowest paid employees

## Example Output

### Main Menu

```
============================================================
Employee Payroll Tracker System
============================================================

1. Employee Management
2. Payroll Operations
3. Generate Reports
4. View Statistics
0. Exit

Enter your choice:
```

### Payslip Report

```
============================================================
                    PAYSLIP REPORT
Generated: 2024-01-15 10:30:00
============================================================

+--------+----------------+-------------------+-------------+----------+------------+
| ID     | Name           | Type              | Gross Pay   | Tax      | Net Pay    |
+--------+----------------+-------------------+-------------+----------+------------+
| FT001  | John Doe       | Full-Time         | $11,000.00  | $2,200   | $8,800.00  |
| FT002  | Jane Smith     | Full-Time         | $13,950.00  | $2,790   | $11,160.00 |
| CT001  | Bob Johnson    | Contract          | $8,500.00   | $850     | $7,650.00  |
| IN001  | Charlie Brown  | Intern            | $2,200.00   | $110     | $2,090.00  |
+--------+----------------+-------------------+-------------+----------+------------+

Summary:
  Total Gross Pay: $35,650.00
  Total Tax:       $5,950.00
  Total Net Pay:   $29,700.00
  Average Net Pay: $7,425.00
```

### System Statistics

```
SYSTEM STATISTICS
==================================================
Total Employees: 6
Total Payroll: $45,234.50
Average Salary: $7,539.08

Employee Type Breakdown:
  • Full-Time Employee: 2 (33.3%)
  • Contract Employee: 2 (33.3%)
  • Intern: 2 (33.3%)

Highest Paid: Jane Smith - $11,160.00
Lowest Paid: Diana Prince - $1,710.00
```

## Project Structure

```
employee-payroll-tracker/
├── src/
│   ├── models/
│   │   └── employee.py         # Employee classes with inheritance
│   ├── utils/
│   │   ├── salary_calculator.py # Salary computation functions
│   │   ├── helpers.py          # Validation and formatting utilities
│   │   └── report_generator.py # Polymorphic report generation
│   └── data/
│       └── init.py             # Data initialization
├── tests/
│   └── test_employee.py        # Unit tests
├── main.py                     # Application entry point
├── app.py                      # Main application class
├── menu_handlers.py            # Menu and UI logic
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

## Class Hierarchy

```
Employee (ABC)
├── FullTimeEmployee
│   ├── Properties: annual_salary, benefits, bonus
│   └── Tax Rate: 20%
├── ContractEmployee
│   ├── Properties: hourly_rate, hours_worked, bonus
│   └── Tax Rate: 10%
└── InternEmployee
    ├── Properties: monthly_stipend, school, bonus
    └── Tax Rate: 5%
```

## Key Features

### 1. Inheritance & Polymorphism

- Base `Employee` class with abstract methods
- Subclasses override `calculate_gross_pay()` with role-specific logic
- Polymorphic report generation

### 2. Property Decorators

```python
@property
def bonus(self) -> float:
    """Get bonus amount."""
    return self._bonus

@bonus.setter
def bonus(self, value: float):
    """Set bonus with validation."""
    if value < 0:
        raise ValueError("Bonus cannot be negative")
    self._bonus = value
```

### 3. Modular Functions

- `calculate_total_payroll()` - Aggregate payroll calculations
- `get_payroll_summary()` - Generate statistics
- `find_highest_paid()` / `find_lowest_paid()` - Analytics

### 4. Data Validation

- Email format validation
- Salary range validation
- Tax rate bounds checking
- Hours worked validation

## Sample Data

The application comes pre-loaded with sample employees:

**Full-Time Employees:**

- John Doe (FT001) - $60,000/year + $5,000 bonus
- Jane Smith (FT002) - $75,000/year + $7,500 bonus

**Contract Employees:**

- Bob Johnson (CT001) - $50/hour, 160 hours
- Alice Williams (CT002) - $45/hour, 180 hours

**Interns:**

- Charlie Brown (IN001) - $2,000/month (MIT)
- Diana Prince (IN002) - $1,800/month (Stanford)

## Salary Calculation Logic

### Full-Time Employee

```
Monthly Gross = (Annual Salary / 12) + Benefits + Bonus
Tax = Gross * 20%
Net Pay = Gross - Tax
```

### Contract Employee

```
Regular Pay = Hours (up to 160) * Hourly Rate
Overtime Pay = Overtime Hours * Hourly Rate * 1.5
Gross = Regular + Overtime + Bonus
Tax = Gross * 10%
Net Pay = Gross - Tax
```

### Intern

```
Gross = Monthly Stipend + Bonus
Tax = Gross * 5%
Net Pay = Gross - Tax
```

## Development Milestones

- **Day 1**: Environment setup, data structures
- **Day 2**: Functions and salary calculations
- **Day 3**: OOP structure with inheritance and properties
- **Day 4**: Packaging, testing, debugging

## Testing

Run unit tests:

```bash
poetry run python -m pytest tests/
```

## Error Handling

The application includes comprehensive error handling:

- Input validation for all user entries
- Email format validation
- Salary and bonus validation
- Tax rate bounds checking
- Graceful handling of keyboard interrupts

## Tips

- Use `Ctrl+C` to safely exit at any time
- Reports can be saved to files with timestamps
- All inputs are validated to prevent errors
- Sample data is loaded automatically for testing

## Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'colorama'`

- **Solution**: Install dependencies using `poetry install`

**Issue**: Application crashes on startup

- **Solution**: Ensure Python 3.10+ is installed: `python --version`

## Grading Criteria Alignment

- **Language Fundamentals (20pts)**: Data types, control structures, comprehensions
- **Functions & Modularity (15pts)**: Reusable functions in salary_calculator.py
- **OOP Design Quality (25pts)**: Class hierarchy, encapsulation, inheritance
- **Code Clarity & Style (15pts)**: PEP 8 adherence, proper naming
- **Documentation & Comments (10pts)**: Docstrings and inline comments
- **Execution & Output Quality (15pts)**: Complete functionality, stable CLI

## Contributing

Contributions are welcome! Please ensure:

- Code follows PEP 8 style guidelines
- Type hints are included
- Docstrings are comprehensive
- Error handling is robust

## License

This project is available for educational purposes.

## Author

EmmanuelSHYIRAMBERE (emashyirambere1@gmail.com)

#
