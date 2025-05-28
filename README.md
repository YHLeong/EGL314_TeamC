# 🎮 EGL314 – Project Documentation

## 🧩 Project Title
**Wall Glyphs: Silent Sequence**

---

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

### 🎲 Random Number Generator - [Click Here](https://github.com/YHLeong/EGL314_TeamC/blob/main/Backlog%202%20sprint%201/RandomNumberGenerator_v4.py)
#### 🧾 Overview

This Python script continuously generates and prints sequences of random integers. Each sequence has a length that cycles through **4**, **8**, and **12**, refreshing every **1 second** until the user stops the script with **Ctrl+C**.

---

### 📚 Libraries Used
```
import random
import time
```
##### 🎰random
Purpose: Used to generate random integers.
<br>
Function Used: random.randint(a, b) returns a random integer N such that a <= N <= b.

##### ⏰time
Purpose: Provides time-related functions. 
<br>
Function Used: time.sleep(seconds) pauses program execution for the given number of seconds.

#### 🔄Index Tracker

```
sequence_lengths = [4, 8, 12]
current_index = 0  # Start at 4
```
- Tracks the current position in the sequence_lengths list.
- Initially set to 0, meaning the sequence will start with a length of 4.

#### 🔁Main Loop
```
while True:
  ...
```
- An infinite loop (while True) is used to continuously generate sequences.
- The loop continues until the user stops it manually (e.g., with Ctrl+C).

#### 🧮Sequence Generation
```
seq_length = sequence_lengths[current_index]
sequence = [random.randint(1, 6) for _ in range(seq_length)]
```
- Retrieves the current sequence length using the current_index.
- Generates a list of random integers between 1 and 6 (inclusive), simulating dice rolls.
- Uses list comprehension for concise generation.

#### 📤Output
```
print(f"Generated sequence ({seq_length} numbers): {sequence}")
```
- Prints the generated sequence along with the number of elements.

#### ➕Index Update
```
current_index = (current_index + 1) % len(sequence_lengths)
```
- Updates current_index to point to the next length in the list.
- Uses modulo (%) to cycle back to the start when the end is reached.

#### ⏳Delay
```
time.sleep(1)
```
- Waits for 1 second before generating the next sequence.
- Helps maintain a steady interval between outputs.

#### ✋Graceful Exit
```
except KeyboardInterrupt:
    print("\nExiting... Program stopped by user.")
```
- Allows the user to stop the program gracefully using Ctrl + C.
- Catches the KeyboardInterrupt exception and prints a message before exiting.
---

test change 



