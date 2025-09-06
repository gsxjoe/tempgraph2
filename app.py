import threading
import time
#added_____________________________________________________
import base64
import io
#end added______________________________________________
from flask import Flask, render_template, jsonify
#added__________________________________________
from matplotlib.figure import Figure
#end added___________________________________________
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import ImageFont
from max6675 import MAX6675

# --- Hardware Configuration ---
# GPIO setup for luma.oled, specifying CS and DC pins
oled_serial = spi(port=0, device=0, cs_high=True, reset=5, dc=6)
oled_device = sh1106(oled_serial)
# MAX6675 sensors using SPI0 bus, with CS on CE0 (device=0) and CE1 (device=1)
sensor1 = MAX6675(bus=0, device=0)
sensor2 = MAX6675(bus=0, device=1)

# Font for the OLED display
font = ImageFont.load_default()

# --- Application State ---
temperature_data = {"sensor1": "N/A", "sensor2": "N/A"}

# --- Background Thread for Sensor Reading and OLED Display ---
def update_sensors():
    global temperature_data
    while True:
        temp1 = sensor1.read_temp()
        temp2 = sensor2.read_temp()
# changed .2f to .1f to bring back only one decimal point and changed C to F for label        
        temperature_data["sensor1"] = f"{temp1:.1f}°F" if not isinstance(temp1, float) or not temp1 is float("NaN") else "Disconnected"
        temperature_data["sensor2"] = f"{temp2:.1f}°F" if not isinstance(temp2, float) or not temp2 is float("NaN") else "Disconnected"

        with canvas(oled_device) as draw:
            draw.text((0, 0), "Temp 1:    " + temperature_data["sensor1"], font=font, fill="white")
            draw.text((0, 20), "Temp 2:    " + temperature_data["sensor2"], font=font, fill="white")

        time.sleep(5)

# --- Flask Web Server ---
app = Flask(__name__, template_folder='templates')
#added code______________________________________________________________________________
# Store a history of temperature data for the plot
temperature_history = []
time_history = []
MAX_DATA_POINTS = 60  # Store 60 data points for one minute of history
def read_temperature():
    """Reads the temperature from the MAX6675 sensor."""
    try:
        temp_c = sensor2.read_temp() # Read temperature in Fahrenheit
        return round(temp_c, 1)
    except Exception as e:
        print(f"Error reading sensor: {e}")
        return None

def create_figure():
    """Generates the Matplotlib plot."""
    # Ensure data lists are not empty
    if not temperature_history:
        fig = Figure(figsize=(8, 6))
        ax = fig.subplots()
        ax.set_title("MAX6675 Temperature Data")
        ax.set_xlabel("Time (seconds ago)")
        ax.set_ylabel("Temperature (°F)")
        ax.text(0.5, 0.5, "Waiting for data...", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        return fig

    # Create the figure **without using pyplot** to prevent memory leaks.
    fig = Figure(figsize=(8, 6))
    ax = fig.subplots()

    # Get data from the past to present
    times = [i for i in range(len(time_history))]

    ax.plot(times, temperature_history)
    ax.set_title("MAX6675 Temperature Data")
    ax.set_xlabel("Time (seconds ago)")
    ax.set_ylabel("Temperature (°F)")
    ax.grid(True)
    return fig
#end added________________________________________________________________________________________________________________________________________________________

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    return jsonify(temperature_data)
#added code________________________________________________________________________________________________
@app.route("/update_data")
def update_data():
    """Reads sensor data and appends it to history."""
    temp_c = read_temperature()
    if temp_c is not None:
        if len(temperature_history) >= MAX_DATA_POINTS:
            temperature_history.pop(0)
            time_history.pop(0)
        temperature_history.append(temp_c)
        time_history.append(time.time())
    return "Data updated", 200
#end added_____________________________________________________________________________________________________

if __name__ == '__main__':
    #added code____________________________________________
     from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

    # Continuously update the sensor data in the background
    import threading
    def data_thread():
        while True:
            read_temperature()
            time.sleep(1) # Read data every second
#end Added_______________________________________________________________________
    # Start the background thread for sensor updates
    thread = threading.Thread(target=update_sensors)
    thread.daemon = True
    thread.start()
    
    # Run the Flask web server
    app.run(host='0.0.0.0', port=5000, debug=False)





