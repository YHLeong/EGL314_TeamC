import RPi.GPIO as GPIO
import tkinter as tk
import random
import time

# Sensor mapping: Sensor numbers 1-6 mapped to GPIO pins
SENSOR_MAP = {1: 5, 2: 6, 3: 19, 4: 16, 5: 20, 6: 21}
SENSOR_PINS = list(SENSOR_MAP.values())  # Extract the pin numbers for GPIO setup

# GPIO setup
GPIO.setmode(GPIO.BCM)
for pin in SENSOR_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Tkinter setup
root = tk.Tk()
root.title("Sensor Randomizer")

status_label = tk.Label(root, text="Press the displayed sensor!", font=("Arial", 16))
status_label.grid(row=0, column=0, pady=10)


sensor_label = tk.Label(root, text="Waiting...", font=("Arial", 16))
status_label.grid(row=0, column=0, pady=10)

current_sensor = None  # Store the currently displayed sensor

# Select and display a single random sensor.
def randomize_sensor():
    global current_sensor
    current_sensor = random.choice(list(SENSOR_MAP.keys()))  # Pick sensor number
    sensor_label.config(text=f"Press sensor {current_sensor}")
    root.update()

# Check if the correct sensor has been pressed before randomising again.
def check_sensor_press():
    global current_sensor

    correct_pin = SENSOR_MAP[current_sensor]  # Get the corresponding GPIO pin

    if GPIO.input(correct_pin) == GPIO.LOW:
        print(f"Sensor {current_sensor} pressed!")  # Debugging print
        time.sleep(2)  # 2-second delay before a new sensor is selected
        randomize_sensor()  # Choose the next sensor

    root.after(100, check_sensor_press)  # checking of sensor input

# Start the program by selecting an initial sensor
randomize_sensor()
check_sensor_press()  # Start monitoring sensor presses

# Run the GUI
try:
    root.mainloop()
finally:
    GPIO.cleanup()
