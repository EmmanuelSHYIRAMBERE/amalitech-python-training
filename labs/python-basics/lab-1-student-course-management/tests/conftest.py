"""Shared fixtures for all test modules."""

import pytest
from src.models.course import Course
from src.models.student import (
    GraduateStudent,
    InternationalStudent,
    UndergraduateStudent,
)


@pytest.fixture
def undergrad() -> UndergraduateStudent:
    return UndergraduateStudent("S001", "Alice Johnson", "alice@example.com", 2)


@pytest.fixture
def grad() -> GraduateStudent:
    return GraduateStudent("S002", "Bob Smith", "bob@example.com", "Machine Learning")


@pytest.fixture
def international() -> InternationalStudent:
    return InternationalStudent(
        "S003", "Carlos Rodriguez", "carlos@example.com", "Spain", 3
    )


@pytest.fixture
def course() -> Course:
    return Course("CS101", "Introduction to Programming", 3, "Dr. Williams", 30)


@pytest.fixture
def small_course() -> Course:
    """Course with capacity of 1 for full-course tests."""
    return Course("CS999", "Tiny Course", 2, "Dr. Tiny", 1)
