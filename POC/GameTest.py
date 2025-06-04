import RPi.GPIO as GPIO
import tkinter as tk
import random
import time
import threading

# Map sensor numbers to GPIO pins
SENSOR_MAP = {1: 17, 2: 6, 3: 19, 4: 16, 5: 20, 6: 21}
PIN_TO_SENSOR = {v: k for k, v in SENSOR_MAP.items()}
SENSOR_PINS = list(SENSOR_MAP.values())

# Setup GPIO
GPIO.setmode(GPIO.BCM)
for pin in SENSOR_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# GUI Setup
root = tk.Tk()
root.title("Sensor Sequence Challenge")

timer_label = tk.Label(root, text="Time Left: 30s", font=("Arial", 16), fg="red")
timer_label.pack(pady=10)

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
current_sequence = []
user_input = []
sensor_monitoring_enabled = False
last_pressed = {}
last_press_time = {}
DEBOUNCE_DELAY = 0.5
sequence_completed = threading.Event()

# Timer variables
TIMER_DURATION_MS = 30000
timer_id = None
timer_update_id = None
timer_remaining_ms = TIMER_DURATION_MS

def update_timer_label():
    global timer_remaining_ms, timer_update_id
    seconds_left = timer_remaining_ms // 1000
    timer_label.config(text=f"Time Left: {seconds_left}s")
    if timer_remaining_ms <= 0:
        return
    timer_remaining_ms -= 1000
    timer_update_id = root.after(1000, update_timer_label)

def start_round_timer():
    global timer_id, timer_remaining_ms, timer_update_id
    cancel_round_timer()
    timer_remaining_ms = TIMER_DURATION_MS
    update_timer_label()
    timer_id = root.after(TIMER_DURATION_MS, on_timer_expire)

def cancel_round_timer():
    global timer_id, timer_update_id
    if timer_id is not None:
        root.after_cancel(timer_id)
        timer_id = None
    if timer_update_id is not None:
        root.after_cancel(timer_update_id)
        timer_update_id = None
    timer_label.config(text="Time Left: --")

def on_timer_expire():
    global sensor_monitoring_enabled
    sensor_monitoring_enabled = False
    result_label.config(text="⏰ Time's up! Game Over.", fg="red")
    sequence_label.config(text="Game Over - You ran out of time.")
    cancel_round_timer()

def show_sequence_step_by_step(seq, length):
    def show_next(index):
        if index < length:
            sequence_label.config(text=f"Sequence Number {index + 1}: {seq[index]}")
            root.after(1000, show_next, index + 1)
        else:
            sequence_label.config(text=f"Repeat the first {length} steps using sensors!")
            start_sensor_monitoring()
    show_next(0)

def start_sensor_monitoring():
    global sensor_monitoring_enabled, user_input
    sensor_monitoring_enabled = True
    user_input = []
    labels_frame.pack()
    update_sensor_status()
    start_round_timer()

def update_sensor_status():
    if sensor_monitoring_enabled:
        current_time = time.time()
        sensor_press_count = {k: user_input.count(k) for k in SENSOR_MAP}

        for sensor_num, pin in sorted(SENSOR_MAP.items()):
            pin_state = GPIO.input(pin)
            status = "Pressed" if pin_state == GPIO.LOW else "Not Pressed"
            labels[sensor_num].config(text=f"Sensor {sensor_num} (Pin {pin}): {status}")

            was_pressed_before = last_pressed.get(pin, True)
            if was_pressed_before and pin_state == GPIO.LOW:
                last_time = last_press_time.get(pin, 0)
                if current_time - last_time > DEBOUNCE_DELAY:
                    if sensor_press_count.get(sensor_num, 0) < 2:
                        user_input.append(sensor_num)
                        last_press_time[pin] = current_time
                        if len(user_input) == len(current_sequence):
                            check_user_sequence()
            last_pressed[pin] = pin_state

        root.after(100, update_sensor_status)

def check_user_sequence():
    global sensor_monitoring_enabled
    sensor_monitoring_enabled = False
    cancel_round_timer()
    expected = current_sequence[:len(user_input)]
    if user_input == expected:
        result_label.config(text="✅ Correct sequence!", fg="green")
        sequence_completed.set()
    else:
        result_label.config(text=f"❌ Wrong sequence!\nExpected: {expected}\nYou: {user_input}", fg="red")

def play_stage(seq, stage_length):
    global current_sequence
    current_sequence = seq[:stage_length]
    sequence_completed.clear()

    root.after(0, lambda: sequence_label.config(text="Generating sequence..."))
    root.after(0, lambda: result_label.config(text=""))
    root.after(0, lambda: [label.config(text=f"Sensor {num} (Pin {pin}): Waiting...") for num, pin in SENSOR_MAP.items()])
    root.after(0, lambda: labels_frame.pack_forget())

    root.after(1000, lambda: show_sequence_step_by_step(current_sequence, stage_length))

    while not sequence_completed.is_set():
        time.sleep(0.1)

    return sequence_completed.is_set()

def run_sequence_challenge():
    full_sequence = [random.randint(1, 6) for _ in range(12)]
    steps_per_stage = [1, 2, 3, 4, 5, 6, 7, 9, 12]
    difficulties = ["Easy", "Medium", "Hard"]

    stage_idx = 0
    for difficulty in difficulties:
        for stage_num in range(1, 4):
            steps = steps_per_stage[stage_idx]
            root.after(0, lambda d=difficulty, s=stage_num: sequence_label.config(
                text=f"🔢 {d} - Stage {s} ({steps} steps)"
            ))
            root.after(0, lambda: result_label.config(text=""))
            time.sleep(2)

            success = play_stage(full_sequence, steps)
            if not success:
                root.after(0, lambda: sequence_label.config(text="🔁 Stage failed. Restarting game..."))
                root.after(0, lambda: result_label.config(text="Try again from Stage 1", fg="orange"))
                time.sleep(3)
                return
            stage_idx += 1
            time.sleep(2)

    root.after(0, lambda: sequence_label.config(text="🎉 All Stages Complete!"))
    root.after(0, lambda: result_label.config(text="🏁 Game Over!", fg="blue"))

threading.Thread(target=run_sequence_challenge, daemon=True).start()

try:
    root.mainloop()
finally:
    GPIO.cleanup()
