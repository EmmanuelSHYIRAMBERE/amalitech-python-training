"""Tests for student creation and constructor validation."""

import pytest
from src.models.student import (
    GraduateStudent,
    InternationalStudent,
    UndergraduateStudent,
)


class TestStudentCreation:
    def test_undergraduate_attributes(self, undergrad):
        assert undergrad.student_id == "S001"
        assert undergrad.name == "Alice Johnson"
        assert undergrad.email == "alice@example.com"
        assert undergrad.year == 2

    def test_graduate_attributes(self, grad):
        assert grad.student_id == "S002"
        assert grad.research_topic == "Machine Learning"
        assert grad.advisor is None

    def test_international_attributes(self, international):
        assert international.country == "Spain"
        assert international.year == 3

    def test_student_id_stripped(self):
        s = UndergraduateStudent("  S010  ", "Test User", "t@example.com", 1)
        assert s.student_id == "S010"

    def test_name_stripped(self):
        s = UndergraduateStudent("S011", "  Jane Doe  ", "j@example.com", 1)
        assert s.name == "Jane Doe"

    @pytest.mark.parametrize("bad_id", ["", "   "])
    def test_empty_student_id_raises(self, bad_id):
        with pytest.raises(ValueError, match="student_id"):
            UndergraduateStudent(bad_id, "Name", "n@example.com", 1)

    @pytest.mark.parametrize("bad_name", ["", " ", "A"])
    def test_short_name_raises(self, bad_name):
        with pytest.raises(ValueError, match="Name"):
            UndergraduateStudent("S020", bad_name, "n@example.com", 1)

    @pytest.mark.parametrize("bad_email", ["notanemail", "missing@", "@nodomain", ""])
    def test_invalid_email_raises(self, bad_email):
        with pytest.raises(ValueError, match="[Ii]nvalid email"):
            UndergraduateStudent("S021", "Valid Name", bad_email, 1)

    @pytest.mark.parametrize("bad_year", [0, 5, -1])
    def test_invalid_year_raises(self, bad_year):
        with pytest.raises(ValueError, match="Year"):
            UndergraduateStudent("S022", "Valid Name", "v@example.com", bad_year)

    def test_graduate_no_topic_defaults(self):
        s = GraduateStudent("S030", "No Topic", "nt@example.com")
        assert s.research_topic == ""
        assert s.advisor is None

    def test_graduate_with_topic(self):
        s = GraduateStudent("S031", "With Topic", "wt@example.com", "AI")
        assert s.research_topic == "AI"

    def test_invalid_country_raises(self):
        with pytest.raises(ValueError, match="Country"):
            InternationalStudent("S023", "Valid Name", "v@example.com", "A", 1)
