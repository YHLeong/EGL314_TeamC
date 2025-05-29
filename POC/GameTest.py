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
sequence_stages = [4, 8, 12]
TIMER_MAP = {4: 30, 8: 60, 12: 90}
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

def show_sequence_step_by_step(seq):
    def show_next(index):
        if index < len(seq):
            sequence_label.config(text=f"Sequence Number {index + 1}: {seq[index]}")
            root.after(1000, show_next, index + 1)
        else:
            sequence_label.config(text="Repeat the sequence using sensors!")
            start_sensor_monitoring()
            start_timer(len(seq))
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

def start_timer(seq_length):
    total_time = TIMER_MAP.get(seq_length, 30)
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
    threading.Thread(target=countdown, daemon=True).start()

def generate_sequence_and_wait(length):
    global current_sequence
    current_sequence = [random.randint(1, 6) for _ in range(length)]
    sequence_completed.clear()
    timer_failed.clear()
    root.after(0, lambda: sequence_label.config(text="Generating sequence..."))
    root.after(0, lambda: result_label.config(text=""))
    root.after(0, lambda: [label.config(text=f"Sensor {num} (Pin {pin}): Waiting...") for num, pin in SENSOR_MAP.items()])
    root.after(0, lambda: labels_frame.pack_forget())
    time.sleep(1)
    root.after(0, lambda seq=current_sequence: show_sequence_step_by_step(seq))

    while not (sequence_completed.is_set() or timer_failed.is_set()):
        time.sleep(0.1)

    return sequence_completed.is_set()

def run_sequence_challenge():
    while True:
        for length in sequence_stages:
            success = generate_sequence_and_wait(length)
            if not success:
                root.after(0, lambda: sequence_label.config(text="🔁 Sequence Failed. Restarting..."))
                root.after(0, lambda: result_label.config(text="Try Again from the Beginning", fg="orange"))
                time.sleep(3)
                break
            time.sleep(2)
        else:
            root.after(0, lambda: sequence_label.config(text="🎉 All sequences complete!"))
            root.after(0, lambda: result_label.config(text="Game Over!", fg="blue"))
            break

threading.Thread(target=run_sequence_challenge, daemon=True).start()

try:
    root.mainloop()
finally:
    GPIO.cleanup()


