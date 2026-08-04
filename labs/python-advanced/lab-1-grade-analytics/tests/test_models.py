"""Tests for data models."""

import pytest

from src.models import Grade, SemesterRecord, Student


def test_grade_letter_grades():
    assert Grade("C1", 95, "S1").letter() == "A"
    assert Grade("C1", 85, "S1").letter() == "B"
    assert Grade("C1", 75, "S1").letter() == "C"
    assert Grade("C1", 65, "S1").letter() == "D"
    assert Grade("C1", 55, "S1").letter() == "F"


def test_student_gpa():
    s = Student("S1", "Alice", "CS", 2, [Grade("C1", 80, "S1"), Grade("C2", 90, "S1")])
    assert s.gpa() == 85.0


def test_student_gpa_none_when_no_grades():
    s = Student("S1", "Alice", "CS", 2)
    assert s.gpa() is None


def test_student_gpa_for_semester():
    s = Student(
        "S1",
        "Alice",
        "CS",
        2,
        [Grade("C1", 80, "S1"), Grade("C2", 90, "S2")],
    )
    assert s.gpa_for_semester("S1") == 80.0
    assert s.gpa_for_semester("S2") == 90.0
    assert s.gpa_for_semester("S3") is None


def test_semester_record_namedtuple():
    rec = SemesterRecord(semester="2024-S1", gpa=85.0)
    assert rec.semester == "2024-S1"
    assert rec.gpa == 85.0
