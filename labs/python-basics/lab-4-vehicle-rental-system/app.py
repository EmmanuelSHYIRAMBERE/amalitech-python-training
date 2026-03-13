#!/usr/bin/env python3
"""
Vehicle Rental System
Main application class for managing vehicles and rentals.
"""

from typing import Dict
from colorama import init

from src.models.vehicle import Vehicle, Car, Truck, Bike
from src.models.rental import Rental

init(autoreset=True)

class VehicleRentalSystem:
    """Main application class."""
    
    def __init__(self):
        self.vehicles: Dict[str, Vehicle] = {}
        self.rentals: Dict[str, Rental] = {}
        self._rental_counter = 1
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample data for testing."""
        # Add sample cars
        car1 = Car("V001", "Toyota", "Camry", 2022, 4, "Hybrid")
        car2 = Car("V002", "Honda", "Civic", 2021, 4, "Petrol")
        car3 = Car("V003", "Tesla", "Model 3", 2023, 4, "Electric")
        
        # Add sample trucks
        truck1 = Truck("V004", "Ford", "F-150", 2020, 3.5)
        truck2 = Truck("V005", "Chevrolet", "Silverado", 2022, 5.0)
        
        # Add sample bikes
        bike1 = Bike("V006", "Yamaha", "R15", 2023, 155)
        bike2 = Bike("V007", "Harley-Davidson", "Street 750", 2021, 750)
        bike3 = Bike("V008", "Honda", "CBR500R", 2022, 500)
        
        self.vehicles = {
            "V001": car1,
            "V002": car2,
            "V003": car3,
            "V004": truck1,
            "V005": truck2,
            "V006": bike1,
            "V007": bike2,
            "V008": bike3
        }
        
        # Create sample rentals
        rental1 = Rental("R001", car1, "John Doe", "john@example.com", 5)
        car1.rent("John Doe")
        
        rental2 = Rental("R002", bike1, "Jane Smith", "jane@example.com", 3)
        bike1.rent("Jane Smith")
        
        self.rentals = {
            "R001": rental1,
            "R002": rental2
        }
        self._rental_counter = 3
    
    def _clear_screen(self):
        """Clear the console screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def generate_rental_id(self) -> str:
        """Generate unique rental ID."""
        rental_id = f"R{self._rental_counter:03d}"
        self._rental_counter += 1
        return rental_id
