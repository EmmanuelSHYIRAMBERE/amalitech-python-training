"""Tests for GradeAggregator collections."""

from src.aggregator import GradeAggregator
from src.models import Grade, Student


def _make_students() -> list[Student]:
    return [
        Student(
            "S1", "Alice", "CS", 2,
            [Grade("C1", 95, "S1"), Grade("C2", 88, "S1")],
        ),
        Student(
            "S2", "Bob", "Math", 3,
            [Grade("C1", 72, "S1"), Grade("C2", 65, "S1")],
        ),
        Student(
            "S3", "Claire", "CS", 1,
            [Grade("C1", 55, "S1")],
        ),
    ]


def test_grade_distribution_keys_ordered():
    agg = GradeAggregator()
    agg.ingest(_make_students())
    dist = agg.grade_distribution()
    assert list(dist.keys()) == ["A", "B", "C", "D", "F"]


def test_grade_distribution_counts():
    agg = GradeAggregator()
    agg.ingest(_make_students())
    dist = agg.grade_distribution()
    assert dist["A"] == 1
    assert dist["B"] == 1
    assert dist["C"] == 1
    assert dist["D"] == 1
    assert dist["F"] == 1


def test_average_gpa_by_major():
    agg = GradeAggregator()
    students = _make_students()
    agg.ingest(students)
    by_major = agg.average_gpa_by_major()
    assert "CS" in by_major
    assert "Math" in by_major


def test_average_gpa_by_year():
    agg = GradeAggregator()
    agg.ingest(_make_students())
    by_year = agg.average_gpa_by_year()
    assert "2" in by_year
    assert "3" in by_year


def test_rolling_average():
    agg = GradeAggregator(rolling_window_size=2)
    agg.ingest(_make_students())
    assert agg.rolling_average() > 0.0


def test_top_n():
    agg = GradeAggregator()
    students = _make_students()
    agg.ingest(students)
    top = agg.top_n(students, n=2)
    assert len(top) == 2
    assert top[0]["name"] == "Alice"


def test_empty_aggregator():
    agg = GradeAggregator()
    assert agg.rolling_average() == 0.0
    assert agg.grade_distribution()["A"] == 0
