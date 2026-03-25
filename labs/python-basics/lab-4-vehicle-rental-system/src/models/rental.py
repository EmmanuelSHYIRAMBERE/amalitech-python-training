"""Rental management and transaction tracking."""

from typing import Optional
from datetime import datetime, timedelta
from src.models.vehicle import Vehicle

class Rental:
    """Rental transaction class."""
    
    def __init__(self, rental_id: str, vehicle: Vehicle, customer_name: str,
                 customer_email: str, rental_days: int):
        self._rental_id = rental_id
        self._vehicle = vehicle
        self._customer_name = customer_name
        self._customer_email = customer_email
        self._rental_days = rental_days
        self._start_date = datetime.now()
        self._end_date = self._start_date + timedelta(days=rental_days)
        self._returned = False
        self._return_date: Optional[datetime] = None
        self._total_cost = vehicle.calculate_rental_cost(rental_days)
    
    @property
    def rental_id(self) -> str:
        """Get rental ID."""
        return self._rental_id
    
    @property
    def vehicle(self) -> Vehicle:
        """Get rented vehicle."""
        return self._vehicle
    
    @property
    def customer_name(self) -> str:
        """Get customer name."""
        return self._customer_name
    
    @property
    def rental_days(self) -> int:
        """Get rental duration in days."""
        return self._rental_days
    
    @property
    def total_cost(self) -> float:
        """Get total rental cost."""
        return self._total_cost
    
    @property
    def is_returned(self) -> bool:
        """Check if vehicle has been returned."""
        return self._returned
    
    @property
    def is_overdue(self) -> bool:
        """Check if rental is overdue."""
        if self._returned:
            return False
        return datetime.now() > self._end_date
    
    def complete_return(self) -> float:
        """Complete the return and calculate final cost."""
        if self._returned:
            return self._total_cost
        
        self._returned = True
        self._return_date = datetime.now()
        
        # Calculate late fees if overdue
        if self.is_overdue:
            days_late = (self._return_date - self._end_date).days
            late_fee = days_late * (self._total_cost / self._rental_days) * 1.5
            self._total_cost += late_fee
        
        return self._total_cost
    
    def __str__(self) -> str:
        """User-friendly representation."""
        status = "Returned" if self._returned else "Active"
        return f"Rental {self._rental_id}: {self._customer_name} - {self._vehicle.brand} {self._vehicle.model} ({status})"
