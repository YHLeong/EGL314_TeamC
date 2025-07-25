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
