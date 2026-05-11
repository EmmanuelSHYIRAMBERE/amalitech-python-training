"""Tests for src/utils/helpers.py."""

import pytest
from src.utils.helpers import (
    calculate_grade_percentage,
    create_menu,
    filter_students_by_course,
    flexible_summary,
    get_user_input,
    safe_divide,
)


class TestCalculateGradePercentage:
    def test_normal_case(self) -> None:
        assert calculate_grade_percentage(80, 100) == pytest.approx(80.0)

    def test_perfect_score(self) -> None:
        assert calculate_grade_percentage(100, 100) == pytest.approx(100.0)

    def test_zero_total_returns_zero(self) -> None:
        assert calculate_grade_percentage(50, 0) == 0


class TestFilterStudentsByCourse:
    def test_returns_matching_students(self) -> None:
        students = {"S001": {"name": "Alice"}, "S002": {"name": "Bob"}}
        enrollments = {"S001": ["CS101"], "S002": ["CS201"]}
        result = filter_students_by_course(students, "CS101", enrollments)
        assert result == ["Alice"]

    def test_no_match_returns_empty(self) -> None:
        students = {"S001": {"name": "Alice"}}
        enrollments = {"S001": ["CS201"]}
        result = filter_students_by_course(students, "CS101", enrollments)
        assert result == []


class TestCreateMenu:
    def test_prints_all_options(self, capsys: pytest.CaptureFixture[str]) -> None:
        create_menu(["Option A", "Option B"])
        out = capsys.readouterr().out
        assert "Option A" in out
        assert "Option B" in out

    def test_options_are_numbered(self, capsys: pytest.CaptureFixture[str]) -> None:
        create_menu(["First", "Second"])
        out = capsys.readouterr().out
        assert "1." in out
        assert "2." in out

    def test_exit_option_shown(self, capsys: pytest.CaptureFixture[str]) -> None:
        create_menu(["Option"])
        out = capsys.readouterr().out
        assert "0." in out


class TestGetUserInput:
    def test_returns_valid_input_immediately(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "hello")
        assert get_user_input("prompt: ") == "hello"

    def test_strips_surrounding_whitespace(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "  hello  ")
        assert get_user_input("prompt: ") == "hello"

    def test_retries_until_valid(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        responses = iter(["bad", "good"])
        monkeypatch.setattr("builtins.input", lambda _: next(responses))
        result = get_user_input("prompt: ", validator=lambda x: x == "good")
        assert result == "good"
        assert "Invalid" in capsys.readouterr().out

    def test_no_validator_accepts_anything(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "anything")
        assert get_user_input("prompt: ") == "anything"


class TestSafeDivide:
    def test_normal_division(self) -> None:
        assert safe_divide(10.0, 2.0) == pytest.approx(5.0)

    def test_zero_denominator_returns_default(self) -> None:
        assert safe_divide(1.0, 0.0) == pytest.approx(0.0)

    def test_custom_default_on_zero(self) -> None:
        assert safe_divide(1.0, 0.0, default=99.0) == pytest.approx(99.0)


class TestFlexibleSummary:
    def test_student_count(self) -> None:
        result = flexible_summary("Alice", "Bob")
        assert result["students_count"] == 2

    def test_students_list(self) -> None:
        result = flexible_summary("Alice", "Bob")
        assert "Alice" in result["students"]

    def test_summary_type_from_kwargs(self) -> None:
        result = flexible_summary(type="enrollment")
        assert result["summary_type"] == "enrollment"

    def test_additional_info_from_kwargs(self) -> None:
        result = flexible_summary(info="Test info")
        assert result["additional_info"] == "Test info"

    def test_defaults_with_no_args(self) -> None:
        result = flexible_summary()
        assert result["students_count"] == 0
        assert result["summary_type"] == "basic"
        assert result["additional_info"] == "No additional info"

    def test_generated_at_present(self) -> None:
        result = flexible_summary()
        assert "generated_at" in result
