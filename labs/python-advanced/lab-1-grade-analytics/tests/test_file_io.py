"""Tests for file I/O utilities."""

import json
from pathlib import Path

import pytest

from src.file_io import read_students_csv, write_report_json


def test_read_students_csv(tmp_path: Path):
    csv_content = (
        "student_id,name,major,year,course_id,score,semester\n"
        "S1,Alice,CS,2,C1,90,2024-S1\n"
        "S1,Alice,CS,2,C2,80,2024-S1\n"
        "S2,Bob,Math,3,C1,70,2024-S1\n"
    )
    csv_file = tmp_path / "students.csv"
    csv_file.write_text(csv_content)

    students = read_students_csv(csv_file)
    assert len(students) == 2
    alice = next(s for s in students if s.student_id == "S1")
    assert len(alice.grades) == 2
    assert alice.gpa() == 85.0


def test_read_students_csv_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_students_csv(Path("nonexistent.csv"))


def test_read_students_csv_invalid_data(tmp_path: Path):
    csv_content = (
        "student_id,name,major,year,course_id,score,semester\n"
        "S1,Alice,CS,two,C1,notanumber,2024-S1\n"
    )
    csv_file = tmp_path / "bad.csv"
    csv_file.write_text(csv_content)
    with pytest.raises(ValueError):
        read_students_csv(csv_file)


def test_write_report_json(tmp_path: Path):
    report = {"total_students": 5, "overall_average": 82.5}
    out = tmp_path / "reports" / "report.json"
    write_report_json(report, out)
    assert out.exists()
    with open(out) as f:
        loaded = json.load(f)
    assert loaded["total_students"] == 5


def test_read_sample_csv():
    """Integration test against the real sample_data/students.csv."""
    csv_path = Path("sample_data/students.csv")
    if not csv_path.exists():
        pytest.skip("sample_data/students.csv not found")
    students = read_students_csv(csv_path)
    assert len(students) == 10
