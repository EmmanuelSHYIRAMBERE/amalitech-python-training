"""Tests for src/reports/report_generator.py."""

import pytest
from src.models.course import Course
from src.models.student import GraduateStudent, UndergraduateStudent
from src.reports.report_generator import (
    CourseReport,
    EnrollmentReport,
    ReportGenerator,
    StudentReport,
)


class TestStudentReport:
    def test_generate_empty_shows_warning(self) -> None:
        report = StudentReport([])
        assert "No students found" in report.generate()

    def test_generate_includes_student_names(
        self, undergrad: UndergraduateStudent, grad: GraduateStudent
    ) -> None:
        output = StudentReport([undergrad, grad]).generate()
        assert "Alice Johnson" in output
        assert "Bob Smith" in output

    def test_generate_includes_title(self, undergrad: UndergraduateStudent) -> None:
        assert "STUDENT REPORT" in StudentReport([undergrad]).generate()

    def test_get_data_returns_students(self, undergrad: UndergraduateStudent) -> None:
        report = StudentReport([undergrad])
        assert undergrad in report.get_data()


class TestCourseReport:
    def test_generate_empty_shows_warning(self) -> None:
        report = CourseReport([])
        assert "No courses found" in report.generate()

    def test_generate_includes_course_name(self, course: Course) -> None:
        output = CourseReport([course]).generate()
        assert "Introduction to Programming" in output

    def test_generate_includes_title(self, course: Course) -> None:
        assert "COURSE REPORT" in CourseReport([course]).generate()

    def test_get_data_returns_courses(self, course: Course) -> None:
        report = CourseReport([course])
        assert course in report.get_data()


class TestEnrollmentReport:
    def test_generate_empty_shows_warning(self) -> None:
        report = EnrollmentReport([], [])
        assert "No enrollments found" in report.generate()

    def test_generate_includes_title(
        self, undergrad: UndergraduateStudent, course: Course
    ) -> None:
        assert "ENROLLMENT REPORT" in EnrollmentReport([undergrad], [course]).generate()

    def test_generate_lists_enrolled_course(
        self, undergrad: UndergraduateStudent, course: Course
    ) -> None:
        course.add_student(undergrad)
        output = EnrollmentReport([undergrad], [course]).generate()
        assert "Introduction to Programming" in output

    def test_generate_shows_no_courses_when_unenrolled(
        self, undergrad: UndergraduateStudent, course: Course
    ) -> None:
        output = EnrollmentReport([undergrad], [course]).generate()
        assert "No courses enrolled" in output

    def test_generate_includes_student_name(
        self, undergrad: UndergraduateStudent, course: Course
    ) -> None:
        output = EnrollmentReport([undergrad], [course]).generate()
        assert "Alice Johnson" in output

    def test_get_data_returns_students(
        self, undergrad: UndergraduateStudent, course: Course
    ) -> None:
        report = EnrollmentReport([undergrad], [course])
        assert undergrad in report.get_data()


class TestReportFactory:
    def test_create_student_report(self, undergrad: UndergraduateStudent) -> None:
        report = ReportGenerator.create_report("student", students=[undergrad])
        assert isinstance(report, StudentReport)

    def test_create_course_report(self, course: Course) -> None:
        report = ReportGenerator.create_report("course", courses=[course])
        assert isinstance(report, CourseReport)

    def test_create_enrollment_report(
        self, undergrad: UndergraduateStudent, course: Course
    ) -> None:
        report = ReportGenerator.create_report(
            "enrollment", students=[undergrad], courses=[course]
        )
        assert isinstance(report, EnrollmentReport)

    def test_invalid_type_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown report type"):
            ReportGenerator.create_report("invalid")

    def test_create_defaults_to_empty_lists(self) -> None:
        report = ReportGenerator.create_report("student")
        assert isinstance(report, StudentReport)
        assert report.get_data() == []
