# AV Game Code Documentation (Beginner-Friendly)

> This document explains the entire AV memory game code using NeoPixels, OSC communication, and a GUI. All code and logic are explained line-by-line in beginner-friendly language.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [NeoPixel LED Setup](#neopixel-led-setup)
3. [OSC Configuration](#osc-configuration)
4. [Lighting Effects](#lighting-effects)
5. [Level and Game Logic](#level-and-game-logic)
6. [OSC Markers and Cues](#osc-markers-and-cues)
7. [GUI Display](#gui-display)
8. [OSC Event Handling](#osc-event-handling)
9. [Game Loop Timing](#game-loop-timing)
10. [Shutdown and Cleanup](#shutdown-and-cleanup)
11. [Logic Diagram](#logic-diagram)
12. [OEM Pressure Sensor Notes](#oem-pressure-sensor-notes)

---

## System Overview

This game runs on a Raspberry Pi with the following components:

* A NeoPixel LED strip (300 pixels)
* An OEM pressure sensor to trigger actions
* REAPER (for audio playback via OSC)
* GrandMA3 (for lighting control via OSC)
* A tkinter GUI for displaying the game status

---

## NeoPixel LED Setup

```python
from rpi_ws281x import Adafruit_NeoPixel, Color

LED_COUNT = 300
strip = Adafruit_NeoPixel(LED_COUNT, 18, 800000, 10, False, 128)
strip.begin()
```

**Explanation:**

* We use 300 LEDs controlled by GPIO 18.
* The `Adafruit_NeoPixel` sets up the strip.
* `strip.begin()` prepares the strip for use.

---

## OSC Configuration

```python
from pythonosc import udp_client

GMA_IP, GMA_PORT = "192.168.254.213", 2000
REAPER_IP, REAPER_PORT = "192.168.254.12", 8000

reaper_client = udp_client.SimpleUDPClient(REAPER_IP, REAPER_PORT)
gma_client = udp_client.SimpleUDPClient(GMA_IP, GMA_PORT)
```

**Explanation:**

* We set up two OSC clients: one for REAPER, one for GrandMA3.
* These send commands over IP to each software.

---

## Lighting Effects

```python
def light_up(n, color):
    for i in range(n):
        strip.setPixelColor(i, color)
    strip.show()
```

**Explanation:** Turns on the first `n` LEDs with the given color.

```python
def red_dim_down(n):
    for i in range(n-1, -1, -1):
        strip.setPixelColor(i, Color(255, 0, 0))
        strip.show()
        time.sleep(0.005)
        strip.setPixelColor(i, 0)
        strip.show()
    for _ in range(5):
        light_up(n, Color(255, 0, 0)); time.sleep(0.3)
        light_up(n, 0); time.sleep(0.3)
    light_up(LED_COUNT, 0)
```

**Explanation:** Turns on LEDs red in reverse, blinks red, and clears the strip.

```python
def flash_bpm(n, bpm=120, duration=5):
    delay = 60 / bpm / 2
    for _ in range(int(duration / (delay * 2))):
        light_up(n, Color(0, 255, 0)); time.sleep(delay)
        light_up(n, 0); time.sleep(delay)
```

**Explanation:** Flashes LEDs on and off like a heartbeat using BPM.

---

## Level and Game Logic

```python
level_goals = {1: 40, 2: 80, 3: 120, 4: 240}
level_times = {1: 30, 2: 40, 3: 50, 4: 60}
```

**Explanation:** Each level has a goal (e.g., hit 40 times) and a time limit.

```python
def get_stage_color(level):
    return {
        1: Color(255, 0, 0),
        2: Color(255, 165, 0),
        3: Color(255, 255, 0),
        4: Color(0, 255, 0)
    }.get(level, Color(255, 255, 255))
```

**Explanation:** Returns a color based on the level number.

---

## OSC Markers and Cues

```python
addr = "/action/41261"   # Marker 21
addr1 = "/action/41262"  # Marker 22
addr15 = "/action/1007"  # Play
addr16 = "/action/1016"  # Stop
```

**Explanation:** These OSC addresses are shortcuts to actions in REAPER.

```python
def trigger_reaper(addr, msg=1.0):
    reaper_client.send_message(addr, msg)
```

**Explanation:** Sends a command to REAPER.

```python
def trigger_reaper_with_delay(marker_addr, play_addr, stop_addr, delay=20):
    def delayed_sequence():
        trigger_reaper(marker_addr)
        time.sleep(0.5)
        trigger_reaper(play_addr)
        time.sleep(delay)
        trigger_reaper(stop_addr)
    threading.Thread(target=delayed_sequence, daemon=True).start()
```

**Explanation:** Starts playback in REAPER, waits, and stops.

---

## GUI Display

```python
import tkinter as tk

root = tk.Tk()
root.title("AV Game")
root.attributes("-fullscreen", True)
```

**Explanation:** Opens a fullscreen window to show game status.

```python
level_label = tk.Label(root, text="Level: 1")
level_label.pack()
```

**Explanation:** Displays the current level to the player.

---

## OSC Event Handling

```python
from pythonosc import dispatcher, osc_server

def print_args(addr, *args):
    if not game_started:
        game_started = True
        level_start_sequence(current_level)
```

**Explanation:** When the sensor sends data, this function reacts.

---

## Game Loop Timing

```python
def start_game_logic():
    while True:
        if timing_started and not timeout_triggered:
            time_left = get_level_time(current_level) - (time.time() - start_time)
```

**Explanation:** Runs a loop to check if time has run out for the level.

---

## Shutdown and Cleanup

```python
def shutdown_sequences(level):
    cues = ["23 cue 1", "23 cue 2", "23 cue 3", "23 cue 4"]
    for cue in cues:
        gma_client.send_message("/gma3/cmd", f"Off Sequence {cue}")
    trigger_reaper(addr16)
```

**Explanation:** Turns off lighting cues and stops audio playback.

---

## Logic Diagram


## OEM Pressure Sensor Notes

* The sensor is not AoKu; it's a generic OEM type.
* Connected via GPIO and sends OSC messages.
* Debouncing and filtering should be handled in `print_args()`.

---
