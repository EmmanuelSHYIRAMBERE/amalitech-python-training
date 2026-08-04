"""Collection-based aggregators for grade data processing."""

from collections import Counter, OrderedDict, defaultdict, deque
from typing import Union

from src.models import Student


class GradeAggregator:
    """Aggregates grade data using advanced collections.

    Attributes:
        _grade_counter: Counter tracking letter grade frequencies.
        _by_major: defaultdict grouping student GPAs by major.
        _by_year: defaultdict grouping student GPAs by year.
        _rolling_window: deque for rolling average calculation.
    """

    def __init__(self, rolling_window_size: int = 5) -> None:
        """Initialise aggregator with empty collections.

        Args:
            rolling_window_size: Max size of the rolling average deque.
        """
        self._grade_counter: Counter[str] = Counter()
        self._by_major: defaultdict[str, list[float]] = defaultdict(list)
        self._by_year: defaultdict[str, list[float]] = defaultdict(list)
        self._rolling_window: deque[float] = deque(maxlen=rolling_window_size)

    def ingest(self, students: list[Student]) -> None:
        """Process a list of students into all internal collections.

        Args:
            students: List of Student objects to aggregate.
        """
        for student in students:
            for grade in student.grades:
                self._grade_counter[grade.letter()] += 1
            gpa = student.gpa()
            if gpa is not None:
                self._by_major[student.major].append(gpa)
                self._by_year[str(student.year)].append(gpa)
                self._rolling_window.append(gpa)

    def grade_distribution(self) -> OrderedDict[str, int]:
        """Return letter grade counts in A to F order.

        Returns:
            OrderedDict mapping letter grade to count.
        """
        ordered: OrderedDict[str, int] = OrderedDict()
        for letter in ["A", "B", "C", "D", "F"]:
            ordered[letter] = self._grade_counter.get(letter, 0)
        return ordered

    def average_gpa_by_major(self) -> dict[str, float]:
        """Return average GPA per major.

        Returns:
            Dict mapping major name to average GPA.
        """
        return {
            major: round(sum(gpas) / len(gpas), 2)
            for major, gpas in self._by_major.items()
        }

    def average_gpa_by_year(self) -> dict[str, float]:
        """Return average GPA per academic year.

        Returns:
            Dict mapping year string to average GPA.
        """
        return {
            year: round(sum(gpas) / len(gpas), 2)
            for year, gpas in self._by_year.items()
        }

    def rolling_average(self) -> float:
        """Return the rolling average of the last N student GPAs.

        Returns:
            Rolling average as float, or 0.0 if no data.
        """
        if not self._rolling_window:
            return 0.0
        return round(sum(self._rolling_window) / len(self._rolling_window), 2)

    def top_n(
        self, students: list[Student], n: int = 5
    ) -> list[dict[str, Union[str, float]]]:
        """Return the top N students by GPA.

        Args:
            students: Full list of Student objects.
            n: Number of top students to return.

        Returns:
            List of dicts with student_id, name, and gpa keys.
        """
        ranked = sorted(
            [s for s in students if s.gpa() is not None],
            key=lambda s: s.gpa(),  # type: ignore[arg-type, return-value]
            reverse=True,
        )
        return [
            {"student_id": s.student_id, "name": s.name, "gpa": s.gpa()}
            for s in ranked[:n]
        ]
