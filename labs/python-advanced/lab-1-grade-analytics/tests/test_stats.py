"""Tests for statistical functions."""

from src.models import Grade, Student
from src.stats import mean, median, mode, percentile_rank, semester_trends, summary_stats


def test_mean():
    assert mean([80, 90, 100]) == 90.0
    assert mean([]) == 0.0


def test_median_odd():
    assert median([70, 80, 90]) == 80.0


def test_median_even():
    assert median([70, 80, 90, 100]) == 85.0


def test_median_empty():
    assert median([]) == 0.0


def test_mode():
    assert mode([80, 90, 80, 70]) == 80.0
    assert mode([]) == 0.0


def test_percentile_rank():
    scores = [60, 70, 80, 90, 100]
    assert percentile_rank(scores, 80) == 40.0
    assert percentile_rank([], 80) == 0.0


def test_semester_trends():
    students = [
        Student("S1", "Alice", "CS", 2, [Grade("C1", 90, "S1"), Grade("C2", 80, "S2")]),
        Student("S2", "Bob", "Math", 3, [Grade("C1", 70, "S1"), Grade("C2", 60, "S2")]),
    ]
    trends = semester_trends(students, ["S1", "S2"])
    assert trends["S1"] == 80.0
    assert trends["S2"] == 70.0


def test_summary_stats():
    students = [
        Student("S1", "Alice", "CS", 2, [Grade("C1", 80, "S1"), Grade("C2", 90, "S1")]),
    ]
    stats = summary_stats(students)
    assert stats["mean"] == 85.0
    assert stats["total_scores"] == 2
