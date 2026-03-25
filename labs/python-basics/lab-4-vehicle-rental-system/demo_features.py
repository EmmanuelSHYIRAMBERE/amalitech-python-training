"""
Demonstration of advanced Python features used in the Vehicle Rental System.
This file showcases *args, **kwargs, and other Python best practices.
"""

from typing import Dict, Any, List
from src.models.vehicle import Car, Truck, Bike
from src.models.rental import Rental

# ============================================================
# 1. *args and **kwargs Demonstration
# ============================================================

def create_vehicle_summary(*vehicles, **options) -> Dict[str, Any]:
    """
    Demonstrate *args and **kwargs usage.
    
    Args:
        *vehicles: Variable number of vehicle objects
        **options: Additional configuration options
            - include_pricing: bool
            - format: str ('simple' or 'detailed')
            - filter_type: str (vehicle type to filter)
    
    Returns:
        Dictionary with summary information
    """
    summary = {
        "total_vehicles": len(vehicles),
        "format": options.get("format", "simple"),
        "vehicles": []
    }
    
    # Filter by type if specified
    filter_type = options.get("filter_type")
    filtered_vehicles = vehicles
    
    if filter_type:
        filtered_vehicles = [v for v in vehicles 
                           if v.__class__.__name__ == filter_type]
    
    # Build vehicle list
    for vehicle in filtered_vehicles:
        vehicle_info = {
            "id": vehicle.vehicle_id,
            "brand": vehicle.brand,
            "model": vehicle.model,
            "type": vehicle.get_vehicle_type(),
            "available": not vehicle.is_rented
        }
        
        # Add pricing if requested
        if options.get("include_pricing", False):
            vehicle_info["daily_rate"] = vehicle.calculate_rental_cost(1)
            vehicle_info["weekly_rate"] = vehicle.calculate_rental_cost(7)
        
        summary["vehicles"].append(vehicle_info)
    
    return summary


def calculate_total_revenue(*rentals, **filters) -> Dict[str, float]:
    """
    Calculate revenue with flexible filtering.
    
    Args:
        *rentals: Variable number of rental objects
        **filters: Revenue calculation filters
            - include_active: bool
            - include_completed: bool
            - vehicle_type: str
    
    Returns:
        Dictionary with revenue breakdown
    """
    include_active = filters.get("include_active", True)
    include_completed = filters.get("include_completed", True)
    vehicle_type = filters.get("vehicle_type")
    
    total = 0.0
    count = 0
    
    for rental in rentals:
        # Apply filters
        if not include_active and not rental.is_returned:
            continue
        if not include_completed and rental.is_returned:
            continue
        if vehicle_type and rental.vehicle.__class__.__name__ != vehicle_type:
            continue
        
        total += rental.total_cost
        count += 1
    
    return {
        "total_revenue": total,
        "rental_count": count,
        "average_revenue": total / count if count > 0 else 0.0
    }


# ============================================================
# 2. Property Decorators Demonstration
# ============================================================

class RentalStatistics:
    """Demonstrates property decorators for computed values."""
    
    def __init__(self, rentals: List[Rental]):
        self._rentals = rentals
    
    @property
    def total_rentals(self) -> int:
        """Get total number of rentals."""
        return len(self._rentals)
    
    @property
    def active_rentals(self) -> int:
        """Get number of active rentals."""
        return sum(1 for r in self._rentals if not r.is_returned)
    
    @property
    def completed_rentals(self) -> int:
        """Get number of completed rentals."""
        return sum(1 for r in self._rentals if r.is_returned)
    
    @property
    def total_revenue(self) -> float:
        """Calculate total revenue from all rentals."""
        return sum(r.total_cost for r in self._rentals)
    
    @property
    def average_rental_value(self) -> float:
        """Calculate average value per rental."""
        if not self._rentals:
            return 0.0
        return self.total_revenue / len(self._rentals)
    
    @property
    def overdue_count(self) -> int:
        """Get number of overdue rentals."""
        return sum(1 for r in self._rentals 
                  if not r.is_returned and r.is_overdue)


# ============================================================
# 3. Polymorphism Demonstration
# ============================================================

def demonstrate_polymorphism():
    """Show how different vehicle types implement the same interface."""
    
    # Create different vehicle types
    vehicles = [
        Car("V001", "Toyota", "Camry", 2022, 4, "Hybrid"),
        Truck("V002", "Ford", "F-150", 2020, 5.0),
        Bike("V003", "Yamaha", "R15", 2023, 155)
    ]
    
    print("\n" + "="*60)
    print("POLYMORPHISM DEMONSTRATION")
    print("="*60)
    
    # Same method call, different implementations
    for vehicle in vehicles:
        print(f"\n{vehicle.get_vehicle_type()}")
        print(f"  1 day:  ${vehicle.calculate_rental_cost(1):.2f}")
        print(f"  7 days: ${vehicle.calculate_rental_cost(7):.2f}")
        print(f"  30 days: ${vehicle.calculate_rental_cost(30):.2f}")


# ============================================================
# 4. Usage Examples
# ============================================================

def example_usage():
    """Demonstrate the usage of *args and **kwargs functions."""
    
    # Create sample vehicles
    car1 = Car("V001", "Toyota", "Camry", 2022)
    car2 = Car("V002", "Honda", "Civic", 2021)
    truck1 = Truck("V003", "Ford", "F-150", 2020, 5.0)
    bike1 = Bike("V004", "Yamaha", "R15", 2023, 155)
    
    print("\n" + "="*60)
    print("*ARGS AND **KWARGS DEMONSTRATION")
    print("="*60)
    
    # Example 1: Simple summary
    print("\n1. Simple Summary (all vehicles):")
    summary1 = create_vehicle_summary(car1, car2, truck1, bike1)
    print(f"   Total vehicles: {summary1['total_vehicles']}")
    
    # Example 2: Summary with pricing
    print("\n2. Summary with Pricing:")
    summary2 = create_vehicle_summary(
        car1, car2, truck1, bike1,
        include_pricing=True,
        format="detailed"
    )
    for v in summary2['vehicles']:
        print(f"   {v['brand']} {v['model']}: ${v['daily_rate']:.2f}/day")
    
    # Example 3: Filtered summary
    print("\n3. Filtered Summary (Cars only):")
    summary3 = create_vehicle_summary(
        car1, car2, truck1, bike1,
        filter_type="Car"
    )
    print(f"   Cars found: {len(summary3['vehicles'])}")
    
    # Example 4: Revenue calculation
    print("\n4. Revenue Calculation:")
    rental1 = Rental("R001", car1, "John", "john@example.com", 5)
    rental2 = Rental("R002", truck1, "Jane", "jane@example.com", 3)
    
    revenue = calculate_total_revenue(
        rental1, rental2,
        include_active=True,
        include_completed=True
    )
    print(f"   Total Revenue: ${revenue['total_revenue']:.2f}")
    print(f"   Average per Rental: ${revenue['average_revenue']:.2f}")


if __name__ == "__main__":
    # Run demonstrations
    demonstrate_polymorphism()
    example_usage()
    
    print("\n" + "="*60)
    print("All demonstrations completed!")
    print("="*60 + "\n")
