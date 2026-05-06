"""Tests for src/models/enrollment.py (procedural / legacy functions)."""

from typing import Any

import pytest
from src.models.enrollment import (
    add_course,
    add_student,
    calculate_average,
    enroll_student,
    generate_enrollment_report,
    get_course_roster,
)


class TestAddStudent:
    def test_adds_new_student(self) -> None:
        db: dict[str, Any] = {}
        assert add_student(db, "S001", "Alice", "alice@example.com") is True
        assert "S001" in db

    def test_stores_student_data(self) -> None:
        db: dict[str, Any] = {}
        add_student(db, "S001", "Alice", "alice@example.com", "graduate")
        assert db["S001"]["name"] == "Alice"
        assert db["S001"]["type"] == "graduate"

    def test_duplicate_returns_false(self) -> None:
        db: dict[str, Any] = {
            "S001": {"name": "Alice", "email": "a@e.com", "type": "undergraduate"}
        }
        assert add_student(db, "S001", "Alice", "a@e.com") is False


class TestAddCourse:
    def test_adds_new_course(self) -> None:
        db: dict[str, Any] = {}
        assert add_course(db, "CS101", "Intro", 3, "Dr. A") is True
        assert "CS101" in db

    def test_stores_course_data(self) -> None:
        db: dict[str, Any] = {}
        add_course(db, "CS101", "Intro", 3, "Dr. A")
        assert db["CS101"]["credits"] == 3
        assert db["CS101"]["instructor"] == "Dr. A"

    def test_duplicate_returns_false(self) -> None:
        db: dict[str, Any] = {
            "CS101": {"name": "Intro", "credits": 3, "instructor": "Dr. A"}
        }
        assert add_course(db, "CS101", "Intro", 3, "Dr. A") is False


class TestEnrollStudent:
    def test_enrolls_in_new_course(self) -> None:
        enrollments: dict[str, list[str]] = {}
        assert enroll_student(enrollments, "S001", "CS101") is True
        assert "CS101" in enrollments["S001"]

    def test_creates_student_entry_if_absent(self) -> None:
        enrollments: dict[str, list[str]] = {}
        enroll_student(enrollments, "S001", "CS101")
        assert "S001" in enrollments

    def test_duplicate_enrollment_returns_false(self) -> None:
        enrollments: dict[str, list[str]] = {"S001": ["CS101"]}
        assert enroll_student(enrollments, "S001", "CS101") is False


class TestCalculateAverage:
    def test_average_of_multiple_grades(self) -> None:
        assert calculate_average([3.0, 4.0, 2.0]) == pytest.approx(3.0)

    def test_single_grade(self) -> None:
        assert calculate_average([3.5]) == pytest.approx(3.5)

    def test_empty_list_returns_zero(self) -> None:
        assert calculate_average([]) == 0.0


class TestGetCourseRoster:
    def test_returns_enrolled_students(self) -> None:
        students: dict[str, Any] = {
            "S001": {"name": "Alice", "email": "a@e.com", "type": "ug"}
        }
        enrollments: dict[str, list[str]] = {"S001": ["CS101"]}
        roster = get_course_roster("CS101", students, enrollments)
        assert len(roster) == 1
        assert roster[0]["name"] == "Alice"

    def test_excludes_students_in_other_courses(self) -> None:
        students: dict[str, Any] = {
            "S001": {"name": "Alice", "email": "a@e.com", "type": "ug"}
        }
        enrollments: dict[str, list[str]] = {"S001": ["CS201"]}
        roster = get_course_roster("CS101", students, enrollments)
        assert roster == []

    def test_roster_includes_student_id(self) -> None:
        students: dict[str, Any] = {
            "S001": {"name": "Alice", "email": "a@e.com", "type": "ug"}
        }
        enrollments: dict[str, list[str]] = {"S001": ["CS101"]}
        roster = get_course_roster("CS101", students, enrollments)
        assert roster[0]["id"] == "S001"


class TestGenerateEnrollmentReport:
    def test_prints_student_name(self, capsys: pytest.CaptureFixture[str]) -> None:
        students: dict[str, Any] = {
            "S001": {"name": "Alice", "email": "a@e.com", "type": "undergraduate"}
        }
        courses: dict[str, Any] = {
            "CS101": {"name": "Intro", "credits": 3, "instructor": "Dr. A"}
        }
        enrollments: dict[str, list[str]] = {"S001": ["CS101"]}
        generate_enrollment_report(students, courses, enrollments)
        out = capsys.readouterr().out
        assert "Alice" in out
        assert "CS101" in out

    def test_shows_no_courses_when_unenrolled(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        students: dict[str, Any] = {
            "S001": {"name": "Alice", "email": "a@e.com", "type": "undergraduate"}
        }
        courses: dict[str, Any] = {}
        enrollments: dict[str, list[str]] = {}
        generate_enrollment_report(students, courses, enrollments)
        out = capsys.readouterr().out
        assert "No courses enrolled" in out

    def test_prints_summary_count(self, capsys: pytest.CaptureFixture[str]) -> None:
        students: dict[str, Any] = {
            "S001": {"name": "Alice", "email": "a@e.com", "type": "undergraduate"}
        }
        generate_enrollment_report(students, {}, {})
        out = capsys.readouterr().out
        assert "1 total students" in out
