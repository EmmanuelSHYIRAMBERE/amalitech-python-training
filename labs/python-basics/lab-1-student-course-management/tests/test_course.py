"""Tests for course management and cross-model sync between Course and Student."""

import pytest

from src.models.course import Course


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


class TestCrossModelSync:
    def test_add_student_syncs_enrolled_courses(self, course, undergrad):
        course.add_student(undergrad)
        assert course.course_code in undergrad.get_enrolled_courses()

    def test_remove_student_syncs_enrolled_courses(self, course, undergrad):
        course.add_student(undergrad)
        course.remove_student(undergrad)
        assert course.course_code not in undergrad.get_enrolled_courses()
