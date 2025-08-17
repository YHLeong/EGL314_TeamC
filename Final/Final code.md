# AV Game Controller — README (Detailed & Beginner-Friendly)

This project runs a **stage-based game** that talks to **GrandMA3** (lighting) and **REAPER** (audio) over **OSC**. It shows live status in a **Tkinter** window and drives a **NeoPixel** LED strip on a Raspberry Pi.

This document explains *what happens*, *why it happens*, and *where to change things* — even if you’ve never written Python before. It also includes practical wiring, network, and testing tips.

> **Project rule (do not break):** From 2025-08-16 onward, only **audio/REAPER messaging** may be edited. **Do not** change game logic or any **GrandMA3 OSC command** logic in code.

---

## Table of Contents

1. [Quick Summary](#quick-summary)
2. [Hardware You Need](#hardware-you-need)
3. [Software You Need](#software-you-need)
4. [Network & OSC Setup](#network--osc-setup)
5. [Configure IPs & Ports](#configure-ips--ports)
6. [How to Run (Step-by-Step)](#how-to-run-step-by-step)
7. [Controls & On-Screen Info](#controls--on-screen-info)
8. [How the Game Works (Conceptual)](#how-the-game-works-conceptual)
9. [Code Walkthrough (Plain English)](#code-walkthrough-plain-english)
   - [Imports](#imports)
   - [NeoPixel Setup](#neopixel-setup)
   - [Lighting Effects](#lighting-effects)
   - [Game State (Variables)](#game-state-variables)
   - [Goals, Time & Milestones](#goals-time--milestones)
   - [REAPER “Address Book”](#reaper-address-book)
   - [GrandMA3 Milestone Commands](#grandma3-milestone-commands)
   - [Helper Functions](#helper-functions)
   - [GUI (Tkinter) & Startup **(+ Restart Feature)**](#gui-tkinter--startup--restart-feature)
   - [Receiving Sensor Presses (OSC)](#receiving-sensor-presses-osc)
   - [Game Tick Loop (Timer, Fail, **Auto-Restart Countdown**)](#game-tick-loop-timer-fail-auto-restart-countdown)
   - [Shutdown Sequence](#shutdown-sequence)
10. [Play Flow Example](#play-flow-example)
11. [What You Can Change Safely](#what-you-can-change-safely)
12. [Troubleshooting & Pitfalls](#troubleshooting--pitfalls)
13. [Testing Without Hardware](#testing-without-hardware)
14. [Glossary (Jargon → Plain Language)](#glossary-jargon--plain-language)
15. [Appendix: OSC Address Reference](#appendix-osc-address-reference)
16. [Appendix: Power & Wiring Notes](#appendix-power--wiring-notes)

---

## Quick Summary

- **Input:** A sensor sends button-press events as OSC messages to the Pi at the address `/print`.
- **Game:** There are **4 levels**. For each level you must press fast enough to reach a **goal** before **time** runs out.
- **Progress:** Each level has **4 milestones** (25%, 50%, 75%, 100%). Hitting a milestone:
  - Fills the LED strip proportionally,
  - Sends a **GrandMA3** cue,
  - Plays a short **SFX** in **REAPER**, then **auto-resumes BGM**.
- **UI:** A fullscreen window shows Level, Time Remaining, Tries, and Game/Stage status.
- **Audio:** Stage Armed, Milestones, Stage Win/Lose, Game Win/Lose, and BGM are triggered via REAPER OSC.
- **New:** A **Restart Countdown** (triggered automatically after a fail, or manually with **R**) pauses the stage and **forces re-arming** on the next sensor press.

---

## Hardware You Need

- **Raspberry Pi** (with PWM-capable pin GPIO 18 for NeoPixel; Pi 3/4 recommended).
- **NeoPixel/WS2812B LED strip**, e.g., 300 LEDs (or set `LED_COUNT` to your real number).
- **Power supply** for LEDs (do *not* power many LEDs from the Pi). Share **GND** between Pi and strip.
- **Network** access to:
  - **GrandMA3** console (OSC in),
  - **REAPER** machine (OSC in).

> **Rule of thumb for LED power:** 5V supply, ~60mA per LED at full white (worst case). For 300 LEDs, budget >18A if you *ever* approach full white. We don’t do full white here, but size your PSU safely and inject power along the strip.

---

## Software You Need

On the **Pi**:

```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-tk
pip3 install rpi-ws281x python-osc
```

> Some setups require root for NeoPixel:
>
> ```bash
> sudo python3 your_script.py
> ```

On the **REAPER** PC:

- Enable an **OSC Control Surface** (Preferences → Control/OSC/Web → Add → OSC).
- Make sure REAPER is listening on the **port** you set in the code (default **8000**).
- Prepare your **Actions** and **Markers** used by this game (see address list below).

On **GrandMA3**:

- Enable **OSC In**,
- Confirm the **port** (default **2000**),
- Verify `/gma3/cmd` receives strings like `Go Sequence 23 cue 1`.

---

## Network & OSC Setup

Think of OSC like “simple network messages” that say: *“Hey, run this!”* The Pi **sends** OSC to GrandMA3 and REAPER, and **listens** for OSC from your **sensor**.

- **To GrandMA3**: `/gma3/cmd` with text commands like `Go Sequence 23 cue 1`.
- **To REAPER**: `/action/<number>` (transport/SFX), `/marker/<number>` (jump to markers).
- **From Sensor**: Sends to the Pi’s `LOCAL_IP:LOCAL_PORT` at address `/print`. Each message counts as a **press**.

---

## Configure IPs & Ports

Inside the script:

```python
GMA_IP, GMA_PORT       = "192.168.254.213", 2000   # GrandMA3 OSC In
REAPER_IP, REAPER_PORT = "192.168.254.12",  8000   # REAPER OSC In
LOCAL_IP, LOCAL_PORT   = "192.168.254.108", 8006   # Pi's local OSC server (sensor sends here)
```

- **GMA_IP/GMA_PORT** → where GrandMA3 listens.
- **REAPER_IP/REAPER_PORT** → where REAPER listens.
- **LOCAL_IP/LOCAL_PORT** → where your sensor must send `/print`.

> **Tip:** `ping` each target from the Pi; if it fails, fix cabling, VLANs, or firewall.

---

## How to Run (Step-by-Step)

1. **Wire the LEDs** and power (see [Power & Wiring Notes](#appendix-power--wiring-notes)). Share **GND**.
2. **Set IPs/ports** in the script to match your network.
3. **Start** GrandMA3 and REAPER with OSC enabled.
4. On the **Pi**, run:
   ```bash
   sudo python3 your_script.py
   ```
5. A **fullscreen** Tkinter window appears.
6. Press **Space** once to run **Startup** (lights intro + start **BGM**). The game is now **Ready**.
7. Press your **sensor** to arm the level, then press again to start the **timer**.

---

## Controls & On-Screen Info

- **Space** → Startup: runs a brief lighting intro, starts **BGM** (loop), sets **Ready**.
- **Sensor press** (OSC to `/print`) while ready:
  - **1st press** → Arms the stage (blue flashes → green), plays *Stage Armed* SFX.
  - **2nd press** → Starts the **timer**.
  - **Next presses** → Increase the **count**; you hit **milestones** at 25/50/75/100%.
- **R**/**Shift+R** → **Manual Restart Countdown** (see detailed behavior below).
- **Esc** → Toggle fullscreen off (useful for debugging).
- **UI shows**:
  - **Level** (1–4),
  - **Time left** for the current stage,
  - **Tries** (failures so far; 3 fails = game over),
  - **Stage status** (Armed / Running / Win / Fail),
  - **Game status** (Win / Lose).

---

## How the Game Works (Conceptual)

- Each **level** has a **goal** (# of presses) and **time limit**. You must reach the **goal** before the **timer** ends.
- Progress is divided into **4 milestones**. Each time you cross a milestone:
  - LEDs fill correspondingly,
  - GrandMA3 gets a cue (visual feedback),
  - REAPER plays a **short SFX**, then automatically **resumes BGM**.
- If you reach the **goal** in time:
  - You get a green pulse + sweep on LEDs,
  - A **Stage Win** audio cue is triggered **after** the sweep,
  - If it’s the **last level**, a **Game Win** cue plays; otherwise, move to the next level.
- If you **run out of time**:
  - Red LED feedback and **Stage Lose** audio,
  - Increase **Tries** by 1,
  - After **3 fails**, **Game Lose** plays and the game resets.
- **New: Restart Countdown** allows a controlled pause/reset between attempts on the same level—either **automatically** after a fail or **manually** via **R**.

---

## Code Walkthrough (Plain English)

This section translates the code into everyday language. Where we mention Python words:

- A **variable** stores a value (like a named box).
- A **function** is a mini-program you can “call” (like pressing a button to do a task).
- A **dictionary** is like a tiny lookup table: `{"apple": 3, "orange": 5}`.
- A **set** stores unique items (`{1, 2, 3}`) and is good for “did this already?” checks.
- A **loop** repeats an action several times.

### Imports

```python
import time, threading, tkinter as tk
from rpi_ws281x import Adafruit_NeoPixel, Color
from pythonosc import udp_client, dispatcher, osc_server
```

- **time**: delays and measuring passing time.
- **threading**: runs a tiny background timer used to resume **BGM** after SFX.
- **tkinter**: creates the on-screen window.
- **rpi_ws281x**: controls the LED strip (hardware driver).
- **python-osc**: sends/receives OSC messages.

### NeoPixel Setup

```python
LED_COUNT = 300
strip = Adafruit_NeoPixel(LED_COUNT, 18, 800000, 10, False, 128)
strip.begin()
```

- `LED_COUNT` → how many LEDs you physically have.
- `18` → **GPIO 18** (hardware PWM pin for smooth LED control).
- `128` → brightness (0–255). Lower = dimmer = less power.
- `strip.begin()` → turns on the driver. Later, `strip.show()` actually pushes color changes out.

### Lighting Effects

**Fill LEDs up to a position (progress bar):**
```python
def light_up(n, color):
    for i in range(n):
        strip.setPixelColor(i, color)
    strip.show()
```

**Red “fail” animation:**
- Sweeps red backward, blinks a few times, then clears.
- Shows a clear “you failed” visual that’s easy to see.

**Green “success” sweep & pulse:**
- `green_dim` sweeps green like a “victory wave.”
- `flash_bpm` pulses at a **beats-per-minute** rate (more “alive” than a steady on).

**Level start sequence:**
- Blue → off (a few flashes) → solid green briefly → off.
- A visual “stage armed” signpost to the audience.

### Game State (Variables)

```python
count      = 0
tries      = 0
started    = False
timing     = False
timeout    = False
ready      = False
waiting    = False
start_time = None
level      = 1
MAX_LEVEL  = 4
```

- **count**: how many presses you’ve accumulated this stage.
- **tries**: how many stage failures so far (max 3 before game over).
- **started**: has the game ever started yet?
- **timing**: is the stage timer currently running?
- **timeout**: did you just run out of time?
- **ready**: did we finish Startup and BGM is rolling?
- **waiting**: between stages (armed state) waiting for the first press.
- **start_time**: when the timer began.
- **level**/**MAX_LEVEL**: current stage number.

### Goals, Time & Milestones

```python
goals = {1: 40, 2: 80, 3: 120, 4: 160}
milestones = {
    1: [10, 20, 30, 40],
    2: [20, 40, 60, 80],
    3: [30, 60, 90, 120],
    4: [40, 80, 120, 160]
}
times = {1: 30, 2: 40, 3: 50, 4: 60}
played_milestones = set()
```

- Each **level** has a **goal** (total presses) and a **time limit** (seconds).
- The **milestones** are the **thresholds** where we trigger cues/SFX (25/50/75/100%).
- `played_milestones` remembers milestones we already fired to avoid double-triggering.

### REAPER “Address Book”

We send these OSC addresses to REAPER:

```python
# Milestone SFX (1..4)
addr   = "/action/41261"
addr1  = "/action/41262"
addr2  = "/action/41263"
addr3  = "/action/41264"
addr4  = "/action/41265"  # spare
addr5  = "/action/41266"  # spare

# Level starts (stage-armed SFX)
addr6  = "/action/41267"  # Level 1
addr7  = "/action/41268"  # Level 2
addr8  = "/action/41269"  # Level 3/4

# Stage/game markers
addr9  = "/marker/19"     # Stage Win (fired AFTER green sweep)
addr10 = "/marker/20"     # Stage Lose
addr11 = "/marker/21"     # Game Win
addr12 = "/marker/22"     # Game Lose
addr13 = "/marker/23"     # BGM Start (loop)
addr14 = "/marker/24"     # Static (optional)

# Transport
addr15 = "/action/1007"   # Play
addr16 = "/action/1016"   # Stop
```

> If your session uses a different number (e.g., an `/action/41270` for Stage Win), change the corresponding **address value** only — keep the overall logic unchanged.

### GrandMA3 Milestone Commands

For each level and milestone index (0..3), send a specific cue:

```python
gma_milestone_cmds = {
  1: ["Go Sequence 23 cue 1", "Go Sequence 23 cue 2", "Go Sequence 23 cue 3", "Go Sequence 23 cue 4"],
  2: ["Go Sequence 23 cue 1", "Go Sequence 23 cue 2", "Go Sequence 23 cue 3", "Go Sequence 23 cue 4"],
  3: ["Go Sequence 23 cue 1", "Go Sequence 23 cue 2", "Go Sequence 23 cue 3", "Go Sequence 23 cue 4"],
  4: ["Go Sequence 23 cue 1", "Go Sequence 23 cue 2", "Go Sequence 23 cue 3", "Go Sequence 23 cue 4"],
}
```

> **Project rule:** Do **not** change these commands or the logic that selects them.

### Helper Functions

**Pick a stage color:**
```python
def get_stage_color(lvl):
  return {
    1: Color(255, 0,   0),   # red
    2: Color(255, 165, 0),   # orange
    3: Color(255, 255, 0),   # yellow
    4: Color(0,   255, 0),   # green
  }.get(lvl, Color(255,255,255))
```

**Send OSC to REAPER:**
```python
def trigger_reaper(addr, msg=1.0):
  client = udp_client.SimpleUDPClient(REAPER_IP, REAPER_PORT)
  client.send_message(addr, msg)
```

**Milestone SFX then auto-resume BGM:**
```python
bgm_timer = None

def play_sfx_then_bgm(sfx_addr, sfx_hold=1.2):
  trigger_reaper(addr16)      # Stop
  trigger_reaper(sfx_addr)    # Play the SFX
  trigger_reaper(addr15)      # Play (so the SFX actually runs)

  # Cancel previous BGM timer, if any
  global bgm_timer
  if bgm_timer is not None and bgm_timer.is_alive():
    bgm_timer.cancel()

  # When the SFX is likely done, flip back to the BGM loop
  def _back_to_bgm():
    trigger_reaper(addr16)    # Stop
    trigger_reaper(addr13)    # Marker: BGM Start
    trigger_reaper(addr15)    # Play

  bgm_timer = threading.Timer(sfx_hold, _back_to_bgm)
  bgm_timer.daemon = True
  bgm_timer.start()
```

- The **threading.Timer** is a tiny background clock. After `sfx_hold` seconds, it runs `_back_to_bgm()` to restore the loop.
- If you trigger another SFX quickly, the **old timer** is canceled so timers don’t stack.

> **Safe tweak:** If your SFX is longer/shorter, adjust `sfx_hold` per milestone level in an `SFX_HOLDS` map — this is considered **audio messaging**, allowed by the project rule.

### GUI (Tkinter) & Startup **(+ Restart Feature)**

- A fullscreen window with large labels shows the current state of the game.
- **Press Space** to run **Startup**:
  - Sends a short **GrandMA3 intro** (e.g., `Go Sequence 102 cue 5` then a couple of `Go+`),
  - Audio: **Stop**, jump to **BGM Start** marker, then **Play**,
  - Sets `ready = True` so sensor presses are honored.

**NEW: Manual Restart Hotkey (R/r)**

- The UI binds **R** and **Shift+R** to `restart_countdown(3)`. You can manually force a **3-second on-screen countdown**, after which the **stage becomes armed** again (but **does not** auto-start — the next sensor press must re-arm/start as normal).
- This is useful for the operator (e.g., pausing the game for an announcement, resetting pacing).

**How `restart_countdown` works (plain English):**

```python
def restart_countdown(self, seconds=3):
    # 1) Guard so we don't start multiple countdowns at once:
    #    if one is running, ignore additional R presses.
    # 2) Pause the game timer (timing=False), clear start_time,
    #    and clear any "timeout" flag.
    # 3) Show a visible countdown in the UI ("Restart in 3...", "2...", "1...").
    #    This uses Tkinter's 'after' method, which schedules updates
    #    without freezing the window (no sleep here).
    # 4) When the countdown reaches zero:
    #       - Set 'waiting=True' so the next sensor press performs the normal
    #         stage-arming sequence (blue flashes → green, play Stage Armed SFX).
    #       - Update the UI to say "Stage armed: press sensor again to start".
    #       - Clear the internal guard to allow future restarts.
```

**Key technical points:**

- Uses `self.root.after(1000, ...)` instead of `time.sleep()` so the UI remains responsive; no blocking threads.
- Sets: `timing=False`, `start_time=None`, `timeout=False` to ensure a clean pause.
- At the end, sets `waiting=True` to require the **normal** re-arming flow on the next sensor press (this preserves game logic).
- `_restart_active` prevents overlapping countdowns if R is pressed repeatedly.

### Receiving Sensor Presses (OSC)

- The Pi runs a **small OSC server** on `LOCAL_IP:LOCAL_PORT` and listens at `/print`.
- Each received `/print` message is treated as **one press** and runs the handler.

**Handler flow (simplified):**

1. If not **ready**, ignore.
2. If **waiting** between stages:
   - Clear `played_milestones`,
   - Run **level start** LEDs + **Stage Armed SFX** for this level (SFX then Play),
   - Reset counters/timer, show UI “Stage armed…”, leave **timer paused**,
   - Exit (the **next** press starts the timer).
3. If first time ever (`started == False`):
   - Mark `started = True`,
   - Arm **Level 1** as above (Level 1 Stage Armed SFX then Play),
   - Exit.
4. If **timer not running**:
   - Start the timer on this press, update UI to “Stage running”, exit.
5. If **timeout**, ignore until reset logic handles it.
6. Otherwise (**normal press**):
   - Increase `count`,
   - On **milestone**: fill LEDs proportionally, send GMA cue, play milestone SFX then auto-resume BGM,
   - On **goal reached**: green pulse + sweep, **Stage Win** audio (fired **after** sweep), move to next level or **Game Win**.

### Game Tick Loop (Timer, Fail, **Auto-Restart Countdown**)

- A loop runs ~every **0.1s** to update the **countdown** UI.
- If time runs out before the goal:
  - LED **red_dim** effect,
  - GMA “Lose Stage”,
  - Audio: **Stop → Stage Lose marker → Play**,
  - `tries += 1`, UI “Stage: Fail”.
  - If `tries >= 3`:
    - Trigger **Game Lose** (Stop → marker → Play), show full red briefly, reset game.
  - Else (`tries < 3`):
    - **Auto-trigger `restart_countdown(3)`**:
      - Timer pauses and UI shows “Restart in 3… 2… 1…”.
      - When it hits zero, `waiting=True` and the UI prompts:
        **“Stage armed: press sensor again to start”**.
      - Operator (or player) must press the sensor to re-arm (blue flashes → green, Stage Armed SFX), then press again to start the timer.

> This auto-restart keeps the show flowing and makes it obvious to the audience when the next attempt will begin.

### Shutdown Sequence

- A helper to **turn off** related GrandMA sequences and trigger a REAPER action (e.g., cut to silence).
- You can wire this to a special **UI button** or operator shortcut if desired.

---

## Play Flow Example

**Clean run:**

1. **Space** → Lights intro runs. REAPER jumps to **BGM Start** and **Plays**. UI shows **Ready**.
2. **Press sensor once** → “Stage armed…”: blue flashes → solid green; Stage Armed SFX plays.
3. **Press sensor again** → Timer starts: UI shows time counting down.
4. **Press repeatedly**:
   - At **25%**: LEDs fill to 25%, GMA cue for milestone 1 runs, REAPER plays SFX 1 then returns to BGM.
   - At **50%**: Same with SFX 2.
   - At **75%**: Same with SFX 3.
   - At **100%** (goal): LEDs pulse then sweep green; **after** the sweep, **Stage Win** plays.
5. **Next level** arms on next press. After Level 4 win, **Game Win** plays and the game resets to idle.

**Fail with auto-restart:**

- Timer hits zero → red LED effect → **Stage Lose**; `tries += 1`.
- UI shows “Restart in 3… 2… 1…”.
- At zero → **waiting=True**; UI: “Stage armed: press sensor again to start”.
- Operator (or player) presses sensor to re-arm (blue flashes, Stage Armed SFX), then presses again to start the timer.

**Manual operator restart (R):**

- Press **R** at any time during a stage → **3s countdown** → force **waiting=True**.
- Next sensor press re-arms (normal arming flow), preserving consistent show behavior.

---

## What You Can Change Safely

> **Remember the project rule**: only **audio/REAPER messaging** may be edited. Don’t alter game logic or GrandMA3 command logic.

- **REAPER SFX mapping:** Repoint which `/action/4126x` plays at each milestone or stage.  
- **SFX hold times:** Adjust how long we wait before resuming BGM (e.g., `SFX_HOLDS = {1:1.0, 2:1.4, ...}`).
- **Marker numbers:** If your **BGM Start** or **Win/Lose** markers are different, update the `/marker/##` values.

---

## Troubleshooting & Pitfalls

**Nothing reacts at all**
- Verify **power** to LEDs.
- Check **IPs/ports** (Pi → GrandMA3, Pi → REAPER, Sensor → Pi).
- Use `ping` from the Pi to REAPER and GrandMA3.

**Sensor presses sporadic / double counts**
- Add **debounce** on the sensor side (hardware or software).
- The code avoids double-firing milestones, but raw presses can still bounce.

**Timer never starts**
- After **Startup**, you must **press once to arm** and **again** to start the timer.

**REAPER not responding**
- Preferences → Control/OSC/Web → ensure an **OSC surface** listens on the right **port**.
- Check firewalls and that REAPER is on the same **network**.

**GrandMA3 not responding**
- Confirm **OSC In** and correct **port**.
- Test a command manually from a tool (e.g., send `/gma3/cmd` → `Go Sequence 23 cue 1`).

**LEDs flicker or dim**
- Inadequate **power** or no **ground sharing**. Inject power along the strip for long runs.

**BGM doesn’t resume after SFX**
- Increase the **SFX hold** (the sound may be longer than the current timer).
- Confirm `/marker/23` exists and loops.

**Restart doesn’t arm automatically**
- That’s by design: after the **countdown**, `waiting=True` requires the **normal arming press**. This keeps behavior consistent and prevents accidental immediate restarts.

---

## Testing Without Hardware

**Simulate a sensor press** to the Pi (replace IP/port as needed):

```bash
oscsend 192.168.254.108 8006 /print i 1
```

**Simulate milestone audio in REAPER**:
```bash
oscsend 192.168.254.12 8000 /action/41261 f 1.0
oscsend 192.168.254.12 8000 /marker/23 f 1.0
oscsend 192.168.254.12 8000 /action/1007 f 1.0
```

**Simulate a GMA cue**:
```bash
oscsend 192.168.254.213 2000 /gma3/cmd s "Go Sequence 23 cue 1"
```

---

## Glossary

- **OSC**: Open Sound Control — tiny network messages like “run this cue” or “jump to this marker.”
- **DAW**: Digital Audio Workstation — here, **REAPER**.
- **Action**: A REAPER command reachable by a number (e.g., Play = `/action/1007`).
- **Marker**: A named/numbered timeline location you can jump to via OSC (e.g., `/marker/23`).
- **PWM**: Pulse-Width Modulation — hardware timing technique used for the LED signal on GPIO 18.
- **Debounce**: Methods to ignore rapid repeats from a single physical press due to mechanical noise.
- **Thread / Timer**: A background helper that does one job later (here, resuming BGM after SFX).

---

## Appendix: OSC Address Reference

### REAPER (used by the script)

| Purpose              | OSC Address      | When it’s used                                    |
|----------------------|------------------|---------------------------------------------------|
| Milestone SFX #1     | `/action/41261`  | On 25% progress                                   |
| Milestone SFX #2     | `/action/41262`  | On 50% progress                                   |
| Milestone SFX #3     | `/action/41263`  | On 75% progress                                   |
| Milestone SFX #4     | `/action/41264`  | On 100% (goal) — then Stage Win after LED sweep   |
| Stage Armed (L1)     | `/action/41267`  | First arm of Level 1                              |
| Stage Armed (L2)     | `/action/41268`  | First arm of Level 2                              |
| Stage Armed (L3/4)   | `/action/41269`  | First arm of Levels 3 and 4                       |
| Stage Win            | `/marker/19`     | **After** green sweep on stage win                |
| Stage Lose           | `/marker/20`     | When timer expires                                |
| Game Win             | `/marker/21`     | After the last stage win                          |
| Game Lose            | `/marker/22`     | After 3 stage fails                               |
| BGM Start (loop)     | `/marker/23`     | Background music loop entry point                 |
| Static (optional)    | `/marker/24`     | Optional bed                                      |
| Play                 | `/action/1007`   | Transport Play                                    |
| Stop                 | `/action/1016`   | Transport Stop                                    |

> **Flow patterns:**  
> • **Milestone:** Stop → SFX → Play → (timer) → Stop → BGM Start → Play  
> • **Stage Win:** LEDs sweep first → marker → Play  
> • **Stage Lose / Game Win / Game Lose:** Stop → marker → Play

### GrandMA3 (examples used)

- **Milestones per level:** `Go Sequence 23 cue 1` → `cue 4`
- **Startup intro:** `Go Sequence 102 cue 5`, then `Go+ Sequence 102` (twice)
- **Other status cues:** “Win Stage”, “Lose Stage”, `Go Sequence 103 cue 1`, `Go Sequence 104 cue 1`, `Go+ sequence 33`, `Go+ sequence 32`

> These are plain text strings sent to `/gma3/cmd`. Adjust to your showfile **outside** of game logic.

---

## Appendix: Power & Wiring Notes

- **5V, high-current PSU** for the LEDs. Connect **+5V** and **GND** to the strip.  
- **Share GND** between **Pi** and **strip** (critical for signaling).  
- **Data line** from **Pi GPIO 18** → strip **DIN** through a **300–500Ω resistor** (good practice).  
- For long strips, **inject power** every 1–2m to prevent dimming and color shift.


