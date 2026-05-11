"""Tests for tuition calculation per student type."""

import pytest
from src.models.student import (
    GraduateStudent,
    InternationalStudent,
    UndergraduateStudent,
)


class TestTuition:
    def test_undergrad_tuition_no_courses(
        self, undergrad: UndergraduateStudent
    ) -> None:
        assert undergrad.calculate_tuition() == UndergraduateStudent.TUITION_BASE

    def test_undergrad_tuition_with_courses(
        self, undergrad: UndergraduateStudent
    ) -> None:
        undergrad.enroll_course("CS101")
        undergrad.enroll_course("CS201")
        expected = (
            UndergraduateStudent.TUITION_BASE
            + 2 * UndergraduateStudent.TUITION_PER_COURSE
        )
        assert undergrad.calculate_tuition() == pytest.approx(expected)

    def test_grad_tuition_no_advisor(self, grad: GraduateStudent) -> None:
        expected = GraduateStudent.TUITION_BASE + GraduateStudent.RESEARCH_FEE
        assert grad.calculate_tuition() == pytest.approx(expected)

    def test_grad_tuition_with_advisor(self, grad: GraduateStudent) -> None:
        grad.advisor = "Dr. Smith"
        expected = (
            GraduateStudent.TUITION_BASE
            + GraduateStudent.RESEARCH_FEE
            + GraduateStudent.ADVISOR_FEE
        )
        assert grad.calculate_tuition() == pytest.approx(expected)

    def test_international_tuition_includes_surcharge(
        self, international: InternationalStudent
    ) -> None:
        base = (
            UndergraduateStudent.TUITION_BASE
            + len(international.get_enrolled_courses())
            * UndergraduateStudent.TUITION_PER_COURSE
        )
        expected = base + InternationalStudent.INTERNATIONAL_FEE
        assert international.calculate_tuition() == pytest.approx(expected)
