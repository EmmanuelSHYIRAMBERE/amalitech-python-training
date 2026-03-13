#!/usr/bin/env python3
"""
Payroll report generation with polymorphism.
"""

from abc import ABC, abstractmethod
from typing import List
from datetime import datetime
from tabulate import tabulate
from src.models.employee import Employee
from src.utils.salary_calculator import get_payroll_summary


class PayrollReport(ABC):
    """Abstract base class for payroll reports."""
    
    def __init__(self, employees: List[Employee]):
        self.employees = employees
        self.generated_date = datetime.now()
    
    @abstractmethod
    def generate(self) -> str:
        """Generate report content."""
        pass
    
    def get_header(self, title: str) -> str:
        """Generate report header."""
        date_str = self.generated_date.strftime("%Y-%m-%d %H:%M:%S")
        return f"\n{'='*60}\n{title.center(60)}\nGenerated: {date_str}\n{'='*60}\n"


class EmployeeListReport(PayrollReport):
    """Report listing all employees with basic info."""
    
    def generate(self) -> str:
        """Generate employee list report."""
        output = self.get_header("EMPLOYEE LIST REPORT")
        
        if not self.employees:
            return output + "\nNo employees found.\n"
        
        data = []
        for emp in self.employees:
            data.append([
                emp.employee_id,
                emp.name,
                emp.get_employee_type(),
                emp.email
            ])
        
        table = tabulate(data, 
                        headers=['ID', 'Name', 'Type', 'Email'],
                        tablefmt='grid')
        
        return output + table + f"\n\nTotal Employees: {len(self.employees)}\n"


class PayslipReport(PayrollReport):
    """Detailed payslip report for all employees."""
    
    def generate(self) -> str:
        """Generate payslip report."""
        output = self.get_header("PAYSLIP REPORT")
        
        if not self.employees:
            return output + "\nNo employees found.\n"
        
        data = []
        for emp in self.employees:
            data.append([
                emp.employee_id,
                emp.name,
                emp.get_employee_type(),
                f"${emp.calculate_gross_pay():,.2f}",
                f"${emp.calculate_tax():,.2f}",
                f"${emp.calculate_net_pay():,.2f}"
            ])
        
        table = tabulate(data,
                        headers=['ID', 'Name', 'Type', 'Gross Pay', 'Tax', 'Net Pay'],
                        tablefmt='grid')
        
        summary = get_payroll_summary(self.employees)
        summary_text = f"""
Summary:
  Total Gross Pay: ${summary['total_gross']:,.2f}
  Total Tax:       ${summary['total_tax']:,.2f}
  Total Net Pay:   ${summary['total_net']:,.2f}
  Average Net Pay: ${summary['average_net']:,.2f}
"""
        
        return output + table + summary_text


class EmployeeTypeReport(PayrollReport):
    """Report grouped by employee type."""
    
    def generate(self) -> str:
        """Generate employee type breakdown report."""
        output = self.get_header("EMPLOYEE TYPE BREAKDOWN")
        
        if not self.employees:
            return output + "\nNo employees found.\n"
        
        # Group by type
        type_groups = {}
        for emp in self.employees:
            emp_type = emp.get_employee_type()
            if emp_type not in type_groups:
                type_groups[emp_type] = []
            type_groups[emp_type].append(emp)
        
        # Generate report for each type
        for emp_type, emps in sorted(type_groups.items()):
            output += f"\n{emp_type} ({len(emps)} employees)\n"
            output += "-" * 60 + "\n"
            
            total_net = sum(e.calculate_net_pay() for e in emps)
            avg_net = total_net / len(emps)
            
            output += f"  Total Net Pay: ${total_net:,.2f}\n"
            output += f"  Average Net Pay: ${avg_net:,.2f}\n"
        
        return output


class TaxReport(PayrollReport):
    """Tax summary report."""
    
    def generate(self) -> str:
        """Generate tax report."""
        output = self.get_header("TAX SUMMARY REPORT")
        
        if not self.employees:
            return output + "\nNo employees found.\n"
        
        data = []
        for emp in self.employees:
            data.append([
                emp.employee_id,
                emp.name,
                f"{emp.tax_rate * 100:.1f}%",
                f"${emp.calculate_gross_pay():,.2f}",
                f"${emp.calculate_tax():,.2f}"
            ])
        
        table = tabulate(data,
                        headers=['ID', 'Name', 'Tax Rate', 'Gross Pay', 'Tax Amount'],
                        tablefmt='grid')
        
        total_tax = sum(emp.calculate_tax() for emp in self.employees)
        
        return output + table + f"\n\nTotal Tax Collected: ${total_tax:,.2f}\n"
