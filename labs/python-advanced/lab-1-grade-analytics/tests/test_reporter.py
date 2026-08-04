"""Tests for reporter and remaining file_io paths."""

from pathlib import Path

import pytest

from src.file_io import stream_students_csv
from src.models import Grade, Student
from src.reporter import build_report, generate_and_save


def _students() -> list[Student]:
    return [
        Student(
            "S1", "Alice", "CS", 2,
            [Grade("C1", 90, "S1"), Grade("C2", 80, "S2")],
        ),
        Student(
            "S2", "Bob", "Math", 3,
            [Grade("C1", 70, "S1"), Grade("C2", 60, "S2")],
        ),
    ]


def test_build_report_keys():
    report = build_report(_students(), ["S1", "S2"])
    assert "generated_at" in report
    assert "total_students" in report
    assert "overall_average" in report
    assert "grade_distribution" in report
    assert "top_performers" in report
    assert "by_major" in report
    assert "by_year" in report
    assert "semester_trends" in report


def test_build_report_values():
    report = build_report(_students(), ["S1", "S2"])
    assert report["total_students"] == 2
    assert report["overall_average"] == 75.0


def test_generate_and_save(tmp_path: Path):
    out = tmp_path / "reports" / "report.json"
    report = generate_and_save(_students(), ["S1", "S2"], out)
    assert out.exists()
    assert report["total_students"] == 2


def test_stream_students_csv(tmp_path: Path):
    csv_content = (
        "student_id,name,major,year,course_id,score,semester\n"
        "S1,Alice,CS,2,C1,90,2024-S1\n"
        "S2,Bob,Math,3,C1,70,2024-S1\n"
    )
    csv_file = tmp_path / "students.csv"
    csv_file.write_text(csv_content)
    students = list(stream_students_csv(csv_file))
    assert len(students) == 2
