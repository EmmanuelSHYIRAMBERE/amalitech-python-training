"""Tests for student enrollment and drop logic."""


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
