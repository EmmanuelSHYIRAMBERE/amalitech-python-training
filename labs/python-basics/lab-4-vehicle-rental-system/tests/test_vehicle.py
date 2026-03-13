import pytest
from src.models.vehicle import Car, Truck, Bike
from src.models.rental import Rental

def test_car_creation():
    """Test car creation and properties."""
    car = Car("V001", "Toyota", "Camry", 2022, 4, "Hybrid")
    assert car.vehicle_id == "V001"
    assert car.brand == "Toyota"
    assert car.model == "Camry"
    assert car.year == 2022
    assert car.num_doors == 4
    assert car.fuel_type == "Hybrid"
    assert not car.is_rented

def test_truck_creation():
    """Test truck creation and capacity."""
    truck = Truck("V002", "Ford", "F-150", 2020, 5.0)
    assert truck.vehicle_id == "V002"
    assert truck.capacity_tons == 5.0
    assert truck.get_vehicle_type() == "Truck (5.0T capacity)"

def test_bike_creation():
    """Test bike creation and engine capacity."""
    bike = Bike("V003", "Yamaha", "R15", 2023, 155)
    assert bike.vehicle_id == "V003"
    assert bike.engine_cc == 155
    assert bike.get_vehicle_type() == "Bike (155cc)"

def test_vehicle_rental():
    """Test vehicle rental functionality."""
    car = Car("V004", "Honda", "Civic", 2021)
    assert car.rent("John Doe") == True
    assert car.is_rented == True
    assert car.rented_by == "John Doe"
    assert car.rent("Jane Smith") == False  # Already rented

def test_vehicle_return():
    """Test vehicle return functionality."""
    car = Car("V005", "Tesla", "Model 3", 2023)
    car.rent("Alice")
    assert car.return_vehicle() == True
    assert car.is_rented == False
    assert car.rented_by is None

def test_rental_cost_calculation():
    """Test rental cost calculations."""
    car = Car("V006", "Toyota", "Corolla", 2019, 4, "Petrol")
    cost_1_day = car.calculate_rental_cost(1)
    cost_7_days = car.calculate_rental_cost(7)
    assert cost_7_days == cost_1_day * 7

def test_truck_cost_with_capacity():
    """Test truck rental cost includes capacity charges."""
    truck = Truck("V007", "Chevrolet", "Silverado", 2022, 3.0)
    cost = truck.calculate_rental_cost(1)
    expected = truck.DAILY_RATE + (truck.CAPACITY_RATE * 3.0)
    assert cost == expected

def test_bike_premium_pricing():
    """Test bike premium pricing for larger engines."""
    small_bike = Bike("V008", "Honda", "CBR150", 2022, 150)
    large_bike = Bike("V009", "Harley", "Street 750", 2021, 750)
    
    small_cost = small_bike.calculate_rental_cost(1)
    large_cost = large_bike.calculate_rental_cost(1)
    
    assert large_cost > small_cost

def test_rental_creation():
    """Test rental object creation."""
    car = Car("V010", "BMW", "X5", 2023)
    rental = Rental("R001", car, "Bob Smith", "bob@example.com", 5)
    
    assert rental.rental_id == "R001"
    assert rental.customer_name == "Bob Smith"
    assert rental.rental_days == 5
    assert not rental.is_returned
    assert rental.total_cost > 0

def test_rental_return():
    """Test rental return process."""
    car = Car("V011", "Audi", "A4", 2022)
    rental = Rental("R002", car, "Charlie", "charlie@example.com", 3)
    
    final_cost = rental.complete_return()
    assert rental.is_returned == True
    assert final_cost == rental.total_cost
