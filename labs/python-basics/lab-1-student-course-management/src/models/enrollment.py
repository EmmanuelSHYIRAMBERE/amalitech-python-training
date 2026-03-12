"""Enrollment management functions."""

from typing import Dict, List, Optional
from src.utils.helpers import flexible_summary

def add_student(students_db: Dict, sid: str, name: str, email: str, 
                student_type: str = "undergraduate") -> bool:
    """Add a new student to the database."""
    if sid in students_db:
        print(f"❌ Student ID {sid} already exists!")
        return False
    
    students_db[sid] = {
        "name": name,
        "email": email,
        "type": student_type
    }
    print(f"✅ Student {name} added successfully!")
    return True

def add_course(courses_db: Dict, code: str, name: str, credits: int, 
               instructor: str) -> bool:
    """Add a new course to the database."""
    if code in courses_db:
        print(f"❌ Course code {code} already exists!")
        return False
    
    courses_db[code] = {
        "name": name,
        "credits": credits,
        "instructor": instructor
    }
    print(f"✅ Course {name} added successfully!")
    return True

def enroll_student(enrollments_db: Dict, sid: str, course_code: str) -> bool:
    """Enroll a student in a course."""
    if sid not in enrollments_db:
        enrollments_db[sid] = []
    
    if course_code in enrollments_db[sid]:
        print(f"❌ Student already enrolled in {course_code}!")
        return False
    
    enrollments_db[sid].append(course_code)
    print(f"✅ Student enrolled in {course_code} successfully!")
    return True

def calculate_average(grades: List[float]) -> float:
    """Calculate average of grades."""
    return sum(grades) / len(grades) if grades else 0.0

def get_course_roster(course_code: str, students_db: Dict, 
                      enrollments_db: Dict) -> List[Dict]:
    """Get all students enrolled in a course."""
    roster = []
    for sid, courses in enrollments_db.items():
        if course_code in courses and sid in students_db:
            student = students_db[sid].copy()
            student["id"] = sid
            roster.append(student)
    return roster

def generate_enrollment_report(students_db: Dict, courses_db: Dict, 
                              enrollments_db: Dict) -> None:
    """Generate comprehensive enrollment report."""
    print("\n" + "="*60)
    print("📊 ENROLLMENT REPORT")
    print("="*60)
    
    for sid, student in students_db.items():
        enrolled_courses = enrollments_db.get(sid, [])
        print(f"\n👤 {student['name']} ({sid}) - {student['type']}")
        if enrolled_courses:
            print("   Enrolled in:")
            for course_code in enrolled_courses:
                course = courses_db.get(course_code, {})
                print(f"   • {course_code}: {course.get('name', 'Unknown')}")
        else:
            print("   📭 No courses enrolled")
    
    print("\n" + "="*60)
    # Demonstrate *args usage
    student_names = [data["name"] for data in students_db.values()]
    summary = flexible_summary(*student_names, type="enrollment", 
                              info="Complete enrollment report")
    print(f"Summary: {summary['students_count']} total students")