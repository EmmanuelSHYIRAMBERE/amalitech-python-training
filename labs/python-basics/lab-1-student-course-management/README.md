# Student Course Management System

A comprehensive console-based application for managing students, courses, and enrollments in an educational institution.

## Features

- **Student Management**: Add and manage undergraduate, graduate, and international students
- **Course Management**: Create and manage courses with schedules and capacities
- **Enrollment Management**: Enroll/drop students, add grades
- **Reporting**: Generate detailed reports with tabular formatting
- **Statistics**: View system-wide statistics and analytics

## Technical Highlights

- Python 3.10+ with type hints
- Object-Oriented Design with inheritance and polymorphism
- Abstract Base Classes for report generation
- Property decorators for encapsulation
- Comprehensive error handling
- Colorful console output using colorama
- Tabulated reports using tabulate

## Prerequisites

- Python 3.10 or higher
- Poetry (Python dependency management tool)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/EmmanuelSHYIRAMBERE/Lab-1-Student-Course-Management-System.git
cd Lab-1-Student-Course-Management-System
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

The application provides an interactive menu system with the following main options:

1. **Student Management**
   - Add Undergraduate Student
   - Add Graduate Student
   - Add International Student
   - View All Students
   - View Student Details
   - Update Student Info

2. **Course Management**
   - Add New Course
   - View All Courses
   - View Course Details
   - Update Course Info
   - View Course Roster

3. **Enrollment Management**
   - Enroll Student in Course
   - Drop Student from Course
   - View Student Enrollments
   - Add Grade for Student

4. **Generate Reports**
   - Student Report (with GPA and tuition)
   - Course Report (with enrollment statistics)
   - Enrollment Report (comprehensive overview)
   - Generate All Reports

5. **View Statistics**
   - System-wide statistics
   - Student type breakdown
   - GPA analytics
   - Course utilization metrics

## Example Output

### Main Menu

```
============================================================
Welcome to the Student Course Management System
============================================================

1. Student Management
2. Course Management
3. Enrollment Management
4. Generate Reports
5. View Statistics
0. Exit

Enter your choice:
```

### Viewing All Students

```
ALL STUDENTS
--------------------------------------------------
Undergraduate Student: Alice Johnson (S001)
  Email: alice@example.com
  Courses: 2
  GPA: 3.50
  Tuition: $12000.00

Graduate Student: Bob Smith (S002)
  Email: bob@example.com
  Courses: 1
  GPA: 4.00
  Tuition: $15000.00

International Student: Carlos Rodriguez (S003) - Spain
  Email: carlos@example.com
  Courses: 1
  GPA: 0.00
  Tuition: $18000.00
```

### Course Details

```
==================================================
COURSE DETAILS: Introduction to Programming
==================================================
Code: CS101
Credits: 3
Instructor: Dr. Williams
Schedule: Monday: 10:00-12:00, Wednesday: 10:00-12:00
Enrollment: 2/30
Available Seats: 28
```

### System Statistics

```
SYSTEM STATISTICS
==================================================
Total Students: 3
Total Courses: 3
Total Enrollments: 4
Avg Courses per Student: 1.33
Course Capacity Utilization: 44.4%

Student Type Breakdown:
  * UndergraduateStudent: 1 (33.3%)
  * GraduateStudent: 1 (33.3%)
  * InternationalStudent: 1 (33.3%)

GPA Statistics:
  * Average GPA: 3.75
  * Highest GPA: 4.00
  * Lowest GPA: 3.50
```

### Student Report (Tabular Format)

```
+----------+-----------------+--------------+---------+----------+
| ID       | Name            | Type         | GPA     | Tuition  |
+----------+-----------------+--------------+---------+----------+
| S001     | Alice Johnson   | Undergrad    | 3.50    | $12000   |
| S002     | Bob Smith       | Graduate     | 4.00    | $15000   |
| S003     | Carlos Rodriguez| International| 0.00    | $18000   |
+----------+-----------------+--------------+---------+----------+
```

## Project Structure

```
student-course-management/
├── src/
│   ├── models/
│   │   ├── student.py          # Student classes (Undergraduate, Graduate, International)
│   │   ├── course.py           # Course class with enrollment management
│   │   └── enrollment.py       # Enrollment tracking
│   ├── reports/
│   │   └── report_generator.py # Report generation classes
│   ├── utils/
│   │   └── helpers.py          # Utility functions
│   └── data/
│       └── init.py             # Data initialization
├── tests/
│   └── test_student.py         # Unit tests
├── main.py                     # Application entry point
├── app.py                      # Main application class
├── menu_handlers.py            # Menu and UI logic
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

## Sample Data

The application comes pre-loaded with sample data:

**Students:**

- Alice Johnson (S001) - Undergraduate, Year 2
- Bob Smith (S002) - Graduate, Research: Machine Learning
- Carlos Rodriguez (S003) - International from Spain, Year 3

**Courses:**

- CS101: Introduction to Programming (Dr. Williams)
- CS201: Data Structures (Dr. Garcia)
- MATH101: Calculus I (Prof. Miller)

## Features in Detail

### Student Types

1. **Undergraduate Students**
   - Year level (1-4)
   - Base tuition: $12,000
   - Standard GPA calculation

2. **Graduate Students**
   - Research topic tracking
   - Optional advisor assignment
   - Base tuition: $15,000

3. **International Students**
   - Country of origin
   - Year level (1-4)
   - Base tuition: $18,000 (includes international fees)

### Course Features

- Course code and name
- Credit hours (1-6)
- Instructor assignment
- Maximum capacity
- Schedule management (day and time)
- Enrollment tracking
- Automatic capacity checking

### Enrollment Features

- Enroll students in courses
- Drop students from courses
- Grade management (0.0 - 4.0 scale)
- GPA calculation
- Enrollment validation

### Reporting Features

- **Student Reports**: Complete student roster with GPA and tuition
- **Course Reports**: Course listings with enrollment statistics
- **Enrollment Reports**: Detailed enrollment overview
- Export reports to text files with timestamps

## Error Handling

The application includes comprehensive error handling:

- Input validation for all user entries
- Email format validation
- Duplicate ID prevention
- Course capacity checking
- Grade range validation (0.0 - 4.0)
- Graceful handling of keyboard interrupts

## Tips

- Use `Ctrl+C` to safely exit the application at any time
- Reports can be saved to files with automatic timestamps
- The system validates all inputs to prevent errors
- Sample data is loaded automatically for testing

## Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'colorama'`

- **Solution**: Install dependencies using `poetry install`

**Issue**: Colors not displaying correctly on Windows

- **Solution**: The application uses colorama which automatically handles Windows console colors

**Issue**: Application crashes on startup

- **Solution**: Ensure Python 3.10+ is installed: `python --version`

## Contributing

Contributions are welcome! Please ensure:

- Code follows PEP 8 style guidelines
- Type hints are included
- Error handling is comprehensive
- Documentation is updated

## License

This project is available for educational purposes.

## Video Tutorial

https://drive.google.com/file/d/1T50mvaxqoquzWzEt3D2s8PbHTAXkm5rx/view?usp=sharing

## Author

EmmanuelSHYIRAMBERE (emashyirambere1@gmail.com)
