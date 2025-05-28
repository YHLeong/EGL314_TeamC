import RPi.GPIO as GPIO
import tkinter as tk
import random
import time

# ------------------------- GPIO & Sensor Setup -------------------------
SENSOR_MAP = {1: 5, 2: 6, 3: 19, 4: 16, 5: 20, 6: 21}
SENSOR_PINS = list(SENSOR_MAP.values())

GPIO.setmode(GPIO.BCM)
for pin in SENSOR_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ------------------------- Game Config -------------------------
LEVELS = {
    "Easy": 4,
    "Medium": 8,
    "Hard": 12
}

current_level = "Easy"
current_sequence = []
player_progress = 0
mistakes = 0
MAX_MISTAKES = 3

# ------------------------- Tkinter Setup -------------------------
root = tk.Tk()
root.title("Memory Sensor Game")

status_label = tk.Label(root, text="Welcome to Our Game!", font=("Arial", 18))
status_label.grid(row=0, column=0, pady=10)

sensor_label = tk.Label(root, text="Press to Begin", font=("Arial", 16))
sensor_label.grid(row=1, column=0, pady=10)

# ------------------------- Sequence Generation -------------------------
def generate_sequence(level):
    steps = LEVELS[level]
    sequence = []
    for _ in range(steps):
        if level == "Easy":
            sequence.append([random.choice(list(SENSOR_MAP.keys()))])
        elif level == "Medium":
            count = random.choice([1, 2])
            sequence.append(random.sample(list(SENSOR_MAP.keys()), count))
        elif level == "Hard":
            count = random.choice([2, 3])
            sequence.append(random.sample(list(SENSOR_MAP.keys()), count))
    return sequence

# ------------------------- Display Sequence -------------------------
def display_sequence(sequence, step_index=0):
    if step_index < len(sequence):
        sensors = sequence[step_index]
        sensor_label.config(text=f"Memorize: Sensor(s) {', '.join(map(str, sensors))}")
        root.update()
        root.after(2000, lambda: display_sequence(sequence, step_index + 1))
    else:
        sensor_label.config(text="Now repeat the sequence!")
        start_input_check()

# ------------------------- Input Handling -------------------------
def start_input_check():
    global player_progress, mistakes
    player_progress = 0
    mistakes = 0
    check_input_step()

def check_input_step():
    global player_progress, mistakes

    expected_sensors = current_sequence[player_progress]
    pressed = [num for num, pin in SENSOR_MAP.items() if GPIO.input(pin) == GPIO.LOW]

    if set(pressed) == set(expected_sensors):
        player_progress += 1
        if player_progress == len(current_sequence):
            sensor_label.config(text="Level complete!")
            root.after(2000, next_level)
            return
        else:
            sensor_label.config(text="Correct! Get ready for next step...")
            root.after(1500, check_input_step)
    elif len(pressed) > 0 and set(pressed) != set(expected_sensors):
        mistakes += 1
        sensor_label.config(text=f"Wrong! Mistakes: {mistakes}/{MAX_MISTAKES}")
        if mistakes >= MAX_MISTAKES:
            sensor_label.config(text="Too many mistakes! Restarting game...")
            root.after(3000, start_game)
        else:
            root.after(1500, check_input_step)
    else:
        root.after(100, check_input_step)

# ------------------------- Level Progression -------------------------
def next_level():
    global current_level, current_sequence

    if current_level == "Easy":
        current_level = "Medium"
    elif current_level == "Medium":
        current_level = "Hard"
    elif current_level == "Hard":
        sensor_label.config(text="Congratulations! You won the game!")
        status_label.config(text="Game Over")
        return

    status_label.config(text=f"Level: {current_level}")
    current_sequence = generate_sequence(current_level)
    root.after(2000, lambda: display_sequence(current_sequence))

# ------------------------- Game Start -------------------------
def start_game():
    global current_level, current_sequence, player_progress
    current_level = "Easy"
    status_label.config(text="Level: Easy")
    sensor_label.config(text="Get ready...")
    current_sequence = generate_sequence(current_level)
    root.after(2000, lambda: display_sequence(current_sequence))

# ------------------------- Start Button -------------------------
start_button = tk.Button(root, text="Start Game", font=("Arial", 14), command=start_game)
start_button.grid(row=2, column=0, pady=10)

# ------------------------- Main Loop -------------------------
try:
    root.mainloop()
finally:
    GPIO.cleanup()