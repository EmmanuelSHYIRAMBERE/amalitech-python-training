"""Vehicle classes with inheritance and polymorphism."""

from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime

class Vehicle(ABC):
    """Abstract base class for all vehicle types."""
    
    def __init__(self, vehicle_id: str, brand: str, model: str, year: int):
        self._vehicle_id = vehicle_id
        self._brand = brand
        self._model = model
        self._year = year
        self._is_rented = False
        self._rented_by: Optional[str] = None
        self._rental_start: Optional[datetime] = None
    
    @property
    def vehicle_id(self) -> str:
        """Get vehicle ID."""
        return self._vehicle_id
    
    @property
    def brand(self) -> str:
        """Get vehicle brand."""
        return self._brand
    
    @property
    def model(self) -> str:
        """Get vehicle model."""
        return self._model
    
    @property
    def year(self) -> int:
        """Get vehicle year."""
        return self._year
    
    @property
    def is_rented(self) -> bool:
        """Check if vehicle is currently rented."""
        return self._is_rented
    
    @property
    def rented_by(self) -> Optional[str]:
        """Get customer who rented the vehicle."""
        return self._rented_by
    
    @abstractmethod
    def calculate_rental_cost(self, days: int) -> float:
        """Calculate rental cost based on vehicle type and duration."""
        pass
    
    @abstractmethod
    def get_vehicle_type(self) -> str:
        """Get vehicle type description."""
        pass
    
    def rent(self, customer_name: str) -> bool:
        """Rent the vehicle to a customer."""
        if self._is_rented:
            return False
        self._is_rented = True
        self._rented_by = customer_name
        self._rental_start = datetime.now()
        return True
    
    def return_vehicle(self) -> bool:
        """Return the vehicle."""
        if not self._is_rented:
            return False
        self._is_rented = False
        self._rented_by = None
        self._rental_start = None
        return True
    
    def __str__(self) -> str:
        """User-friendly representation."""
        status = "Rented" if self._is_rented else "Available"
        return f"{self.get_vehicle_type()}: {self._brand} {self._model} ({self._year}) - {status}"
    
    def __repr__(self) -> str:
        """Developer representation."""
        return f"{self.__class__.__name__}(id='{self._vehicle_id}', brand='{self._brand}')"

class Car(Vehicle):
    """Car vehicle implementation."""
    
    DAILY_RATE = 50.0
    
    def __init__(self, vehicle_id: str, brand: str, model: str, year: int, 
                 num_doors: int = 4, fuel_type: str = "Petrol"):
        super().__init__(vehicle_id, brand, model, year)
        self._num_doors = num_doors
        self._fuel_type = fuel_type
    
    @property
    def num_doors(self) -> int:
        """Get number of doors."""
        return self._num_doors
    
    @property
    def fuel_type(self) -> str:
        """Get fuel type."""
        return self._fuel_type
    
    def calculate_rental_cost(self, days: int) -> float:
        """Calculate car rental cost."""
        base_cost = self.DAILY_RATE * days
        # Premium for newer cars
        if self._year >= 2020:
            base_cost *= 1.2
        return base_cost
    
    def get_vehicle_type(self) -> str:
        """Get vehicle type."""
        return f"Car ({self._num_doors}-door, {self._fuel_type})"

class Truck(Vehicle):
    """Truck vehicle implementation."""
    
    DAILY_RATE = 100.0
    CAPACITY_RATE = 10.0  # Per ton
    
    def __init__(self, vehicle_id: str, brand: str, model: str, year: int,
                 capacity_tons: float = 5.0):
        super().__init__(vehicle_id, brand, model, year)
        self._capacity_tons = capacity_tons
    
    @property
    def capacity_tons(self) -> float:
        """Get cargo capacity in tons."""
        return self._capacity_tons
    
    def calculate_rental_cost(self, days: int) -> float:
        """Calculate truck rental cost."""
        base_cost = self.DAILY_RATE * days
        capacity_cost = self.CAPACITY_RATE * self._capacity_tons * days
        return base_cost + capacity_cost
    
    def get_vehicle_type(self) -> str:
        """Get vehicle type."""
        return f"Truck ({self._capacity_tons}T capacity)"

class Bike(Vehicle):
    """Bike vehicle implementation."""
    
    DAILY_RATE = 20.0
    
    def __init__(self, vehicle_id: str, brand: str, model: str, year: int,
                 engine_cc: int = 150):
        super().__init__(vehicle_id, brand, model, year)
        self._engine_cc = engine_cc
    
    @property
    def engine_cc(self) -> int:
        """Get engine capacity in CC."""
        return self._engine_cc
    
    def calculate_rental_cost(self, days: int) -> float:
        """Calculate bike rental cost."""
        base_cost = self.DAILY_RATE * days
        # Premium for larger engines
        if self._engine_cc > 500:
            base_cost *= 1.5
        elif self._engine_cc > 250:
            base_cost *= 1.2
        return base_cost
    
    def get_vehicle_type(self) -> str:
        """Get vehicle type."""
        return f"Bike ({self._engine_cc}cc)"
