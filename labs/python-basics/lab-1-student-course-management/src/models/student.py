"""Student class and specialized student types."""

import logging
from abc import ABC, abstractmethod
from datetime import datetime

from src.utils.helpers import validate_email

logger = logging.getLogger(__name__)


class Student(ABC):
    """Abstract base class for all student types.

    Subclasses must implement :meth:`calculate_tuition` and
    :meth:`get_student_type`.
    """

    def __init__(self, student_id: str, name: str, email: str) -> None:
        """Initialise a student.

        Args:
            student_id: Unique identifier for the student.
            name: Full name (minimum 2 characters).
            email: Valid email address.

        Raises:
            ValueError: If name or email fails validation.
        """
        if not student_id or not student_id.strip():
            raise ValueError("student_id must not be empty")
        self._student_id = student_id.strip()
        self._name = ""
        self._email = ""
        self.name = name  # use setter for validation
        self.email = email  # use setter for validation
        self._enrolled_courses: list[str] = []
        self._grades: dict[str, list[float]] = {}
        self._enrollment_date: datetime = datetime.now()
        logger.debug("Created %s id=%s", self.__class__.__name__, self._student_id)

    # ------------------------------------------------------------------ #
    # Properties                                                           #
    # ------------------------------------------------------------------ #

    @property
    def student_id(self) -> str:
        """Unique student identifier (read-only)."""
        return self._student_id

    @property
    def name(self) -> str:
        """Full name of the student."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set student name.

        Args:
            value: New name (minimum 2 non-whitespace characters).

        Raises:
            ValueError: If value is too short.
        """
        if not value or len(value.strip()) < 2:
            raise ValueError("Name must be at least 2 characters long")
        self._name = value.strip()

    @property
    def email(self) -> str:
        """Email address of the student."""
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        """Set student email.

        Args:
            value: New email address.

        Raises:
            ValueError: If value is not a valid email format.
        """
        if not validate_email(value):
            raise ValueError(f"Invalid email format: {value!r}")
        self._email = value

    @property
    def enrollment_date(self) -> datetime:
        """Date and time the student record was created (read-only)."""
        return self._enrollment_date

    # ------------------------------------------------------------------ #
    # Abstract interface                                                   #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def calculate_tuition(self) -> float:
        """Return the tuition amount for this student type.

        Returns:
            Tuition in USD as a float.
        """

    @abstractmethod
    def get_student_type(self) -> str:
        """Return a human-readable description of the student type.

        Returns:
            A descriptive string, e.g. ``"Undergraduate (Year 2)"``.
        """

    # ------------------------------------------------------------------ #
    # Public methods                                                       #
    # ------------------------------------------------------------------ #

    def enroll_course(self, course_code: str) -> bool:
        """Enroll this student in a course.

        Args:
            course_code: The course identifier to enrol in.

        Returns:
            ``True`` if newly enrolled, ``False`` if already enrolled.
        """
        if course_code in self._enrolled_courses:
            logger.debug(
                "Student %s already enrolled in %s", self._student_id, course_code
            )
            return False
        self._enrolled_courses.append(course_code)
        logger.info("Student %s enrolled in course %s", self._student_id, course_code)
        return True

    def drop_course(self, course_code: str) -> bool:
        """Remove this student from a course.

        Args:
            course_code: The course identifier to drop.

        Returns:
            ``True`` if dropped, ``False`` if not enrolled.
        """
        if course_code not in self._enrolled_courses:
            return False
        self._enrolled_courses.remove(course_code)
        logger.info("Student %s dropped course %s", self._student_id, course_code)
        return True

    def add_grade(self, course_code: str, grade: float) -> None:
        """Record a grade for a course.

        Args:
            course_code: The course the grade belongs to.
            grade: Grade value on a 0.0–4.0 scale.

        Raises:
            ValueError: If grade is outside the 0.0–4.0 range.
        """
        if not (0.0 <= grade <= 4.0):
            raise ValueError(f"Grade must be between 0.0 and 4.0, got {grade}")
        self._grades.setdefault(course_code, []).append(grade)
        logger.debug(
            "Added grade %.2f for student %s in %s",
            grade,
            self._student_id,
            course_code,
        )

    def calculate_gpa(self) -> float:
        """Calculate GPA as the mean of all recorded grades.

        Returns:
            GPA on a 4.0 scale, or ``0.0`` if no grades exist.
        """
        all_grades = [g for grades in self._grades.values() for g in grades]
        if not all_grades:
            return 0.0
        return sum(all_grades) / len(all_grades)

    def get_enrolled_courses(self) -> list[str]:
        """Return a copy of the enrolled course codes.

        Returns:
            List of course code strings.
        """
        return self._enrolled_courses.copy()

    # ------------------------------------------------------------------ #
    # Dunder methods                                                       #
    # ------------------------------------------------------------------ #

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(id={self._student_id!r}, name={self._name!r})"
        )

    def __str__(self) -> str:
        return f"{self.get_student_type()}: {self._name} ({self._student_id})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Student):
            return NotImplemented
        return self._student_id == other._student_id

    def __hash__(self) -> int:
        # Required because __eq__ is defined; students are uniquely identified by ID.
        return hash(self._student_id)

    def __lt__(self, other: "Student") -> bool:
        return self._name < other._name


# --------------------------------------------------------------------------- #
# Concrete student types                                                        #
# --------------------------------------------------------------------------- #


class UndergraduateStudent(Student):
    """Undergraduate student with a year level (1–4)."""

    TUITION_BASE: float = 500.0
    TUITION_PER_COURSE: float = 300.0

    def __init__(self, student_id: str, name: str, email: str, year: int = 1) -> None:
        """Initialise an undergraduate student.

        Args:
            student_id: Unique identifier.
            name: Full name.
            email: Valid email address.
            year: Year of study (1–4). Defaults to 1.

        Raises:
            ValueError: If year is outside 1–4.
        """
        super().__init__(student_id, name, email)
        self._year = 0
        self.year = year  # use setter for validation

    @property
    def year(self) -> int:
        """Current year of study (1–4)."""
        return self._year

    @year.setter
    def year(self, value: int) -> None:
        """Set year of study.

        Raises:
            ValueError: If value is not between 1 and 4.
        """
        if not (1 <= value <= 4):
            raise ValueError(f"Year must be between 1 and 4, got {value}")
        self._year = value

    def calculate_tuition(self) -> float:
        """Return tuition: base fee plus per-course fee.

        Returns:
            Total tuition in USD.
        """
        return self.TUITION_BASE + len(self._enrolled_courses) * self.TUITION_PER_COURSE

    def get_student_type(self) -> str:
        return f"Undergraduate (Year {self._year})"

    def can_graduate(self) -> bool:
        """Return ``True`` if the student meets graduation requirements.

        Requirements: year 4 and at least 8 enrolled courses.
        """
        return self._year >= 4 and len(self._enrolled_courses) >= 8


class GraduateStudent(Student):
    """Graduate student with an optional research topic and advisor."""

    TUITION_BASE: float = 800.0
    RESEARCH_FEE: float = 500.0
    ADVISOR_FEE: float = 200.0
    THESIS_CREDITS: int = 6

    def __init__(
        self,
        student_id: str,
        name: str,
        email: str,
        research_topic: str = "",
    ) -> None:
        """Initialise a graduate student.

        Args:
            student_id: Unique identifier.
            name: Full name.
            email: Valid email address.
            research_topic: Optional research topic description.
        """
        super().__init__(student_id, name, email)
        self._research_topic: str = research_topic
        self._advisor: str | None = None

    @property
    def research_topic(self) -> str:
        """Research topic for this graduate student."""
        return self._research_topic

    @research_topic.setter
    def research_topic(self, topic: str) -> None:
        self._research_topic = topic

    @property
    def advisor(self) -> str | None:
        """Name of the assigned advisor, or ``None`` if unassigned."""
        return self._advisor

    @advisor.setter
    def advisor(self, advisor_name: str) -> None:
        self._advisor = advisor_name

    def calculate_tuition(self) -> float:
        """Return tuition: base + research fee + optional advisor fee.

        Returns:
            Total tuition in USD.
        """
        tuition = self.TUITION_BASE + self.RESEARCH_FEE
        if self._advisor:
            tuition += self.ADVISOR_FEE
        return tuition

    def get_student_type(self) -> str:
        suffix = f" (Research: {self._research_topic})" if self._research_topic else ""
        return f"Graduate{suffix}"

    def is_thesis_complete(self, credits_completed: int) -> bool:
        """Return ``True`` if thesis credit requirement is met.

        Args:
            credits_completed: Number of thesis credits completed.
        """
        return credits_completed >= self.THESIS_CREDITS


class InternationalStudent(UndergraduateStudent):
    """Undergraduate student from outside the country, with an extra fee."""

    INTERNATIONAL_FEE: float = 1000.0

    def __init__(
        self,
        student_id: str,
        name: str,
        email: str,
        country: str,
        year: int = 1,
    ) -> None:
        """Initialise an international student.

        Args:
            student_id: Unique identifier.
            name: Full name.
            email: Valid email address.
            country: Country of origin (minimum 2 characters).
            year: Year of study (1–4). Defaults to 1.

        Raises:
            ValueError: If country name is too short.
        """
        if not country or len(country.strip()) < 2:
            raise ValueError("Country name must be at least 2 characters long")
        super().__init__(student_id, name, email, year)
        self._country: str = country.strip()

    @property
    def country(self) -> str:
        """Country of origin (read-only)."""
        return self._country

    def calculate_tuition(self) -> float:
        """Return tuition including the international surcharge.

        Returns:
            Total tuition in USD.
        """
        return super().calculate_tuition() + self.INTERNATIONAL_FEE

    def get_student_type(self) -> str:
        return f"International Student from {self._country}"
