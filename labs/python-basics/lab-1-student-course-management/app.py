#!/usr/bin/env python3
"""
Student Course Management System
Main application class for managing students and courses.
"""

from typing import Dict
from colorama import Fore, init

from src.models.student import Student, UndergraduateStudent, GraduateStudent, InternationalStudent
from src.models.course import Course

# Initialize colorama
init(autoreset=True)

class StudentCourseManagementSystem:
    """Main application class."""
    
    def __init__(self):
        self.students: Dict[str, Student] = {}
        self.courses: Dict[str, Course] = {}
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample data for testing."""
        # Add sample students
        student1 = UndergraduateStudent("S001", "Alice Johnson", "alice@example.com", 2)
        student2 = GraduateStudent("S002", "Bob Smith", "bob@example.com", "Machine Learning")
        student3 = InternationalStudent("S003", "Carlos Rodriguez", "carlos@example.com", "Spain", 3)
        
        self.students = {
            "S001": student1,
            "S002": student2,
            "S003": student3
        }
        
        # Add sample courses
        course1 = Course("CS101", "Introduction to Programming", 3, "Dr. Williams", 30)
        course1.set_schedule("Monday", "10:00-12:00")
        course1.set_schedule("Wednesday", "10:00-12:00")
        
        course2 = Course("CS201", "Data Structures", 4, "Dr. Garcia", 25)
        course2.set_schedule("Tuesday", "14:00-16:00")
        course2.set_schedule("Thursday", "14:00-16:00")
        
        course3 = Course("MATH101", "Calculus I", 4, "Prof. Miller", 35)
        course3.set_schedule("Monday", "13:00-15:00")
        course3.set_schedule("Wednesday", "13:00-15:00")
        
        self.courses = {
            "CS101": course1,
            "CS201": course2,
            "MATH101": course3
        }
        
        # Enroll some students
        course1.add_student(student1)
        course1.add_student(student3)
        course2.add_student(student2)
        course3.add_student(student1)
        
        # Add some grades
        student1.add_grade("CS101", 3.7)
        student1.add_grade("MATH101", 3.3)
        student2.add_grade("CS201", 4.0)
    
    def _clear_screen(self):
        """Clear the console screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')