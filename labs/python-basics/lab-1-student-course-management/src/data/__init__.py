"""Data storage module using built-in types."""

from typing import Any

# Global data stores (will be replaced by OOP later)
students_db: dict[str, Any] = {}  # Dictionary: student_id -> student_data
courses_db: dict[str, Any] = {}  # Dictionary: course_code -> course_data
enrollments_db: dict[str, Any] = {}  # Dictionary: student_id -> list of course codes


def initialize_data() -> None:
    """Initialize the data stores with sample data."""
    global students_db, courses_db, enrollments_db

    # Sample students
    students_db = {
        "S001": {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "type": "undergraduate",
        },
        "S002": {"name": "Bob Smith", "email": "bob@example.com", "type": "graduate"},
        "S003": {
            "name": "Charlie Brown",
            "email": "charlie@example.com",
            "type": "undergraduate",
        },
    }

    # Sample courses
    courses_db = {
        "CS101": {
            "name": "Introduction to Programming",
            "credits": 3,
            "instructor": "Dr. Williams",
        },
        "CS201": {"name": "Data Structures", "credits": 4, "instructor": "Dr. Garcia"},
        "MATH101": {"name": "Calculus I", "credits": 4, "instructor": "Prof. Miller"},
    }

    # Sample enrollments
    enrollments_db = {
        "S001": ["CS101", "MATH101"],
        "S002": ["CS201"],
        "S003": ["CS101"],
    }


# Comprehensions examples
def get_student_names() -> dict[str, str]:
    """Use dictionary comprehension to extract student names."""
    return {sid: str(data["name"]) for sid, data in students_db.items()}


def get_courses_by_credits(min_credits: int = 3) -> list[str]:
    """Use list comprehension to filter courses by credits."""
    return [
        str(course["name"])
        for course in courses_db.values()
        if course["credits"] >= min_credits
    ]


def get_enrollment_summary() -> dict[str, int]:
    """Use set operations to analyze enrollments."""
    all_enrolled_courses = set()
    for courses in enrollments_db.values():
        all_enrolled_courses.update(courses)

    return {
        "total_students": len(students_db),
        "total_courses": len(courses_db),
        "courses_with_enrollments": len(all_enrolled_courses),
    }
