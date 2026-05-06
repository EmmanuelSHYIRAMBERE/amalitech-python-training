"""Tests for student property setters."""

import pytest
from src.models.student import GraduateStudent, UndergraduateStudent


class TestStudentSetters:
    def test_update_name(self, undergrad: UndergraduateStudent) -> None:
        undergrad.name = "Alice Smith"
        assert undergrad.name == "Alice Smith"

    def test_update_email(self, undergrad: UndergraduateStudent) -> None:
        undergrad.email = "new@example.com"
        assert undergrad.email == "new@example.com"

    def test_update_year(self, undergrad: UndergraduateStudent) -> None:
        undergrad.year = 4
        assert undergrad.year == 4

    def test_update_year_invalid(self, undergrad: UndergraduateStudent) -> None:
        with pytest.raises(ValueError):
            undergrad.year = 5

    def test_update_research_topic(self, grad: GraduateStudent) -> None:
        grad.research_topic = "Deep Learning"
        assert grad.research_topic == "Deep Learning"

    def test_set_advisor(self, grad: GraduateStudent) -> None:
        grad.advisor = "Dr. Smith"
        assert grad.advisor == "Dr. Smith"
