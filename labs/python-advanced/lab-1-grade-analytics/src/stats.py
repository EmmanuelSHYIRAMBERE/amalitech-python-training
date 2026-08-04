"""Statistical processing for grade analytics."""

from collections import Counter, deque
from typing import Union

from src.models import Student


def mean(values: list[float]) -> float:
    """Calculate arithmetic mean.

    Args:
        values: List of numeric values.

    Returns:
        Mean as float, or 0.0 if empty.
    """
    if not values:
        return 0.0
    return round(sum(values) / len(values), 2)


def median(values: list[float]) -> float:
    """Calculate median value.

    Args:
        values: List of numeric values.

    Returns:
        Median as float, or 0.0 if empty.
    """
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    mid = len(sorted_vals) // 2
    if len(sorted_vals) % 2 == 0:
        return round((sorted_vals[mid - 1] + sorted_vals[mid]) / 2, 2)
    return round(sorted_vals[mid], 2)


def mode(values: list[float]) -> float:
    """Calculate mode using Counter.

    Args:
        values: List of numeric values.

    Returns:
        Most common value, or 0.0 if empty.
    """
    if not values:
        return 0.0
    counter: Counter[float] = Counter(values)
    return counter.most_common(1)[0][0]


def percentile_rank(values: list[float], score: float) -> float:
    """Compute the percentile rank of a score within a list.

    Args:
        values: List of all scores.
        score: The score to rank.

    Returns:
        Percentile rank as float (0-100).
    """
    if not values:
        return 0.0
    below = sum(1 for v in values if v < score)
    return round((below / len(values)) * 100, 2)


def semester_trends(
    students: list[Student], semesters: list[str]
) -> dict[str, float]:
    """Track average GPA per semester using a deque for rolling context.

    Args:
        students: List of Student objects.
        semesters: Ordered list of semester labels to track.

    Returns:
        Dict mapping semester label to average GPA for that semester.
    """
    trend_deque: deque[tuple[str, float]] = deque()
    for semester in semesters:
        scores: list[float] = []
        for student in students:
            gpa = student.gpa_for_semester(semester)
            if gpa is not None:
                scores.append(gpa)
        avg = mean(scores) if scores else 0.0
        trend_deque.append((semester, avg))
    return dict(trend_deque)


def all_scores(students: list[Student]) -> list[float]:
    """Flatten all scores from all students into a single list.

    Args:
        students: List of Student objects.

    Returns:
        Flat list of all numeric scores.
    """
    return [g.score for s in students for g in s.grades]


def summary_stats(
    students: list[Student],
) -> dict[str, Union[float, int]]:
    """Generate overall summary statistics.

    Args:
        students: List of Student objects.

    Returns:
        Dict with mean, median, mode, and total_scores keys.
    """
    scores = all_scores(students)
    return {
        "mean": mean(scores),
        "median": median(scores),
        "mode": mode(scores),
        "total_scores": len(scores),
    }
