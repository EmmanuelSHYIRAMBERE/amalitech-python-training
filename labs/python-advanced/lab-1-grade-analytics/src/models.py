"""Data models for the Student Grade Analytics Tool."""

from collections import namedtuple
from dataclasses import dataclass, field
from typing import Optional, TypedDict

SemesterRecord = namedtuple("SemesterRecord", ["semester", "gpa"])


@dataclass
class Grade:
    """A single grade entry for a student in a course.

    Attributes:
        course_id: Unique identifier for the course.
        score: Numeric score (0-100).
        semester: Semester label e.g. '2024-S1'.
    """

    course_id: str
    score: float
    semester: str

    def letter(self) -> str:
        """Return the letter grade for this score.

        Returns:
            Letter grade: A, B, C, D, or F.
        """
        if self.score >= 90:
            return "A"
        if self.score >= 80:
            return "B"
        if self.score >= 70:
            return "C"
        if self.score >= 60:
            return "D"
        return "F"


@dataclass
class Course:
    """Represents a course.

    Attributes:
        course_id: Unique course identifier.
        name: Human-readable course name.
        credits: Credit hours for the course.
    """

    course_id: str
    name: str
    credits: int = 3


@dataclass
class Student:
    """Represents a student with their grades.

    Attributes:
        student_id: Unique student identifier.
        name: Full name of the student.
        major: Student's declared major.
        year: Academic year (1-4).
        grades: List of Grade entries.
    """

    student_id: str
    name: str
    major: str
    year: int
    grades: list[Grade] = field(default_factory=list)

    def gpa(self) -> Optional[float]:
        """Calculate GPA as a simple average of all scores.

        Returns:
            Average score as float, or None if no grades exist.
        """
        if not self.grades:
            return None
        return round(sum(g.score for g in self.grades) / len(self.grades), 2)

    def gpa_for_semester(self, semester: str) -> Optional[float]:
        """Calculate GPA for a specific semester.

        Args:
            semester: Semester label to filter by.

        Returns:
            Average score for the semester, or None if no grades found.
        """
        sem_grades = [g.score for g in self.grades if g.semester == semester]
        if not sem_grades:
            return None
        return round(sum(sem_grades) / len(sem_grades), 2)


class ReportDict(TypedDict):
    """TypedDict schema for the JSON report output."""

    generated_at: str
    total_students: int
    overall_average: float
    grade_distribution: dict[str, int]
    top_performers: list[dict[str, object]]
    by_major: dict[str, float]
    by_year: dict[str, float]
    semester_trends: dict[str, float]
