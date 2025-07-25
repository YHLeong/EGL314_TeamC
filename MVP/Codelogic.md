# AV Game Code Documentation

> This markdown explains the full codebase for the AV memory game with NeoPixel lighting, OSC communication with REAPER and GrandMA3, and a tkinter GUI interface.

---

## 📂 Table of Contents

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
11. [📁 Subpages & Modules](#subpages--modules)  
12. [⚙️ OEM Pressure Sensor Notes](#oem-pressure-sensor-notes)  
13. [Credits](#credits)  

---

## System Overview

This is a memory-style AV game built using:

- **Raspberry Pi** running the game code.  
- **NeoPixel Strip (WS281x)** for lighting feedback (300 pixels).  
- **OEM Pressure Sensor** (not AoKu) to register input events.  
- **GrandMA3 (GMA3)** and **REAPER** controlled via OSC (Open Sound Control).  
- **Tkinter** for GUI status display.  
- Code is written in **Python 3**.

---

## NeoPixel LED Setup

The NeoPixel strip is configured for 300 LEDs and connected to GPIO 18.

```python
LED_COUNT = 300
strip = Adafruit_NeoPixel(LED_COUNT, 18, 800000, 10, False, 128)
strip.begin()
```

- `LED_COUNT`: Number of LEDs used in the strip.  
- `Adafruit_NeoPixel`: From the `rpi_ws281x` library.  
- `strip.begin()`: Starts communication with the LED hardware.

### Logic Diagram (placeholder)

```plaintext
┌──────────────┐
│ Raspberry Pi │
└──────┬───────┘
       │
   GPIO 18
       │
┌──────▼──────┐
│ 300 NeoPixel│
└─────────────┘
```

### Credits

- NeoPixel code based on `rpi_ws281x` Python library.  
- Configuration tested on Raspberry Pi GPIO.

---

## OSC Configuration

OSC is used to send messages to:

- **GrandMA3 lighting desk**
- **REAPER audio workstation**

We use Python’s `python-osc` library to send and receive OSC messages.

```python
from pythonosc import udp_client

GMA_IP, GMA_PORT = "192.168.254.213", 2000
REAPER_IP, REAPER_PORT = "192.168.254.12", 8000

gma_client = udp_client.SimpleUDPClient(GMA_IP, GMA_PORT)
reaper_client = udp_client.SimpleUDPClient(REAPER_IP, REAPER_PORT)
```

These clients let us send commands like:

```python
gma_client.send_message("/gma3/cmd", "Go Sequence 23 cue 1")
reaper_client.send_message("/action/41261", 1.0)
```

### OSC Server (for receiving sensor events)

The local OSC server runs on port `8001` and listens for `/print` messages.

```python
from pythonosc import dispatcher, osc_server

LOCAL_IP, LOCAL_PORT = "192.168.254.108", 8001

osc_dispatcher = dispatcher.Dispatcher()
osc_dispatcher.map("/print", print_args)

osc_server_thread = osc_server.ThreadingOSCUDPServer(
    (LOCAL_IP, LOCAL_PORT), osc_dispatcher
)
```

### Credits

- OSC communication is handled by the `python-osc` package.  
- GMA3 and REAPER must be preconfigured to match these IPs and ports.

---
# AV Game Code (Beginner-Friendly Explanation)

This document explains every part of the AV game code using NeoPixels, OSC, and tkinter in simple language. Code snippets are followed by clear explanations so even beginners can understand how it works.

---

## 1. NeoPixel Setup

```python
from rpi_ws281x import Adafruit_NeoPixel, Color

LED_COUNT = 300
strip = Adafruit_NeoPixel(LED_COUNT, 18, 800000, 10, False, 128)
strip.begin()
```

**Explanation:**
- We are using 300 LEDs connected to GPIO pin 18.
- The strip needs some parameters like frequency and brightness.
- `strip.begin()` is required to activate it before use.

---

## 2. Turning on LEDs

```python
def light_up(n, color):
    for i in range(n):
        strip.setPixelColor(i, color)
    strip.show()
```

**Explanation:**
- Lights up the first `n` LEDs with the given `color`.
- Uses a loop to assign the color to each LED.
- `strip.show()` updates the LED strip with the changes.

---

## 3. Red Dim Down Animation

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

**Explanation:**
- Lights LEDs red one at a time from end to start.
- Then it blinks the entire strip red 5 times.
- Finally, it turns everything off.

---

## 4. Green Dim Down

```python
def green_dim_down(n):
    for i in range(n-1, -1, -1):
        strip.setPixelColor(i, Color(0, 255, 0))
        strip.show()
        time.sleep(0.005)
        strip.setPixelColor(i, 0)
        strip.show()
```

**Explanation:**
- Same concept as red dim down, but with green color.

---

## 5. Flash LEDs to BPM

```python
def flash_bpm(n, bpm=120, duration=5):
    delay = 60 / bpm / 2
    for _ in range(int(duration / (delay * 2))):
        light_up(n, Color(0, 255, 0)); time.sleep(delay)
        light_up(n, 0); time.sleep(delay)
```

**Explanation:**
- Flashes the lights to a beat (like music tempo).
- `bpm` is beats per minute. 120 bpm is a fast pace.
- `duration` is total time for the flashing.

---

## 6. Getting a Color Based on Level

```python
def get_stage_color(level):
    return {
        1: Color(255, 0, 0),
        2: Color(255, 165, 0),
        3: Color(255, 255, 0),
        4: Color(0, 255, 0)
    }.get(level, Color(255, 255, 255))
```

**Explanation:**
- Returns a specific color for each level.
- If the level doesn’t match, it defaults to white.

---

## 7. Starting the Level Sequence

```python
def level_start_sequence(level):
    if level == 1:
        trigger_reaper_with_level_delay(addr6, 1)
        for _ in range(6):
            light_up(LED_COUNT, Color(0, 0, 255)); time.sleep(0.25)
            light_up(LED_COUNT, 0); time.sleep(0.25)
        light_up(LED_COUNT, Color(0, 255, 0)); time.sleep(2)
        light_up(LED_COUNT, 0)
```

**Explanation:**
- Each level plays a specific animation.
- This one flashes blue lights for Level 1.
- Then it turns green for 2 seconds, meaning “Go!”

---

## 8. REAPER OSC Trigger

```python
from pythonosc import udp_client

REAPER_IP, REAPER_PORT = "192.168.254.12", 8000
reaper_client = udp_client.SimpleUDPClient(REAPER_IP, REAPER_PORT)

def trigger_reaper(addr, msg=1.0):
    reaper_client.send_message(addr, msg)
```

**Explanation:**
- Sends commands to REAPER audio software using OSC protocol.
- `addr` is the OSC address to target.
- `msg` is the value to send.

---

## 9. Trigger REAPER with Delay

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

**Explanation:**
- Jumps to a marker in REAPER, plays audio, waits, then stops.
- Runs in a background thread so the main game can continue.

---

## 10. GrandMA3 OSC Setup

```python
GMA_IP, GMA_PORT = "192.168.254.213", 2000
gma_client = udp_client.SimpleUDPClient(GMA_IP, GMA_PORT)
```

**Explanation:**
- Sets up another OSC client, but this time for GrandMA3 lighting controller.

---

## 11. Sending Lighting Cues

```python
gma_client.send_message("/gma3/cmd", "Go Sequence 23 cue 1")
```

**Explanation:**
- Tells the lighting desk to start a specific cue from a sequence.

---

## 12. GUI for Game Display

```python
import tkinter as tk

self.root = tk.Tk()
self.root.title("AV Game Status")
self.root.geometry("300x220")
```

**Explanation:**
- Creates a fullscreen window that shows level, time left, and tries.
- Useful for the operator or players to see progress visually.

---

## 13. Game State Variables

```python
count = 0
stage_tries = 0
game_started = False
...
current_level = 1
```

**Explanation:**
- Tracks game progress: score, current level, and how many tries the player has used.

---

## 14. Game Loop (Timing and Loss Detection)

```python
def start_game_logic():
    while True:
        if timing_started and not timeout_triggered:
            time_left = get_level_time(current_level) - (time.time() - start_time)
            if time_left <= 0:
                # trigger lose logic
```

**Explanation:**
- Keeps checking how much time is left.
- If the time runs out, the game knows the player lost the level.

---

## 15. OSC Event Handler (From Sensor)

```python
def print_args(addr, *args):
    if not game_started:
        game_started = True
        level_start_sequence(current_level)
```

**Explanation:**
- When the sensor sends a signal, this function runs.
- If the game hasn’t started yet, it starts the current level.

---

## 16. Logic Diagram (How Everything Connects)

```plaintext
OEM Pressure Sensor
         │
         ▼
     OSC Server
         │
     Game Logic
      /     \
GUI Display  Lighting
                │
       OSC to REAPER + GMA3
```

**Explanation:**
- This shows how the hardware and software are connected.
- Sensor → OSC → Game logic → Lights & Sound

---

## 17. Pressure Sensor Notes

- The sensor is not an AoKu brand. It’s an OEM sensor.
- It triggers input through OSC to `/print`.
- Use `print_args()` to handle the response.
- Debounce in code or hardware to avoid false triggers.

---

## Summary

This game connects:
- NeoPixels for lighting
- GrandMA3 for lighting control
- REAPER for audio playback
- A physical pressure sensor for input
- A tkinter GUI to show game status

Each part works using Python functions, OSC messages, and GPIO control.

---
