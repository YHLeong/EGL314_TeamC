import RPi.GPIO as GPIO
import tkinter as tk
import random

# Map sensor numbers (1–6) to GPIO pins.
SENSOR_MAP = {1: 5, 2: 6, 3: 19, 4: 16, 5: 20, 6: 21}

# Setup GPIO
GPIO.setmode(GPIO.BCM)
for pin in SENSOR_MAP.values():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Tkinter setup
root = tk.Tk()
root.title("Sensor Randomizer")
tk.Label(root, text="Press the displayed sensor!", font=("Arial", 16)).pack(pady=10)
sensor_label = tk.Label(root, text="Waiting...", font=("Arial", 14))
sensor_label.pack(pady=10)

current_sensor = None  # Currently displayed sensor number
waiting = False       # Flag to prevent repeated triggering

def randomize_sensor():
    global current_sensor, waiting
    waiting = False
    current_sensor = random.choice(list(SENSOR_MAP))  # Select one random sensor number
    sensor_label.config(text=f"Press sensor {current_sensor}")

def check_sensor():
    global waiting
    if not waiting and current_sensor is not None:
        # Check the corresponding GPIO pin, LOW means pressed.
        if GPIO.input(SENSOR_MAP[current_sensor]) == GPIO.LOW:
            print(f"Sensor {current_sensor} pressed!")
            waiting = True  # Prevent further checks until new sensor is randomized.
            root.after(2000, randomize_sensor)  # Wait 2 seconds, then randomize.
    root.after(100, check_sensor)  # Check sensor input every 100ms

# Start by randomizing the first sensor and initiating the check loop.
randomize_sensor()
check_sensor()

try:
    root.mainloop()
finally:
    GPIO.cleanup()
