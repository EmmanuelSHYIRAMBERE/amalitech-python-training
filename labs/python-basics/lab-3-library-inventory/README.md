# Library Inventory Application

A comprehensive library management system for tracking books, eBooks, audiobooks, and borrowers with file I/O persistence, search/filter capabilities, and OOP best practices.

## Features

- **Resource Management**: Manage books, eBooks, and audiobooks
- **Borrower Management**: Track library members and their borrowed items
- **Borrow/Return Operations**: Handle lending and returns with due dates
- **Search & Filter**: Advanced search using list comprehensions
- **File I/O**: Persist data in JSON format
- **Reports**: Generate detailed inventory and borrowing reports
- **Statistics**: View library analytics and metrics

## Technical Highlights

- Python 3.10+ with type hints
- Abstract Base Classes (ABC) for library resources
- Inheritance for specialized materials (Book, EBook, AudioBook)
- List comprehensions for search and filtering
- File I/O with JSON persistence
- `__repr__`, `__eq__`, and `super()` implementation
- Property decorators for encapsulation
- Modular package structure
- Comprehensive error handling

## Prerequisites

- Python 3.10 or higher
- Poetry (Python dependency management tool)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/EmmanuelSHYIRAMBERE/Lab-3-Library-Inventory-Application.git
cd Lab-3-Library-Inventory-Application
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

1. **Resource Management**
   - Add Book/EBook/AudioBook
   - View All Resources
   - View Resource Details
   - Remove Resource

2. **Borrower Management**
   - Add Borrower
   - View All Borrowers
   - View Borrower Details
   - Remove Borrower

3. **Borrow/Return Operations**
   - Borrow Resource
   - Return Resource
   - View Borrowed Items
   - View Overdue Items

4. **Search & Filter**
   - Search by Title
   - Search by Author
   - Filter by Type
   - Filter Available/Borrowed

5. **Generate Reports**
   - Inventory Report
   - Borrowed Items Report
   - Resource Type Report
   - Borrower Report
   - Export to Text File

6. **View Statistics**
   - Total resources and availability
   - Resource type breakdown
   - Borrower statistics

## Example Output

### Main Menu

```
============================================================
Library Inventory Management System
============================================================

1. Resource Management
2. Borrower Management
3. Borrow/Return Operations
4. Search & Filter
5. Generate Reports
6. View Statistics
0. Back/Exit

Enter your choice:
```

### Inventory Report

```
============================================================
                LIBRARY INVENTORY REPORT
            Generated: 2024-01-15 10:30:00
============================================================

+------+--------------------------------+----------------------+------+------------+-----------+
| ID   | Title                          | Author               | Year | Type       | Available |
+------+--------------------------------+----------------------+------+------------+-----------+
| B001 | To Kill a Mockingbird          | Harper Lee           | 1960 | Book       | No        |
| B002 | 1984                           | George Orwell        | 1949 | Book       | Yes       |
| E001 | The Great Gatsby               | F. Scott Fitzgerald  | 1925 | EBook      | No        |
| A001 | Harry Potter and the Sorcerer  | J.K. Rowling         | 1997 | AudioBook  | Yes       |
+------+--------------------------------+----------------------+------+------------+-----------+

Summary:
  Total Resources: 7
  Available: 4
  Borrowed: 3
  Overdue: 0
```

### Library Statistics

```
📊 LIBRARY STATISTICS
==================================================
📚 Total Resources: 7
✅ Available: 4
📖 Borrowed: 3
⚠️ Overdue: 0

📊 By Type:
  • Book: 3
  • EBook: 2
  • AudioBook: 2

👥 Total Borrowers: 3
```

## Project Structure

```
library-inventory/
├── src/
│   ├── models/
│   │   └── library_resource.py  # ABC and resource classes
│   ├── utils/
│   │   ├── file_io.py           # JSON persistence
│   │   ├── search.py            # Search with comprehensions
│   │   ├── helpers.py           # Validation utilities
│   │   └── reports.py           # Report generation
│   └── data/
│       └── library_data.json    # Persisted data
├── reports/                     # Generated reports
├── tests/
│   └── test_library.py          # Unit tests
├── main.py                      # Application entry point
├── app.py                       # Main system class
├── menu_handlers.py             # CLI interface
├── pyproject.toml               # Poetry configuration
└── README.md                    # This file
```

## Class Hierarchy

```
LibraryResource (ABC)
├── Book
│   ├── Properties: isbn, pages
│   └── Loan Period: 14 days
├── EBook
│   ├── Properties: file_size, format
│   └── Loan Period: 21 days
└── AudioBook
    ├── Properties: duration, narrator
    └── Loan Period: 7 days

Author
└── Properties: name, birth_year, nationality

Borrower
└── Properties: borrower_id, name, email, borrowed_items
```

## Key Features

### 1. Abstract Base Classes

```python
class LibraryResource(ABC):
    @abstractmethod
    def get_resource_type(self) -> str:
        pass

    @abstractmethod
    def get_loan_period(self) -> int:
        pass
```

### 2. Inheritance with super()

```python
class Book(LibraryResource):
    def __init__(self, resource_id, title, author, year, isbn, pages):
        super().__init__(resource_id, title, author, year)
        self._isbn = isbn
        self._pages = pages
```

### 3. Special Methods

```python
def __repr__(self) -> str:
    return f"Book(id='{self._resource_id}', title='{self._title}')"

def __eq__(self, other) -> bool:
    if not isinstance(other, LibraryResource):
        return False
    return self._resource_id == other._resource_id
```

### 4. List Comprehensions

```python
def search_by_title(resources, query):
    return [r for r in resources if query.lower() in r.title.lower()]

def filter_available(resources):
    return [r for r in resources if r.is_available]

def get_unique_authors(resources):
    return sorted(list({r.author for r in resources}))
```

### 5. File I/O with JSON

```python
def save_library_data(resources, borrowers, filename):
    data = {'resources': [], 'borrowers': []}
    # Serialize data
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def load_library_data(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    # Deserialize and return
```

## Sample Data

The application comes pre-loaded with sample data:

**Books:**

- To Kill a Mockingbird by Harper Lee (1960)
- 1984 by George Orwell (1949)
- Pride and Prejudice by Jane Austen (1813)

**EBooks:**

- The Great Gatsby by F. Scott Fitzgerald (1925)
- Moby Dick by Herman Melville (1851)

**AudioBooks:**

- Harry Potter and the Sorcerer's Stone by J.K. Rowling (1997)
- The Hobbit by J.R.R. Tolkien (1937)

**Borrowers:**

- John Doe (M001)
- Jane Smith (M002)
- Bob Johnson (M003)

## Development Milestones

- ✅ **Day 1**: Setup & base data structure
- ✅ **Day 2**: Functional logic (add/search books)
- ✅ **Day 3**: OOP classes and inheritance
- ✅ **Day 4**: Packaging, testing, documentation

## Features in Detail

### Resource Management

- Add different types of resources (Book, EBook, AudioBook)
- Each type has specific properties and loan periods
- View detailed information about any resource
- Remove resources from inventory

### Borrower Management

- Register library members
- Track borrowed items per member
- View borrower history
- Prevent removal of borrowers with outstanding items

### Borrow/Return Operations

- Borrow available resources
- Automatic due date calculation based on resource type
- Return borrowed items
- Track overdue items with warnings

### Search & Filter

- Search by title or author (case-insensitive)
- Filter by resource type
- Filter available vs borrowed items
- All using efficient list comprehensions

### Data Persistence

- Automatic save on data changes
- JSON format for human-readable storage
- Load previous session data on startup
- Export reports to text files

## Error Handling

The application includes comprehensive error handling:

- Input validation for all user entries
- Email and ISBN format validation
- Duplicate ID prevention
- Resource availability checking
- Graceful handling of keyboard interrupts
- File I/O error handling

## Tips

- Use `Ctrl+C` to safely exit at any time
- Data is automatically saved after each operation
- Reports are saved in the `reports/` directory
- Search is case-insensitive for better results
- Overdue items are highlighted in red

## Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'colorama'`

- **Solution**: Install dependencies using `poetry install`

**Issue**: Data not persisting

- **Solution**: Check write permissions in `src/data/` directory

**Issue**: Application crashes on startup

- **Solution**: Ensure Python 3.10+ is installed: `python --version`

## Testing

Run unit tests:

```bash
poetry run python -m pytest tests/
```

## Contributing

Contributions are welcome! Please ensure:

- Code follows PEP 8 style guidelines
- Type hints are included
- Docstrings are comprehensive
- Error handling is robust
- Tests are updated

## License

This project is available for educational purposes.

## Author

EmmanuelSHYIRAMBERE (emashyirambere1@gmail.com)
