"""Course class definition."""

import logging
from datetime import datetime

from src.models.student import Student

logger = logging.getLogger(__name__)


class Course:
    """Represents an academic course with enrollment management."""

    def __init__(
        self,
        course_code: str,
        name: str,
        credits: int,
        instructor: str,
        max_students: int = 30,
    ) -> None:
        """Initialise a course.

        Args:
            course_code: Unique course identifier (e.g. ``"CS101"``).
            name: Course name (minimum 3 characters).
            credits: Credit hours (1–6).
            instructor: Name of the instructor.
            max_students: Maximum enrollment capacity. Defaults to 30.

        Raises:
            ValueError: If name or credits fail validation.
        """
        if not course_code or not course_code.strip():
            raise ValueError("course_code must not be empty")
        self._course_code: str = course_code.strip()
        self._name: str = ""
        self._credits: int = 0
        self._instructor: str = instructor
        self._max_students: int = max(1, max_students)
        self._enrolled_students: list[Student] = []
        self._schedule: dict[str, str] = {}
        self._created_at: datetime = datetime.now()

        # Use setters for validated fields
        self.name = name
        self.credits = credits
        logger.debug("Created Course code=%s name=%r", self._course_code, self._name)

    # ------------------------------------------------------------------ #
    # Properties                                                           #
    # ------------------------------------------------------------------ #

    @property
    def course_code(self) -> str:
        """Unique course code (read-only)."""
        return self._course_code

    @property
    def name(self) -> str:
        """Course name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set course name.

        Raises:
            ValueError: If value is shorter than 3 characters.
        """
        if not value or len(value.strip()) < 3:
            raise ValueError("Course name must be at least 3 characters long")
        self._name = value.strip()

    @property
    def credits(self) -> int:
        """Credit hours for this course."""
        return self._credits

    @credits.setter
    def credits(self, value: int) -> None:
        """Set credit hours.

        Raises:
            ValueError: If value is outside 1–6.
        """
        if not (1 <= value <= 6):
            raise ValueError(f"Credits must be between 1 and 6, got {value}")
        self._credits = value

    @property
    def instructor(self) -> str:
        """Name of the course instructor."""
        return self._instructor

    @instructor.setter
    def instructor(self, value: str) -> None:
        self._instructor = value

    @property
    def max_students(self) -> int:
        """Maximum enrollment capacity (read-only)."""
        return self._max_students

    @property
    def current_enrollment(self) -> int:
        """Number of students currently enrolled."""
        return len(self._enrolled_students)

    @property
    def is_full(self) -> bool:
        """``True`` when enrollment has reached capacity."""
        return self.current_enrollment >= self._max_students

    # ------------------------------------------------------------------ #
    # Enrollment management                                                #
    # ------------------------------------------------------------------ #

    def add_student(self, student: Student) -> bool:
        """Enroll a student in this course.

        Args:
            student: The student to enroll.

        Returns:
            ``True`` if enrolled successfully, ``False`` if the course is
            full or the student is already enrolled.
        """
        if self.is_full:
            logger.warning(
                "Course %s is full; cannot add student %s",
                self._course_code,
                student.student_id,
            )
            return False
        if student in self._enrolled_students:
            logger.debug(
                "Student %s already in course %s", student.student_id, self._course_code
            )
            return False
        self._enrolled_students.append(student)
        student.enroll_course(self._course_code)
        logger.info(
            "Student %s added to course %s", student.student_id, self._course_code
        )
        return True

    def remove_student(self, student: Student) -> bool:
        """Drop a student from this course.

        Args:
            student: The student to remove.

        Returns:
            ``True`` if removed, ``False`` if the student was not enrolled.
        """
        if student not in self._enrolled_students:
            return False
        self._enrolled_students.remove(student)
        student.drop_course(self._course_code)
        logger.info(
            "Student %s removed from course %s", student.student_id, self._course_code
        )
        return True

    def get_student_list(self) -> list[Student]:
        """Return a copy of the enrolled student list.

        Returns:
            List of :class:`Student` objects.
        """
        return self._enrolled_students.copy()

    # ------------------------------------------------------------------ #
    # Schedule management                                                  #
    # ------------------------------------------------------------------ #

    def set_schedule(self, day: str, time: str) -> None:
        """Set or update the schedule for a given day.

        Args:
            day: Day of the week (e.g. ``"Monday"``).
            time: Time slot (e.g. ``"10:00-12:00"``).
        """
        self._schedule[day] = time

    def get_schedule(self) -> str:
        """Return a formatted schedule string.

        Returns:
            Comma-separated ``"Day: Time"`` pairs, or
            ``"Schedule not set"`` if no schedule exists.
        """
        if not self._schedule:
            return "Schedule not set"
        return ", ".join(f"{day}: {time}" for day, time in self._schedule.items())

    # ------------------------------------------------------------------ #
    # Summary                                                              #
    # ------------------------------------------------------------------ #

    def get_enrollment_summary(self) -> dict:
        """Return a dict with enrollment statistics.

        Returns:
            Dictionary with keys: ``course_code``, ``name``, ``enrolled``,
            ``capacity``, ``available``, ``is_full``.
        """
        return {
            "course_code": self._course_code,
            "name": self._name,
            "enrolled": self.current_enrollment,
            "capacity": self._max_students,
            "available": self._max_students - self.current_enrollment,
            "is_full": self.is_full,
        }

    # ------------------------------------------------------------------ #
    # Dunder methods                                                       #
    # ------------------------------------------------------------------ #

    def __repr__(self) -> str:
        return f"Course(code={self._course_code!r}, name={self._name!r})"

    def __str__(self) -> str:
        return f"{self._course_code}: {self._name} ({self._credits} cr) - {self._instructor}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Course):
            return NotImplemented
        return self._course_code == other._course_code

    def __hash__(self) -> int:
        return hash(self._course_code)

    def __len__(self) -> int:
        return self.current_enrollment
