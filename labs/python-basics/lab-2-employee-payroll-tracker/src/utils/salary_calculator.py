#!/usr/bin/env python3
"""
Salary computation utilities and helper functions.
"""

from typing import List, Dict
from src.models.employee import Employee


def calculate_total_payroll(employees: List[Employee]) -> float:
    """
    Calculate total payroll for all employees.
    
    Args:
        employees: List of Employee objects
        
    Returns:
        Total net pay for all employees
    """
    return sum(emp.calculate_net_pay() for emp in employees)


def calculate_average_salary(employees: List[Employee]) -> float:
    """
    Calculate average net salary across all employees.
    
    Args:
        employees: List of Employee objects
        
    Returns:
        Average net pay
    """
    if not employees:
        return 0.0
    return calculate_total_payroll(employees) / len(employees)


def get_payroll_summary(employees: List[Employee]) -> Dict[str, float]:
    """
    Generate payroll summary statistics.
    
    Args:
        employees: List of Employee objects
        
    Returns:
        Dictionary with payroll statistics
    """
    if not employees:
        return {
            'total_gross': 0.0,
            'total_tax': 0.0,
            'total_net': 0.0,
            'average_net': 0.0,
            'employee_count': 0
        }
    
    total_gross = sum(emp.calculate_gross_pay() for emp in employees)
    total_tax = sum(emp.calculate_tax() for emp in employees)
    total_net = sum(emp.calculate_net_pay() for emp in employees)
    
    return {
        'total_gross': total_gross,
        'total_tax': total_tax,
        'total_net': total_net,
        'average_net': total_net / len(employees),
        'employee_count': len(employees)
    }


def get_employees_by_type(employees: List[Employee]) -> Dict[str, List[Employee]]:
    """
    Group employees by their type.
    
    Args:
        employees: List of Employee objects
        
    Returns:
        Dictionary mapping employee types to lists of employees
    """
    result = {}
    for emp in employees:
        emp_type = emp.get_employee_type()
        if emp_type not in result:
            result[emp_type] = []
        result[emp_type].append(emp)
    return result


def calculate_tax_bracket_distribution(employees: List[Employee]) -> Dict[str, int]:
    """
    Calculate distribution of employees across tax brackets.
    
    Args:
        employees: List of Employee objects
        
    Returns:
        Dictionary with tax bracket counts
    """
    brackets = {
        '0-10%': 0,
        '10-20%': 0,
        '20%+': 0
    }
    
    for emp in employees:
        rate = emp.tax_rate
        if rate < 0.10:
            brackets['0-10%'] += 1
        elif rate < 0.20:
            brackets['10-20%'] += 1
        else:
            brackets['20%+'] += 1
    
    return brackets


def find_highest_paid(employees: List[Employee]) -> Employee:
    """
    Find the highest paid employee.
    
    Args:
        employees: List of Employee objects
        
    Returns:
        Employee with highest net pay
        
    Raises:
        ValueError: If employee list is empty
    """
    if not employees:
        raise ValueError("No employees to compare")
    return max(employees, key=lambda emp: emp.calculate_net_pay())


def find_lowest_paid(employees: List[Employee]) -> Employee:
    """
    Find the lowest paid employee.
    
    Args:
        employees: List of Employee objects
        
    Returns:
        Employee with lowest net pay
        
    Raises:
        ValueError: If employee list is empty
    """
    if not employees:
        raise ValueError("No employees to compare")
    return min(employees, key=lambda emp: emp.calculate_net_pay())
