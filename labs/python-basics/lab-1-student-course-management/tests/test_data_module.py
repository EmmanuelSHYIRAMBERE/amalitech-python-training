"""Tests for src/data/__init__.py (sample data store and comprehensions)."""

import src.data as data_module
from src.data import (
    get_courses_by_credits,
    get_enrollment_summary,
    get_student_names,
    initialize_data,
)


class TestInitializeData:
    def setup_method(self) -> None:
        initialize_data()

    def test_students_populated(self) -> None:
        assert len(data_module.students_db) == 3

    def test_known_student_present(self) -> None:
        assert "S001" in data_module.students_db

    def test_courses_populated(self) -> None:
        assert len(data_module.courses_db) == 3

    def test_known_course_present(self) -> None:
        assert "CS101" in data_module.courses_db

    def test_enrollments_populated(self) -> None:
        assert "S001" in data_module.enrollments_db
        assert "CS101" in data_module.enrollments_db["S001"]


class TestGetStudentNames:
    def setup_method(self) -> None:
        initialize_data()

    def test_returns_all_students(self) -> None:
        names = get_student_names()
        assert len(names) == 3

    def test_maps_id_to_name(self) -> None:
        names = get_student_names()
        assert names["S001"] == "Alice Johnson"
        assert names["S002"] == "Bob Smith"


class TestGetCoursesByCredits:
    def setup_method(self) -> None:
        initialize_data()

    def test_default_min_credits_returns_results(self) -> None:
        assert len(get_courses_by_credits()) > 0

    def test_very_high_min_returns_empty(self) -> None:
        assert get_courses_by_credits(min_credits=10) == []

    def test_low_min_returns_all(self) -> None:
        assert len(get_courses_by_credits(min_credits=1)) == 3

    def test_filters_below_threshold(self) -> None:
        all_courses = get_courses_by_credits(min_credits=1)
        high_credit = get_courses_by_credits(min_credits=4)
        assert len(high_credit) < len(all_courses)


class TestGetEnrollmentSummary:
    def setup_method(self) -> None:
        initialize_data()

    def test_total_students(self) -> None:
        assert get_enrollment_summary()["total_students"] == 3

    def test_total_courses(self) -> None:
        assert get_enrollment_summary()["total_courses"] == 3

    def test_courses_with_enrollments(self) -> None:
        summary = get_enrollment_summary()
        assert "courses_with_enrollments" in summary
        assert summary["courses_with_enrollments"] > 0
