"""Course class definition."""

from typing import List, Dict, Optional
from datetime import datetime
from src.models.student import Student

class Course:
    """Course class representing a academic course."""
    
    def __init__(self, course_code: str, name: str, credits: int, 
                 instructor: str, max_students: int = 30):
        self._course_code = course_code
        self._name = name
        self._credits = credits
        self._instructor = instructor
        self._max_students = max_students
        self._enrolled_students: List[Student] = []
        self._schedule: Dict[str, str] = {}  # day: time
        self._created_at = datetime.now()
    
    @property
    def course_code(self) -> str:
        """Get course code."""
        return self._course_code
    
    @property
    def name(self) -> str:
        """Get course name."""
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        """Set course name with validation."""
        if not value or len(value.strip()) < 3:
            raise ValueError("Course name must be at least 3 characters long")
        self._name = value.strip()
    
    @property
    def credits(self) -> int:
        """Get course credits."""
        return self._credits
    
    @credits.setter
    def credits(self, value: int) -> None:
        """Set course credits with validation."""
        if 1 <= value <= 6:
            self._credits = value
        else:
            raise ValueError("Credits must be between 1 and 6")
    
    @property
    def instructor(self) -> str:
        """Get instructor name."""
        return self._instructor
    
    @instructor.setter
    def instructor(self, value: str) -> None:
        """Set instructor name."""
        self._instructor = value
    
    @property
    def current_enrollment(self) -> int:
        """Get current enrollment count."""
        return len(self._enrolled_students)
    
    @property
    def is_full(self) -> bool:
        """Check if course is full."""
        return self.current_enrollment >= self._max_students
    
    def add_student(self, student: Student) -> bool:
        """Add a student to the course."""
        if self.is_full:
            return False
        
        if student not in self._enrolled_students:
            self._enrolled_students.append(student)
            student.enroll_course(self._course_code)
            return True
        return False
    
    def remove_student(self, student: Student) -> bool:
        """Remove a student from the course."""
        if student in self._enrolled_students:
            self._enrolled_students.remove(student)
            return True
        return False
    
    def get_student_list(self) -> List[Student]:
        """Get list of enrolled students."""
        return self._enrolled_students.copy()
    
    def get_enrollment_summary(self) -> Dict:
        """Get enrollment summary statistics."""
        return {
            "course_code": self._course_code,
            "name": self._name,
            "enrolled": self.current_enrollment,
            "capacity": self._max_students,
            "available": self._max_students - self.current_enrollment,
            "is_full": self.is_full
        }
    
    def set_schedule(self, day: str, time: str) -> None:
        """Set course schedule."""
        self._schedule[day] = time
    
    def get_schedule(self) -> str:
        """Get formatted schedule."""
        if not self._schedule:
            return "Schedule not set"
        return ", ".join([f"{day}: {time}" for day, time in self._schedule.items()])
    
    def __repr__(self) -> str:
        """Developer representation."""
        return f"Course(code='{self._course_code}', name='{self._name}')"
    
    def __str__(self) -> str:
        """User-friendly representation."""
        return f"{self._course_code}: {self._name} ({self._credits} cr) - {self._instructor}"
    
    def __eq__(self, other) -> bool:
        """Compare courses by code."""
        if not isinstance(other, Course):
            return False
        return self._course_code == other._course_code
    
    def __len__(self) -> int:
        """Return number of enrolled students."""
        return self.current_enrollment