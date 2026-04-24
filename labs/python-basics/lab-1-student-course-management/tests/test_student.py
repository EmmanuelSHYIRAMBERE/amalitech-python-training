"""
Unit tests for the Student Course Management System.

Run with:
    poetry run pytest tests/ -v
"""

import pytest

from src.models.course import Course
from src.models.student import (
    GraduateStudent,
    InternationalStudent,
    UndergraduateStudent,
)


# --------------------------------------------------------------------------- #
# Fixtures                                                                      #
# --------------------------------------------------------------------------- #


@pytest.fixture
def undergrad():
    return UndergraduateStudent("S001", "Alice Johnson", "alice@example.com", 2)


@pytest.fixture
def grad():
    return GraduateStudent("S002", "Bob Smith", "bob@example.com", "Machine Learning")


@pytest.fixture
def international():
    return InternationalStudent("S003", "Carlos Rodriguez", "carlos@example.com", "Spain", 3)


@pytest.fixture
def course():
    return Course("CS101", "Introduction to Programming", 3, "Dr. Williams", 30)


@pytest.fixture
def small_course():
    """Course with capacity of 1 for full-course tests."""
    return Course("CS999", "Tiny Course", 2, "Dr. Tiny", 1)


# --------------------------------------------------------------------------- #
# Student creation                                                              #
# --------------------------------------------------------------------------- #


class TestStudentCreation:
    def test_undergraduate_attributes(self, undergrad):
        assert undergrad.student_id == "S001"
        assert undergrad.name == "Alice Johnson"
        assert undergrad.email == "alice@example.com"
        assert undergrad.year == 2

    def test_graduate_attributes(self, grad):
        assert grad.student_id == "S002"
        assert grad.research_topic == "Machine Learning"
        assert grad.advisor is None

    def test_international_attributes(self, international):
        assert international.country == "Spain"
        assert international.year == 3

    def test_student_id_stripped(self):
        s = UndergraduateStudent("  S010  ", "Test User", "t@example.com", 1)
        assert s.student_id == "S010"

    def test_name_stripped(self):
        s = UndergraduateStudent("S011", "  Jane Doe  ", "j@example.com", 1)
        assert s.name == "Jane Doe"

    @pytest.mark.parametrize("bad_id", ["", "   "])
    def test_empty_student_id_raises(self, bad_id):
        with pytest.raises(ValueError, match="student_id"):
            UndergraduateStudent(bad_id, "Name", "n@example.com", 1)

    @pytest.mark.parametrize("bad_name", ["", " ", "A"])
    def test_short_name_raises(self, bad_name):
        with pytest.raises(ValueError, match="Name"):
            UndergraduateStudent("S020", bad_name, "n@example.com", 1)

    @pytest.mark.parametrize("bad_email", ["notanemail", "missing@", "@nodomain", ""])
    def test_invalid_email_raises(self, bad_email):
        with pytest.raises(ValueError, match="[Ii]nvalid email"):
            UndergraduateStudent("S021", "Valid Name", bad_email, 1)

    @pytest.mark.parametrize("bad_year", [0, 5, -1])
    def test_invalid_year_raises(self, bad_year):
        with pytest.raises(ValueError, match="Year"):
            UndergraduateStudent("S022", "Valid Name", "v@example.com", bad_year)

    def test_invalid_country_raises(self):
        with pytest.raises(ValueError, match="Country"):
            InternationalStudent("S023", "Valid Name", "v@example.com", "A", 1)


# --------------------------------------------------------------------------- #
# Student property setters                                                      #
# --------------------------------------------------------------------------- #


class TestStudentSetters:
    def test_update_name(self, undergrad):
        undergrad.name = "Alice Smith"
        assert undergrad.name == "Alice Smith"

    def test_update_email(self, undergrad):
        undergrad.email = "new@example.com"
        assert undergrad.email == "new@example.com"

    def test_update_year(self, undergrad):
        undergrad.year = 4
        assert undergrad.year == 4

    def test_update_year_invalid(self, undergrad):
        with pytest.raises(ValueError):
            undergrad.year = 5

    def test_update_research_topic(self, grad):
        grad.research_topic = "Deep Learning"
        assert grad.research_topic == "Deep Learning"

    def test_set_advisor(self, grad):
        grad.advisor = "Dr. Smith"
        assert grad.advisor == "Dr. Smith"


# --------------------------------------------------------------------------- #
# Enrollment                                                                    #
# --------------------------------------------------------------------------- #


class TestEnrollment:
    def test_enroll_new_course(self, undergrad):
        assert undergrad.enroll_course("CS101") is True
        assert "CS101" in undergrad.get_enrolled_courses()

    def test_enroll_duplicate_returns_false(self, undergrad):
        undergrad.enroll_course("CS101")
        assert undergrad.enroll_course("CS101") is False

    def test_enrolled_courses_returns_copy(self, undergrad):
        undergrad.enroll_course("CS101")
        courses = undergrad.get_enrolled_courses()
        courses.append("INJECTED")
        assert "INJECTED" not in undergrad.get_enrolled_courses()

    def test_drop_enrolled_course(self, undergrad):
        undergrad.enroll_course("CS101")
        assert undergrad.drop_course("CS101") is True
        assert "CS101" not in undergrad.get_enrolled_courses()

    def test_drop_unenrolled_course_returns_false(self, undergrad):
        assert undergrad.drop_course("CS999") is False

    def test_enroll_multiple_courses(self, undergrad):
        for code in ["CS101", "CS201", "MATH101"]:
            undergrad.enroll_course(code)
        assert len(undergrad.get_enrolled_courses()) == 3


# --------------------------------------------------------------------------- #
# Grades & GPA                                                                  #
# --------------------------------------------------------------------------- #


class TestGradesAndGPA:
    def test_gpa_no_grades(self, undergrad):
        assert undergrad.calculate_gpa() == 0.0

    def test_gpa_single_grade(self, undergrad):
        undergrad.add_grade("CS101", 3.5)
        assert undergrad.calculate_gpa() == pytest.approx(3.5)

    def test_gpa_multiple_courses(self, undergrad):
        undergrad.add_grade("CS101", 3.5)
        undergrad.add_grade("CS101", 4.0)
        undergrad.add_grade("MATH101", 3.0)
        # (3.5 + 4.0 + 3.0) / 3 = 3.5
        assert undergrad.calculate_gpa() == pytest.approx(3.5, abs=1e-9)

    @pytest.mark.parametrize("grade", [-0.1, 4.1, 5.0])
    def test_invalid_grade_raises(self, undergrad, grade):
        with pytest.raises(ValueError, match="Grade"):
            undergrad.add_grade("CS101", grade)

    @pytest.mark.parametrize("grade", [0.0, 2.0, 4.0])
    def test_boundary_grades_accepted(self, undergrad, grade):
        undergrad.add_grade("CS101", grade)  # should not raise


# --------------------------------------------------------------------------- #
# Tuition calculation                                                           #
# --------------------------------------------------------------------------- #


class TestTuition:
    def test_undergrad_tuition_no_courses(self, undergrad):
        # base only
        assert undergrad.calculate_tuition() == UndergraduateStudent.TUITION_BASE

    def test_undergrad_tuition_with_courses(self, undergrad):
        undergrad.enroll_course("CS101")
        undergrad.enroll_course("CS201")
        expected = (
            UndergraduateStudent.TUITION_BASE
            + 2 * UndergraduateStudent.TUITION_PER_COURSE
        )
        assert undergrad.calculate_tuition() == pytest.approx(expected)

    def test_grad_tuition_no_advisor(self, grad):
        expected = GraduateStudent.TUITION_BASE + GraduateStudent.RESEARCH_FEE
        assert grad.calculate_tuition() == pytest.approx(expected)

    def test_grad_tuition_with_advisor(self, grad):
        grad.advisor = "Dr. Smith"
        expected = (
            GraduateStudent.TUITION_BASE
            + GraduateStudent.RESEARCH_FEE
            + GraduateStudent.ADVISOR_FEE
        )
        assert grad.calculate_tuition() == pytest.approx(expected)

    def test_international_tuition_includes_surcharge(self, international):
        base = (
            UndergraduateStudent.TUITION_BASE
            + len(international.get_enrolled_courses()) * UndergraduateStudent.TUITION_PER_COURSE
        )
        expected = base + InternationalStudent.INTERNATIONAL_FEE
        assert international.calculate_tuition() == pytest.approx(expected)


# --------------------------------------------------------------------------- #
# Student type strings                                                          #
# --------------------------------------------------------------------------- #


class TestStudentType:
    def test_undergrad_type_string(self, undergrad):
        assert "Undergraduate" in undergrad.get_student_type()
        assert "2" in undergrad.get_student_type()

    def test_grad_type_with_topic(self, grad):
        assert "Graduate" in grad.get_student_type()
        assert "Machine Learning" in grad.get_student_type()

    def test_grad_type_without_topic(self):
        s = GraduateStudent("S099", "No Topic", "nt@example.com")
        assert s.get_student_type() == "Graduate"

    def test_international_type_string(self, international):
        assert "Spain" in international.get_student_type()


# --------------------------------------------------------------------------- #
# Dunder methods                                                                #
# --------------------------------------------------------------------------- #


class TestDunderMethods:
    def test_equality_same_id(self):
        s1 = UndergraduateStudent("S001", "Alice", "a@example.com", 1)
        s2 = UndergraduateStudent("S001", "Different Name", "b@example.com", 2)
        assert s1 == s2

    def test_inequality_different_id(self, undergrad, grad):
        assert undergrad != grad

    def test_hash_consistency(self, undergrad):
        assert hash(undergrad) == hash(undergrad)

    def test_equal_students_same_hash(self):
        s1 = UndergraduateStudent("S001", "Alice", "a@example.com", 1)
        s2 = UndergraduateStudent("S001", "Alice", "a@example.com", 1)
        assert hash(s1) == hash(s2)

    def test_students_usable_in_set(self, undergrad, grad):
        student_set = {undergrad, grad}
        assert len(student_set) == 2

    def test_str_contains_name_and_id(self, undergrad):
        s = str(undergrad)
        assert "Alice Johnson" in s
        assert "S001" in s

    def test_repr(self, undergrad):
        r = repr(undergrad)
        assert "UndergraduateStudent" in r
        assert "S001" in r


# --------------------------------------------------------------------------- #
# Course management                                                             #
# --------------------------------------------------------------------------- #


class TestCourse:
    def test_course_attributes(self, course):
        assert course.course_code == "CS101"
        assert course.name == "Introduction to Programming"
        assert course.credits == 3
        assert course.instructor == "Dr. Williams"
        assert course.max_students == 30

    def test_add_student(self, course, undergrad):
        assert course.add_student(undergrad) is True
        assert course.current_enrollment == 1

    def test_add_duplicate_student(self, course, undergrad):
        course.add_student(undergrad)
        assert course.add_student(undergrad) is False
        assert course.current_enrollment == 1

    def test_remove_student(self, course, undergrad):
        course.add_student(undergrad)
        assert course.remove_student(undergrad) is True
        assert course.current_enrollment == 0

    def test_remove_unenrolled_student(self, course, undergrad):
        assert course.remove_student(undergrad) is False

    def test_course_full(self, small_course, undergrad, grad):
        small_course.add_student(undergrad)
        assert small_course.is_full is True
        assert small_course.add_student(grad) is False

    def test_get_student_list_returns_copy(self, course, undergrad):
        course.add_student(undergrad)
        lst = course.get_student_list()
        lst.clear()
        assert course.current_enrollment == 1

    def test_schedule(self, course):
        course.set_schedule("Monday", "10:00-12:00")
        assert "Monday" in course.get_schedule()
        assert "10:00-12:00" in course.get_schedule()

    def test_schedule_not_set(self, course):
        assert course.get_schedule() == "Schedule not set"

    def test_enrollment_summary_keys(self, course):
        summary = course.get_enrollment_summary()
        for key in ("course_code", "name", "enrolled", "capacity", "available", "is_full"):
            assert key in summary

    def test_course_len(self, course, undergrad):
        course.add_student(undergrad)
        assert len(course) == 1

    def test_course_equality(self):
        c1 = Course("CS101", "Intro", 3, "Dr. A")
        c2 = Course("CS101", "Different Name", 4, "Dr. B")
        assert c1 == c2

    def test_course_hash_in_set(self, course):
        course_set = {course}
        assert course in course_set

    @pytest.mark.parametrize("bad_credits", [0, 7, -1])
    def test_invalid_credits_raises(self, bad_credits):
        with pytest.raises(ValueError, match="Credits"):
            Course("XX101", "Valid Name", bad_credits, "Instructor")

    def test_invalid_course_name_raises(self):
        with pytest.raises(ValueError, match="Course name"):
            Course("XX101", "AB", 3, "Instructor")


# --------------------------------------------------------------------------- #
# Cross-model: add_student syncs student enrollment list                        #
# --------------------------------------------------------------------------- #


class TestCrossModelSync:
    def test_add_student_syncs_enrolled_courses(self, course, undergrad):
        course.add_student(undergrad)
        assert course.course_code in undergrad.get_enrolled_courses()

    def test_remove_student_syncs_enrolled_courses(self, course, undergrad):
        course.add_student(undergrad)
        course.remove_student(undergrad)
        assert course.course_code not in undergrad.get_enrolled_courses()


# --------------------------------------------------------------------------- #
# Graduate-specific                                                             #
# --------------------------------------------------------------------------- #


class TestGraduateSpecific:
    def test_thesis_complete(self, grad):
        assert grad.is_thesis_complete(6) is True
        assert grad.is_thesis_complete(5) is False

    def test_can_graduate_undergrad(self):
        s = UndergraduateStudent("S050", "Senior", "s@example.com", 4)
        for i in range(8):
            s.enroll_course(f"C{i:03d}")
        assert s.can_graduate() is True

    def test_cannot_graduate_too_few_courses(self):
        s = UndergraduateStudent("S051", "Junior", "j@example.com", 4)
        s.enroll_course("CS101")
        assert s.can_graduate() is False

    def test_cannot_graduate_wrong_year(self):
        s = UndergraduateStudent("S052", "Sophomore", "so@example.com", 2)
        for i in range(8):
            s.enroll_course(f"C{i:03d}")
        assert s.can_graduate() is False
