import RPi.GPIO as GPIO
import tkinter as tk
import random
import time
import threading

# Sensor mapping: sensor numbers 1–6 mapped to specific GPIO pins
SENSOR_MAP = {1: 5, 2: 6, 3: 19, 4: 16, 5: 20, 6: 21}
PIN_TO_SENSOR = {v: k for k, v in SENSOR_MAP.items()}
SENSOR_PINS = list(SENSOR_MAP.values())

# Setup GPIO
GPIO.setmode(GPIO.BCM)
for pin in SENSOR_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# GUI setup
root = tk.Tk()
root.title("Sensor Sequence Challenge")

sequence_label = tk.Label(root, text="Generated Sequence: ", font=("Arial", 18), fg="blue")
sequence_label.pack(pady=20)

result_label = tk.Label(root, text="", font=("Arial", 16), fg="green")
result_label.pack(pady=10)

labels_frame = tk.Frame(root)
labels = {}
for sensor_num, pin in sorted(SENSOR_MAP.items()):
    label = tk.Label(labels_frame, text=f"Sensor {sensor_num} (Pin {pin}): Waiting...", font=("Arial", 14))
    label.pack(anchor="w", padx=10, pady=2)
    labels[sensor_num] = label

# Game state
sequence_stages = [4, 8, 12]
current_sequence = []
user_input = []
sensor_monitoring_enabled = False
last_pressed = {}
sequence_completed = threading.Event()

def show_sequence_step_by_step(seq):
    """Display each number in the sequence one by one."""
    def show_next(index):
        if index < len(seq):
            sequence_label.config(text=f"Sequence Number {index + 1}: {seq[index]}")
            root.after(1000, show_next, index + 1)
        else:
            sequence_label.config(text=f"Repeat the sequence using sensors!")
            start_sensor_monitoring()
    show_next(0)

def start_sensor_monitoring():
    global sensor_monitoring_enabled, user_input
    sensor_monitoring_enabled = True
    user_input = []
    labels_frame.pack()
    update_sensor_status()

def update_sensor_status():
    """Poll sensor inputs and detect order of presses (with repeats)."""
    if sensor_monitoring_enabled:
        for sensor_num, pin in sorted(SENSOR_MAP.items()):
            pin_state = GPIO.input(pin)
            status = "Pressed" if pin_state == GPIO.LOW else "Not Pressed"
            labels[sensor_num].config(text=f"Sensor {sensor_num} (Pin {pin}): {status}")

            # Detect new press (edge detection)
            if last_pressed.get(pin, True) and pin_state == GPIO.LOW:
                user_input.append(sensor_num)
                print(f"Pressed: {sensor_num}, User input: {user_input}")
                if len(user_input) == len(current_sequence):
                    check_user_sequence()
            last_pressed[pin] = pin_state

        root.after(100, update_sensor_status)

def check_user_sequence():
    global sensor_monitoring_enabled
    sensor_monitoring_enabled = False
    if user_input == current_sequence:
        result_label.config(text="✅ Correct sequence!", fg="green")
        sequence_completed.set()
    else:
        result_label.config(
            text=f"❌ Wrong sequence!\nExpected: {current_sequence}\nYou: {user_input}",
            fg="red"
        )

def generate_sequence_and_wait(length):
    """Generate a sequence and wait for correct sensor input."""
    global current_sequence
    current_sequence = [random.randint(1, 6) for _ in range(length)]

    root.after(0, lambda: sequence_label.config(text="Generating sequence..."))
    root.after(0, lambda: result_label.config(text=""))
    root.after(0, lambda: [label.config(text=f"Sensor {num} (Pin {pin}): Waiting...")
                           for num, pin in SENSOR_MAP.items()])
    root.after(0, lambda: labels_frame.pack_forget())

    time.sleep(1)
    root.after(0, lambda seq=current_sequence: show_sequence_step_by_step(seq))

    sequence_completed.clear()
    sequence_completed.wait()

def run_sequence_challenge():
    """Progress through 4, 8, 12-length sequences if successful."""
    for length in sequence_stages:
        generate_sequence_and_wait(length)
        time.sleep(2)
    root.after(0, lambda: sequence_label.config(text="🎉 All sequences complete!"))
    root.after(0, lambda: result_label.config(text="Game Over!", fg="blue"))

# Start game in background thread
threading.Thread(target=run_sequence_challenge, daemon=True).start()

# Start GUI loop
try:
    root.mainloop()
finally:
    GPIO.cleanup()

