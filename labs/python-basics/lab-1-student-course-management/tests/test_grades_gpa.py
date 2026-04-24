"""Tests for grade recording and GPA calculation."""

import pytest


class TestGradesAndGPA:
    def test_gpa_no_grades(self, undergrad):
        assert undergrad.calculate_gpa() == 0.0

    def test_gpa_single_grade(self, undergrad):
        undergrad.add_grade("CS101", 3.5)
        assert undergrad.calculate_gpa() == pytest.approx(3.5)

    def test_gpa_multiple_courses(self, undergrad):
        undergrad.add_grade("CS101", 3.5)
        undergrad.add_grade("CS101", 4.0)
        undergrad.add_grade("MATH101", 3.0)
        # (3.5 + 4.0 + 3.0) / 3 = 3.5
        assert undergrad.calculate_gpa() == pytest.approx(3.5, abs=1e-9)

    @pytest.mark.parametrize("grade", [-0.1, 4.1, 5.0])
    def test_invalid_grade_raises(self, undergrad, grade):
        with pytest.raises(ValueError, match="Grade"):
            undergrad.add_grade("CS101", grade)

    @pytest.mark.parametrize("grade", [0.0, 2.0, 4.0])
    def test_boundary_grades_accepted(self, undergrad, grade):
        undergrad.add_grade("CS101", grade)  # should not raise
