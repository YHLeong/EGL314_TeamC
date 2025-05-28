import RPi.GPIO as GPIO
import tkinter as tk
import random
import time
import threading

# Sensor mapping: sensor numbers 1–6 mapped to specific GPIO pins
SENSOR_MAP = {1: 5, 2: 6, 3: 19, 4: 16, 5: 20, 6: 21}
SENSOR_PINS = list(SENSOR_MAP.values())

# Setup GPIO
GPIO.setmode(GPIO.BCM)
for pin in SENSOR_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Create GUI window
root = tk.Tk()
root.title("Sensor Game")

# Create sequence display label
sequence_label = tk.Label(root, text="Generated Sequence: ", font=("Arial", 18), fg="blue")
sequence_label.pack(pady=20)

# Create sensor status labels (hidden at first)
labels_frame = tk.Frame(root)
labels = {}
for sensor_num, pin in sorted(SENSOR_MAP.items()):
    label = tk.Label(labels_frame, text=f"Sensor {sensor_num} (Pin {pin}): Waiting...", font=("Arial", 14))
    label.pack(anchor="w", padx=10, pady=2)
    labels[sensor_num] = label

# Control flags and variables
sequence_lengths = [4, 8, 12]
current_index = 0
sensor_monitoring_enabled = False
current_sequence = []

def show_sequence_step_by_step(seq):
    """Display each number in the sequence one by one"""
    def show_next(index):
        if index < len(seq):
            sequence_label.config(text=f"Sequence Number {index + 1}: {seq[index]}")
            root.after(1000, show_next, index + 1)
        else:
            sequence_label.config(text="Sequence Complete! Start interacting with sensors.")
            start_sensor_monitoring()
    show_next(0)

def start_sensor_monitoring():
    """Reveal the sensor labels and start updating statuses"""
    global sensor_monitoring_enabled
    sensor_monitoring_enabled = True
    labels_frame.pack()
    update_sensor_status()

def update_sensor_status():
    """Update GPIO sensor statuses if monitoring is enabled"""
    if sensor_monitoring_enabled:
        for sensor_num, pin in sorted(SENSOR_MAP.items()):
            status = "Pressed" if GPIO.input(pin) == GPIO.LOW else "Not Pressed"
            labels[sensor_num].config(text=f"Sensor {sensor_num} (Pin {pin}): {status}")
        root.after(500, update_sensor_status)

def generate_sequence():
    """Generate and display a new sequence every 1 second"""
    global current_index, current_sequence, sensor_monitoring_enabled
    while True:
        sensor_monitoring_enabled = False
        current_sequence = [random.randint(1, 6) for _ in range(sequence_lengths[current_index])]
        current_index = (current_index + 1) % len(sequence_lengths)

        # Reset GUI state
        root.after(0, lambda: sequence_label.config(text="Generating new sequence..."))
        root.after(0, lambda: [label.config(text=f"Sensor {num} (Pin {pin}): Waiting...") 
                               for num, pin in SENSOR_MAP.items()])
        root.after(0, lambda: labels_frame.pack_forget())

        # Wait a moment before displaying the sequence
        time.sleep(1)
        root.after(0, lambda seq=current_sequence: show_sequence_step_by_step(seq))

        # Wait until the full sequence is shown before continuing the loop
        time.sleep(len(current_sequence) + 2)

# Start sequence generation in a background thread
threading.Thread(target=generate_sequence, daemon=True).start()

# Run the GUI loop with GPIO cleanup
try:
    root.mainloop()
finally:
    GPIO.cleanup()

