"""Report generation using ABC and polymorphism."""

from abc import ABC, abstractmethod
from typing import List, Any
from datetime import datetime
from tabulate import tabulate
from colorama import Fore, Style, init

init(autoreset=True)

class ReportGenerator(ABC):
    """Abstract base class for report generators."""
    
    def __init__(self, title: str):
        self.title = title
        self.generated_at = datetime.now()
    
    @abstractmethod
    def generate(self) -> str:
        """Generate the report content."""
        pass
    
    @abstractmethod
    def get_data(self) -> List[Any]:
        """Get the data for the report."""
        pass
    
    def _format_header(self) -> str:
        """Format report header."""
        header = f"\n{Fore.CYAN}{'='*70}\n"
        header += f"{self.title.center(70)}\n"
        header += f"{'='*70}{Style.RESET_ALL}\n"
        header += f"Generated: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        return header

class VehicleReport(ReportGenerator):
    """Vehicle inventory report generator."""
    
    def __init__(self, vehicles: List):
        super().__init__("VEHICLE INVENTORY REPORT")
        self._vehicles = vehicles
    
    def get_data(self) -> List[Any]:
        return self._vehicles
    
    def generate(self) -> str:
        """Generate vehicle report."""
        report = self._format_header()
        
        if not self._vehicles:
            report += f"{Fore.YELLOW}No vehicles found.{Style.RESET_ALL}\n"
            return report
        
        table_data = []
        for vehicle in self._vehicles:
            status = "🔴 Rented" if vehicle.is_rented else "🟢 Available"
            rented_by = vehicle.rented_by if vehicle.is_rented else "-"
            table_data.append([
                vehicle.vehicle_id,
                vehicle.brand,
                vehicle.model,
                vehicle.year,
                vehicle.get_vehicle_type(),
                status,
                rented_by
            ])
        
        headers = ["ID", "Brand", "Model", "Year", "Type", "Status", "Rented By"]
        report += tabulate(table_data, headers=headers, tablefmt="grid")
        
        available = sum(1 for v in self._vehicles if not v.is_rented)
        rented = len(self._vehicles) - available
        report += f"\n\n{Fore.GREEN}Total Vehicles: {len(self._vehicles)} | "
        report += f"Available: {available} | Rented: {rented}{Style.RESET_ALL}\n"
        
        return report

class RentalReport(ReportGenerator):
    """Rental transaction report generator."""
    
    def __init__(self, rentals: List):
        super().__init__("RENTAL TRANSACTION REPORT")
        self._rentals = rentals
    
    def get_data(self) -> List[Any]:
        return self._rentals
    
    def generate(self) -> str:
        """Generate rental report."""
        report = self._format_header()
        
        if not self._rentals:
            report += f"{Fore.YELLOW}No rentals found.{Style.RESET_ALL}\n"
            return report
        
        table_data = []
        for rental in self._rentals:
            status = "✅ Returned" if rental.is_returned else "🔄 Active"
            if not rental.is_returned and rental.is_overdue:
                status = "⚠️ Overdue"
            
            table_data.append([
                rental.rental_id,
                rental.customer_name,
                f"{rental.vehicle.brand} {rental.vehicle.model}",
                rental.rental_days,
                f"${rental.total_cost:.2f}",
                status
            ])
        
        headers = ["Rental ID", "Customer", "Vehicle", "Days", "Cost", "Status"]
        report += tabulate(table_data, headers=headers, tablefmt="grid")
        
        total_revenue = sum(r.total_cost for r in self._rentals)
        active = sum(1 for r in self._rentals if not r.is_returned)
        report += f"\n\n{Fore.GREEN}Total Rentals: {len(self._rentals)} | "
        report += f"Active: {active} | Revenue: ${total_revenue:.2f}{Style.RESET_ALL}\n"
        
        return report

class RevenueReport(ReportGenerator):
    """Revenue and statistics report generator."""
    
    def __init__(self, rentals: List, vehicles: List):
        super().__init__("REVENUE & STATISTICS REPORT")
        self._rentals = rentals
        self._vehicles = vehicles
    
    def get_data(self) -> List[Any]:
        return self._rentals
    
    def generate(self) -> str:
        """Generate revenue report."""
        report = self._format_header()
        
        total_revenue = sum(r.total_cost for r in self._rentals)
        completed_revenue = sum(r.total_cost for r in self._rentals if r.is_returned)
        active_revenue = total_revenue - completed_revenue
        
        report += f"\n{Fore.CYAN}💰 REVENUE SUMMARY{Style.RESET_ALL}\n"
        report += f"Total Revenue: ${total_revenue:.2f}\n"
        report += f"Completed Rentals Revenue: ${completed_revenue:.2f}\n"
        report += f"Active Rentals Revenue: ${active_revenue:.2f}\n"
        
        # Vehicle type breakdown
        vehicle_types = {}
        for rental in self._rentals:
            v_type = rental.vehicle.__class__.__name__
            if v_type not in vehicle_types:
                vehicle_types[v_type] = {"count": 0, "revenue": 0.0}
            vehicle_types[v_type]["count"] += 1
            vehicle_types[v_type]["revenue"] += rental.total_cost
        
        report += f"\n{Fore.CYAN}📊 VEHICLE TYPE BREAKDOWN{Style.RESET_ALL}\n"
        for v_type, data in vehicle_types.items():
            report += f"  • {v_type}: {data['count']} rentals, ${data['revenue']:.2f}\n"
        
        # Fleet utilization
        total_vehicles = len(self._vehicles)
        rented_vehicles = sum(1 for v in self._vehicles if v.is_rented)
        utilization = (rented_vehicles / total_vehicles * 100) if total_vehicles else 0
        
        report += f"\n{Fore.CYAN}🚗 FLEET UTILIZATION{Style.RESET_ALL}\n"
        report += f"Total Vehicles: {total_vehicles}\n"
        report += f"Currently Rented: {rented_vehicles}\n"
        report += f"Utilization Rate: {utilization:.1f}%\n"
        
        return report
