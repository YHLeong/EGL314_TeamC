import time
import threading
import tkinter as tk
from rpi_ws281x import *
from pythonosc import udp_client, dispatcher, osc_server

# OSC Setup
GMA_IP, GMA_PORT       = "192.168.254.213", 2000
REAPER_IP, REAPER_PORT = "192.168.254.12", 8000
LOCAL_IP, LOCAL_PORT   = "192.168.254.108", 8001

gma     = udp_client.SimpleUDPClient(GMA_IP, GMA_PORT)
reaper  = udp_client.SimpleUDPClient(REAPER_IP, REAPER_PORT)

LED_COUNT = 300
strip = Adafruit_NeoPixel(LED_COUNT, 18, 800000, 10, False, 128)
strip.begin()

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
        light_up(n, Color(255, 0, 0)); time.sleep(0.3)
        light_up(n, 0); time.sleep(0.3)
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
        light_up(n, Color(0, 255, 0)); time.sleep(delay)
        light_up(n, 0); time.sleep(delay)

def level_start_sequence(level):
    blink = {1: 0.3, 2: 0.2, 3: 0.15, 4: 0.1}.get(level, 0.25)
    for _ in range(6):
        light_up(LED_COUNT, Color(0, 0, 255)); time.sleep(blink)
        light_up(LED_COUNT, 0); time.sleep(blink)
    light_up(LED_COUNT, Color(0, 255, 0)); time.sleep(2)
    light_up(LED_COUNT, 0)

def shutdown_sequences():
    for cue in ["23 cue 1", "23 cue 2", "23 cue 3", "23 cue 4"]:
        gma.send_message("/gma3/cmd", f"Off Sequence {cue}")
    reaper.send_message("/action/40042", 1.0)

count         = 0
tries         = 0
started       = False
timing        = False
timeout       = False
ready         = False
waiting       = False
start_time    = None
level         = 1
MAX_LEVEL     = 4

goals = {1: 40, 2: 80, 3: 120, 4: 240}
times = {1: 30, 2: 40, 3: 50, 4: 60}
milestones = {
    1: [10, 20, 30, 40],
    2: [20, 40, 60, 80],
    3: [30, 60, 90, 120],
    4: [60, 120, 180, 240]
}

def get_stage_color(level):
    return {
        1: Color(255, 0, 0),
        2: Color(255, 165, 0),
        3: Color(255, 255, 0),
        4: Color(0, 255, 0)
    }.get(level, Color(255, 255, 255))

def trigger_reaper(id):
    global level
    stage_time = times.get(level, 30)  # Get the time limit for current level
    
    # Check if id is a full OSC address (starts with "/") or just an action number
    if id.startswith("/"):
        reaper.send_message(id, 1.0)  # Send full OSC address directly
    else:
        reaper.send_message(f"/action/{id}", 1.0)  # Jump to marker using action number
    
    reaper.send_message("/action/1007", 1.0)   # Play
    # Schedule stop after stage time limit without blocking
    threading.Timer(stage_time, lambda: reaper.send_message("/action/1016", 1.0)).start()

def trigger_osc(n):
    cues = milestones.get(level, [])
    if n == cues[0]: gma.send_message("/gma3/cmd", "Go Sequence 23 cue 1"); trigger_reaper("41261")
    elif n == cues[1]: gma.send_message("/gma3/cmd", "Go Sequence 23 cue 2"); trigger_reaper("41262")
    elif n == cues[2]: gma.send_message("/gma3/cmd", "Go Sequence 23 cue 3"); trigger_reaper("41263")
    elif n == cues[3]: gma.send_message("/gma3/cmd", "Go Sequence 23 cue 4"); trigger_reaper("41264"); trigger_reaper("41270")

class GameUI:
    def _init_(self):
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))
        self.root.bind("<space>", self.start_sequence)

        font = ("Arial", 28)
        self.labels = {
            "level":  tk.Label(self.root, text="Level: 1", font=font),
            "time":   tk.Label(self.root, text="Time: 0", font=font),
            "result": tk.Label(self.root, text="Stage: In Progress", font=font, fg="blue"),
            "game":   tk.Label(self.root, text="Game: Waiting", font=font, fg="gray"),
            "tries":  tk.Label(self.root, text="Tries Left: 3", font=font)
        }
        for lbl in self.labels.values(): lbl.pack(pady=10)

    def update(self, key, value, color=None):
        if key in self.labels:
            self.labels[key].config(text=value)
            if color: self.labels[key].config(fg=color)

    def start_sequence(self, e=None):
        global ready
        self.update("game", "Startup", "orange")
        gma.send_message("/gma3/cmd", "Go Sequence 38 cue 3")
        time.sleep(0.3)
        gma.send_message("/gma3/cmd", "Go+ Sequence 41")
        time.sleep(0.9)
        gma.send_message("/gma3/cmd", "On Sequence 207")
        trigger_reaper("41100")
        ready = True
        self.update("game", "Ready", "blue")


    def off_sequence(self, e=None):
            global ready
            self.update("game", "Shutting Down", "red")
            gma.send_message("/gma3/cmd", "Go Sequence 36 cue 1")
            time.sleep(0.3)
            gma.send_message("/gma3/cmd", "Go Sequence 23 cue 7")
            time.sleep(0.5)
            gma.send_message("/gma3/cmd", "Off Sequence 41")
            time.sleep(0.5)
            gma.send_message("/gma3/cmd", "Off Sequence 38")
            time.sleep(0.5)
            gma.send_message("/gma3/cmd", "On Sequence 207")
            ready = True
            self.update("game", "Off", "gray")
 


def print_args(addr, *args):
    global count, started, timing, start_time, timeout, level, tries, waiting

    if not ready: return

    if waiting:
        level_start_sequence(level)
        gma.send_message("/gma3/cmd", f"Level {level} Start")
        ui.update("level", f"Level: {level}")
        ui.update("tries", "Tries Left: 3")
        count = 0; tries = 0; timing = False; timeout = False
        start_time = None; waiting = False
        return

    if not started:
        started = True
        level_start_sequence(level)
        gma.send_message("/gma3/cmd", "Level Start")
        ui.update("level", f"Level: {level}")
        ui.update("tries", "Tries Left: 3")
        return

    if not timing:
        start_time = time.time()
        timing = True
        return

    if timeout: return

    count += 1
    if count in milestones.get(level, []):
        progress = int(LED_COUNT * (count / goals[level]))
        light_up(progress, get_stage_color(level))
        trigger_osc(count)

    if count == goals[level]:
        flash_bpm(LED_COUNT)
        green_dim(LED_COUNT)
        gma.send_message("/gma3/cmd", "Win Stage")
        trigger_reaper("41270")
        shutdown_sequences()
        ui.update("result", "Stage: Win", "green")

        if level == MAX_LEVEL:
            gma.send_message("/gma3/cmd", "Go+ sequence 23")
            gma.send_message("/gma3/cmd", "Go sequence 33")
            trigger_reaper("/marker/19", 1.0)
            light_up(LED_COUNT, Color(0, 255, 0)); time.sleep(2)
            light_up(LED_COUNT, 0)
            ui.update("game", "Game: Win", "green")
            started = False; timing = False
            return

        level += 1
        waiting = True
        return

def start_game_logic():
    global timing, timeout, start_time, level, tries, started, count
    osc_dispatcher = dispatcher.Dispatcher()
    osc_dispatcher.map("/print", print_args)
    server = osc_server.ThreadingOSCUDPServer((LOCAL_IP, LOCAL_PORT), osc_dispatcher)
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
                    tries += 1
                    ui.update("tries", f"Tries Left: {max(0, 3 - tries)}")
                    red_dim(int(LED_COUNT * (count / goals[level])))
                    gma.send_message("/gma3/cmd", "Lose Stage")
                    trigger_reaper("/marker/18", 1.0)
                    shutdown_sequences()
                    ui.update("result", "Stage: Fail", "red")

                    if tries >= 3:
                        gma.send_message("/gma3/cmd", "Go+ sequence 32")
                        trigger_reaper("/marker/20", 1.0)
                        ui.update("game", "Game: Lose", "red")
                        started = False
                        timing = False
                    else:
                        count = 0
                        timing = False
                        timeout = False
            time.sleep(0.01)
    except KeyboardInterrupt:
        light_up(LED_COUNT, 0)
        server.shutdown()

if _name_ == "_main_":
    ui = GameUI()
    threading.Thread(target=start_game_logic, daemon=True).start()
    ui.root.mainloop()