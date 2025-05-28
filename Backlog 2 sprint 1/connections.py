import RPi.GPIO as GPIO
import tkinter as tk

# Sensor mapping: sensor numbers 1–6 mapped to specific GPIO pins
SENSOR_MAP = {1: 5, 2: 6, 3: 19, 4: 16, 5: 20, 6: 21}
SENSOR_PINS = list(SENSOR_MAP.values())

# Setup GPIO with BCM numbering and configure each sensor pin
GPIO.setmode(GPIO.BCM)
for pin in SENSOR_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Create Tkinter window
root = tk.Tk()
root.title("Sensor Connection Status")

# Create a label for each sensor using the SENSOR_MAP
labels = {}
for sensor_num, pin in sorted(SENSOR_MAP.items()):
    label = tk.Label(root, text=f"Sensor {sensor_num} (Pin {pin}): Checking...", font=("Arial", 16))
    label.grid(row=0, column=0, pady=5)
    labels[sensor_num] = label

# Update each sensor's status based on its GPIO input.
def update_status():
    for sensor_num, pin in sorted(SENSOR_MAP.items()):
        status = "Pressed" if GPIO.input(pin) == GPIO.LOW else "Not Pressed"
        labels[sensor_num].config(text=f"Sensor {sensor_num} (Pin {pin}): {status}")
    root.after(500, update_status)  # Update every 500 milliseconds

# Start the status update loop
update_status()

# Run the GUI main loop with GPIO cleanup on exit.
try:
    root.mainloop()
finally:
    GPIO.cleanup()
