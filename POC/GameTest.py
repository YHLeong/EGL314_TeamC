import RPi.GPIO as GPIO
import tkinter as tk
import random
import time
import threading

# Map sensor numbers to GPIO pins
SENSOR_MAP = {1: 5, 2: 6, 3: 19, 4: 16, 5: 20, 6: 21}
PIN_TO_SENSOR = {v: k for k, v in SENSOR_MAP.items()}
SENSOR_PINS = list(SENSOR_MAP.values())

# Setup GPIO
GPIO.setmode(GPIO.BCM)
for pin in SENSOR_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# GUI Setup
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

# Game State
sequence_stages = [4, 8, 12]  # Easy, Medium, Hard levels
current_sequence = []
user_input = []
sensor_monitoring_enabled = False
expected_sequence_length = 0
last_pressed = {}
last_press_time = {}
DEBOUNCE_DELAY = 0.5
sequence_completed = threading.Event()

def show_partial_sequence(seq, length):
    def show_next(index):
        if index < length:
            sequence_label.config(text=f"Sequence Number {index + 1}: {seq[index]}")
            root.after(1000, show_next, index + 1)
        else:
            sequence_label.config(text=f"Repeat the first {length} sensor(s) using sensors!")
            start_sensor_monitoring(length)
    show_next(0)

def start_sensor_monitoring(expected_length):
    global sensor_monitoring_enabled, user_input, expected_sequence_length
    sensor_monitoring_enabled = True
    user_input = []
    expected_sequence_length = expected_length
    labels_frame.pack()
    update_sensor_status()

def update_sensor_status():
    if sensor_monitoring_enabled:
        current_time = time.time()
        for sensor_num, pin in sorted(SENSOR_MAP.items()):
            pin_state = GPIO.input(pin)
            status = "Pressed" if pin_state == GPIO.LOW else "Not Pressed"
            labels[sensor_num].config(text=f"Sensor {sensor_num} (Pin {pin}): {status}")

            was_pressed_before = last_pressed.get(pin, True)
            if was_pressed_before and pin_state == GPIO.LOW:
                last_time = last_press_time.get(pin, 0)
                if current_time - last_time > DEBOUNCE_DELAY:
                    user_input.append(sensor_num)
                    last_press_time[pin] = current_time
                    if len(user_input) == expected_sequence_length:
                        check_user_sequence()
            last_pressed[pin] = pin_state

        root.after(100, update_sensor_status)

def check_user_sequence():
    global sensor_monitoring_enabled
    sensor_monitoring_enabled = False
    expected = current_sequence[:expected_sequence_length]
    if user_input == expected:
        result_label.config(text="✅ Correct sequence!", fg="green")
    else:
        result_label.config(text=f"❌ Wrong sequence!\nExpected: {expected}\nYou: {user_input}", fg="red")
    sequence_completed.set()

def generate_sequence(length):
    return [random.randint(1, 6) for _ in range(length)]

def run_sequence_challenge():
    while True:
        for level_length in sequence_stages:
            global current_sequence
            current_sequence = generate_sequence(level_length)
            sequence_completed.clear()
            result_label.config(text="")
            labels_frame.pack_forget()

            for stage in range(1, level_length + 1):
                sequence_completed.clear()
                # Show partial sequence for current stage
                root.after(0, lambda seq=current_sequence, l=stage: show_partial_sequence(seq, l))

                # Wait until user completes input
                while not sequence_completed.is_set():
                    time.sleep(0.1)

                expected = current_sequence[:stage]
                if user_input != expected:
                    root.after(0, lambda: sequence_label.config(text="🔁 Failed! Restarting from level 1..."))
                    root.after(0, lambda: result_label.config(text="Try Again!", fg="orange"))
                    time.sleep(3)
                    break  # fail current level; restart game loop
                else:
                    time.sleep(1)  # pause before next stage
            else:
                # Completed all stages in this level, continue to next level
                continue
            # Failure happened, break level loop to restart from beginning
            break

        else:
            # All levels passed
            root.after(0, lambda: sequence_label.config(text="🎉 All levels complete!"))
            root.after(0, lambda: result_label.config(text="Game Over!", fg="blue"))
            break

threading.Thread(target=run_sequence_challenge, daemon=True).start()

try:
    root.mainloop()
finally:
    GPIO.cleanup()





