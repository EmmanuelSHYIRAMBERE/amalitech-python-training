"""Student class and specialized student types."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from datetime import datetime
from src.utils.helpers import validate_email


class Student(ABC):
    """Abstract base class for all student types."""

    def __init__(self, student_id: str, name: str, email: str):
        self._student_id = student_id
        self._name = name
        self._email = email
        self._enrolled_courses: List[str] = []
        self._grades: Dict[str, List[float]] = {}
        self._enrollment_date = datetime.now()

    @property
    def student_id(self) -> str:
        """Get student ID."""
        return self._student_id

    @property
    def name(self) -> str:
        """Get student name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set student name with validation."""
        if not value or len(value.strip()) < 2:
            raise ValueError("Name must be at least 2 characters long")
        self._name = value.strip()

    @property
    def email(self) -> str:
        """Get student email."""
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        """Set student email with validation."""
        if not validate_email(value):
            raise ValueError("Invalid email format")
        self._email = value

    @property
    def enrollment_date(self) -> datetime:
        """Get enrollment date."""
        return self._enrollment_date

    @abstractmethod
    def calculate_tuition(self) -> float:
        """Calculate tuition based on student type."""
        pass

    @abstractmethod
    def get_student_type(self) -> str:
        """Get student type description."""
        pass

    def enroll_course(self, course_code: str) -> bool:
        """Enroll in a course."""
        if course_code not in self._enrolled_courses:
            self._enrolled_courses.append(course_code)
            return True
        return False

    def add_grade(self, course_code: str, grade: float) -> None:
        """Add a grade for a course."""
        if course_code not in self._grades:
            self._grades[course_code] = []
        self._grades[course_code].append(grade)

    def calculate_gpa(self) -> float:
        """Calculate GPA based on all grades."""
        all_grades = []
        for grades in self._grades.values():
            all_grades.extend(grades)

        if not all_grades:
            return 0.0

        # Assuming 4.0 scale
        total_points = sum(all_grades)
        return total_points / len(all_grades)

    def get_enrolled_courses(self) -> List[str]:
        """Get list of enrolled courses."""
        return self._enrolled_courses.copy()

    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"{self.__class__.__name__}(id='{self._student_id}', name='{self._name}')"
        )

    def __str__(self) -> str:
        """User-friendly representation."""
        return f"{self.get_student_type()}: {self._name} ({self._student_id})"

    def __eq__(self, other) -> bool:
        """Compare students by ID."""
        if not isinstance(other, Student):
            return False
        return self._student_id == other._student_id

    def __lt__(self, other) -> bool:
        """Compare students by name for sorting."""
        return self._name < other._name


class UndergraduateStudent(Student):
    """Undergraduate student implementation."""

    UNDERGRADUATE_TUITION_RATE = 500.0
    UNDERGRADUATE_CREDIT_COST = 300.0

    def __init__(self, student_id: str, name: str, email: str, year: int = 1):
        super().__init__(student_id, name, email)
        self._year = year

    @property
    def year(self) -> int:
        """Get current year of study."""
        return self._year

    @year.setter
    def year(self, value: int) -> None:
        """Set year of study with validation."""
        if 1 <= value <= 4:
            self._year = value
        else:
            raise ValueError("Year must be between 1 and 4")

    def calculate_tuition(self) -> float:
        """Calculate undergraduate tuition."""
        base_tuition = self.UNDERGRADUATE_TUITION_RATE
        credit_costs = len(self._enrolled_courses) * self.UNDERGRADUATE_CREDIT_COST
        return base_tuition + credit_costs

    def get_student_type(self) -> str:
        """Get student type."""
        return f"Undergraduate (Year {self._year})"

    def can_graduate(self) -> bool:
        """Check if student can graduate."""
        return self._year >= 4 and len(self._enrolled_courses) >= 8


class GraduateStudent(Student):
    """Graduate student implementation."""

    GRADUATE_TUITION_RATE = 800.0
    RESEARCH_FEE = 500.0
    THESIS_CREDITS = 6

    def __init__(
        self, student_id: str, name: str, email: str, research_topic: str = ""
    ):
        super().__init__(student_id, name, email)
        self._research_topic = research_topic
        self._advisor: Optional[str] = None

    @property
    def research_topic(self) -> str:
        """Get research topic."""
        return self._research_topic

    @research_topic.setter
    def research_topic(self, topic: str) -> None:
        """Set research topic."""
        self._research_topic = topic

    @property
    def advisor(self) -> Optional[str]:
        """Get advisor name."""
        return self._advisor

    @advisor.setter
    def advisor(self, advisor_name: str) -> None:
        """Set advisor name."""
        self._advisor = advisor_name

    def calculate_tuition(self) -> float:
        """Calculate graduate tuition."""
        tuition = self.GRADUATE_TUITION_RATE + self.RESEARCH_FEE
        if self._advisor:
            tuition += 200  # Additional fee for advisor
        return tuition

    def get_student_type(self) -> str:
        """Get student type."""
        type_str = "Graduate"
        if self._research_topic:
            type_str += f" (Research: {self._research_topic})"
        return type_str

    def is_thesis_complete(self, credits_completed: int) -> bool:
        """Check if thesis requirements are met."""
        return credits_completed >= self.THESIS_CREDITS


class InternationalStudent(UndergraduateStudent):
    """International student (demonstrating multiple inheritance later)."""

    INTERNATIONAL_FEE = 1000.0

    def __init__(
        self, student_id: str, name: str, email: str, country: str, year: int = 1
    ):
        super().__init__(student_id, name, email, year)
        self._country = country

    @property
    def country(self) -> str:
        """Get country of origin."""
        return self._country

    def calculate_tuition(self) -> float:
        """Calculate international student tuition."""
        return super().calculate_tuition() + self.INTERNATIONAL_FEE

    def get_student_type(self) -> str:
        """Get student type with country info."""
        return f"International Student from {self._country}"
