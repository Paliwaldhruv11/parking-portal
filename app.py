from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Use SQLite database file
db_path = 'parking_portal.db'
db = sqlite3.connect(db_path, check_same_thread=False)
cursor = db.cursor()

# Create tables if they don't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS Vehicles (
    vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_number TEXT UNIQUE,
    vehicle_type TEXT,
    owner_name TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS ParkingSpaces (
    space_id INTEGER PRIMARY KEY AUTOINCREMENT,
    is_occupied INTEGER DEFAULT 0
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS ParkingRecords (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER,
    space_id INTEGER,
    entry_time TEXT,
    exit_time TEXT,
    total_parking_duration INTEGER,
    FOREIGN KEY (vehicle_id) REFERENCES Vehicles(vehicle_id),
    FOREIGN KEY (space_id) REFERENCES ParkingSpaces(space_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS PaymentRecords (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER,
    payment_amount REAL,
    payment_time TEXT,
    FOREIGN KEY (record_id) REFERENCES ParkingRecords(record_id)
)
''')

# Insert some default parking spaces if none exist
cursor.execute("SELECT COUNT(*) FROM ParkingSpaces")
if cursor.fetchone()[0] == 0:
    for i in range(1, 11):  # 10 parking spaces
        cursor.execute("INSERT INTO ParkingSpaces (space_id) VALUES (?)", (i,))
    db.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/park', methods=['GET', 'POST'])
def park():
    if request.method == 'POST':
        reg = request.form['reg_number']
        owner = request.form['owner_name']
        v_type = request.form['vehicle_type']

        cursor.execute("INSERT INTO Vehicles (registration_number, vehicle_type, owner_name) VALUES (?, ?, ?)", (reg, v_type, owner))
        db.commit()

        cursor.execute("SELECT space_id FROM ParkingSpaces WHERE is_occupied = 0 LIMIT 1")
        space = cursor.fetchone()
        if not space:
            return "No space available"
        space_id = space[0]

        cursor.execute("UPDATE ParkingSpaces SET is_occupied = 1 WHERE space_id = ?", (space_id,))
        entry_time = datetime.now()
        cursor.execute("SELECT vehicle_id FROM Vehicles WHERE registration_number = ?", (reg,))
        vehicle_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO ParkingRecords (vehicle_id, space_id, entry_time) VALUES (?, ?, ?)", (vehicle_id, space_id, str(entry_time)))
        db.commit()
        return redirect('/view')
    return render_template('park.html')

@app.route('/exit', methods=['GET', 'POST'])
def vehicle_exit():
    if request.method == 'POST':
        reg = request.form['reg_number']
        cursor.execute("SELECT vehicle_id FROM Vehicles WHERE registration_number = ?", (reg,))
        vehicle = cursor.fetchone()
        if not vehicle:
            return "Vehicle not found."
        vehicle_id = vehicle[0]

        cursor.execute("SELECT record_id, space_id, entry_time FROM ParkingRecords WHERE vehicle_id = ? AND exit_time IS NULL", (vehicle_id,))
        record = cursor.fetchone()
        if not record:
            return "Vehicle is not currently parked."
        record_id, space_id, entry_time_str = record
        entry_time = datetime.fromisoformat(entry_time_str)

        exit_time = datetime.now()
        duration = int((exit_time - entry_time).total_seconds())
        amount = duration * 0.10  # ₹0.10 per second

        cursor.execute("UPDATE ParkingSpaces SET is_occupied = 0 WHERE space_id = ?", (space_id,))
        cursor.execute("UPDATE ParkingRecords SET exit_time = ?, total_parking_duration = ? WHERE record_id = ?", (str(exit_time), duration, record_id))
        cursor.execute("INSERT INTO PaymentRecords (record_id, payment_amount, payment_time) VALUES (?, ?, ?)", (record_id, amount, str(exit_time)))
        db.commit()
        return f"Vehicle exited. Total time: {duration}s. Payment: ₹{round(amount,2)}"
    return render_template('exit.html')

@app.route('/view')
def view():
    cursor.execute("""
        SELECT v.registration_number, v.owner_name, v.vehicle_type, p.space_id, r.entry_time
        FROM Vehicles v
        JOIN ParkingRecords r ON v.vehicle_id = r.vehicle_id
        JOIN ParkingSpaces p ON p.space_id = r.space_id
        WHERE r.exit_time IS NULL
    """)
    vehicles = cursor.fetchall()
    return render_template('view.html', vehicles=vehicles)

@app.route('/reset')
def reset():
    cursor.execute("UPDATE ParkingSpaces SET is_occupied = 0")
    db.commit()
    return "All parking spaces have been reset."

if __name__ == '__main__':
    app.run(debug=True)
