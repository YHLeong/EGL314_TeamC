# EGL314 – Project Documentation

## Project Title
**Wall Glyphs: Silent Sequence**

## Introduction
This project involves the development of an immersive, non-verbal multiplayer game titled **Wall Glyphs: Silent Sequence**. The game is designed for 3 to 4 players who must collaborate to activate six wall-mounted glyphs in a specific sequence—without any verbal communication or visual cues.

## Objective
Players must replicate a pre-defined glyph activation sequence, demonstrated through a lighting display, by physically triggering pressure-sensitive stones in the correct order. The sequence must be completed within a set time limit after a spatial audio cue signals the start of the attempt.

## Dependencies
### hardware
- 1x Raspberry Pi 4 Model B
- 6x AoKu AK-399 Car seat pressure sensor
- 6x WAGO Connector
- 13x Jumper Wire
   
### Software
- Random Number Generator
- Sensor Signal Detector 

## System Diagram
![System Diagram](AssetsFolder/SystemDiagram_Updated.png)

## Code Logic
### Random Number Generator
#### Overview

This Python script generates and prints sequences of random integers at regular intervals. The sequence length cycles through a predefined list of values: `4`, `8`, and `12`. The process repeats every 1 second until the user manually interrupts it.

#### Library Used
```
import random
import time
```
##### random
Purpose: Used to generate random integers.
<br>
Function Used: random.randint(a, b) returns a random integer N such that a <= N <= b.

##### time
Purpose: Provides time-related functions. 
<br>
Function Used: time.sleep(seconds) pauses execution of the program for the given number of seconds.

#### Index Tracker

```
sequence_lengths = [4, 8, 12]
current_index = 0  # Start at 4
```
- Tracks the current position in the sequence_lengths list.
- Initially set to 0, meaning the sequence will start with a length of 4.

#### Main Loop
```
while True:
  ...
```
- An infinite loop (while True) is used to continuously generate sequences.
- The loop continues until the user stops it manually (e.g., with Ctrl+C).

#### Sequence Generation
```
seq_length = sequence_lengths[current_index]
sequence = [random.randint(1, 6) for _ in range(seq_length)]
```
- Retrieves the current sequence length using the current_index.
- Generates a list of random integers between 1 and 6 (inclusive), simulating dice rolls.
- Uses list comprehension for concise generation.

#### Output
```
print(f"Generated sequence ({seq_length} numbers): {sequence}")
```
- Prints the generated sequence along with the number of elements.

#### Index Update
```
current_index = (current_index + 1) % len(sequence_lengths)
```
- Updates current_index to point to the next length in the list.
- Uses modulo (%) to cycle back to the start when the end is reached.

#### Delay
```
time.sleep(1)
```
- Waits for 1 second before generating the next sequence.
- Helps maintain a steady interval between outputs.

#### Graceful Exit
```
except KeyboardInterrupt:
    print("\nExiting... Program stopped by user.")
```
- Allows the user to stop the program gracefully using Ctrl+C.
- Catches the KeyboardInterrupt exception and prints a message before exiting.

