"""Report generation using ABC and polymorphism."""

from abc import ABC, abstractmethod
from typing import List, Any
from datetime import datetime
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


class ReportGenerator(ABC):
    """Abstract base class for report generators."""

    def __init__(self, title: str):
        self.title = title
        self.generated_at = datetime.now()

    @abstractmethod
    def generate(self) -> str:
        """Generate the report content."""
        pass

    @abstractmethod
    def get_data(self) -> List[Any]:
        """Get the data for the report."""
        pass

    @classmethod
    def create_report(cls, report_type: str, **kwargs):
        """Factory method to create reports."""
        if report_type == "student":
            return StudentReport(kwargs.get("students", []))
        elif report_type == "course":
            return CourseReport(kwargs.get("courses", []))
        elif report_type == "enrollment":
            return EnrollmentReport(
                kwargs.get("students", []), kwargs.get("courses", [])
            )
        else:
            raise ValueError(f"Unknown report type: {report_type}")

    def _format_header(self) -> str:
        """Format report header."""
        header = f"\n{Fore.CYAN}{'='*60}\n"
        header += f"{self.title.center(60)}\n"
        header += f"{'='*60}{Style.RESET_ALL}\n"
        header += f"Generated: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        return header


class StudentReport(ReportGenerator):
    """Student-specific report generator."""

    def __init__(self, students: List):
        super().__init__("STUDENT REPORT")
        self._students = students

    def get_data(self) -> List[Any]:
        return self._students

    def generate(self) -> str:
        """Generate student report."""
        report = self._format_header()

        if not self._students:
            report += f"{Fore.YELLOW}No students found.{Style.RESET_ALL}\n"
            return report

        # Prepare data for tabulation
        table_data = []
        for student in self._students:
            table_data.append(
                [
                    student.student_id,
                    student.name,
                    student.get_student_type(),
                    student.email,
                    f"{student.calculate_gpa():.2f}",
                    len(student.get_enrolled_courses()),
                ]
            )

        headers = ["ID", "Name", "Type", "Email", "GPA", "Courses"]
        report += tabulate(table_data, headers=headers, tablefmt="grid")
        report += (
            f"\n\n{Fore.GREEN}Total Students: {len(self._students)}{Style.RESET_ALL}\n"
        )

        return report


class CourseReport(ReportGenerator):
    """Course-specific report generator."""

    def __init__(self, courses: List):
        super().__init__("COURSE REPORT")
        self._courses = courses

    def get_data(self) -> List[Any]:
        return self._courses

    def generate(self) -> str:
        """Generate course report."""
        report = self._format_header()

        if not self._courses:
            report += f"{Fore.YELLOW}No courses found.{Style.RESET_ALL}\n"
            return report

        table_data = []
        for course in self._courses:
            summary = course.get_enrollment_summary()
            table_data.append(
                [
                    course.course_code,
                    course.name,
                    course.credits,
                    course.instructor,
                    f"{summary['enrolled']}/{summary['capacity']}",
                    course.get_schedule(),
                ]
            )

        headers = ["Code", "Name", "Credits", "Instructor", "Enrolled", "Schedule"]
        report += tabulate(table_data, headers=headers, tablefmt="grid")

        total_capacity = sum(c._max_students for c in self._courses)
        total_enrolled = sum(c.current_enrollment for c in self._courses)
        report += f"\n\n{Fore.GREEN}Total Courses: {len(self._courses)} | "
        report += (
            f"Total Enrollment: {total_enrolled}/{total_capacity}{Style.RESET_ALL}\n"
        )

        return report


class EnrollmentReport(ReportGenerator):
    """Enrollment-specific report generator."""

    def __init__(self, students: List, courses: List):
        super().__init__("ENROLLMENT REPORT")
        self._students = students
        self._courses = {c.course_code: c for c in courses}

    def get_data(self) -> List[Any]:
        return self._students

    def generate(self) -> str:
        """Generate enrollment report."""
        report = self._format_header()

        if not self._students:
            report += f"{Fore.YELLOW}No enrollments found.{Style.RESET_ALL}\n"
            return report

        for student in self._students:
            report += f"\n{Fore.CYAN}{student}{Style.RESET_ALL}\n"
            courses = student.get_enrolled_courses()

            if not courses:
                report += f"  {Fore.YELLOW}No courses enrolled{Style.RESET_ALL}\n"
                continue

            for course_code in courses:
                course = self._courses.get(course_code)
                if course:
                    report += (
                        f"  • {course.name} ({course_code}) - {course.instructor}\n"
                    )

        # Summary statistics
        total_enrollments = sum(len(s.get_enrolled_courses()) for s in self._students)
        avg_courses = total_enrollments / len(self._students) if self._students else 0

        report += f"\n{Fore.GREEN}{'='*60}\n"
        report += "SUMMARY:\n"
        report += f"Total Students: {len(self._students)}\n"
        report += f"Total Enrollments: {total_enrollments}\n"
        report += f"Average Courses per Student: {avg_courses:.2f}{Style.RESET_ALL}\n"

        return report
