import csv
import time
from datetime import datetime
import os.path
from max6675 import MAX6675

# --- Application State ---
temperature_data = {"sensor1": "N/A", "sensor2": "N/A"}

# --- Replace with your sensor's library and reading function ---
#def get_sensor_data():
def update_sensors():
    global temperature_data
    while True:
        temp1 = sensor1.read_temp()
        temp2 = sensor2.read_temp()
# changed .2f to .1f to bring back only one decimal point and changed C to F for label        
        temperature_data["sensor1"] = f"{temp1:.1f}°F" if not isinstance(temp1, float) or not temp1 is float("NaN") else "Disconnected"
        temperature_data["sensor2"] = f"{temp2:.1f}°F" if not isinstance(temp2, float) or not temp2 is float("NaN") else "Disconnected"
        
        time.sleep(5)

# --- CSV logging setup ---
filename = "sensor_readings.csv"
fieldnames = ["timestamp", "Grill", "Meat"]

# Check if the file already exists to decide whether to write headers
file_exists = os.path.isfile(filename)

# Main logging loop
print("Starting sensor data logging. Press Ctrl+C to exit.")
try:
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header row only if the file is new
        if not file_exists:
            writer.writeheader()
            
        while True:
            # Get data from your sensor
            temp1, temp2 = get_sensor_data()
            
            # Create a dictionary with a timestamp and sensor data
            data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Grill": temp1,
                "Meat": temp2
            }
            
            # Write the data to the CSV file
            writer.writerow(data)
            csvfile.flush() # Ensure data is written immediately
            
            print(f"Logged: {data}")
            
            # Wait for 5 seconds before the next reading
            time.sleep(5)
            
except KeyboardInterrupt:
    print("\nLogging stopped by user. CSV file is saved.")
except Exception as e:
    print(f"An error occurred: {e}")
