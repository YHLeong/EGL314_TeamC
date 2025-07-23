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
-  1x Raspberry Pi 4 Model B  
-  6x AoKu AK-399 Car Seat Pressure Sensors  
-  6x WAGO Connectors  
-  2x LAN cables
-  6x Carboard Button
-  1x Rasp Pi display V1
-  1x Display holder

### 💻 Software
-  Random Number Generator  
-  Sensor Signal Detector
---


## Physical connections and Props

Cabling
- 2x LAN cable

Since there are six sensors I needed twelve wires in total. I didn't want to use jumper wires as there would be too many points of failure over a long cable. I decided to use LAN cables by isolating two wires per sensor. Since a LAN cable only has four pairs and I needed six, I used two LAN cables.

Props
- Buttons
- Screen holder
- Prop Materials: Cardboard Glue 

We are using cardboard to make everything. For the buttons, we layered three pieces of cardboard and carved a shape into the top two layers to create a 3D effect. For the screen holder, I used glue and cardboard to make an angled piece of cardboard with a hole for the screen. 



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


## Prove Of Concept - [Click Here]()insert link here
### 🧾 Overview

This Python script implements a **progressive memory game** using a **Raspberry Pi** and **Tkinter GUI**. Players must memorize and replicate sequences shown on screen by pressing corresponding physical buttons connected via **GPIO pins**. The game consists of **multiple stages** with increasing sequence lengths, categorized into **Easy, Medium, and Hard** difficulty levels.



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
Purpose: Interface with Raspberry Pi’s physical GPIO pins.

Used For: Configuring buttons as inputs and detecting button presses with debounce logic.

#### 🖼️ tkinter
- Purpose: Render and manage the GUI.
- Used For: Displaying sequences, sensor statuses, timers, and results dynamically.

#### 🎰 random
- Purpose: Sequence generation.
- Used For: `random.randint(1, 6)` to create a randomized pattern of sensor numbers.

#### ⏰ time
- Purpose: Sleep timing and debouncing.
- Used For: `time.sleep()`, `time.time()` to handle delays and debounce checks.

#### 🧵 threading
- Purpose: Keep GUI responsive while running game logic.    
- Used For: Running the main game function `(run_sequence_challenge)` in a separate thread.
---

### 🧭 GPIO Setup
```
SENSOR_MAP = {1: 17, 2: 6, 3: 19, 4: 16, 5: 20, 6: 21}
GPIO.setmode(GPIO.BCM)
for pin in SENSOR_MAP.values():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
```
- Six sensors are mapped to GPIO pins.
- Input pins use pull-up resistors (active-low).
- BCM mode used for pin numbering.
---

### 🖥️ GUI Layout
```
root = tk.Tk()
root.title("Sensor Sequence Challenge")
```
- Main Window: Title set to "Sensor Sequence Challenge".

```
timer_label = tk.Label(...)  
sequence_label = tk.Label(...)  
result_label = tk.Label(...)  
labels_frame = tk.Frame(root)
```
- Timer Label: Shows time remaining for current stage.
- Sequence Label: Shows instructions and sequence step-by-step.
- Result Label: Displays success/failure feedback.
- Sensor Labels: Dynamically update with sensor states ("Pressed"/"Not Pressed").


---

### 🎮 Game Flow
```
steps_per_stage = [1, 2, 3, 4, 5, 6, 7, 9, 12]
difficulties = ["Easy", "Medium", "Hard"]
```
- Stages: 9 in total, increasing step complexity.
- Grouped into: 3 difficulty levels × 3 stages each.
  
### 🔢 Sequence Generation
```
full_sequence = [random.randint(1, 6) for _ in range(12)]
```
- A full 12-step random sequence is generated at the start and split across stages.

### 👁️ Displaying Sequence
```
def show_sequence_step_by_step(seq, length):
    def show_next(index):
        if index < length:
            sequence_label.config(text=f"Sequence Number {index + 1}: {seq[index]}")
            root.after(1000, show_next, index + 1)
        else:
            sequence_label.config(text=f"Repeat the first {length} steps using sensors!")
            start_sensor_monitoring()
    show_next(0)
```
- Displays the sequence one number per second using `root.after`.
- Informs the player when it's time to repeat the steps using sensors.
- Monitoring only starts after the full display finishes.

### 🧠 Sensor Monitoring
```
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

```
- Polls GPIO pins every 100ms to detect button presses.
- Debounce protection: Only accepts inputs spaced by `DEBOUNCE_DELAY = 0.5` seconds.
- Press limit: Each sensor can only be pressed twice per round.
- Inputs get appended to `user_input` until it matches expected length.



### ✔️ Sequence Validation
```
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
```
- Compares player input to the expected segment of the full sequence.
- Displays ✅ if correct, ❌ if wrong (with expected vs. actual).
- Ends stage on validation result.

### ⏱️ Countdown Timer
```
def start_timer(seq_length):
    total_time = TIMER_MAP.get(seq_length, 30)
    def countdown():
        nonlocal total_time
        while total_time > 0 and not sequence_completed.is_set():
            mins, secs = divmod(total_time, 60)
            timer_label.config(text=f" Time Left: {mins:02d}:{secs:02d}")
            time.sleep(1)
            total_time -= 1
        if not sequence_completed.is_set():
            timer_label.config(text=" Time's up!")
            timer_failed.set()
```
- The timer starts only after the sequence is shown.
- Counts down in real time and ends the round on timeout.
---

### 🧵 Threaded Execution
```
threading.Thread(target=run_sequence_challenge, daemon=True).start()
```
- Main game loop runs on a background thread.
- Keeps GUI responsive and prevents freezing during time delays or blocking calls.
---

### 🧩 Stage Logic
```
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
```
- Each stage resets labels and displays the assigned sequence portion.
- Waits for user to complete input or timeout.
- Returns whether the user passed the stage.
---

### 🚦 GUI Main Loop & Cleanup
```
try:
    root.mainloop()
finally:
    GPIO.cleanup()
```
- Main GUI loop keeps the window running.
- On exit (even via Ctrl+C), GPIO pins are reset properly to avoid hangups or damage.
---

### ✋ Graceful Exit
```
finally:
    GPIO.cleanup()
```
- Ensures all GPIO pins are released properly.
- Required for hardware stability and avoiding pin lockups after crash or forced quit.
---

## MVP Stage - [Click Here](https://github.com/YHLeong/EGL314_TeamC/blob/main/Backlog%203%20Sprint%202/game%20code.py)
### 🧾 Overview

This Python script implements an **interactive light-up game** using a **Raspberry Pi 4** with **WS281x LED strips**, **OSC communication**, and **Tkinter GUI**. Players must reach specific milestones by activating sensors while lights progressively fill up. The game integrates with **REAPER audio software** and **GrandMA3 lighting console** for immersive audio-visual feedback across **4 progressive difficulty levels**.

---

### 📚 Python Packages Used
```python
import time
import threading
import tkinter as tk
from rpi_ws281x import *
from pythonosc import udp_client, dispatcher, osc_server
```

#### ⏰ time
- Purpose: Timing controls and delays
- Used For: `time.time()` for elapsed time tracking, `time.sleep()` for LED animations

#### 🧵 threading
- Purpose: Multi-threaded execution
- Used For: Running OSC server, game logic, and GUI simultaneously without blocking

#### 🖼️ tkinter
- Purpose: GUI interface
- Used For: Displaying game status, level info, timer, and results in fullscreen mode

#### 💡 rpi_ws281x
- Purpose: Control addressable LED strips
- Used For: 300-LED strip animations, progress visualization, and stage feedback

#### 📡 pythonosc
- Purpose: OSC (Open Sound Control) communication
- Used For: Bidirectional communication with REAPER audio and GrandMA3 lighting

---

### 🌐 Network Setup
```python
GMA_IP, GMA_PORT       = "192.168.254.213", 2000  # GrandMA3 Console
REAPER_IP, REAPER_PORT = "192.168.254.12", 8000   # REAPER Audio
LOCAL_IP, LOCAL_PORT   = "192.168.254.108", 8001  # Game Controller
```
- **GrandMA3**: Receives lighting cue commands
- **REAPER**: Receives audio marker triggers and playback control
- **Local**: Listens for sensor input via OSC messages

---

### 💡 LED Strip Configuration
```python
LED_COUNT = 300
strip = Adafruit_NeoPixel(LED_COUNT, 18, 800000, 10, False, 128)
strip.begin()
```
- **300 LEDs** on GPIO pin 18
- **800kHz** signal frequency
- **128** brightness level for optimal visibility

### 🎨 LED Animation Functions
```python
def light_up(n, color):
    for i in range(n):
        strip.setPixelColor(i, color)
    strip.show()

def red_dim(n):
    for i in range(n - 1, -1, -1):
        strip.setPixelColor(i, Color(255, 0, 0))
        strip.show()
        time.sleep(0.005)
        strip.setPixelColor(i, 0)
        strip.show()
```
- **Instant fill**: `light_up()` for progress visualization
- **Animated dimming**: `red_dim()` for failure feedback with reverse countdown
- **Stage-specific colors**: Dynamic color mapping based on difficulty level

---

### 🎮 Game Progression System
```python
goals = {1: 40, 2: 80, 3: 120, 4: 240}
times = {1: 30, 2: 40, 3: 50, 4: 60}
milestones = {
    1: [10, 20, 30, 40],
    2: [20, 40, 60, 80],
    3: [30, 60, 90, 120],
    4: [60, 120, 180, 240]
}
```
- **4 Levels** with increasing difficulty
- **Progressive goals**: 40 → 80 → 120 → 240 sensor activations
- **Extended time limits**: 30s → 60s per level
- **Milestone triggers**: Audio/lighting cues at 25%, 50%, 75%, 100% completion

---

### 🎵 Audio Integration (REAPER)
```python
def trigger_reaper(id):
    global level
    stage_time = times.get(level, 30)
    
    if id.startswith("/"):
        reaper.send_message(id, 1.0)  # Full OSC address
    else:
        reaper.send_message(f"/action/{id}", 1.0)  # Action number
    
    reaper.send_message("/action/1007", 1.0)   # Play
    threading.Timer(stage_time, lambda: reaper.send_message("/action/1016", 1.0)).start()
```
- **Dual format support**: Handles both action numbers (`"41261"`) and full paths (`"/marker/18"`)
- **Auto-play**: Jumps to marker and starts playback automatically
- **Timed stop**: Audio stops after stage time limit expires
- **Milestone audio**: Different markers for progress points and game events

---

### 💡 Lighting Integration (GrandMA3)
```python
def trigger_osc(n):
    cues = milestones.get(level, [])
    if n == cues[0]: gma.send_message("/gma3/cmd", "Go Sequence 23 cue 1"); trigger_reaper("41261")
    elif n == cues[1]: gma.send_message("/gma3/cmd", "Go Sequence 23 cue 2"); trigger_reaper("41262")
    elif n == cues[2]: gma.send_message("/gma3/cmd", "Go Sequence 23 cue 3"); trigger_reaper("41263")
    elif n == cues[3]: gma.send_message("/gma3/cmd", "Go Sequence 23 cue 4"); trigger_reaper("41264")
```
- **Milestone lighting**: Triggers specific lighting sequences at progress points
- **Synchronized audio**: Each lighting cue paired with corresponding audio marker
- **Stage management**: Separate sequences for wins, losses, and level transitions

---

### 🖥️ GUI Interface
```python
class GameUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))
        self.root.bind("<space>", self.start_sequence)
        
        self.labels = {
            "level":  tk.Label(self.root, text="Level: 1", font=("Arial", 28)),
            "time":   tk.Label(self.root, text="Time: 0", font=("Arial", 28)),
            "result": tk.Label(self.root, text="Stage: In Progress", fg="blue"),
            "game":   tk.Label(self.root, text="Game: Waiting", fg="gray"),
            "tries":  tk.Label(self.root, text="Tries Left: 3", font=("Arial", 28))
        }
```
- **Fullscreen mode**: Immersive gaming experience
- **Real-time updates**: Level, timer, tries, and status indicators
- **Keyboard controls**: Spacebar to start, Escape to exit fullscreen
- **Color-coded feedback**: Success (green), failure (red), progress (blue)

---

### 📡 OSC Communication Handler
```python
def print_args(addr, *args):
    global count, started, timing, start_time, timeout, level, tries, waiting

    if not ready: return
    
    if not started:
        started = True
        level_start_sequence(level)
        return
        
    if not timing:
        start_time = time.time()
        timing = True
        return
        
    count += 1
    if count in milestones.get(level, []):
        progress = int(LED_COUNT * (count / goals[level]))
        light_up(progress, get_stage_color(level))
        trigger_osc(count)
```
- **State management**: Handles game initialization, timing, and progress tracking
- **Sensor counting**: Increments progress on each OSC message received
- **Visual feedback**: Updates LED strip to show completion percentage
- **Milestone detection**: Triggers audio/lighting when reaching progress points

---

### ⏱️ Real-time Game Loop
```python
def start_game_logic():
    while True:
        if timing and not timeout:
            elapsed = time.time() - start_time
            remaining = times.get(level, 30) - elapsed
            ui.update("time", f"Time: {max(0, int(remaining))}")
            
            if elapsed > times[level] and count < goals[level]:
                timeout = True
                tries += 1
                trigger_reaper("/marker/18")  # Failure audio
                
        time.sleep(0.01)
```
- **60Hz update rate**: Smooth timer and status updates
- **Timeout detection**: Automatically fails stage when time expires
- **Try management**: Tracks failed attempts (3 strikes = game over)
- **Non-blocking**: Runs in separate thread to maintain GUI responsiveness

---

### 🏆 Win/Loss Logic
```python
if count == goals[level]:
    flash_bpm(LED_COUNT)
    green_dim(LED_COUNT)
    trigger_reaper("41270")  # Stage win audio
    
    if level == MAX_LEVEL:
        trigger_reaper("/marker/19")  # Game win audio
        ui.update("game", "Game: Win", "green")
    else:
        level += 1
        waiting = True
```
- **Stage completion**: Visual celebration with LED animations
- **Progressive difficulty**: Automatic advancement to next level
- **Game completion**: Special audio/visual for final victory
- **Failure handling**: Audio feedback and retry system with limited attempts

---

### 🧵 Threaded Architecture
```python
threading.Thread(target=start_game_logic, daemon=True).start()
ui.root.mainloop()
```
- **Main thread**: GUI event loop for responsive interface
- **Game thread**: Core game logic and timing (daemon mode)
- **OSC thread**: Network communication handler (auto-managed)
- **Timer threads**: Audio stop scheduling (background)

---

### 🔧 Hardware Integration
- **Raspberry Pi 4**: Main controller running Python game logic
- **WS281x LED Strip**: 300-LED visual progress indicator
- **OSC Sensors**: External devices sending activation signals
- **Network**: Ethernet connection for reliable OSC communication
- **Audio**: REAPER software on separate PC for immersive sound
- **Lighting**: GrandMA3 console for professional stage lighting effects

---

## REAPER Marker Configuration
| Marker | REAPER Action   | Command ID   |
|:------:|:---------------:|:------------:|
| 21     | Load sound 1     | 41261        |
| 22     | Load sound 2     | 41262        |
| 23     | Load sound 3     | 41263        |
| 24     | Load sound 4     | 41264        |
| 25     | Load sound 5     | 41265        |
| 26     | Load sound 6     | 41266        |
| 27     | Level 1 start    | 41267        |
| 28     | Level 2 start    | 41268        |
| 29     | Level 3 start    | 41269        |
| 30     | Win stage        | 41270        |
| 31     | Lose stage       | /marker/18   |
| 32     | Win game         | /marker/19   |
| 33     | Lose game        | /marker/20   |





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
-  1x Raspberry Pi 4 Model B  
-  6x AoKu AK-399 Car Seat Pressure Sensors  
-  6x WAGO Connectors  
-  2x LAN cables
-  6x Carboard Button
-  1x Rasp Pi display V1
-  1x Display holder

### 💻 Software
-  Random Number Generator  
-  Sensor Signal Detector
---


## Physical connections and Props

Cabling
- 2x LAN cable

Since there are six sensors I needed twelve wires in total. I didn't want to use jumper wires as there would be too many points of failure over a long cable. I decided to use LAN cables by isolating two wires per sensor. Since a LAN cable only has four pairs and I needed six, I used two LAN cables.

Props
- Buttons
- Screen holder
- Prop Materials: Cardboard Glue 

We are using cardboard to make everything. For the buttons, we layered three pieces of cardboard and carved a shape into the top two layers to create a 3D effect. For the screen holder, I used glue and cardboard to make an angled piece of cardboard with a hole for the screen. 



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


## Prove Of Concept - [Click Here]()insert link here
### 🧾 Overview

This Python script implements a **progressive memory game** using a **Raspberry Pi** and **Tkinter GUI**. Players must memorize and replicate sequences shown on screen by pressing corresponding physical buttons connected via **GPIO pins**. The game consists of **multiple stages** with increasing sequence lengths, categorized into **Easy, Medium, and Hard** difficulty levels.



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
Purpose: Interface with Raspberry Pi’s physical GPIO pins.

Used For: Configuring buttons as inputs and detecting button presses with debounce logic.

#### 🖼️ tkinter
- Purpose: Render and manage the GUI.
- Used For: Displaying sequences, sensor statuses, timers, and results dynamically.

#### 🎰 random
- Purpose: Sequence generation.
- Used For: `random.randint(1, 6)` to create a randomized pattern of sensor numbers.

#### ⏰ time
- Purpose: Sleep timing and debouncing.
- Used For: `time.sleep()`, `time.time()` to handle delays and debounce checks.

#### 🧵 threading
- Purpose: Keep GUI responsive while running game logic.    
- Used For: Running the main game function `(run_sequence_challenge)` in a separate thread.
---

### 🧭 GPIO Setup
```
SENSOR_MAP = {1: 17, 2: 6, 3: 19, 4: 16, 5: 20, 6: 21}
GPIO.setmode(GPIO.BCM)
for pin in SENSOR_MAP.values():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
```
- Six sensors are mapped to GPIO pins.
- Input pins use pull-up resistors (active-low).
- BCM mode used for pin numbering.
---

### 🖥️ GUI Layout
```
root = tk.Tk()
root.title("Sensor Sequence Challenge")
```
- Main Window: Title set to "Sensor Sequence Challenge".

```
timer_label = tk.Label(...)  
sequence_label = tk.Label(...)  
result_label = tk.Label(...)  
labels_frame = tk.Frame(root)
```
- Timer Label: Shows time remaining for current stage.
- Sequence Label: Shows instructions and sequence step-by-step.
- Result Label: Displays success/failure feedback.
- Sensor Labels: Dynamically update with sensor states ("Pressed"/"Not Pressed").


---

### 🎮 Game Flow
```
steps_per_stage = [1, 2, 3, 4, 5, 6, 7, 9, 12]
difficulties = ["Easy", "Medium", "Hard"]
```
- Stages: 9 in total, increasing step complexity.
- Grouped into: 3 difficulty levels × 3 stages each.
  
### 🔢 Sequence Generation
```
full_sequence = [random.randint(1, 6) for _ in range(12)]
```
- A full 12-step random sequence is generated at the start and split across stages.

### 👁️ Displaying Sequence
```
def show_sequence_step_by_step(seq, length):
    def show_next(index):
        if index < length:
            sequence_label.config(text=f"Sequence Number {index + 1}: {seq[index]}")
            root.after(1000, show_next, index + 1)
        else:
            sequence_label.config(text=f"Repeat the first {length} steps using sensors!")
            start_sensor_monitoring()
    show_next(0)
```
- Displays the sequence one number per second using `root.after`.
- Informs the player when it's time to repeat the steps using sensors.
- Monitoring only starts after the full display finishes.

### 🧠 Sensor Monitoring
```
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

```
- Polls GPIO pins every 100ms to detect button presses.
- Debounce protection: Only accepts inputs spaced by `DEBOUNCE_DELAY = 0.5` seconds.
- Press limit: Each sensor can only be pressed twice per round.
- Inputs get appended to `user_input` until it matches expected length.



### ✔️ Sequence Validation
```
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
```
- Compares player input to the expected segment of the full sequence.
- Displays ✅ if correct, ❌ if wrong (with expected vs. actual).
- Ends stage on validation result.

### ⏱️ Countdown Timer
```
def start_timer(seq_length):
    total_time = TIMER_MAP.get(seq_length, 30)
    def countdown():
        nonlocal total_time
        while total_time > 0 and not sequence_completed.is_set():
            mins, secs = divmod(total_time, 60)
            timer_label.config(text=f" Time Left: {mins:02d}:{secs:02d}")
            time.sleep(1)
            total_time -= 1
        if not sequence_completed.is_set():
            timer_label.config(text=" Time's up!")
            timer_failed.set()
```
- The timer starts only after the sequence is shown.
- Counts down in real time and ends the round on timeout.
---

### 🧵 Threaded Execution
```
threading.Thread(target=run_sequence_challenge, daemon=True).start()
```
- Main game loop runs on a background thread.
- Keeps GUI responsive and prevents freezing during time delays or blocking calls.
---

### 🧩 Stage Logic
```
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
```
- Each stage resets labels and displays the assigned sequence portion.
- Waits for user to complete input or timeout.
- Returns whether the user passed the stage.
---

### 🚦 GUI Main Loop & Cleanup
```
try:
    root.mainloop()
finally:
    GPIO.cleanup()
```
- Main GUI loop keeps the window running.
- On exit (even via Ctrl+C), GPIO pins are reset properly to avoid hangups or damage.
---

### ✋ Graceful Exit
```
finally:
    GPIO.cleanup()
```
- Ensures all GPIO pins are released properly.
- Required for hardware stability and avoiding pin lockups after crash or forced quit.
- ---

## MVP
### Audio
| Marker | REAPER Action   | Command ID   |
|:------:|:---------------:|:------------:|
| 21     | Load sound 1     | 41261        |
| 22     | Load sound 2     | 41262        |
| 23     | Load sound 3     | 41263        |
| 24     | Load sound 4     | 41264        |
| 25     | Load sound 5     | 41265        |
| 26     | Load sound 6     | 41266        |
| 27     | Level 1 start    | 41267        |
| 28     | Level 2 start    | 41268        |
| 29     | Level 3 start    | 41269        |
| 30     | Win stage        | 41270        |
| 31     | Lose stage       | /marker/18   |
| 32     | Win game         | /marker/19   |
| 33     | Lose game        | /marker/20   |

### Lighting
| Sequence/Cue|     Action    | 
|:-----------:|:-------------:|
| 23          |   Charging    |
| 32          |   Game Lose   |
| 33          |   Game Win    |
| 38          |   Game Play   |
| 41          |   During Game | 




