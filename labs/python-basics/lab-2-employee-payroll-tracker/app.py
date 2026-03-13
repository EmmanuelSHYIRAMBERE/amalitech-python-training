#!/usr/bin/env python3
"""
Employee Payroll Tracker
Main application class.
"""

from typing import Dict
from colorama import init
from src.models.employee import Employee, FullTimeEmployee, ContractEmployee, InternEmployee

# Initialize colorama
init(autoreset=True)


class PayrollSystem:
    """Main payroll system class."""
    
    def __init__(self):
        self.employees: Dict[str, Employee] = {}
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample employee data."""
        # Full-time employees
        emp1 = FullTimeEmployee("FT001", "John Doe", "john@company.com", 60000)
        emp1.bonus = 5000
        emp1.benefits = 1000
        
        emp2 = FullTimeEmployee("FT002", "Jane Smith", "jane@company.com", 75000)
        emp2.bonus = 7500
        emp2.benefits = 1200
        
        # Contract employees
        emp3 = ContractEmployee("CT001", "Bob Johnson", "bob@contractor.com", 50, 160)
        emp3.bonus = 500
        
        emp4 = ContractEmployee("CT002", "Alice Williams", "alice@contractor.com", 45, 180)
        
        # Interns
        emp5 = InternEmployee("IN001", "Charlie Brown", "charlie@intern.com", 2000, "MIT")
        emp5.bonus = 200
        
        emp6 = InternEmployee("IN002", "Diana Prince", "diana@intern.com", 1800, "Stanford")
        
        self.employees = {
            "FT001": emp1,
            "FT002": emp2,
            "CT001": emp3,
            "CT002": emp4,
            "IN001": emp5,
            "IN002": emp6
        }
    
    def add_employee(self, employee: Employee):
        """Add an employee to the system."""
        self.employees[employee.employee_id] = employee
    
    def remove_employee(self, employee_id: str) -> bool:
        """Remove an employee from the system."""
        if employee_id in self.employees:
            del self.employees[employee_id]
            return True
        return False
    
    def get_employee(self, employee_id: str) -> Employee:
        """Get an employee by ID."""
        return self.employees.get(employee_id)
    
    def get_all_employees(self) -> list:
        """Get all employees."""
        return list(self.employees.values())
