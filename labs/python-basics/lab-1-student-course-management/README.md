# Student Course Management System

A console-based application for managing students, courses, and enrollments in an educational institution.

## Features

- **Student Management** — Add and manage undergraduate, graduate, and international students
- **Course Management** — Create and manage courses with schedules and capacities
- **Enrollment Management** — Enroll/drop students, record grades
- **Reporting** — Generate detailed tabular reports (save to file with timestamp)
- **Statistics** — System-wide analytics: GPA, utilisation, student-type breakdown
- **Logging** — Structured application logs via Python's `logging` module

## Technical Highlights

- Python 3.10+ with full type hints
- OOP: abstract base classes, inheritance, polymorphism, encapsulation
- Property decorators — no direct private attribute access from outside a class
- `__hash__` defined alongside `__eq__` (students/courses are hashable and set-safe)
- Input validation in constructors **and** setters (fail-fast)
- 78 pytest unit tests with parameterized cases and cross-model sync checks
- Colorful console output via `colorama`; tabulated reports via `tabulate`

## Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/)

## Installation

```bash
git clone https://github.com/EmmanuelSHYIRAMBERE/Lab-1-Student-Course-Management-System.git
cd lab-1-student-course-management
poetry install
```

## Running the Application

```bash
poetry run python main.py
```

## Running Tests

```bash
# Run all tests
poetry run pytest

# With coverage report
poetry run pytest --cov=src --cov-report=term-missing
```

## Project Structure

```
lab-1-student-course-management/
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── student.py          # Student, UndergraduateStudent, GraduateStudent, InternationalStudent
│   │   ├── course.py           # Course with enrollment management
│   │   └── enrollment.py       # Legacy dict-based enrollment helpers
│   ├── reports/
│   │   ├── __init__.py
│   │   └── report_generator.py # ReportGenerator ABC + StudentReport, CourseReport, EnrollmentReport
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py          # validate_email, get_user_input, flexible_summary, …
│   └── data/
│       └── __init__.py         # In-memory data stores + sample-data initialiser
├── tests/
│   ├── __init__.py
│   └── test_student.py         # 78 unit tests (pytest)
├── main.py                     # Entry point — configures logging, starts app
├── app.py                      # StudentCourseManagementSystem facade
├── menu_handlers.py            # All CLI menu logic
├── pyproject.toml
└── README.md
```

## Logging

Logging is configured in `main.py` at `INFO` level with timestamps:

```
2025-01-15 10:30:00 [INFO] app: StudentCourseManagementSystem initialised with sample data
2025-01-15 10:30:05 [INFO] src.models.student: Student S001 enrolled in course CS101
```

Set `level=logging.DEBUG` in `main.py` for verbose output during development.

## Sample Data

Pre-loaded on startup:

| ID   | Name             | Type                        |
|------|------------------|-----------------------------|
| S001 | Alice Johnson    | Undergraduate (Year 2)      |
| S002 | Bob Smith        | Graduate (Research: ML)     |
| S003 | Carlos Rodriguez | International from Spain    |

| Code    | Name                        | Instructor    |
|---------|-----------------------------|---------------|
| CS101   | Introduction to Programming | Dr. Williams  |
| CS201   | Data Structures             | Dr. Garcia    |
| MATH101 | Calculus I                  | Prof. Miller  |

## Architecture Notes

| Concern          | Location                          |
|------------------|-----------------------------------|
| Business logic   | `src/models/`                     |
| UI / CLI         | `menu_handlers.py`                |
| Reporting        | `src/reports/report_generator.py` |
| Data init        | `src/data/__init__.py`            |
| App wiring       | `app.py`                          |
| Entry point      | `main.py`                         |

## Error Handling

- All constructors validate inputs and raise `ValueError` with descriptive messages
- Email format validated via regex in `validate_email`
- Duplicate student/course IDs rejected at the menu layer
- Course capacity enforced in `Course.add_student`
- Grade range (0.0–4.0) enforced in `Student.add_grade`
- `KeyboardInterrupt` caught gracefully in `main.py`

## Author

Emmanuel SHYIRAMBERE — [LinkedIn](https://www.linkedin.com/in/emashyirambere)
