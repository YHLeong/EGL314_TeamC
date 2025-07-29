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

# NeoPixel setup
LED_COUNT = 300
strip = Adafruit_NeoPixel(LED_COUNT, 18, 800000, 10, False, 128)
strip.begin()

def light_up(n, color):
    for i in range(n):
        strip.setPixelColor(i, color)
    strip.show()

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

def green_dim_down(n):
    for i in range(n-1, -1, -1):
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

def get_stage_color(level):
    return {
        1: Color(255, 0, 0),
        2: Color(255, 165, 0),
        3: Color(255, 255, 0),
        4: Color(0, 255, 0)
    }.get(level, Color(255, 255, 255))

def level_start_sequence(level):
    if level == 1:
        trigger_reaper_with_level_delay(addr6, 1)  # Level 1 start with 30s delay
        for _ in range(6):
            light_up(LED_COUNT, Color(0, 0, 255)); time.sleep(0.25)
            light_up(LED_COUNT, 0); time.sleep(0.25)
        light_up(LED_COUNT, Color(0, 255, 0)); time.sleep(2)
        light_up(LED_COUNT, 0)
    elif level == 2:
        trigger_reaper_with_level_delay(addr6, 2)  # Level 2 start with 40s delay
        for _ in range(5):
            light_up(LED_COUNT, Color(255, 140, 0)); time.sleep(0.1)
            light_up(LED_COUNT, 0); time.sleep(0.1)
        light_up(LED_COUNT, Color(0, 255, 0)); time.sleep(2)
        light_up(LED_COUNT, 0)
    elif level == 3:
        trigger_reaper_with_level_delay(addr7, 3)  # Level 3 start with 50s delay
        for _ in range(3):
            light_up(LED_COUNT, Color(255, 255, 0)); time.sleep(0.3)
            light_up(LED_COUNT, 0); time.sleep(0.3)
        light_up(LED_COUNT, Color(0, 255, 0)); time.sleep(2)
        light_up(LED_COUNT, 0)
    elif level == 4:
        trigger_reaper_with_level_delay(addr8, 4)  # Level 3 start with 60s delay
        for i in range(6):
            strip.setPixelColor(i * 50, Color(0, 255, 0)); strip.show(); time.sleep(0.1)
        light_up(LED_COUNT, Color(0, 255, 0)); time.sleep(2)
        light_up(LED_COUNT, 0)

def shutdown_sequences(level):
    cues = ["23 cue 1", "23 cue 2", "23 cue 3", "23 cue 4"]
    for cue in cues:
        gma_client.send_message("/gma3/cmd", f"Off Sequence {cue}")
    trigger_reaper(addr16)  # Stop

# Game state
count = 0
stage_tries = 0
game_started = False
timing_started = False
timeout_triggered = False
startup_complete = False
waiting_for_next = False
start_time = None
current_level = 1
max_levels = 4

milestones = {
    1: [10, 20, 30, 40],
    2: [20, 40, 60, 80],
    3: [30, 60, 90, 120],
    4: [60, 120, 180, 240]
}
level_goals = {1: 40, 2: 80, 3: 120, 4: 240}
level_times = {1: 30, 2: 40, 3: 50, 4: 60}

def get_level_time(level): return level_times.get(level, 30)

def trigger_reaper(addr, msg=1.0):
    """Send OSC message to Reaper with the specified address and message"""
    client = udp_client.SimpleUDPClient(REAPER_IP, REAPER_PORT)
    client.send_message(addr, msg)

def trigger_reaper_with_delay(marker_addr, play_addr, stop_addr, delay=20):
    """Jump to marker, trigger play, wait for delay, then trigger stop - runs in background"""
    def delayed_sequence():
        trigger_reaper(marker_addr)  # Jump to marker first
        time.sleep(0.5)  # Small delay to ensure marker jump completes
        trigger_reaper(play_addr)  # Trigger play
        time.sleep(delay)  # Wait for specified delay
        trigger_reaper(stop_addr)  # Trigger stop
    # Run in background thread so it doesn't block game logic
    threading.Thread(target=delayed_sequence, daemon=True).start()

def trigger_reaper_with_level_delay(marker_addr, level):
    """Trigger level start with delay matching level duration"""
    level_delay = level_times.get(level, 30)
    trigger_reaper_with_delay(marker_addr, addr15, addr16, level_delay)

def trigger_reaper_with_delay_no_stop(marker_addr, play_addr, delay=20):
    """Jump to marker, trigger play, wait for delay - NO STOP COMMAND - runs in background"""
    def delayed_sequence():
        trigger_reaper(marker_addr)  # Jump to marker first
        time.sleep(0.5)  # Small delay to ensure marker jump completes
        trigger_reaper(play_addr)  # Trigger play
        time.sleep(delay)  # Wait for specified delay
        # NO STOP COMMAND - let shutdown_sequences handle it
    # Run in background thread so it doesn't block game logic
    threading.Thread(target=delayed_sequence, daemon=True).start()

def trigger_reaper_with_level_delay_no_stop(marker_addr, level):
    """Trigger level start with delay matching level duration - NO STOP"""
    level_delay = level_times.get(level, 30)
    trigger_reaper_with_delay_no_stop(marker_addr, addr15, level_delay)

#OSC Address
addr="/action/41261"  # Marker 21
addr1="/action/41262"  # Marker 22
addr2="/action/41263"  # Marker 23
addr3="/action/41264"  # Marker 24
addr4="/action/41265"  # Marker 25
addr5="/action/41266"  # Marker 26
addr6="/action/41267"  # Marker 27
addr7="/action/41268"  # Marker 28
addr8="/action/41269"  # Marker 29
addr9="/action/41270"  # Marker 30
addr10="/marker/20"  # Marker 31
addr11="/marker/21"  # Marker 32
addr12="/marker/22"  # Marker 33
addr13="/marker/23"  # Marker 34
addr14="/marker/24"  # Marker 35
addr15="/action/1007"  # Play
addr16="/action/1016"  # Stop



def trigger_osc(count):
    if current_level in milestones:
        if count == milestones[current_level][0]: gma_client.send_message("/gma3/cmd", "Go Sequence 23 cue 1"); trigger_reaper(addr)
        elif count == milestones[current_level][1]: gma_client.send_message("/gma3/cmd", "Go Sequence 23 cue 2"); trigger_reaper(addr1)
        elif count == milestones[current_level][2]: gma_client.send_message("/gma3/cmd", "Go Sequence 23 cue 3"); trigger_reaper(addr2)
        elif count == milestones[current_level][3]: gma_client.send_message("/gma3/cmd", "Go Sequence 23 cue 4"); trigger_reaper(addr3); trigger_reaper(addr9)

class GameUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AV Game Status")
        self.root.geometry("300x220")
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))
        self.root.bind("<space>", self.trigger_startup_sequence)

        font_large = ("Arial", 28)
        self.level_label = tk.Label(self.root, text="Level: 1", font=font_large); self.level_label.pack(pady=10)
        self.time_label = tk.Label(self.root, text="Remaining Time: 30s", font=font_large); self.time_label.pack(pady=10)
        self.stage_result = tk.Label(self.root, text="Stage: In Progress", font=font_large, fg="blue"); self.stage_result.pack(pady=10)
        self.game_result = tk.Label(self.root, text="Game: Waiting", font=font_large, fg="gray"); self.game_result.pack(pady=10)
        self.tries_label = tk.Label(self.root, text="Tries Left: 3", font=font_large); self.tries_label.pack(pady=10)

    def update_level(self, level): self.root.after(0, lambda: self.level_label.config(text=f"Level: {level}"))
    def update_time(self, time_left): self.root.after(0, lambda: self.time_label.config(text=f"Remaining Time: {int(time_left)}s"))
    def update_tries(self, tries): self.root.after(0, lambda: self.tries_label.config(text=f"Tries Left: {tries}"))
    def show_stage_result(self, result): color = "green" if result == "Win" else "red"; self.root.after(0, lambda: self.stage_result.config(text=f"Stage: {result}", fg=color))
    def show_game_result(self, result): color = {"Win": "green", "Lose": "red", "Startup": "orange", "Ready": "blue", "Waiting": "gray"}.get(result, "gray"); self.root.after(0, lambda: self.game_result.config(text=f"Game: {result}", fg=color))

    def trigger_startup_sequence(self, event=None):
        global startup_complete
        self.show_game_result("Startup")
        gma_client.send_message("/gma3/cmd", "Go Sequence 38 cue 3")
        time.sleep(0.3)
        gma_client.send_message("/gma3/cmd", "Go+ Sequence 41")
        time.sleep(0.9)
        gma_client.send_message("/gma3/cmd", "On Sequence 207")
        trigger_reaper(addr13)  # Jump to Marker 34
        time.sleep(0.1)  # Small delay to ensure marker jump completes
        trigger_reaper(addr15)  # Start playing
        startup_complete = True
        self.show_game_result("Ready")

def print_args(addr, *args):
    global count, game_started, timing_started, start_time
    global timeout_triggered, current_level, stage_tries, waiting_for_next

    if not startup_complete:
        return

    if waiting_for_next:
        level_start_sequence(current_level)
        gma_client.send_message("/gma3/cmd", f"Level {current_level} Start")
        ui.update_level(current_level)
        ui.update_tries(3)
        count = 0
        timing_started = False
        timeout_triggered = False
        stage_tries = 0
        waiting_for_next = False
        return

    if not game_started:
        game_started = True
        level_start_sequence(current_level)  # First sensor press - triggers level start audio/LEDs
        gma_client.send_message("/gma3/cmd", "Level Start")
        ui.update_level(current_level)
        ui.update_tries(3)
        # Don't return here - continue to start timing
        start_time = time.time()
        timing_started = True
        return

    if not timing_started:
        start_time = time.time()
        timing_started = True
        return

    if timeout_triggered or not timing_started:
        return

    count += 1
    if count in milestones.get(current_level, []):
        lit_pixels = int(LED_COUNT * (count / level_goals[current_level]))
        light_up(lit_pixels, get_stage_color(current_level))
        trigger_osc(count)

    if count == level_goals[current_level]:
        trigger_reaper(addr16)  # Stop current level audio
        time.sleep(0.3)         # Shorter initial delay
        
        # Start win audio immediately in background
        def win_stage_audio():
            trigger_reaper(addr9)   # Jump to Marker 30
            time.sleep(0.5)         # delay for 0.5s
            trigger_reaper(addr15)  # Play win audio
            time.sleep(20)          # delay for 20s
            trigger_reaper(addr16)  # Stop win audio
        threading.Thread(target=win_stage_audio, daemon=True).start()
        
        # LED animations happen while audio plays
        flash_bpm(LED_COUNT)
        green_dim_down(LED_COUNT)
        gma_client.send_message("/gma3/cmd", "Win Stage")
        ui.show_stage_result("Win")

        if current_level == max_levels:
            gma_client.send_message("/gma3/cmd", "Go+ sequence 23")
            gma_client.send_message("/gma3/cmd", "Go sequence 33")
            
            # Start win game audio immediately in background (same pattern as win stage)
            def win_game_audio():
                trigger_reaper(addr11)  # Jump to Marker 32
                time.sleep(0.5)         # delay for 0.5s
                trigger_reaper(addr15)  # Play win game audio
                time.sleep(20)          # delay for 20s
                trigger_reaper(addr16)  # Stop win game audio
            threading.Thread(target=win_game_audio, daemon=True).start()
            
            ui.show_game_result("Win")
            game_started = False
            timing_started = False
            return

        current_level += 1
        waiting_for_next = True
        ui.show_stage_result("In Progress")
        ui.update_level(current_level)
        return

def start_game_logic():
    global timing_started, timeout_triggered, start_time, current_level
    global stage_tries, game_started, count
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

                if time.time() - start_time > get_level_time(current_level) and count < level_goals[current_level]:
                    timeout_triggered = True
                    stage_tries += 1
                    ui.update_tries(3 - stage_tries)
                    red_dim_down(min(LED_COUNT, int(LED_COUNT * (count / level_goals[current_level]))))
                    gma_client.send_message("/gma3/cmd", "Lose Stage")
                    
                    # Start lose stage audio immediately in background
                    def lose_stage_audio():
                        trigger_reaper(addr10)  # Jump to Marker 31
                        time.sleep(0.5)         # delay for 0.5s
                        trigger_reaper(addr15)  # Play lose stage audio
                        time.sleep(20)          # delay for 20s
                        trigger_reaper(addr16)  # Stop lose stage audio
                    threading.Thread(target=lose_stage_audio, daemon=True).start()
                    
                    shutdown_sequences(current_level)
                    ui.show_stage_result("Lose")

                    if stage_tries >= 3:
                        gma_client.send_message("/gma3/cmd", "Go+ sequence 32")
                        
                        # Start lose game audio immediately in background
                        def lose_game_audio():
                            trigger_reaper(addr12)  # Jump to Marker 33
                            time.sleep(0.5)         # delay for 0.5s
                            trigger_reaper(addr15)  # Play lose game audio
                            time.sleep(20)          # delay for 20s
                            trigger_reaper(addr16)  # Stop lose game audio
                        threading.Thread(target=lose_game_audio, daemon=True).start()
                        
                        ui.show_game_result("Lose")
                        game_started = False
                        timing_started = False
                    else:
                        count = 0
                        timing_started = False
                        timeout_triggered = False
            time.sleep(0.01)
    except KeyboardInterrupt:
        light_up(LED_COUNT, 0)
        osc_server_thread.shutdown()

# 🚀 Start the GUI and game logic
if __name__ == "__main__":
    ui = GameUI()
    threading.Thread(target=start_game_logic, daemon=True).start()
    ui.root.mainloop()