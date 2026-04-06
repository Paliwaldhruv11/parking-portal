# Parking Portal

A simple Flask-based parking management system that allows users to park vehicles, track parking duration, and calculate payments.

## Features

- Park vehicles with registration number, owner name, and vehicle type
- Track parking duration and calculate payments (₹0.10 per second)
- View currently parked vehicles
- Exit vehicles and generate payment receipts
- Reset all parking spaces

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/parking-portal.git
   cd parking-portal
   ```

2. Install dependencies:
   ```bash
   pip install flask
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and go to `http://127.0.0.1:5000/`

## Database

The application uses SQLite database (`parking_portal.db`) which is created automatically when you first run the app. The database includes:
- Vehicles table
- ParkingSpaces table (10 spaces by default)
- ParkingRecords table
- PaymentRecords table

## Usage

1. **Park Vehicle**: Enter vehicle details and park
2. **Exit Vehicle**: Enter registration number to exit and calculate payment
3. **View Parked Vehicles**: See all currently parked vehicles
4. **Reset Spaces**: Clear all parking spaces (admin function)

## Technologies Used

- Python Flask
- SQLite
- HTML/CSS

## License

MIT License