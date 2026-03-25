#!/usr/bin/env python3
"""
Menu handlers and CLI interface.
"""

import os
from colorama import Fore
from datetime import datetime
from src.models.employee import FullTimeEmployee, ContractEmployee, InternEmployee
from src.utils.helpers import get_user_input, validate_email, create_menu, format_currency
from src.utils.report_generator import (EmployeeListReport, PayslipReport, 
                                        EmployeeTypeReport, TaxReport)
from src.utils.salary_calculator import (get_payroll_summary, find_highest_paid, 
                                         find_lowest_paid)


class MenuHandlers:
    """Handles all menu operations."""
    
    def __init__(self, system):
        self.system = system
    
    def run_main_menu(self):
        """Main application loop."""
        while True:
            print(Fore.YELLOW + "\n" + "="*60)
            print("Employee Payroll Tracker System")
            print("="*60)
            
            options = [
                "Employee Management",
                "Payroll Operations",
                "Generate Reports",
                "View Statistics"
            ]
            
            create_menu(options)
            
            choice = get_user_input("Enter your choice: ",
                                   lambda x: x.isdigit() and 0 <= int(x) <= len(options))
            choice = int(choice)
            
            if choice == 0:
                print(Fore.GREEN + "\nThank you for using the system. Goodbye!")
                break
            elif choice == 1:
                self._employee_management_menu()
            elif choice == 2:
                self._payroll_operations_menu()
            elif choice == 3:
                self._reports_menu()
            elif choice == 4:
                self._view_statistics()
    
    def _employee_management_menu(self):
        """Employee management submenu."""
        while True:
            print(Fore.CYAN + "\n📋 EMPLOYEE MANAGEMENT")
            print("="*40)
            
            options = [
                "Add Full-Time Employee",
                "Add Contract Employee",
                "Add Intern",
                "View All Employees",
                "View Employee Details",
                "Remove Employee",
                "Back to Main Menu"
            ]
            
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")
            print("0. Back")
            
            choice = get_user_input("Enter your choice: ",
                                   lambda x: x.isdigit() and 0 <= int(x) <= len(options))
            choice = int(choice)
            
            if choice == 0:
                break
            elif choice == 1:
                self._add_fulltime_employee()
            elif choice == 2:
                self._add_contract_employee()
            elif choice == 3:
                self._add_intern()
            elif choice == 4:
                self._view_all_employees()
            elif choice == 5:
                self._view_employee_details()
            elif choice == 6:
                self._remove_employee()
            
            input("\nPress Enter to continue...")
    
    def _add_fulltime_employee(self):
        """Add a full-time employee."""
        print(Fore.CYAN + "\n➕ ADD FULL-TIME EMPLOYEE")
        print("-"*30)
        
        emp_id = get_user_input("Employee ID: ",
                               lambda x: x not in self.system.employees,
                               "Employee ID already exists!")
        
        name = get_user_input("Full Name: ",
                            lambda x: len(x.strip()) >= 2,
                            "Name must be at least 2 characters!")
        
        email = get_user_input("Email: ", validate_email, "Invalid email format!")
        
        salary = float(get_user_input("Annual Salary: ",
                                     lambda x: x.replace('.', '').isdigit() and float(x) > 0,
                                     "Salary must be positive!"))
        
        employee = FullTimeEmployee(emp_id, name, email, salary)
        
        # Optional: Add benefits
        add_benefits = get_user_input("Add monthly benefits? (y/n): ",
                                     lambda x: x.lower() in ['y', 'n'])
        if add_benefits.lower() == 'y':
            benefits = float(get_user_input("Monthly Benefits: ",
                                          lambda x: x.replace('.', '').isdigit() and float(x) >= 0))
            employee.benefits = benefits
        
        self.system.add_employee(employee)
        print(Fore.GREEN + f"✅ Full-time employee {name} added successfully!")
    
    def _add_contract_employee(self):
        """Add a contract employee."""
        print(Fore.CYAN + "\n➕ ADD CONTRACT EMPLOYEE")
        print("-"*30)
        
        emp_id = get_user_input("Employee ID: ",
                               lambda x: x not in self.system.employees,
                               "Employee ID already exists!")
        
        name = get_user_input("Full Name: ",
                            lambda x: len(x.strip()) >= 2)
        
        email = get_user_input("Email: ", validate_email)
        
        hourly_rate = float(get_user_input("Hourly Rate: ",
                                          lambda x: x.replace('.', '').isdigit() and float(x) > 0))
        
        hours = float(get_user_input("Hours Worked This Month: ",
                                    lambda x: x.replace('.', '').isdigit() and 0 <= float(x) <= 744))
        
        employee = ContractEmployee(emp_id, name, email, hourly_rate, hours)
        self.system.add_employee(employee)
        print(Fore.GREEN + f"✅ Contract employee {name} added successfully!")
    
    def _add_intern(self):
        """Add an intern."""
        print(Fore.CYAN + "\n➕ ADD INTERN")
        print("-"*30)
        
        emp_id = get_user_input("Employee ID: ",
                               lambda x: x not in self.system.employees)
        
        name = get_user_input("Full Name: ",
                            lambda x: len(x.strip()) >= 2)
        
        email = get_user_input("Email: ", validate_email)
        
        stipend = float(get_user_input("Monthly Stipend: ",
                                      lambda x: x.replace('.', '').isdigit() and float(x) > 0))
        
        school = get_user_input("School/University (optional): ")
        
        employee = InternEmployee(emp_id, name, email, stipend, school if school else None)
        self.system.add_employee(employee)
        print(Fore.GREEN + f"✅ Intern {name} added successfully!")
    
    def _view_all_employees(self):
        """View all employees."""
        employees = self.system.get_all_employees()
        
        if not employees:
            print(Fore.YELLOW + "No employees in the system.")
            return
        
        print(Fore.CYAN + "\n📋 ALL EMPLOYEES")
        print("-"*50)
        
        for emp in sorted(employees, key=lambda e: e.employee_id):
            print(f"\n{emp}")
            print(f"  📧 {emp.email}")
            print(f"  💰 Gross Pay: {format_currency(emp.calculate_gross_pay())}")
            print(f"  📊 Net Pay: {format_currency(emp.calculate_net_pay())}")
    
    def _view_employee_details(self):
        """View detailed employee information."""
        if not self.system.employees:
            print(Fore.YELLOW + "No employees in the system.")
            return
        
        print(Fore.CYAN + "\n🔍 EMPLOYEE DETAILS")
        print("-"*30)
        
        for emp_id, emp in self.system.employees.items():
            print(f"{emp_id}: {emp.name}")
        
        emp_id = get_user_input("\nEnter Employee ID: ",
                               lambda x: x in self.system.employees,
                               "Employee not found!")
        
        emp = self.system.get_employee(emp_id)
        
        print(Fore.CYAN + "\n" + "="*50)
        print(f"EMPLOYEE DETAILS: {emp.name}")
        print("="*50)
        print(f"ID: {emp.employee_id}")
        print(f"Type: {emp.get_employee_type()}")
        print(f"Email: {emp.email}")
        print(f"Tax Rate: {emp.tax_rate * 100:.1f}%")
        print(f"\nPAYROLL INFORMATION:")
        print(f"  Gross Pay: {format_currency(emp.calculate_gross_pay())}")
        print(f"  Tax: {format_currency(emp.calculate_tax())}")
        print(f"  Net Pay: {format_currency(emp.calculate_net_pay())}")
    
    def _remove_employee(self):
        """Remove an employee."""
        if not self.system.employees:
            print(Fore.YELLOW + "No employees in the system.")
            return
        
        print(Fore.CYAN + "\n🗑️ REMOVE EMPLOYEE")
        print("-"*30)
        
        for emp_id, emp in self.system.employees.items():
            print(f"{emp_id}: {emp.name}")
        
        emp_id = get_user_input("\nEnter Employee ID to remove: ",
                               lambda x: x in self.system.employees)
        
        emp = self.system.get_employee(emp_id)
        confirm = get_user_input(f"Remove {emp.name}? (y/n): ",
                                lambda x: x.lower() in ['y', 'n'])
        
        if confirm.lower() == 'y':
            self.system.remove_employee(emp_id)
            print(Fore.GREEN + f"✅ Employee {emp.name} removed successfully!")
        else:
            print(Fore.YELLOW + "Operation cancelled.")
    
    def _payroll_operations_menu(self):
        """Payroll operations submenu."""
        while True:
            print(Fore.CYAN + "\n💰 PAYROLL OPERATIONS")
            print("="*40)
            
            options = [
                "Update Employee Bonus",
                "Update Tax Rate",
                "Update Contract Hours",
                "Calculate Total Payroll",
                "Back to Main Menu"
            ]
            
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")
            print("0. Back")
            
            choice = get_user_input("Enter your choice: ",
                                   lambda x: x.isdigit() and 0 <= int(x) <= len(options))
            choice = int(choice)
            
            if choice == 0:
                break
            elif choice == 1:
                self._update_bonus()
            elif choice == 2:
                self._update_tax_rate()
            elif choice == 3:
                self._update_contract_hours()
            elif choice == 4:
                self._calculate_total_payroll()
            
            input("\nPress Enter to continue...")
    
    def _update_bonus(self):
        """Update employee bonus."""
        if not self.system.employees:
            print(Fore.YELLOW + "No employees in the system.")
            return
        
        print(Fore.CYAN + "\n💵 UPDATE BONUS")
        print("-"*30)
        
        for emp_id, emp in self.system.employees.items():
            print(f"{emp_id}: {emp.name} (Current: {format_currency(emp.bonus)})")
        
        emp_id = get_user_input("\nEnter Employee ID: ",
                               lambda x: x in self.system.employees)
        
        emp = self.system.get_employee(emp_id)
        bonus = float(get_user_input("New Bonus Amount: ",
                                    lambda x: x.replace('.', '').isdigit() and float(x) >= 0))
        
        emp.bonus = bonus
        print(Fore.GREEN + f"✅ Bonus updated for {emp.name}!")
    
    def _update_tax_rate(self):
        """Update employee tax rate."""
        if not self.system.employees:
            print(Fore.YELLOW + "No employees in the system.")
            return
        
        print(Fore.CYAN + "\n📊 UPDATE TAX RATE")
        print("-"*30)
        
        for emp_id, emp in self.system.employees.items():
            print(f"{emp_id}: {emp.name} (Current: {emp.tax_rate * 100:.1f}%)")
        
        emp_id = get_user_input("\nEnter Employee ID: ",
                               lambda x: x in self.system.employees)
        
        emp = self.system.get_employee(emp_id)
        rate = float(get_user_input("New Tax Rate (0-100): ",
                                   lambda x: x.replace('.', '').isdigit() and 0 <= float(x) <= 100))
        
        emp.tax_rate = rate / 100
        print(Fore.GREEN + f"✅ Tax rate updated for {emp.name}!")
    
    def _update_contract_hours(self):
        """Update contract employee hours."""
        contracts = [e for e in self.system.get_all_employees() 
                    if isinstance(e, ContractEmployee)]
        
        if not contracts:
            print(Fore.YELLOW + "No contract employees in the system.")
            return
        
        print(Fore.CYAN + "\n⏰ UPDATE CONTRACT HOURS")
        print("-"*30)
        
        for emp in contracts:
            print(f"{emp.employee_id}: {emp.name} (Current: {emp.hours_worked} hrs)")
        
        emp_id = get_user_input("\nEnter Employee ID: ",
                               lambda x: x in [e.employee_id for e in contracts])
        
        emp = self.system.get_employee(emp_id)
        hours = float(get_user_input("Hours Worked: ",
                                    lambda x: x.replace('.', '').isdigit() and 0 <= float(x) <= 744))
        
        emp.hours_worked = hours
        print(Fore.GREEN + f"✅ Hours updated for {emp.name}!")
    
    def _calculate_total_payroll(self):
        """Calculate and display total payroll."""
        employees = self.system.get_all_employees()
        
        if not employees:
            print(Fore.YELLOW + "No employees in the system.")
            return
        
        summary = get_payroll_summary(employees)
        
        print(Fore.CYAN + "\n💰 TOTAL PAYROLL SUMMARY")
        print("="*50)
        print(f"Total Employees: {summary['employee_count']}")
        print(f"Total Gross Pay: {format_currency(summary['total_gross'])}")
        print(f"Total Tax: {format_currency(summary['total_tax'])}")
        print(f"Total Net Pay: {format_currency(summary['total_net'])}")
        print(f"Average Net Pay: {format_currency(summary['average_net'])}")
    
    def _reports_menu(self):
        """Reports generation submenu."""
        while True:
            print(Fore.CYAN + "\n📊 REPORTS")
            print("="*40)
            
            options = [
                "Employee List Report",
                "Payslip Report",
                "Employee Type Report",
                "Tax Report",
                "Generate All Reports",
                "Back to Main Menu"
            ]
            
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")
            print("0. Back")
            
            choice = get_user_input("Enter your choice: ",
                                   lambda x: x.isdigit() and 0 <= int(x) <= len(options))
            choice = int(choice)
            
            if choice == 0:
                break
            elif choice == 1:
                self._generate_employee_list()
            elif choice == 2:
                self._generate_payslip_report()
            elif choice == 3:
                self._generate_type_report()
            elif choice == 4:
                self._generate_tax_report()
            elif choice == 5:
                self._generate_all_reports()
            
            input("\nPress Enter to continue...")
    
    def _generate_employee_list(self):
        """Generate employee list report."""
        report = EmployeeListReport(self.system.get_all_employees())
        print(report.generate())
        
        save = get_user_input("\nSave report to file? (y/n): ",
                            lambda x: x.lower() in ['y', 'n'])
        if save.lower() == 'y':
            os.makedirs('reports', exist_ok=True)
            filename = f"reports/employee_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(report.generate())
            print(Fore.GREEN + f"✅ Report saved to {filename}")
    
    def _generate_payslip_report(self):
        """Generate payslip report."""
        report = PayslipReport(self.system.get_all_employees())
        print(report.generate())
        
        save = get_user_input("\nSave report to file? (y/n): ",
                            lambda x: x.lower() in ['y', 'n'])
        if save.lower() == 'y':
            os.makedirs('reports', exist_ok=True)
            filename = f"reports/payslip_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(report.generate())
            print(Fore.GREEN + f"✅ Report saved to {filename}")
    
    def _generate_type_report(self):
        """Generate employee type report."""
        report = EmployeeTypeReport(self.system.get_all_employees())
        print(report.generate())
    
    def _generate_tax_report(self):
        """Generate tax report."""
        report = TaxReport(self.system.get_all_employees())
        print(report.generate())
    
    def _generate_all_reports(self):
        """Generate all reports."""
        self._generate_employee_list()
        print("\n" + "="*60)
        self._generate_payslip_report()
        print("\n" + "="*60)
        self._generate_type_report()
        print("\n" + "="*60)
        self._generate_tax_report()
    
    def _view_statistics(self):
        """View system statistics."""
        employees = self.system.get_all_employees()
        
        if not employees:
            print(Fore.YELLOW + "No employees in the system.")
            input("\nPress Enter to continue...")
            return
        
        print(Fore.CYAN + "\n📊 SYSTEM STATISTICS")
        print("="*50)
        
        summary = get_payroll_summary(employees)
        
        print(f"👥 Total Employees: {summary['employee_count']}")
        print(f"💰 Total Payroll: {format_currency(summary['total_net'])}")
        print(f"📊 Average Salary: {format_currency(summary['average_net'])}")
        
        # Employee type breakdown
        type_counts = {}
        for emp in employees:
            emp_type = emp.get_employee_type()
            type_counts[emp_type] = type_counts.get(emp_type, 0) + 1
        
        print("\n👤 Employee Type Breakdown:")
        for emp_type, count in type_counts.items():
            percentage = (count / len(employees)) * 100
            print(f"  • {emp_type}: {count} ({percentage:.1f}%)")
        
        # Highest and lowest paid
        try:
            highest = find_highest_paid(employees)
            lowest = find_lowest_paid(employees)
            
            print(f"\n💎 Highest Paid: {highest.name} - {format_currency(highest.calculate_net_pay())}")
            print(f"💵 Lowest Paid: {lowest.name} - {format_currency(lowest.calculate_net_pay())}")
        except ValueError:
            pass
        
        input("\nPress Enter to continue...")
