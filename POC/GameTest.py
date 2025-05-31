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

# Level label
level_label = tk.Label(root, text="", font=("Arial", 16), fg="purple")
level_label.pack(pady=5)

stage_label = tk.Label(root, text="", font=("Arial", 16), fg="brown")
stage_label.pack(pady=5)

result_label = tk.Label(root, text="", font=("Arial", 16), fg="green")
result_label.pack(pady=10)

labels_frame = tk.Frame(root)
labels = {}
for sensor_num, pin in sorted(SENSOR_MAP.items()):
    label = tk.Label(labels_frame, text=f"Sensor {sensor_num} (Pin {pin}): Waiting...", font=("Arial", 14))
    label.pack(anchor="w", padx=10, pady=2)
    labels[sensor_num] = label

# Game State
LEVELS = [
    {"length": 4, "name": "Easy", "timer": 30},
    {"length": 8, "name": "Medium", "timer": 60},
    {"length": 12, "name": "Hard", "timer": 90},
]
current_sequence = []
user_input = []
sensor_monitoring_enabled = False
last_pressed = {}
last_press_time = {}
DEBOUNCE_DELAY = 0.5
sequence_completed = threading.Event()
timer_failed = threading.Event()

# GUI Timer Label
timer_label = tk.Label(root, text="", font=("Arial", 20), fg="red")
timer_label.pack(pady=10)

def show_sequence_step_by_step(seq, reveal_len):
    timer_label.pack_forget()
    def show_next(index):
        if index < reveal_len:
            sequence_label.config(text=f"Sequence Number {index + 1}: {seq[index]}")
            root.after(1000, show_next, index + 1)
        else:
            sequence_label.config(text="Repeat the sequence using sensors!")
            start_sensor_monitoring()
            timer_label.pack(pady=10)
            start_timer(reveal_len)
    show_next(0)

def start_sensor_monitoring():
    global sensor_monitoring_enabled, user_input
    sensor_monitoring_enabled = True
    user_input = []
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
        result_label.config(text=f"❌ Wrong sequence!\nExpected: {current_sequence}\nYou: {user_input}", fg="red")
        timer_failed.set()
        timer_label.config(text="")

def start_timer(seq_length):
    # Find timer for current level
    total_time = 30
    for lvl in LEVELS:
        if seq_length <= lvl["length"]:
            total_time = lvl["timer"]
            break
    def countdown():
        nonlocal total_time
        while total_time > 0 and not sequence_completed.is_set():
            mins, secs = divmod(total_time, 60)
            timer_label.config(text=f"⏳ Time Left: {mins:02d}:{secs:02d}")
            time.sleep(1)
            total_time -= 1
        if not sequence_completed.is_set():
            timer_label.config(text="⏰ Time's up!")
            timer_failed.set()
            time.sleep(1)
            timer_label.config(text="")
    threading.Thread(target=countdown, daemon=True).start()

def generate_sequence_and_wait(sequence, reveal_len, level_name, stage_num, stage_max):
    global current_sequence
    current_sequence = sequence[:reveal_len]
    sequence_completed.clear()
    timer_failed.clear()
    root.after(0, lambda: level_label.config(text=f"Level: {level_name}"))
    root.after(0, lambda: stage_label.config(text=f"Stage: {stage_num}/{stage_max}"))
    root.after(0, lambda: sequence_label.config(text="Generating sequence..."))
    root.after(0, lambda: result_label.config(text=""))
    root.after(0, lambda: [label.config(text=f"Sensor {num} (Pin {pin}): Waiting...") for num, pin in SENSOR_MAP.items()])
    root.after(0, lambda: labels_frame.pack_forget())
    root.after(1000, lambda: show_sequence_step_by_step(sequence, reveal_len))
    while not (sequence_completed.is_set() or timer_failed.is_set()):
        time.sleep(0.1)
    return sequence_completed.is_set()

def run_sequence_challenge():
    for lvl in LEVELS:
        seq_len = lvl["length"]
        level_name = lvl["name"]
        sequence = [random.randint(1, 6) for _ in range(seq_len)]
        for stage in range(1, seq_len + 1):
            success = generate_sequence_and_wait(sequence, stage, level_name, stage, seq_len)
            if not success:
                root.after(0, lambda: sequence_label.config(text="🔁 Sequence Failed. Restarting Level..."))
                root.after(0, lambda: result_label.config(text="Try Again from the Beginning of This Level", fg="orange"))
                time.sleep(3)
                return run_sequence_challenge()  # Restart from the beginning
            time.sleep(2)
    root.after(0, lambda: sequence_label.config(text="🎉 All sequences complete!"))
    root.after(0, lambda: result_label.config(text="Game Over!", fg="blue"))

threading.Thread(target=run_sequence_challenge, daemon=True).start()

try:
    root.mainloop()
finally:
    GPIO.cleanup()