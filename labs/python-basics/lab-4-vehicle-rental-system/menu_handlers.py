#!/usr/bin/env python3
"""
Vehicle Rental System
Menu handlers and user interface logic.
"""

import os
from datetime import datetime
from colorama import Fore, Style

from src.models.vehicle import Car, Truck, Bike
from src.models.rental import Rental
from src.utils.helpers import create_menu, get_user_input, validate_email, format_currency, calculate_discount
from src.reports.report_generator import VehicleReport, RentalReport, RevenueReport

class MenuHandlers:
    """Handles all menu operations and user interactions."""
    
    def __init__(self, system):
        self.system = system
    
    def run_main_menu(self):
        """Main application loop."""
        while True:
            self.system._clear_screen()
            
            print(Fore.YELLOW + "="*60)
            print("Welcome to the Vehicle Rental System")
            print("="*60 + Style.RESET_ALL)
            
            options = [
                "Vehicle Management",
                "Rental Management",
                "Return Vehicle",
                "View Available Vehicles",
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
                self._vehicle_management_menu()
            elif choice == 2:
                self._rental_management_menu()
            elif choice == 3:
                self._return_vehicle()
                input("\nPress Enter to continue...")
            elif choice == 4:
                self._view_available_vehicles()
                input("\nPress Enter to continue...")
            elif choice == 5:
                self._reports_menu()
            elif choice == 6:
                self._view_statistics()
                input("\nPress Enter to continue...")
    
    def _vehicle_management_menu(self):
        """Vehicle management submenu."""
        while True:
            self.system._clear_screen()
            print(Fore.CYAN + "\n🚗 VEHICLE MANAGEMENT")
            print("="*40)
            
            options = [
                "Add Car",
                "Add Truck",
                "Add Bike",
                "View All Vehicles",
                "View Vehicle Details",
                "Remove Vehicle",
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
                self._add_car()
            elif choice == 2:
                self._add_truck()
            elif choice == 3:
                self._add_bike()
            elif choice == 4:
                self._view_all_vehicles()
            elif choice == 5:
                self._view_vehicle_details()
            elif choice == 6:
                self._remove_vehicle()
            
            input("\nPress Enter to continue...")
    
    def _add_car(self):
        """Add a new car."""
        print(Fore.CYAN + "\n➕ ADD CAR")
        print("-"*30)
        
        vehicle_id = get_user_input("Vehicle ID: ",
                                   lambda x: x not in self.system.vehicles,
                                   "Vehicle ID already exists!")
        
        brand = get_user_input("Brand: ",
                             lambda x: len(x.strip()) >= 2,
                             "Brand must be at least 2 characters!")
        
        model = get_user_input("Model: ",
                             lambda x: len(x.strip()) >= 1,
                             "Model is required!")
        
        year = int(get_user_input("Year: ",
                                lambda x: x.isdigit() and 1900 <= int(x) <= 2024,
                                "Invalid year!"))
        
        doors = int(get_user_input("Number of doors (2/4): ",
                                 lambda x: x.isdigit() and int(x) in [2, 4],
                                 "Must be 2 or 4!"))
        
        fuel_type = get_user_input("Fuel type (Petrol/Diesel/Electric/Hybrid): ",
                                  lambda x: x.capitalize() in ["Petrol", "Diesel", "Electric", "Hybrid"],
                                  "Invalid fuel type!")
        
        car = Car(vehicle_id, brand, model, year, doors, fuel_type.capitalize())
        self.system.vehicles[vehicle_id] = car
        print(Fore.GREEN + f"✅ Car {brand} {model} added successfully!")
    
    def _add_truck(self):
        """Add a new truck."""
        print(Fore.CYAN + "\n➕ ADD TRUCK")
        print("-"*30)
        
        vehicle_id = get_user_input("Vehicle ID: ",
                                   lambda x: x not in self.system.vehicles,
                                   "Vehicle ID already exists!")
        
        brand = get_user_input("Brand: ",
                             lambda x: len(x.strip()) >= 2,
                             "Brand must be at least 2 characters!")
        
        model = get_user_input("Model: ")
        
        year = int(get_user_input("Year: ",
                                lambda x: x.isdigit() and 1900 <= int(x) <= 2024,
                                "Invalid year!"))
        
        capacity = float(get_user_input("Capacity (tons): ",
                                      lambda x: x.replace('.', '').isdigit() and float(x) > 0,
                                      "Capacity must be positive!"))
        
        truck = Truck(vehicle_id, brand, model, year, capacity)
        self.system.vehicles[vehicle_id] = truck
        print(Fore.GREEN + f"✅ Truck {brand} {model} added successfully!")
    
    def _add_bike(self):
        """Add a new bike."""
        print(Fore.CYAN + "\n➕ ADD BIKE")
        print("-"*30)
        
        vehicle_id = get_user_input("Vehicle ID: ",
                                   lambda x: x not in self.system.vehicles,
                                   "Vehicle ID already exists!")
        
        brand = get_user_input("Brand: ",
                             lambda x: len(x.strip()) >= 2,
                             "Brand must be at least 2 characters!")
        
        model = get_user_input("Model: ")
        
        year = int(get_user_input("Year: ",
                                lambda x: x.isdigit() and 1900 <= int(x) <= 2024,
                                "Invalid year!"))
        
        engine_cc = int(get_user_input("Engine CC: ",
                                     lambda x: x.isdigit() and int(x) > 0,
                                     "Engine CC must be positive!"))
        
        bike = Bike(vehicle_id, brand, model, year, engine_cc)
        self.system.vehicles[vehicle_id] = bike
        print(Fore.GREEN + f"✅ Bike {brand} {model} added successfully!")
    
    def _view_all_vehicles(self):
        """View all vehicles."""
        if not self.system.vehicles:
            print(Fore.YELLOW + "No vehicles in the system.")
            return
        
        print(Fore.CYAN + "\n🚗 ALL VEHICLES")
        print("-"*60)
        
        for vehicle_id, vehicle in sorted(self.system.vehicles.items()):
            print(f"\n{vehicle}")
            print(f"  ID: {vehicle.vehicle_id}")
            if vehicle.is_rented:
                print(f"  🔴 Rented by: {vehicle.rented_by}")
            else:
                print(f"  🟢 Available for rent")
    
    def _view_vehicle_details(self):
        """View detailed information about a specific vehicle."""
        if not self.system.vehicles:
            print(Fore.YELLOW + "No vehicles in the system.")
            return
        
        print(Fore.CYAN + "\n🔍 VEHICLE DETAILS")
        print("-"*30)
        
        for vehicle_id, vehicle in self.system.vehicles.items():
            print(f"{vehicle_id}: {vehicle.brand} {vehicle.model}")
        
        vehicle_id = get_user_input("\nEnter Vehicle ID: ",
                                   lambda x: x in self.system.vehicles,
                                   "Vehicle not found!")
        
        vehicle = self.system.vehicles[vehicle_id]
        
        print(Fore.CYAN + "\n" + "="*50)
        print(f"VEHICLE DETAILS: {vehicle.brand} {vehicle.model}")
        print("="*50)
        print(f"ID: {vehicle.vehicle_id}")
        print(f"Type: {vehicle.get_vehicle_type()}")
        print(f"Year: {vehicle.year}")
        print(f"Status: {'🔴 Rented' if vehicle.is_rented else '🟢 Available'}")
        
        if vehicle.is_rented:
            print(f"Rented by: {vehicle.rented_by}")
        
        # Show pricing
        print(f"\nRental Rates:")
        for days in [1, 7, 14, 30]:
            cost = vehicle.calculate_rental_cost(days)
            discount = calculate_discount(cost, days)
            final_cost = cost - discount
            print(f"  {days} day(s): {format_currency(final_cost)}", end="")
            if discount > 0:
                print(f" (Save {format_currency(discount)})")
            else:
                print()
    
    def _remove_vehicle(self):
        """Remove a vehicle from the system."""
        if not self.system.vehicles:
            print(Fore.YELLOW + "No vehicles in the system.")
            return
        
        print(Fore.CYAN + "\n🗑️ REMOVE VEHICLE")
        print("-"*30)
        
        vehicle_id = get_user_input("Enter Vehicle ID: ",
                                   lambda x: x in self.system.vehicles,
                                   "Vehicle not found!")
        
        vehicle = self.system.vehicles[vehicle_id]
        
        if vehicle.is_rented:
            print(Fore.RED + "❌ Cannot remove a rented vehicle!")
            return
        
        confirm = get_user_input(f"Remove {vehicle.brand} {vehicle.model}? (y/n): ",
                               lambda x: x.lower() in ['y', 'n'])
        
        if confirm.lower() == 'y':
            del self.system.vehicles[vehicle_id]
            print(Fore.GREEN + "✅ Vehicle removed successfully!")
    
    def _rental_management_menu(self):
        """Rental management submenu."""
        while True:
            self.system._clear_screen()
            print(Fore.CYAN + "\n📝 RENTAL MANAGEMENT")
            print("="*40)
            
            options = [
                "Create New Rental",
                "View All Rentals",
                "View Rental Details",
                "View Active Rentals",
                "View Overdue Rentals",
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
                self._create_rental()
            elif choice == 2:
                self._view_all_rentals()
            elif choice == 3:
                self._view_rental_details()
            elif choice == 4:
                self._view_active_rentals()
            elif choice == 5:
                self._view_overdue_rentals()
            
            input("\nPress Enter to continue...")
    
    def _create_rental(self):
        """Create a new rental."""
        print(Fore.CYAN + "\n📝 CREATE NEW RENTAL")
        print("-"*30)
        
        # Show available vehicles
        available = {vid: v for vid, v in self.system.vehicles.items() if not v.is_rented}
        
        if not available:
            print(Fore.YELLOW + "No vehicles available for rent!")
            return
        
        print("\nAvailable Vehicles:")
        for vehicle_id, vehicle in available.items():
            print(f"  {vehicle_id}: {vehicle.brand} {vehicle.model} - {vehicle.get_vehicle_type()}")
        
        vehicle_id = get_user_input("\nEnter Vehicle ID: ",
                                   lambda x: x in available,
                                   "Vehicle not available!")
        
        customer_name = get_user_input("Customer Name: ",
                                      lambda x: len(x.strip()) >= 2,
                                      "Name must be at least 2 characters!")
        
        customer_email = get_user_input("Customer Email: ",
                                       validate_email,
                                       "Invalid email format!")
        
        rental_days = int(get_user_input("Rental Days: ",
                                       lambda x: x.isdigit() and int(x) > 0,
                                       "Days must be positive!"))
        
        vehicle = self.system.vehicles[vehicle_id]
        
        # Calculate cost with discount
        base_cost = vehicle.calculate_rental_cost(rental_days)
        discount = calculate_discount(base_cost, rental_days)
        final_cost = base_cost - discount
        
        print(f"\n💰 Rental Cost Breakdown:")
        print(f"  Base Cost: {format_currency(base_cost)}")
        if discount > 0:
            print(f"  Discount: -{format_currency(discount)}")
        print(f"  Final Cost: {format_currency(final_cost)}")
        
        confirm = get_user_input("\nConfirm rental? (y/n): ",
                               lambda x: x.lower() in ['y', 'n'])
        
        if confirm.lower() == 'y':
            rental_id = self.system.generate_rental_id()
            rental = Rental(rental_id, vehicle, customer_name, customer_email, rental_days)
            vehicle.rent(customer_name)
            self.system.rentals[rental_id] = rental
            
            print(Fore.GREEN + f"\n✅ Rental created successfully!")
            print(f"Rental ID: {rental_id}")
            print(f"Total Cost: {format_currency(final_cost)}")
    
    def _view_all_rentals(self):
        """View all rentals."""
        if not self.system.rentals:
            print(Fore.YELLOW + "No rentals in the system.")
            return
        
        print(Fore.CYAN + "\n📋 ALL RENTALS")
        print("-"*60)
        
        for rental_id, rental in sorted(self.system.rentals.items()):
            status = "✅ Returned" if rental.is_returned else "🔄 Active"
            if not rental.is_returned and rental.is_overdue:
                status = "⚠️ Overdue"
            
            print(f"\n{rental} - {status}")
            print(f"  Vehicle: {rental.vehicle.brand} {rental.vehicle.model}")
            print(f"  Duration: {rental.rental_days} days")
            print(f"  Cost: {format_currency(rental.total_cost)}")
    
    def _view_rental_details(self):
        """View detailed rental information."""
        if not self.system.rentals:
            print(Fore.YELLOW + "No rentals in the system.")
            return
        
        print(Fore.CYAN + "\n🔍 RENTAL DETAILS")
        print("-"*30)
        
        rental_id = get_user_input("Enter Rental ID: ",
                                  lambda x: x in self.system.rentals,
                                  "Rental not found!")
        
        rental = self.system.rentals[rental_id]
        
        print(Fore.CYAN + "\n" + "="*50)
        print(f"RENTAL DETAILS: {rental.rental_id}")
        print("="*50)
        print(f"Customer: {rental.customer_name}")
        print(f"Vehicle: {rental.vehicle.brand} {rental.vehicle.model}")
        print(f"Duration: {rental.rental_days} days")
        print(f"Total Cost: {format_currency(rental.total_cost)}")
        print(f"Status: {'✅ Returned' if rental.is_returned else '🔄 Active'}")
        
        if not rental.is_returned and rental.is_overdue:
            print(Fore.RED + "⚠️ OVERDUE!")
    
    def _view_active_rentals(self):
        """View active rentals."""
        active = [r for r in self.system.rentals.values() if not r.is_returned]
        
        if not active:
            print(Fore.YELLOW + "No active rentals.")
            return
        
        print(Fore.CYAN + "\n🔄 ACTIVE RENTALS")
        print("-"*60)
        
        for rental in active:
            status = "⚠️ Overdue" if rental.is_overdue else "🔄 Active"
            print(f"\n{rental} - {status}")
            print(f"  Vehicle: {rental.vehicle.brand} {rental.vehicle.model}")
            print(f"  Duration: {rental.rental_days} days")
    
    def _view_overdue_rentals(self):
        """View overdue rentals."""
        overdue = [r for r in self.system.rentals.values() 
                  if not r.is_returned and r.is_overdue]
        
        if not overdue:
            print(Fore.GREEN + "✅ No overdue rentals!")
            return
        
        print(Fore.RED + "\n⚠️ OVERDUE RENTALS")
        print("-"*60)
        
        for rental in overdue:
            print(f"\n{rental}")
            print(f"  Customer: {rental.customer_name}")
            print(f"  Vehicle: {rental.vehicle.brand} {rental.vehicle.model}")
    
    def _return_vehicle(self):
        """Process vehicle return."""
        active = {rid: r for rid, r in self.system.rentals.items() if not r.is_returned}
        
        if not active:
            print(Fore.YELLOW + "No active rentals to return.")
            return
        
        print(Fore.CYAN + "\n🔙 RETURN VEHICLE")
        print("-"*30)
        
        print("\nActive Rentals:")
        for rental_id, rental in active.items():
            print(f"  {rental_id}: {rental.customer_name} - {rental.vehicle.brand} {rental.vehicle.model}")
        
        rental_id = get_user_input("\nEnter Rental ID: ",
                                  lambda x: x in active,
                                  "Rental not found or already returned!")
        
        rental = self.system.rentals[rental_id]
        
        final_cost = rental.complete_return()
        rental.vehicle.return_vehicle()
        
        print(Fore.GREEN + f"\n✅ Vehicle returned successfully!")
        print(f"Final Cost: {format_currency(final_cost)}")
        
        if rental.is_overdue:
            print(Fore.YELLOW + "⚠️ Late fees applied!")
    
    def _view_available_vehicles(self):
        """View available vehicles."""
        available = [v for v in self.system.vehicles.values() if not v.is_rented]
        
        if not available:
            print(Fore.YELLOW + "No vehicles available.")
            return
        
        print(Fore.CYAN + "\n🟢 AVAILABLE VEHICLES")
        print("-"*60)
        
        for vehicle in available:
            print(f"\n{vehicle}")
            print(f"  Daily Rate: {format_currency(vehicle.calculate_rental_cost(1))}")
    
    def _reports_menu(self):
        """Reports generation submenu."""
        while True:
            self.system._clear_screen()
            print(Fore.CYAN + "\n📊 REPORTS")
            print("="*40)
            
            options = [
                "Vehicle Inventory Report",
                "Rental Transaction Report",
                "Revenue & Statistics Report",
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
                self._generate_vehicle_report()
            elif choice == 2:
                self._generate_rental_report()
            elif choice == 3:
                self._generate_revenue_report()
            elif choice == 4:
                self._generate_all_reports()
            
            input("\nPress Enter to continue...")
    
    def _generate_vehicle_report(self):
        """Generate vehicle inventory report."""
        report = VehicleReport(list(self.system.vehicles.values()))
        print(report.generate())
        
        save = get_user_input("\nSave report to file? (y/n): ",
                            lambda x: x.lower() in ['y', 'n'])
        if save.lower() == 'y':
            os.makedirs('reports', exist_ok=True)
            filename = f"reports/vehicle_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(report.generate())
            print(Fore.GREEN + f"✅ Report saved to {filename}")
    
    def _generate_rental_report(self):
        """Generate rental transaction report."""
        report = RentalReport(list(self.system.rentals.values()))
        print(report.generate())
        
        save = get_user_input("\nSave report to file? (y/n): ",
                            lambda x: x.lower() in ['y', 'n'])
        if save.lower() == 'y':
            os.makedirs('reports', exist_ok=True)
            filename = f"reports/rental_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(report.generate())
            print(Fore.GREEN + f"✅ Report saved to {filename}")
    
    def _generate_revenue_report(self):
        """Generate revenue and statistics report."""
        report = RevenueReport(list(self.system.rentals.values()),
                              list(self.system.vehicles.values()))
        print(report.generate())
        
        save = get_user_input("\nSave report to file? (y/n): ",
                            lambda x: x.lower() in ['y', 'n'])
        if save.lower() == 'y':
            os.makedirs('reports', exist_ok=True)
            filename = f"reports/revenue_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(report.generate())
            print(Fore.GREEN + f"✅ Report saved to {filename}")
    
    def _generate_all_reports(self):
        """Generate all reports."""
        self._generate_vehicle_report()
        print("\n" + "="*70)
        self._generate_rental_report()
        print("\n" + "="*70)
        self._generate_revenue_report()
    
    def _view_statistics(self):
        """View system statistics."""
        print(Fore.CYAN + "\n📊 SYSTEM STATISTICS")
        print("="*60)
        
        total_vehicles = len(self.system.vehicles)
        available_vehicles = sum(1 for v in self.system.vehicles.values() if not v.is_rented)
        rented_vehicles = total_vehicles - available_vehicles
        
        total_rentals = len(self.system.rentals)
        active_rentals = sum(1 for r in self.system.rentals.values() if not r.is_returned)
        completed_rentals = total_rentals - active_rentals
        
        total_revenue = sum(r.total_cost for r in self.system.rentals.values())
        
        print(f"\n🚗 FLEET OVERVIEW")
        print(f"  Total Vehicles: {total_vehicles}")
        print(f"  Available: {available_vehicles}")
        print(f"  Rented: {rented_vehicles}")
        
        if total_vehicles > 0:
            utilization = (rented_vehicles / total_vehicles * 100)
            print(f"  Utilization Rate: {utilization:.1f}%")
        
        print(f"\n📝 RENTAL OVERVIEW")
        print(f"  Total Rentals: {total_rentals}")
        print(f"  Active: {active_rentals}")
        print(f"  Completed: {completed_rentals}")
        
        print(f"\n💰 REVENUE")
        print(f"  Total Revenue: {format_currency(total_revenue)}")
        
        if total_rentals > 0:
            avg_rental = total_revenue / total_rentals
            print(f"  Average per Rental: {format_currency(avg_rental)}")
        
        # Vehicle type breakdown
        vehicle_types = {}
        for vehicle in self.system.vehicles.values():
            v_type = vehicle.__class__.__name__
            vehicle_types[v_type] = vehicle_types.get(v_type, 0) + 1
        
        print(f"\n🚙 VEHICLE TYPE BREAKDOWN")
        for v_type, count in vehicle_types.items():
            percentage = (count / total_vehicles * 100) if total_vehicles else 0
            print(f"  • {v_type}: {count} ({percentage:.1f}%)")
