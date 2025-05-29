import RPi.GPIO as GPIO             # Import GPIO module to read Raspberry Pi pins
import tkinter as tk                # Import Tkinter for GUI
import random                       # For generating random sensor sequences
import time                         # For time-related functions (delays, timestamps)
import threading                    # For running GUI and game logic in parallel

# Map sensor numbers to GPIO pins
SENSOR_MAP = {1: 5, 2: 6, 3: 19, 4: 16, 5: 20, 6: 21}
PIN_TO_SENSOR = {v: k for k, v in SENSOR_MAP.items()}  # Reverse map for quick lookup
SENSOR_PINS = list(SENSOR_MAP.values())                # List of all GPIO pin numbers

# Setup GPIO pins for input with internal pull-up resistors
GPIO.setmode(GPIO.BCM)                                 # Use Broadcom (BCM) numbering
for pin in SENSOR_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set pins as input with pull-up

# GUI setup using Tkinter
root = tk.Tk()                                         # Create main window
root.title("Sensor Sequence Challenge")                # Window title

# Label to show the current sequence being displayed
sequence_label = tk.Label(root, text="Generated Sequence: ", font=("Arial", 18), fg="blue")
sequence_label.pack(pady=20)

# Label to show results (correct or incorrect)
result_label = tk.Label(root, text="", font=("Arial", 16), fg="green")
result_label.pack(pady=10)

# Frame to hold sensor status labels
labels_frame = tk.Frame(root)
labels = {}                                            # Dictionary to hold sensor labels

# Create and pack labels for each sensor
for sensor_num, pin in sorted(SENSOR_MAP.items()):
    label = tk.Label(labels_frame, text=f"Sensor {sensor_num} (Pin {pin}): Waiting...", font=("Arial", 14))
    label.pack(anchor="w", padx=10, pady=2)
    labels[sensor_num] = label

# Game variables
sequence_stages = [4, 8, 12]                           # Stages of the game (lengths of sequences)
current_sequence = []                                  # Holds the current generated sequence
user_input = []                                        # Stores the user's input sequence
sensor_monitoring_enabled = False                      # True if system is watching for sensor input
last_pressed = {}                                      # Tracks last state of each sensor (for edge detection)
last_press_time = {}                                   # Time of last valid press (for debounce)
DEBOUNCE_DELAY = 0.5                                   # Minimum time between presses (in seconds)
sequence_completed = threading.Event()                 # Event flag to signal sequence completion

# Function to show the generated sequence one number at a time
def show_sequence_step_by_step(seq):
    def show_next(index):
        if index < len(seq):
            sequence_label.config(text=f"Sequence Number {index + 1}: {seq[index]}")  # Show current item
            root.after(1000, show_next, index + 1)  # Wait 1 second, then show next
        else:
            sequence_label.config(text="Repeat the sequence using sensors!")  # Prompt user to input
            start_sensor_monitoring()
    show_next(0)  # Start showing the sequence from index 0

# Enable sensor monitoring and clear previous input
def start_sensor_monitoring():
    global sensor_monitoring_enabled, user_input
    sensor_monitoring_enabled = True
    user_input = []
    labels_frame.pack()               # Show the sensor status labels
    update_sensor_status()           # Start polling the sensors

# Poll sensors and detect presses with debounce
def update_sensor_status():
    if sensor_monitoring_enabled:
        current_time = time.time()   # Get current timestamp
        for sensor_num, pin in sorted(SENSOR_MAP.items()):
            pin_state = GPIO.input(pin)  # Read pin state
            status = "Pressed" if pin_state == GPIO.LOW else "Not Pressed"
            labels[sensor_num].config(text=f"Sensor {sensor_num} (Pin {pin}): {status}")

            was_pressed_before = last_pressed.get(pin, True)  # True if pin was HIGH last time

            # Check for falling edge (unpressed → pressed) and debounce
            if was_pressed_before and pin_state == GPIO.LOW:
                last_time = last_press_time.get(pin, 0)
                if current_time - last_time > DEBOUNCE_DELAY:
                    user_input.append(sensor_num)             # Register the sensor press
                    last_press_time[pin] = current_time       # Update the last press time
                    print(f"Pressed: {sensor_num}, User input: {user_input}")
                    if len(user_input) == len(current_sequence):  # Check if sequence is complete
                        check_user_sequence()

            last_pressed[pin] = pin_state  # Update the last pin state

        root.after(100, update_sensor_status)  # Continue polling every 100ms

# Compare user input to generated sequence and display result
def check_user_sequence():
    global sensor_monitoring_enabled
    sensor_monitoring_enabled = False
    if user_input == current_sequence:
        result_label.config(text="✅ Correct sequence!", fg="green")
        sequence_completed.set() # Mark sequence as complete
    else:
        result_label.config(
            text=f"❌ Wrong sequence!\nExpected: {current_sequence}\nYou: {user_input}",
            fg="red"
        )

# Generate a random sequence and wait for user to input it correctly
def generate_sequence_and_wait(length):
    global current_sequence
    current_sequence = [random.randint(1, 6) for _ in range(length)]  # Random sequence

    # Reset UI and state
    root.after(0, lambda: sequence_label.config(text="Generating sequence..."))
    root.after(0, lambda: result_label.config(text=""))
    root.after(0, lambda: [label.config(text=f"Sensor {num} (Pin {pin}): Waiting...")
                           for num, pin in SENSOR_MAP.items()])
    root.after(0, lambda: labels_frame.pack_forget())

    time.sleep(1) # Short pause before showing sequence
    root.after(0, lambda seq=current_sequence: show_sequence_step_by_step(seq))

    sequence_completed.clear() # Reset event flag
    sequence_completed.wait()  # Wait until user finishes the sequence

# Run through all stages of the game
def run_sequence_challenge():
    for length in sequence_stages:
        generate_sequence_and_wait(length)             # Play one round
        time.sleep(2)                                  # Short pause between rounds
    root.after(0, lambda: sequence_label.config(text="🎉 All sequences complete!"))
    root.after(0, lambda: result_label.config(text="Game Over!", fg="blue"))

# Run game logic in a separate thread so GUI remains responsive
threading.Thread(target=run_sequence_challenge, daemon=True).start()

# Start the GUI main loop
try:
    root.mainloop()             # Start the Tkinter event loop
finally:
    GPIO.cleanup()              # Reset GPIO on exit

