# 🎮 EGL314 – Project Documentation

## 🎯 Introduction

**Wall Glyphs: Silent Sequence** is an immersive, non-verbal multiplayer game designed for **3 to 4 players**. The objective? Collaborate **without speaking or using visual cues** to activate six glyphs on a wall in the correct order. 🤐✨

Players must rely solely on intuition and audio cues to work together and solve the sequence challenge!

---

## 🕹️ Objective

Players will:
- Observe a light-based demo of the correct glyph sequence 🔆
- Receive a **spatial audio signal** 🎧 to begin
- Step on **pressure-sensitive stones** 🪨 in the correct order
- Complete the sequence within a **set time limit** ⏱️


---

## 🔌 Dependencies

### 🛠️ Hardware
- 🖥️ 1x Raspberry Pi 4 Model B  
- 🪑 6x AoKu AK-399 Car Seat Pressure Sensors  
- 🔌 6x WAGO Connectors  
- 🧵 13x Jumper Wires  

### 💻 Software
- 🎲 Random Number Generator  
- 📡 Sensor Signal Detector
---

## 🧭 System Diagram
![System Diagram](AssetsFolder/SystemDiagram_Updated.png)

---

## 💡 Code Logic

## 🎲 Random Number Generator - [Click Here](https://github.com/YHLeong/EGL314_TeamC/blob/main/Backlog%202%20sprint%201/RandomNumberGenerator_v4.py)
#### 🧾 Overview

This Python script continuously generates and prints sequences of random integers. Each sequence has a length that cycles through **4**, **8**, and **12**, refreshing every **1 second** until the user stops the script with **Ctrl+C**.

---

### 📚 Python Packages Used
```
import random
import time
```
#### 🎰random
Purpose: Used to generate random integers.
<br>
Function Used: random.randint(a, b) returns a random integer N such that a <= N <= b.

#### ⏰time
Purpose: Provides time-related functions. 
<br>
Function Used: time.sleep(seconds) pauses program execution for the given number of seconds.

### 🔄Index Tracker

```
sequence_lengths = [4, 8, 12]
current_index = 0  # Start at 4
```
- Tracks the current position in the sequence_lengths list.
- Initially set to 0, meaning the sequence will start with a length of 4.

### 🔁Main Loop
```
while True:
  ...
```
- An infinite loop (while True) is used to continuously generate sequences.
- The loop continues until the user stops it manually (e.g., with Ctrl+C).

### 🧮Sequence Generation
```
seq_length = sequence_lengths[current_index]
sequence = [random.randint(1, 6) for _ in range(seq_length)]
```
- Retrieves the current sequence length using the current_index.
- Generates a list of random integers between 1 and 6 (inclusive), simulating dice rolls.
- Uses list comprehension for concise generation.

### 📤Output
```
print(f"Generated sequence ({seq_length} numbers): {sequence}")
```
- Prints the generated sequence along with the number of elements.

### ➕Index Update
```
current_index = (current_index + 1) % len(sequence_lengths)
```
- Updates current_index to point to the next length in the list.
- Uses modulo (%) to cycle back to the start when the end is reached.

### ⏳Delay
```
time.sleep(1)
```
- Waits for 1 second before generating the next sequence.
- Helps maintain a steady interval between outputs.

### ✋Graceful Exit
```
except KeyboardInterrupt:
    print("\nExiting... Program stopped by user.")
```
- Allows the user to stop the program gracefully using Ctrl + C.
- Catches the KeyboardInterrupt exception and prints a message before exiting.
---

## Connection []()


## Prove Of Concept
### 🧾 Overview

This Python script creates an interactive sensor-based memory game using a **Raspberry Pi** and **Tkinter GUI**. The game generates random sequences, displays them one by one, and then waits for the player to replicate them using physical button presses (sensors). It progresses through sequences of length **4**, **8**, and **12**.

---

### 📚 Python Packages Used
```
import RPi.GPIO as GPIO             
import tkinter as tk                
import random                       
import time                         
import threading 
```
#### 📟 RPi.GPIO
- **Purpose:** Controls and reads the Raspberry Pi’s GPIO pins.
- **Functionality:** Configures pins for input and reads pin states.

#### 🖼️ tkinter
- **Purpose:** Builds the graphical user interface (GUI).
- **Functionality:** Displays the sequence, sensor status, and game results.

#### 🎰 random
- **Purpose:** Generates random sequences of sensor numbers.
- **Function Used:** `random.randint(a, b)` for random integers.

#### ⏰ time
- **Purpose:** Provides time-related functions like delays.
- **Function Used:** `time.sleep(seconds)` and `time.time()`.

#### 🧵 threading
- **Purpose:** Allows the GUI and game logic to run concurrently without freezing.
- **Function Used:** `threading.Thread`, `threading.Event`.
---

### 🧭 GPIO Setup
```
SENSOR_MAP = {1: 5, 2: 6, 3: 19, 4: 16, 5: 20, 6: 21}
GPIO.setmode(GPIO.BCM)
```
- Maps sensor numbers to GPIO pins.
- Configures pins as input with pull-up      resistors.
- Uses BCM numbering mode.
---

### 🖥️ GUI Layout
```
root = tk.Tk()
root.title("Sensor Sequence Challenge")
```
- Main Window: Title set to "Sensor Sequence Challenge".

```
sequence_label = tk.Label(root, text="Generated Sequence: ", font=("Arial", 18), fg="blue")
result_label = tk.Label(root, text="", font=("Arial", 16), fg="green")
labels_frame = tk.Frame(root)
```
- Sequence Label: Shows generated numbers.
- Result Label: Shows result after user input.
- Sensor Labels: Show live status (pressed/not pressed) for each sensor.
---

### 🎮 Game Flow
```
sequence_stages = [4, 8, 12]
```
- Defines the game rounds with increasing difficulty.
  
### 🔢 Sequence Generation
```
current_sequence = [random.randint(1, 6) for _ in range(length)]
```
- Randomly generates a sequence for the current round.

### 👁️ Displaying Sequence
```
def show_sequence_step_by_step(seq):
    def show_next(index):
        if index < len(seq):
            sequence_label.config(text=f"Sequence Number {index + 1}: {seq[index]}")
            root.after(1000, show_next, index + 1)
        else:
            sequence_label.config(text="Repeat the sequence using sensors!")
            start_sensor_monitoring()
    show_next(0)
```
- Displays one number per second in the GUI using root.after().

### 🧠 Sensor Monitoring
```
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
```
- Continuously checks the GPIO inputs every 100ms.
- Uses debounce logic (0.5s delay) to avoid multiple triggers.
- Detects a valid press (falling edge) and records it.

### ✔️ Sequence Validation
```
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
```
- Compares user input with the generated sequence.
- Displays ✅ if correct, ❌ with expected/actual if wrong.
- Triggers next round or ends the game.
---

### 🧵 Threaded Execution
```
threading.Thread(target=run_sequence_challenge, daemon=True).start()
```
- Runs the sequence game logic in a separate thread.
- Keeps the GUI responsive during gameplay.

### 🚦 GUI Main Loop & Cleanup
```
try:
    root.mainloop()
finally:
    GPIO.cleanup()
```
- Starts the GUI event loop.
- Cleans up GPIO on program exit (even with Ctrl+C).
---

### ✋ Graceful Exit
python
```
finally:
    GPIO.cleanup()
```
- Ensures the GPIO pins are properly reset when the program ends.


