import time
import threading
import tkinter as tk
from rpi_ws281x import *
from pythonosc import udp_client, dispatcher, osc_server

# OSC addresses
GMA_IP, GMA_PORT       = "192.168.254.213", 2000
REAPER_IP, REAPER_PORT = "192.168.254.12", 8000
LOCAL_IP, LOCAL_PORT   = "192.168.254.108", 8001

gma_client    = udp_client.SimpleUDPClient(GMA_IP, GMA_PORT)
reaper_client = udp_client.SimpleUDPClient(REAPER_IP, REAPER_PORT)

# NeoPixel configuration
LED_COUNT = 300
strip = Adafruit_NeoPixel(LED_COUNT, 18, 800000, 10, False, 128)
strip.begin()

# GUI Class
class GameUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Battery Charger")
        self.root.geometry("300x220")

        self.level_label = tk.Label(self.root, text="Level: 1", font=("Arial", 16))
        self.level_label.pack(pady=10)

        self.time_label = tk.Label(self.root, text="Remaining Time: 20s", font=("Arial", 16))
        self.time_label.pack(pady=10)

        self.stage_result = tk.Label(self.root, text="Stage: In Progress", font=("Arial", 16), fg="blue")
        self.stage_result.pack(pady=10)

        self.game_result = tk.Label(self.root, text="Game: Running", font=("Arial", 16), fg="green")
        self.game_result.pack(pady=10)

    def update_level(self, level):
        self.root.after(0, lambda: self.level_label.config(text=f"Level: {level}"))

    def update_time(self, time_left):
        self.root.after(0, lambda: self.time_label.config(text=f"Remaining Time: {int(time_left)}s"))

    def show_stage_result(self, result):
        color = "green" if result == "Win" else "red"
        self.root.after(0, lambda: self.stage_result.config(text=f"Stage: {result}", fg=color))

    def show_game_result(self, result):
        color = "green" if result == "Win" else "red"
        self.root.after(0, lambda: self.game_result.config(text=f"Game: {result}", fg=color))

# Game state
count = 0
lit_pixels = 0
lose_count = 0
game_started = False
timing_started = False
timeout_triggered = False
start_time = None
current_level = 1
max_levels = 3
colors = {5: Color(255,0,0), 10: Color(255,50,0), 15: Color(255,165,0), 20: Color(0,255,0)}

def get_level_time(level): return {1: 20, 2: 15, 3: 10}.get(level, 10)

def trigger_osc(count):
    if count == 5:
        gma_client.send_message("/gma3/cmd", "On Sequence 71")
        reaper_client.send_message("/action/41261", 1.0)
    elif count == 10:
        gma_client.send_message("/gma3/cmd", "Go+ Sequence 71")
        reaper_client.send_message("/action/41262", 1.0)
    elif count == 15:
        gma_client.send_message("/gma3/cmd", "Go+ Sequence 71")
        reaper_client.send_message("/action/41263", 1.0)
    elif count == 20:
        gma_client.send_message("/gma3/cmd", "Go+ Sequence 71")
        reaper_client.send_message("/action/41264", 1.0)
        reaper_client.send_message("/action/41270", 1.0)

def trigger_stage_transition(level):
    if level == 2:
        gma_client.send_message("/gma3/cmd", "On Sequence 81")
        reaper_client.send_message("/action/41268", 1.0)
    elif level == 3:
        gma_client.send_message("/gma3/cmd", "On Sequence 91")
        reaper_client.send_message("/action/41269", 1.0)

def light_up(n, color): [strip.setPixelColor(i, color) for i in range(n)]; strip.show()
def flash_bpm(n, bpm=120, duration=5):
    delay = 60/bpm/2
    for _ in range(int(duration/(delay*2))):
        light_up(n, Color(0,255,0)); time.sleep(delay); light_up(n, 0); time.sleep(delay)
def red_dim_down(n):
    for i in range(n-1, -1, -1):
        strip.setPixelColor(i, Color(255,0,0)); strip.show(); time.sleep(0.005)
        strip.setPixelColor(i, 0); strip.show()
    for _ in range(5):
        light_up(n, Color(255,0,0)); time.sleep(0.3); light_up(n, 0); time.sleep(0.3)
    light_up(LED_COUNT, 0)
def level_start_sequence():
    for _ in range(6): light_up(LED_COUNT, Color(0,0,255)); time.sleep(0.25); light_up(LED_COUNT, 0); time.sleep(0.25)
    light_up(LED_COUNT, Color(0,255,0)); time.sleep(3); light_up(LED_COUNT, 0)

def print_args(addr, *args):
    global count, lit_pixels, game_started, timing_started
    global start_time, timeout_triggered, current_level, lose_count

    if not game_started:
        game_started = True
        level_start_sequence()
        ui.update_level(current_level)
        return

    if not timing_started:
        start_time = time.time()
        timing_started = True
        return

    if timeout_triggered or not timing_started:
        return

    count += 1
    if count in colors:
        lit_pixels += 50
        light_up(lit_pixels, colors[count])
        trigger_osc(count)

    if count == 20:
        flash_bpm(lit_pixels)
        gma_client.send_message("/gma3/cmd", "Win Stage")
        reaper_client.send_message("/action/41270", 1.0)
        ui.show_stage_result("Win")

        if current_level == max_levels:
            gma_client.send_message("/gma3/cmd", "Win Game")
            reaper_client.send_message("/marker/19", 1.0)
            ui.show_game_result("Win")
            game_started = False
            timing_started = False
            return

        current_level += 1
        trigger_stage_transition(current_level)
        gma_client.send_message("/gma3/cmd", f"Level {current_level} Start")
        ui.update_level(current_level)
        count = 0
        lit_pixels = 0
        timing_started = False
        timeout_triggered = False
        level_start_sequence()
        start_time = time.time()
        timing_started = True

def start_game_logic():
    global timing_started, timeout_triggered, start_time, current_level, lose_count, game_started, count, lit_pixels    
    osc_dispatcher = dispatcher.Dispatcher()
    osc_dispatcher.map("/print", print_args)
    osc_server_thread = osc_server.ThreadingOSCUDPServer((LOCAL_IP, LOCAL_PORT), osc_dispatcher)
    threading.Thread(target=osc_server_thread.serve_forever, daemon=True).start()
    print(f"OSC server listening on {LOCAL_IP}:{LOCAL_PORT}")

    try:
        while True:
            if timing_started and not timeout_triggered:
                time_left = get_level_time(current_level) - (time.time() - start_time)
                ui.update_time(max(0, time_left))

                if time.time() - start_time > get_level_time(current_level) and count < 20:
                    timeout_triggered = True
                    red_dim_down(lit_pixels if lit_pixels > 0 else 10)
                    gma_client.send_message("/gma3/cmd", "Lose Stage")
                    reaper_client.send_message("/marker/18", 1.0)
                    ui.show_stage_result("Lose")
                    lose_count += 1
                    if lose_count >= 3:
                        gma_client.send_message("/gma3/cmd", "Lose Game")
                        reaper_client.send_message("/marker/20", 1.0)
                        ui.show_game_result("Lose")
                        game_started = False
                        timing_started = False
            time.sleep(0.01)
    except KeyboardInterrupt:
        light_up(LED_COUNT, 0)
        osc_server_thread.shutdown()

# Start everything safely
if __name__ == "__main__":
    ui = GameUI()
    threading.Thread(target=start_game_logic, daemon=True).start()
    ui.root.mainloop()
