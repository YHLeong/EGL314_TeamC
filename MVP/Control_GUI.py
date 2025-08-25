import tkinter as tk
from tkinter import ttk, messagebox
from pythonosc import udp_client
import threading
import time

class AVControlGUI:
    def __init__(self):
        # OSC Network Settings
        self.GMA_IP, self.GMA_PORT = "192.168.254.213", 2000
        self.REAPER_IP, self.REAPER_PORT = "192.168.254.12", 8000

        # Set up OSC clients
        self.gma_client = udp_client.SimpleUDPClient(self.GMA_IP, self.GMA_PORT)
        self.reaper_client = udp_client.SimpleUDPClient(self.REAPER_IP, self.REAPER_PORT)

        # Create and configure main window
        self.root = tk.Tk()
        self.root.title("AV Control Panel")
        self.root.geometry("1400x800")
        self.root.configure(bg="#f8f9fa")

        # Widget style settings
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Title.TLabel', font=('Arial', 18, 'bold'), background="#f8f9fa", foreground="#343a40")
        self.style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'), background="#f8f9fa", foreground="#495057")

        # REAPER markers and actions
        self.reaper_addresses = {
            "Load Sound 1": "/action/41261",
            "Load Sound 2": "/action/41262",
            "Load Sound 3": "/action/41263",
            "Load Sound 4": "/action/41264",
            "Load Sound 5": "/action/41265",
            "Load Sound 6": "/action/41266",
            "Level 1 start": "/action/41267",
            "Level 2 start": "/action/41268",
            "Level 3 start": "/action/41269",
            "Win Stage": "/action/41270",
            "Win Game": "/marker/21",
            "BGM": "/marker/23",
            "Static": "/marker/24",
            "Are you reeady?": "/marker/47",
            "Sit Down": "/marker/48",
            "Play": "/action/1007",
            "Stop": "/action/1016"
        }

        # GrandMA3 lighting cue commands with custom names
        self.gma_cues = {
            "Win Game Lighting": "Go sequence 105 cue 1",
            "Lose Game Lighting": "Go sequence 106 cue 1", 
            "Game Start Lighting": "Go sequence 104 cue 5",
            "Light Flashing": "Go sequence 104 cue 5.1",
            "Normal Lighting": "Go sequence 104 cue 5.2",
            "During Game Lighting": "Go sequence 104 cue 6",
            "Transition Effect": "Release sequence 83; Go sequence 108 cue 1",
            "End Transition": "Go sequence 83 cue 1",
            "End buttons": "Go sequence 83 cue+",
            "End Sequence": "Go sequence 13 cue 1",
            "Turn Off All Lights": "Off sequence thru please",
            "phtography": "Go sequence 120 cue 1"
        }

        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg="#f8f9fa")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        title_label = ttk.Label(main_frame, text="AV Control Panel", style='Title.TLabel')
        title_label.pack(pady=(0, 15))

        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        reaper_frame = tk.Frame(notebook, bg="#ffffff")
        gma_frame = tk.Frame(notebook, bg="#ffffff")
        quick_frame = tk.Frame(notebook, bg="#ffffff")

        notebook.add(reaper_frame, text="Audio")
        notebook.add(gma_frame, text="Lighting")
        notebook.add(quick_frame, text="Quick Actions")

        self.create_reaper_controls(reaper_frame)
        self.create_gma_controls(gma_frame)
        self.create_quick_actions(quick_frame)

    def create_reaper_controls(self, parent):
        reaper_label = ttk.Label(parent, text="Audio Controls", style='Subtitle.TLabel')
        reaper_label.pack(pady=15)
        
        # Transport Controls
        transport_frame = tk.Frame(parent, bg="#ffffff")
        transport_frame.pack(pady=10)
        
        play_btn = tk.Button(transport_frame, text="▶ PLAY", font=('Arial', 12, 'bold'),
                           bg="#28a745", fg="white", padx=25, pady=12, relief="flat",
                           command=lambda: self.trigger_reaper("/action/1007"))
        play_btn.pack(side=tk.LEFT, padx=5)
        
        stop_btn = tk.Button(transport_frame, text="⏹ STOP", font=('Arial', 12, 'bold'),
                           bg="#dc3545", fg="white", padx=25, pady=12, relief="flat",
                           command=lambda: self.trigger_reaper("/action/1016"))
        stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Marker Controls
        marker_frame = tk.Frame(parent, bg="#ffffff")
        marker_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Add marker buttons in simple grid
        row, col = 0, 0
        for name, address in self.reaper_addresses.items():
            if name not in ["Play", "Stop"]:
                btn = tk.Button(marker_frame, text=name, font=('Arial', 10),
                              bg="#007bff", fg="white", padx=12, pady=8, relief="flat",
                              command=lambda addr=address, n=name: self.trigger_reaper_and_play(addr, n))
                btn.grid(row=row, column=col, padx=3, pady=3, sticky="ew")
                
                col += 1
                if col > 3:
                    col = 0
                    row += 1
        
        for i in range(4):
            marker_frame.grid_columnconfigure(i, weight=1)

    def create_gma_controls(self, parent):
        gma_label = ttk.Label(parent, text="Lighting Controls", style='Subtitle.TLabel')
        gma_label.pack(pady=15)
        
        # Simple grid of lighting buttons
        button_frame = tk.Frame(parent, bg="#ffffff")
        button_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        row, col = 0, 0
        for display_name, command in self.gma_cues.items():
            btn = tk.Button(button_frame, text=display_name, font=('Arial', 10),
                          bg="#ffc107", fg="#212529", padx=12, pady=8, relief="flat",
                          command=lambda c=command: self.trigger_gma(c))
            btn.grid(row=row, column=col, padx=3, pady=3, sticky="ew")
            
            col += 1
            if col > 3:
                col = 0
                row += 1
        
        for i in range(4):
            button_frame.grid_columnconfigure(i, weight=1)

    def create_quick_actions(self, parent):
        quick_label = ttk.Label(parent, text="Game Actions", style='Subtitle.TLabel')
        quick_label.pack(pady=15)
        
        actions_frame = tk.Frame(parent, bg="#ffffff")
        actions_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        actions = [
            ("Game Startup", self.game_startup, "#28a745"),
            ("Win Stage", self.win_stage, "#ffc107"),
            ("Win Game", self.win_game, "#28a745"),
            ("Static + Flash", self.static_and_flash, "#fd7e14"),
            ("Emergency Stop", self.emergency_stop, "#dc3545"),
            ("Reset All", self.reset_all, "#6c757d")
        ]
        
        for i, (text, command, color) in enumerate(actions):
            btn = tk.Button(actions_frame, text=text, font=('Arial', 12, 'bold'),
                          bg=color, fg="white", padx=20, pady=15, relief="flat",
                          command=command)
            btn.grid(row=i//2, column=i%2, padx=8, pady=8, sticky="ew")
        
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)

    def create_status_display(self, parent):
        status_label = ttk.Label(parent, text="System Status", style='Subtitle.TLabel')
        status_label.pack(pady=(20, 10))
        
        # Network status
        network_frame = tk.LabelFrame(parent, text="Network Configuration", font=('Arial', 12, 'bold'),
                                    bg="#34495e", fg="white", padx=10, pady=10)
        network_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.status_text = tk.Text(network_frame, height=10, font=('Courier', 10),
                                 bg="#2c3e50", fg="#ecf0f1", wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.update_status()
        
        # Command log
        log_frame = tk.LabelFrame(parent, text="Command Log", font=('Arial', 12, 'bold'),
                                bg="#34495e", fg="white", padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.log_text = tk.Text(log_frame, height=15, font=('Courier', 10),
                              bg="#2c3e50", fg="#1abc9c", wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        clear_btn = tk.Button(log_frame, text="Clear Log", font=('Arial', 10),
                            bg="#7f8c8d", fg="white", padx=15, pady=5,
                            command=self.clear_log)
        clear_btn.pack(pady=5)

    def trigger_reaper(self, address, msg=1.0):
        try:
            self.reaper_client.send_message(address, msg)
            self.log_command(f"REAPER: {address} → {msg}")
        except Exception as e:
            self.log_command(f"ERROR REAPER: {address} → {str(e)}")
            messagebox.showerror("REAPER Error", f"Failed to send: {address}\n{str(e)}")

    def trigger_reaper_and_play(self, address, name):
        def sequence():
            try:
                self.trigger_reaper(address)
                time.sleep(0.5)
                self.trigger_reaper("/action/1007")
                self.log_command(f"SEQUENCE: {name} → Jump + Play")
            except Exception as e:
                self.log_command(f"ERROR SEQUENCE: {name} → {str(e)}")

        threading.Thread(target=sequence, daemon=True).start()

    def trigger_gma(self, command):
        try:
            self.gma_client.send_message("/gma3/cmd", command)
            self.log_command(f"GMA3: {command}")
        except Exception as e:
            self.log_command(f"ERROR GMA3: {command} → {str(e)}")
            messagebox.showerror("GMA3 Error", f"Failed to send: {command}\n{str(e)}")

    def log_command(self, message):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")  # Simple console logging

    # Quick Action Methods
    def game_startup(self):
        def startup_sequence():
            self.trigger_reaper("/marker/23")
            time.sleep(0.1)
            self.trigger_reaper("/action/1007")
            self.log_command("GAME: Startup sequence completed")
        
        threading.Thread(target=startup_sequence, daemon=True).start()

    def win_stage(self):
        def win_sequence():
            self.trigger_reaper("/action/1016")
            time.sleep(0.5)
            self.trigger_reaper("/action/41270")
            time.sleep(0.5)
            self.trigger_reaper("/action/1007")
            self.log_command("GAME: Win stage sequence")
        
        threading.Thread(target=win_sequence, daemon=True).start()

    def win_game(self):
        def win_sequence():
            self.gma_client.send_message("/gma3/cmd", "Go sequence 105 cue 1")
            self.trigger_reaper("/action/1016")
            time.sleep(0.1)
            self.trigger_reaper("/marker/24")
            time.sleep(0.5)
            self.trigger_reaper("/action/1007")
            self.log_command("GAME: Win game sequence with lighting")
        
        threading.Thread(target=win_sequence, daemon=True).start()

    def static_and_flash(self):
        def static_flash_sequence():
            self.gma_client.send_message("/gma3/cmd", "Go sequence 104 cue 5.1")
            self.trigger_reaper("/action/1016")
            time.sleep(0.1)
            self.trigger_reaper("/marker/24")
            time.sleep(0.5)
            self.trigger_reaper("/action/1007")
            self.log_command("GAME: Static audio + light flash sequence")
        
        threading.Thread(target=static_flash_sequence, daemon=True).start()

    def emergency_stop(self):
        # Stop audio
        self.trigger_reaper("/action/1016")
        # Turn off all lights
        self.trigger_gma("Off sequence thru please")
        self.log_command("EMERGENCY: Audio stopped and all lights turned off")
        messagebox.showwarning("Emergency Stop", "Audio has been stopped and all lights turned off!")

    def reset_all(self):
        def reset_sequence():
            self.trigger_reaper("/action/1016")
            time.sleep(0.5)
            self.trigger_reaper("/marker/24")
            time.sleep(0.5)
            self.trigger_reaper("/action/1007")
            self.log_command("SYSTEM: Reset to base state")
        
        threading.Thread(target=reset_sequence, daemon=True).start()

    def run(self):
        try:
            self.log_command("SYSTEM: AV Control Panel started")
            self.root.mainloop()
        except KeyboardInterrupt:
            self.log_command("SYSTEM: Shutdown requested")
            self.emergency_stop()
            self.root.quit()

if __name__ == "__main__":
    app = AVControlGUI()
    app.run()
