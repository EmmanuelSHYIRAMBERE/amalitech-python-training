# Python Basics Labs

A comprehensive collection of Python programming labs demonstrating Object-Oriented Programming (OOP), data structures, file I/O, and software design principles.

## Labs Overview

### Lab 1: Student Course Management System
**Status:** Complete  
**Topics:** OOP Fundamentals, Classes, Inheritance, File I/O

A console-based application for managing students, courses, and enrollments in an educational institution.

**Key Features:**
- Student management (Undergraduate, Graduate, International)
- Course management with enrollment tracking
- GPA calculation and reporting
- Tabulated reports with export functionality

**Technologies:** Python 3.10+, colorama, tabulate

**Repository:** [Lab-1-Student-Course-Management-System](https://github.com/EmmanuelSHYIRAMBERE/Lab-1-Student-Course-Management-System)

---

### Lab 2: Employee Payroll Tracker
**Status:** Complete  
**Topics:** Inheritance, Polymorphism, Property Decorators, Modular Functions

A comprehensive payroll management system for computing pay slips across multiple employee categories.

**Key Features:**
- Employee management (Full-time, Contract, Intern)
- Payroll calculations with bonuses and taxes
- Role-based salary computations
- Property decorators for data validation
- Comprehensive payroll reports

**Technologies:** Python 3.10+, colorama, tabulate

**Repository:** [Lab-2-Employee-Payroll-Tracker](https://github.com/EmmanuelSHYIRAMBERE/Lab-2-Employee-Payroll-Tracker)

---

### Lab 3: Library Inventory Application
**Status:** Complete  
**Topics:** Abstract Base Classes, File I/O, List Comprehensions, JSON Persistence

A library management system for tracking books, eBooks, audiobooks, and borrowers.

**Key Features:**
- Resource management (Books, EBooks, AudioBooks)
- Borrower management with lending operations
- Advanced search using list comprehensions
- JSON file persistence
- Overdue tracking and reports

**Technologies:** Python 3.10+, colorama, tabulate

**Repository:** [Lab-3-Library-Inventory-Application](https://github.com/EmmanuelSHYIRAMBERE/Lab-3-Library-Inventory-Application)

---

### Lab 4: Vehicle Rental System
**Status:** Complete  
**Topics:** Inheritance, Polymorphism, Abstract Base Classes, Property Decorators

A vehicle rental management system supporting cars, trucks, and bikes with dynamic pricing.

**Key Features:**
- Multiple vehicle types with unique attributes
- Dynamic pricing based on type and duration
- Rental management with overdue tracking
- Discount system and late fee calculation
- Revenue analytics and reporting

**Technologies:** Python 3.10+, colorama, tabulate

**Repository:** [Lab-4-Vehicle-Rental-System](https://github.com/EmmanuelSHYIRAMBERE/Lab-4-Vehicle-Rental-System)

---

### Lab 5: Personal Finance Tracker
**Status:** Complete  
**Topics:** Operator Overloading, Property Decorators, JSON Storage, Exception Handling

A personal finance management application for tracking accounts, transactions, and savings goals.

**Key Features:**
- Multiple account types (Checking, Savings, Investment)
- Transaction tracking with categorization
- Savings goal management with progress tracking
- Operator overloading (__eq__, __add__, __lt__)
- JSON persistence with exception handling
- Comprehensive financial reports

**Technologies:** Python 3.10+, colorama, tabulate

**Repository:** [Lab-5-Personal-Finance-Tracker](https://github.com/EmmanuelSHYIRAMBERE/Lab-5-Personal-Finance-Tracker)

---

## Learning Objectives

### Core Python Concepts
- Object-Oriented Programming (OOP)
- Inheritance and Polymorphism
- Abstract Base Classes (ABC)
- Property Decorators
- Operator Overloading
- Exception Handling
- File I/O and JSON Storage
- List Comprehensions

### Software Design Principles
- Encapsulation
- Abstraction
- Modular Architecture
- Separation of Concerns
- DRY (Don't Repeat Yourself)
- Type Hints and Documentation

### Data Structures & Algorithms
- Lists, Dictionaries, Sets
- List Comprehensions
- Generator Expressions
- Sorting and Filtering
- Aggregations and Statistics

## Quick Start

### Prerequisites
- Python 3.10 or higher
- Poetry (Python dependency management)

### Installation

```bash
# Install Poetry (if not already installed)
pip install poetry

# Clone any lab repository
git clone https://github.com/EmmanuelSHYIRAMBERE/Lab-1-Student-Course-Management-System.git
cd Lab-1-Student-Course-Management-System

# Install dependencies
poetry install

# Run the application
poetry run python main.py

# Run tests
poetry run pytest tests/ -v
```

## Project Structure

Each lab follows a consistent structure:

```
lab-name/
├── src/
│   ├── models/          # Core business logic
│   ├── reports/         # Report generators
│   └── utils/           # Helper functions
├── tests/               # Unit tests
├── data/                # Data files (if applicable)
├── main.py             # Entry point
├── app.py              # Application class
├── menu_handlers.py    # UI logic
├── pyproject.toml      # Dependencies
└── README.md           # Lab-specific documentation
```

## Testing

All labs include comprehensive unit tests:

```bash
# Run tests for a specific lab
cd Lab-1-Student-Course-Management-System
poetry run pytest tests/ -v

# Run tests with coverage
poetry run pytest tests/ --cov=src --cov-report=html
```

## Documentation

Each lab includes:
- **README.md** - User guide and features
- **Code comments** - Inline documentation
- **Type hints** - Function signatures
- **Docstrings** - Class and method documentation

## Code Quality

All projects follow:
- PEP 8 style guidelines
- Type hints throughout
- Comprehensive error handling
- Input validation
- Modular design
- DRY principles

## Technologies Used

- **Python 3.10+** - Core language
- **Poetry** - Dependency management
- **colorama** - Colored console output
- **tabulate** - Formatted table output
- **pytest** - Unit testing framework
- **ABC** - Abstract base classes
- **JSON** - Data persistence
- **datetime** - Date/time handling
- **typing** - Type hints

## Key Concepts by Lab

### Lab 1: Student Course Management
- Class hierarchies
- Inheritance (Student → Undergraduate/Graduate/International)
- File I/O operations
- Data validation
- Report generation

### Lab 2: Employee Payroll Tracker
- Property decorators for validation
- Modular salary calculation functions
- Polymorphic payroll computation
- Tax and bonus calculations
- Comprehensive error handling

### Lab 3: Library Inventory Application
- Abstract Base Classes (LibraryResource)
- List comprehensions for search/filter
- JSON serialization/deserialization
- __repr__ and __eq__ implementation
- super() for inheritance

### Lab 4: Vehicle Rental System
- Abstract Base Classes
- Polymorphism (calculate_rental_cost)
- Property decorators
- State management
- Dynamic pricing algorithms

### Lab 5: Personal Finance Tracker
- Operator overloading (__eq__, __add__, __lt__, __str__, __repr__)
- Property decorators (@property)
- List comprehensions
- JSON serialization
- Exception handling
- Numeric operations

## Educational Value

These labs are designed to teach:

1. **Fundamental OOP Concepts**
   - Classes and objects
   - Inheritance and polymorphism
   - Encapsulation and abstraction

2. **Advanced Python Features**
   - Property decorators
   - Operator overloading
   - Abstract base classes
   - List comprehensions

3. **Software Engineering Practices**
   - Modular design
   - Error handling
   - Unit testing
   - Documentation

4. **Real-World Applications**
   - Student management systems
   - Payroll processing
   - Library management
   - Rental management
   - Financial tracking

## Lab Progression

The labs are designed to build upon each other:

1. **Lab 1** - Introduction to OOP basics
2. **Lab 2** - Property decorators and modular functions
3. **Lab 3** - File I/O and list comprehensions
4. **Lab 4** - Advanced OOP with polymorphism
5. **Lab 5** - Operator overloading and exception handling

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is available for educational purposes.

## Author

**EmmanuelSHYIRAMBERE**
- Email: emashyirambere1@gmail.com
- GitHub: [@EmmanuelSHYIRAMBERE](https://github.com/EmmanuelSHYIRAMBERE)

## Acknowledgments

- Python Software Foundation
- Poetry team
- Open source community

## Support

For questions or issues:
- Open an issue on the respective lab repository
- Email: emashyirambere1@gmail.com

## Video Tutorials

- **Lab 1:** [Student Course Management System](https://drive.google.com/file/d/1T50mvaxqoquzWzEt3D2s8PbHTAXkm5rx/view?usp=sharing)

---

## Quick Links

| Lab | Repository | Documentation |
|-----|-----------|---------------|
| Lab 1 | [Student Course Management](https://github.com/EmmanuelSHYIRAMBERE/Lab-1-Student-Course-Management-System) | [README](https://github.com/EmmanuelSHYIRAMBERE/Lab-1-Student-Course-Management-System#readme) |
| Lab 2 | [Employee Payroll Tracker](https://github.com/EmmanuelSHYIRAMBERE/Lab-2-Employee-Payroll-Tracker) | [README](https://github.com/EmmanuelSHYIRAMBERE/Lab-2-Employee-Payroll-Tracker#readme) |
| Lab 3 | [Library Inventory Application](https://github.com/EmmanuelSHYIRAMBERE/Lab-3-Library-Inventory-Application) | [README](https://github.com/EmmanuelSHYIRAMBERE/Lab-3-Library-Inventory-Application#readme) |
| Lab 4 | [Vehicle Rental System](https://github.com/EmmanuelSHYIRAMBERE/Lab-4-Vehicle-Rental-System) | [README](https://github.com/EmmanuelSHYIRAMBERE/Lab-4-Vehicle-Rental-System#readme) |
| Lab 5 | [Personal Finance Tracker](https://github.com/EmmanuelSHYIRAMBERE/Lab-5-Personal-Finance-Tracker) | [README](https://github.com/EmmanuelSHYIRAMBERE/Lab-5-Personal-Finance-Tracker#readme) |

---

**Happy Coding!**

