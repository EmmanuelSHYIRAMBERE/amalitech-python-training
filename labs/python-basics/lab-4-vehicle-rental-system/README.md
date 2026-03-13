# Vehicle Rental System

A comprehensive console-based application for managing vehicle rentals including cars, trucks, and bikes with dynamic pricing and rental management.

## Features

- **Vehicle Management**: Add and manage cars, trucks, and bikes with unique attributes
- **Rental Management**: Create rentals, track active rentals, and process returns
- **Dynamic Pricing**: Calculate rental costs based on vehicle type, duration, and discounts
- **Overdue Tracking**: Monitor and apply late fees for overdue rentals
- **Reporting**: Generate detailed reports with tabular formatting
- **Statistics**: View system-wide statistics and revenue analytics

## Technical Highlights

- Python 3.10+ with type hints
- Object-Oriented Design with inheritance and polymorphism
- Abstract Base Classes for uniform vehicle operations
- Property decorators for encapsulation
- Comprehensive error handling
- Colorful console output using colorama
- Tabulated reports using tabulate

## Prerequisites

- Python 3.10 or higher
- Poetry (Python dependency management tool)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/EmmanuelSHYIRAMBERE/Lab-4-Vehicle-Rental-System.git
cd Lab-4-Vehicle-Rental-System
```

### 2. Install Dependencies with Poetry

```bash
poetry install
```

## Usage

### Running the Application

```bash
poetry run python main.py
```

## 🧪 Run Tests

```bash
poetry run pytest tests/ -v
```

## 🎨 Run Feature Demo

```bash
poetry run python demo_features.py
```

### Main Menu Options

The application provides an interactive menu system with the following main options:

1. **Vehicle Management**
   - Add Car
   - Add Truck
   - Add Bike
   - View All Vehicles
   - View Vehicle Details
   - Remove Vehicle

2. **Rental Management**
   - Create New Rental
   - View All Rentals
   - View Rental Details
   - View Active Rentals
   - View Overdue Rentals

3. **Return Vehicle**
   - Process vehicle returns
   - Calculate final costs with late fees

4. **View Available Vehicles**
   - Browse vehicles ready for rent

5. **Generate Reports**
   - Vehicle Inventory Report
   - Rental Transaction Report
   - Revenue & Statistics Report
   - Generate All Reports

6. **View Statistics**
   - System-wide statistics
   - Fleet utilization metrics
   - Revenue analytics
   - Vehicle type breakdown

## Example Output

### Main Menu

```
============================================================
Welcome to the Vehicle Rental System
============================================================

1. Vehicle Management
2. Rental Management
3. Return Vehicle
4. View Available Vehicles
5. Generate Reports
6. View Statistics
0. Exit

Enter your choice:
```

### Available Vehicles

```
🟢 AVAILABLE VEHICLES
------------------------------------------------------------

Car (4-door, Hybrid): Toyota Camry (2022) - Available
  Daily Rate: $60.00

Truck (5.0T capacity): Chevrolet Silverado (2022) - Available
  Daily Rate: $150.00

Bike (500cc): Honda CBR500R (2022) - Available
  Daily Rate: $24.00
```

### Rental Cost Breakdown

```
💰 Rental Cost Breakdown:
  Base Cost: $420.00
  Discount: -$42.00
  Final Cost: $378.00
```

### System Statistics

```
📊 SYSTEM STATISTICS
============================================================

🚗 FLEET OVERVIEW
  Total Vehicles: 8
  Available: 6
  Rented: 2
  Utilization Rate: 25.0%

📝 RENTAL OVERVIEW
  Total Rentals: 2
  Active: 2
  Completed: 0

💰 REVENUE
  Total Revenue: $378.00
  Average per Rental: $189.00

🚙 VEHICLE TYPE BREAKDOWN
  • Car: 3 (37.5%)
  • Truck: 2 (25.0%)
  • Bike: 3 (37.5%)
```

## Project Structure

```
vehicle-rental-system/
├── src/
│   ├── models/
│   │   ├── vehicle.py          # Vehicle classes (Car, Truck, Bike)
│   │   └── rental.py           # Rental transaction management
│   ├── reports/
│   │   └── report_generator.py # Report generation classes
│   └── utils/
│       └── helpers.py          # Utility functions
├── tests/
│   └── test_vehicle.py         # Unit tests
├── main.py                     # Application entry point
├── app.py                      # Main application class
├── menu_handlers.py            # Menu and UI logic
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

## Sample Data

The application comes pre-loaded with sample data:

**Vehicles:**

- Toyota Camry 2022 (Car, Hybrid)
- Honda Civic 2021 (Car, Petrol)
- Tesla Model 3 2023 (Car, Electric)
- Ford F-150 2020 (Truck, 3.5T)
- Chevrolet Silverado 2022 (Truck, 5.0T)
- Yamaha R15 2023 (Bike, 155cc)
- Harley-Davidson Street 750 2021 (Bike, 750cc)
- Honda CBR500R 2022 (Bike, 500cc)

**Active Rentals:**

- John Doe renting Toyota Camry for 5 days
- Jane Smith renting Yamaha R15 for 3 days

## Features in Detail

### Vehicle Types

1. **Cars**
   - Number of doors (2/4)
   - Fuel type (Petrol/Diesel/Electric/Hybrid)
   - Base rate: $50/day
   - 20% premium for 2020+ models

2. **Trucks**
   - Cargo capacity in tons
   - Base rate: $100/day
   - Additional $10/day per ton capacity

3. **Bikes**
   - Engine capacity in CC
   - Base rate: $20/day
   - 20% premium for 250-500cc
   - 50% premium for 500cc+

### Pricing & Discounts

- **7-14 days**: 10% discount
- **14-30 days**: 15% discount
- **30+ days**: 20% discount
- **Late fees**: 1.5x daily rate per day overdue

### Rental Features

- Customer information tracking
- Rental duration management
- Automatic cost calculation
- Overdue detection
- Late fee calculation
- Return processing

### Reporting Features

- **Vehicle Reports**: Complete inventory with status
- **Rental Reports**: Transaction history with costs
- **Revenue Reports**: Financial analytics and statistics
- Export reports to text files with timestamps

## Error Handling

The application includes comprehensive error handling:

- Input validation for all user entries
- Email format validation
- Duplicate ID prevention
- Vehicle availability checking
- Rental status validation
- Graceful handling of keyboard interrupts

## Tips

- Use `Ctrl+C` to safely exit the application at any time
- Reports can be saved to files with automatic timestamps
- The system validates all inputs to prevent errors
- Sample data is loaded automatically for testing
- Longer rental periods receive automatic discounts

## Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'colorama'`

- **Solution**: Install dependencies using `poetry install`

**Issue**: Colors not displaying correctly on Windows

- **Solution**: The application uses colorama which automatically handles Windows console colors

**Issue**: Application crashes on startup

- **Solution**: Ensure Python 3.10+ is installed: `python --version`

## Running Tests

```bash
poetry run pytest tests/
```

## Contributing

Contributions are welcome! Please ensure:

- Code follows PEP 8 style guidelines
- Type hints are included
- Error handling is comprehensive
- Documentation is updated

## License

This project is available for educational purposes.

## Author

EmmanuelSHYIRAMBERE (emashyirambere1@gmail.com)
