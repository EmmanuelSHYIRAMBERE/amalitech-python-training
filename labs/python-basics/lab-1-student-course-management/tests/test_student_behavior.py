"""Tests for student type strings, dunder methods, and graduate-specific logic."""

import pytest

from src.models.student import GraduateStudent, UndergraduateStudent


class TestStudentType:
    def test_undergrad_type_string(self, undergrad):
        assert "Undergraduate" in undergrad.get_student_type()
        assert "2" in undergrad.get_student_type()

    def test_grad_type_with_topic(self, grad):
        assert "Graduate" in grad.get_student_type()
        assert "Machine Learning" in grad.get_student_type()

    def test_grad_type_without_topic(self):
        s = GraduateStudent("S099", "No Topic", "nt@example.com")
        assert s.get_student_type() == "Graduate"

    def test_international_type_string(self, international):
        assert "Spain" in international.get_student_type()


class TestDunderMethods:
    def test_equality_same_id(self):
        s1 = UndergraduateStudent("S001", "Alice", "a@example.com", 1)
        s2 = UndergraduateStudent("S001", "Different Name", "b@example.com", 2)
        assert s1 == s2

    def test_inequality_different_id(self, undergrad, grad):
        assert undergrad != grad

    def test_hash_consistency(self, undergrad):
        assert hash(undergrad) == hash(undergrad)

    def test_equal_students_same_hash(self):
        s1 = UndergraduateStudent("S001", "Alice", "a@example.com", 1)
        s2 = UndergraduateStudent("S001", "Alice", "a@example.com", 1)
        assert hash(s1) == hash(s2)

    def test_students_usable_in_set(self, undergrad, grad):
        student_set = {undergrad, grad}
        assert len(student_set) == 2

    def test_str_contains_name_and_id(self, undergrad):
        s = str(undergrad)
        assert "Alice Johnson" in s
        assert "S001" in s

    def test_repr(self, undergrad):
        r = repr(undergrad)
        assert "UndergraduateStudent" in r
        assert "S001" in r


class TestGraduateSpecific:
    def test_thesis_complete(self, grad):
        assert grad.is_thesis_complete(6) is True
        assert grad.is_thesis_complete(5) is False

    def test_can_graduate_undergrad(self):
        s = UndergraduateStudent("S050", "Senior", "s@example.com", 4)
        for i in range(8):
            s.enroll_course(f"C{i:03d}")
        assert s.can_graduate() is True

    def test_cannot_graduate_too_few_courses(self):
        s = UndergraduateStudent("S051", "Junior", "j@example.com", 4)
        s.enroll_course("CS101")
        assert s.can_graduate() is False

    def test_cannot_graduate_wrong_year(self):
        s = UndergraduateStudent("S052", "Sophomore", "so@example.com", 2)
        for i in range(8):
            s.enroll_course(f"C{i:03d}")
        assert s.can_graduate() is False
