import time
import threading
import tkinter as tk
from rpi_ws281x import Adafruit_NeoPixel, Color
from pythonosc import udp_client, dispatcher, osc_server

# -------- OSC Setup --------
GMA_IP, GMA_PORT       = "192.168.254.213", 2000
REAPER_IP, REAPER_PORT = "192.168.254.12",   8000
LOCAL_IP, LOCAL_PORT   = "192.168.254.108",  8006

gma    = udp_client.SimpleUDPClient(GMA_IP, GMA_PORT)
reaper = udp_client.SimpleUDPClient(REAPER_IP, REAPER_PORT)

# -------- LED Strip Setup --------
LED_COUNT = 300
strip = Adafruit_NeoPixel(LED_COUNT, 18, 800000, 10, False, 128)
strip.begin()

# -------- Lighting Effect Functions (unchanged) --------
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
    for _ in range(5):
        light_up(n, Color(255, 0, 0))
        time.sleep(0.3)
        light_up(n, 0)
        time.sleep(0.3)
    light_up(n, 0)

def green_dim(n):
    for i in range(n - 1, -1, -1):
        strip.setPixelColor(i, Color(0, 255, 0))
        strip.show()
        time.sleep(0.005)
        strip.setPixelColor(i, 0)
        strip.show()

def flash_bpm(n, bpm=120, duration=5):
    delay = 60 / bpm / 2
    for _ in range(int(duration / (delay * 2))):
        light_up(n, Color(0, 255, 0))
        time.sleep(delay)
        light_up(n, 0)
        time.sleep(delay)

def level_start_sequence(level):
    blink = {1: 0.3, 2: 0.2, 3: 0.15, 4: 0.1}.get(level, 0.25)
    for _ in range(6):  # 3 blue flashes (on/off)
        light_up(LED_COUNT, Color(0, 0, 255))
        time.sleep(blink)
        light_up(LED_COUNT, 0)
        time.sleep(blink)
    light_up(LED_COUNT, Color(0, 255, 0))  # solid green once
    time.sleep(2)
    light_up(LED_COUNT, 0)

def shutdown_sequences():
    for cue in ["23 cue 1", "23 cue 2", "23 cue 3", "23 cue 4"]:
        gma.send_message("/gma3/cmd", f"Off Sequence {cue}")
    reaper.send_message("/action/40042", 1.0)

# -------- Game State & Milestones --------
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

# Targets and FOUR equal milestone portions
goals = {1: 40, 2: 80, 3: 120, 4: 160}
milestones = {
    1: [10, 20, 30, 40],
    2: [20, 40, 60, 80],
    3: [30, 60, 90, 120],
    4: [40, 80, 120, 160]
}
times = {1: 30, 2: 40, 3: 50, 4: 60}

# ---- Audio dedupe / debounce state ----
played_milestones = set()  # milestones triggered this level
last_marker_time = {}      # marker -> last time sent
MARKER_COOLDOWN = 0.6      # seconds

# ---- GrandMA milestone command map (NEW) ----
# One command per milestone (4 per level). Customize freely.
gma_milestone_cmds = {
    1: ["Go Sequence 23 cue 1",
        "Go Sequence 23 cue 2",
        "Go Sequence 23 cue 3",
        "Go Sequence 23 cue 4"],
    2: ["Go Sequence 23 cue 1",
        "Go Sequence 23 cue 2",
        "Go Sequence 23 cue 3",
        "Go Sequence 23 cue 4"],
    3: ["Go Sequence 23 cue 1",
        "Go Sequence 23 cue 2",
        "Go Sequence 23 cue 3",
        "Go Sequence 23 cue 4"],
    4: ["Go Sequence 23 cue 1",
        "Go Sequence 23 cue 2",
        "Go Sequence 23 cue 3",
        "Go Sequence 23 cue 4"],
}

# -------- OSC Helper Functions --------
def get_stage_color(lvl):
    return {
        1: Color(255, 0,   0),
        2: Color(255, 165, 0),
        3: Color(255, 255, 0),
        4: Color(0,   255, 0)
    }.get(lvl, Color(255, 255, 255))

def trigger_reaper(marker: str):
    """Debounced wrapper to fire a REAPER action only once per cooldown window."""
    now = time.time()
    if marker in last_marker_time and (now - last_marker_time[marker]) < MARKER_COOLDOWN:
        return
    last_marker_time[marker] = now
    reaper.send_message("/action/40044", 1.0)
    reaper.send_message(f"/action/{marker}", 1.0)
    reaper.send_message("/action/40045", 1.0)

def trigger_osc(n):
    """Fire milestone GrandMA cmd + audio ONCE per milestone per level (four total)."""
    global played_milestones, level
    cues = milestones.get(level, [])
    if not cues or n in played_milestones:
        return
    played_milestones.add(n)

    # Which milestone index is this? (0..3)
    try:
        idx = cues.index(n)
    except ValueError:
        return

    # --- GrandMA command for this milestone (NEW) ---
    cmds = gma_milestone_cmds.get(level, [])
    if idx < len(cmds):
        gma.send_message("/gma3/cmd", cmds[idx])

    # --- Audio marker (unchanged) ---
    if idx == 0:
        trigger_reaper("41261")
    elif idx == 1:
        trigger_reaper("41262")
    elif idx == 2:
        trigger_reaper("41263")
    elif idx == 3:
        trigger_reaper("41264")
        # Stage Win audio plays ONLY at stage complete (below)

# -------- Manual Controls Data --------
audio_cmds = {
    "Startup Audio":  "41100",
    "Level 1 Audio":  "41261",
    "Level 2 Audio":  "41262",
    "Level 3 Audio":  "41263",
    "Level 4 Audio":  "41264",
    "Stage Win":      "41270",
    "Stage Fail":     "18",
    "Game Win":       "19",
    "Game Lose":      "20",
    "Shutdown Audio": None
}

cues_map = {
    102: ["5"],
    103: ["1", "2", "3", "4", "5", "5.1", "5.2", "6"],
    104: ["1"]
}

# -------- UI Class --------
class GameUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))
        self.root.bind("<space>", self.start_sequence)

        font = ("Arial", 28)
        self.labels = {
            "level":  tk.Label(self.root, text="Level: 1",           font=font),
            "time":   tk.Label(self.root, text="Time: 0",            font=font),
            "result": tk.Label(self.root, text="Stage: In Progress", font=font, fg="blue"),
            "game":   tk.Label(self.root, text="Game: Waiting",      font=font, fg="gray"),
            "tries":  tk.Label(self.root, text="Tries Left: 3",      font=font)
        }
        for lbl in self.labels.values():
            lbl.pack(pady=5)

        # -- Manual Lighting Controls --
        lighting_frame = tk.LabelFrame(self.root, text="Manual Lighting Controls",
                                       font=("Arial", 16))
        lighting_frame.pack(fill="x", padx=10, pady=5)
        for seq in (102, 103, 104):
            seq_frame = tk.LabelFrame(lighting_frame, text=f"Seq {seq}", padx=5, pady=5)
            seq_frame.pack(side="left", padx=10)
            tk.Button(seq_frame,
                      text=f"Go+ Seq {seq}",
                      command=lambda s=seq: self.send_gma_go_plus(s),
                      width=12).pack(pady=2)
            for cue in cues_map[seq]:
                tk.Button(seq_frame,
                          text=f"Cue {cue}",
                          command=lambda s=seq, c=cue: self.send_gma_cue(s, c),
                          width=12).pack(pady=2)

        # -- Manual Audio Controls --
        audio_frame = tk.LabelFrame(self.root, text="Manual Audio Controls",
                                    font=("Arial", 16))
        audio_frame.pack(fill="x", padx=10, pady=5)
        for label, marker in audio_cmds.items():
            btn = tk.Button(audio_frame,
                            text=label,
                            width=14,
                            command=lambda l=label, m=marker: self.send_audio_cmd(l, m))
            btn.pack(side="left", padx=5, pady=4)

    def update(self, key, value, color=None):
        if key in self.labels:
            self.labels[key].config(text=value)
            if color:
                self.labels[key].config(fg=color)

    def start_sequence(self, e=None):
        global ready
        self.update("game", "Startup", "orange")
        gma.send_message("/gma3/cmd", "Go Sequence 102 cue 5")
        time.sleep(0.2)
        gma.send_message("/gma3/cmd", "Go+ Sequence 102")
        time.sleep(0.2)
        gma.send_message("/gma3/cmd", "Go+ Sequence 102")
        trigger_reaper("41100")
        ready = True
        self.update("game", "Ready", "blue")

    # lighting triggers
    def send_gma_go_plus(self, seq):
        gma.send_message("/gma3/cmd", f"Go+ Sequence {seq}")
        self.update("game", f"Sent Go+ Seq {seq}", "purple")

    def send_gma_cue(self, seq, cue):
        gma.send_message("/gma3/cmd", f"Go Sequence {seq} cue {cue}")
        self.update("game", f"Sent Seq {seq} cue {cue}", "purple")

    # audio triggers
    def send_audio_cmd(self, label, marker):
        if label == "Shutdown Audio":
            shutdown_sequences()
        elif label in ("Stage Fail", "Game Win", "Game Lose"):
            reaper.send_message(f"/marker/{marker}", 1.0)
        else:
            trigger_reaper(marker)
        self.update("game", f"Audio: {label}", "purple")

# -------- OSC Handler --------
def print_args(addr, *args):
    global count, started, timing, start_time, timeout, level, tries, waiting, played_milestones

    if not ready:
        return

    # If we're between stages waiting for the next stage to arm
    if waiting:
        played_milestones.clear()          # reset milestone dedupe for new level
        level_start_sequence(level)        # (blue flashes x3, then green once)
        gma.send_message("/gma3/cmd", f"Level {level} Start")
        ui.update("level", f"Level: {level}")
        ui.update("tries", "Tries Left: 3")
        count = 0
        tries = 0
        timing = False                     # timer remains paused until next press
        timeout = False
        start_time = None
        waiting = False
        ui.update("time", "Time: Paused")
        ui.update("game", "Stage armed: press sensor again to start", "orange")
        return

    # First ever press to start the game
    if not started:
        started = True
        played_milestones.clear()
        level_start_sequence(level)        # (blue flashes x3, then green once)
        gma.send_message("/gma3/cmd", "Level Start")
        ui.update("level", f"Level: {level}")
        ui.update("tries", "Tries Left: 3")
        ui.update("time", "Time: Paused")
        ui.update("game", "Stage armed: press sensor again to start", "orange")
        return

    # Start the countdown on the next press after arming
    if not timing:
        start_time = time.time()
        timing = True
        ui.update("game", "Stage running", "blue")
        return

    # If timed out, ignore inputs until the loop handles reset/advance
    if timeout:
        return

    # Regular counting press
    count += 1
    if count in milestones.get(level, []):
        progress = int(LED_COUNT * (count / goals[level]))
        light_up(progress, get_stage_color(level))
        trigger_osc(count)

    # Stage complete
    if count == goals[level]:
        flash_bpm(LED_COUNT)               # green pulse x3 (duration-limited)
        green_dim(LED_COUNT)               # green sweep
        gma.send_message("/gma3/cmd", "Win Stage")
        trigger_reaper("41270")            # single win audio here
        gma.send_message("/gma3/cmd", "Go+ sequence 33")   # follow-up lighting
        shutdown_sequences()
        ui.update("result", "Stage: Win", "green")

        # Pause timer; wait for next press to arm next stage
        timing = False
        start_time = None
        timeout = False
        ui.update("time", "Time: Paused")

        if level == MAX_LEVEL:
            gma.send_message("/gma3/cmd", "Go Sequence 103 cue 1")
            reaper.send_message("/marker/19", 1.0)
            light_up(LED_COUNT, Color(0, 255, 0))
            time.sleep(2)
            light_up(LED_COUNT, 0)
            ui.update("game", "Game: Win", "green")
            started = False
            return

        level += 1
        waiting = True   # next press arms next stage
        return

# -------- Main game loop & OSC Server --------
def start_game_logic():
    global timeout, tries, waiting, started, timing, start_time, count, level

    disp = dispatcher.Dispatcher()
    disp.map("/print", print_args)
    disp.set_default_handler(lambda a, *b: print(f"Unhandled OSC: {a}, {b}"))

    server = osc_server.ThreadingOSCUDPServer((LOCAL_IP, LOCAL_PORT), disp)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"OSC server listening on {LOCAL_IP}:{LOCAL_PORT}")

    try:
        while True:
            if timing and not timeout:
                elapsed = time.time() - start_time
                remaining = times.get(level, 30) - elapsed
                ui.update("time", f"Time: {max(0, int(remaining))}")

                if elapsed > times[level] and count < goals[level]:
                    timeout = True
                    # stage fail lighting & audio
                    red_dim(LED_COUNT)
                    gma.send_message("/gma3/cmd", "Lose Stage")
                    reaper.send_message("/marker/18", 1.0)
                    ui.update("result", "Stage: Fail", "red")

                    tries += 1
                    if tries >= 3:
                        # game lose sequence
                        gma.send_message("/gma3/cmd", "Go+ sequence 32")  # follow-up lighting
                        gma.send_message("/gma3/cmd", "Go Sequence 104 cue 1")
                        reaper.send_message("/marker/20", 1.0)
                        light_up(LED_COUNT, Color(255, 0, 0))
                        time.sleep(2)
                        light_up(LED_COUNT, 0)
                        ui.update("game", "Game: Lose", "red")
                        started = False
                        timing = False
                        ui.update("time", "Time: Paused")
                    else:
                        # allow re-arming same level on next press
                        waiting = True
                        timing = False
                        start_time = None
                        ui.update("time", "Time: Paused")

            time.sleep(0.1)

    except KeyboardInterrupt:
        server.shutdown()
        print("OSC server stopped.")

if __name__ == "__main__":
    ui = GameUI()
    threading.Thread(target=start_game_logic, daemon=True).start()
    ui.root.mainloop()
