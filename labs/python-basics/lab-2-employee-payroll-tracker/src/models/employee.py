#!/usr/bin/env python3
"""
Employee Payroll Tracker
Employee models with inheritance and polymorphism.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional


class Employee(ABC):
    """Base Employee class with common attributes and abstract methods."""
    
    def __init__(self, employee_id: str, name: str, email: str, base_salary: float):
        self._employee_id = employee_id
        self._name = name
        self._email = email
        self._base_salary = base_salary
        self._bonus = 0.0
        self._tax_rate = 0.15  # Default 15% tax
        self._hire_date = datetime.now()
    
    @property
    def employee_id(self) -> str:
        """Get employee ID."""
        return self._employee_id
    
    @property
    def name(self) -> str:
        """Get employee name."""
        return self._name
    
    @name.setter
    def name(self, value: str):
        """Set employee name with validation."""
        if not value or len(value.strip()) < 2:
            raise ValueError("Name must be at least 2 characters")
        self._name = value.strip()
    
    @property
    def email(self) -> str:
        """Get employee email."""
        return self._email
    
    @email.setter
    def email(self, value: str):
        """Set employee email with validation."""
        if "@" not in value:
            raise ValueError("Invalid email format")
        self._email = value
    
    @property
    def base_salary(self) -> float:
        """Get base salary."""
        return self._base_salary
    
    @base_salary.setter
    def base_salary(self, value: float):
        """Set base salary with validation."""
        if value < 0:
            raise ValueError("Salary cannot be negative")
        self._base_salary = value
    
    @property
    def bonus(self) -> float:
        """Get bonus amount."""
        return self._bonus
    
    @bonus.setter
    def bonus(self, value: float):
        """Set bonus with validation."""
        if value < 0:
            raise ValueError("Bonus cannot be negative")
        self._bonus = value
    
    @property
    def tax_rate(self) -> float:
        """Get tax rate."""
        return self._tax_rate
    
    @tax_rate.setter
    def tax_rate(self, value: float):
        """Set tax rate with validation."""
        if not 0 <= value <= 1:
            raise ValueError("Tax rate must be between 0 and 1")
        self._tax_rate = value
    
    @abstractmethod
    def calculate_gross_pay(self) -> float:
        """Calculate gross pay (to be implemented by subclasses)."""
        pass
    
    def calculate_tax(self) -> float:
        """Calculate tax amount."""
        return self.calculate_gross_pay() * self._tax_rate
    
    def calculate_net_pay(self) -> float:
        """Calculate net pay after tax."""
        return self.calculate_gross_pay() - self.calculate_tax()
    
    @abstractmethod
    def get_employee_type(self) -> str:
        """Return employee type."""
        pass
    
    def __str__(self) -> str:
        return f"{self.get_employee_type()}: {self._name} ({self._employee_id})"


class FullTimeEmployee(Employee):
    """Full-time employee with annual salary and benefits."""
    
    def __init__(self, employee_id: str, name: str, email: str, annual_salary: float):
        super().__init__(employee_id, name, email, annual_salary)
        self._benefits = 0.0
        self._tax_rate = 0.20  # Higher tax rate for full-time
    
    @property
    def benefits(self) -> float:
        """Get benefits amount."""
        return self._benefits
    
    @benefits.setter
    def benefits(self, value: float):
        """Set benefits with validation."""
        if value < 0:
            raise ValueError("Benefits cannot be negative")
        self._benefits = value
    
    def calculate_gross_pay(self) -> float:
        """Calculate monthly gross pay including benefits and bonus."""
        monthly_salary = self._base_salary / 12
        return monthly_salary + self._benefits + self._bonus
    
    def get_employee_type(self) -> str:
        return "Full-Time Employee"


class ContractEmployee(Employee):
    """Contract employee paid hourly."""
    
    def __init__(self, employee_id: str, name: str, email: str, hourly_rate: float, 
                 hours_worked: float = 0):
        super().__init__(employee_id, name, email, hourly_rate)
        self._hours_worked = hours_worked
        self._tax_rate = 0.10  # Lower tax rate for contractors
    
    @property
    def hourly_rate(self) -> float:
        """Get hourly rate."""
        return self._base_salary
    
    @hourly_rate.setter
    def hourly_rate(self, value: float):
        """Set hourly rate."""
        self.base_salary = value
    
    @property
    def hours_worked(self) -> float:
        """Get hours worked."""
        return self._hours_worked
    
    @hours_worked.setter
    def hours_worked(self, value: float):
        """Set hours worked with validation."""
        if value < 0:
            raise ValueError("Hours cannot be negative")
        if value > 744:  # Max hours in a month (31 days * 24 hours)
            raise ValueError("Hours exceed maximum monthly hours")
        self._hours_worked = value
    
    def calculate_gross_pay(self) -> float:
        """Calculate gross pay based on hours worked."""
        overtime_threshold = 160  # Standard monthly hours
        regular_hours = min(self._hours_worked, overtime_threshold)
        overtime_hours = max(0, self._hours_worked - overtime_threshold)
        
        regular_pay = regular_hours * self._base_salary
        overtime_pay = overtime_hours * self._base_salary * 1.5  # 1.5x for overtime
        
        return regular_pay + overtime_pay + self._bonus
    
    def get_employee_type(self) -> str:
        return "Contract Employee"


class InternEmployee(Employee):
    """Intern employee with stipend."""
    
    def __init__(self, employee_id: str, name: str, email: str, monthly_stipend: float,
                 school: Optional[str] = None):
        super().__init__(employee_id, name, email, monthly_stipend)
        self._school = school
        self._tax_rate = 0.05  # Minimal tax for interns
    
    @property
    def school(self) -> Optional[str]:
        """Get school name."""
        return self._school
    
    @school.setter
    def school(self, value: str):
        """Set school name."""
        self._school = value
    
    def calculate_gross_pay(self) -> float:
        """Calculate gross pay (stipend + bonus)."""
        return self._base_salary + self._bonus
    
    def get_employee_type(self) -> str:
        return "Intern"
