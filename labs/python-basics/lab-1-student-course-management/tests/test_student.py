import pytest
from src.models.student import UndergraduateStudent, GraduateStudent, InternationalStudent

def test_undergraduate_student_creation():
    student = UndergraduateStudent("S001", "Test Student", "test@example.com", 2)
    assert student.student_id == "S001"
    assert student.name == "Test Student"
    assert student.email == "test@example.com"
    assert student.year == 2
    assert student.calculate_tuition() > 0

def test_graduate_student_research_topic():
    student = GraduateStudent("S002", "Grad Student", "grad@example.com", "AI Research")
    assert student.research_topic == "AI Research"
    student.advisor = "Dr. Smith"
    assert student.advisor == "Dr. Smith"

def test_student_enrollment():
    student = UndergraduateStudent("S003", "Enroll Test", "enroll@example.com", 1)
    assert student.enroll_course("CS101") == True
    assert student.enroll_course("CS101") == False  # Already enrolled
    assert len(student.get_enrolled_courses()) == 1

def test_gpa_calculation():
    student = UndergraduateStudent("S004", "GPA Test", "gpa@example.com", 3)
    student.add_grade("CS101", 3.5)
    student.add_grade("CS101", 4.0)
    student.add_grade("MATH101", 3.0)
    assert student.calculate_gpa() == pytest.approx(3.5, 0.1)