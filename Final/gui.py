import tkinter as tk
from tkinter import ttk, messagebox
from pythonosc import udp_client
import threading
import time
import random

class AVControlGUI:
    def __init__(self):
        # -------- OSC Network Settings --------
        self.GMA_IP, self.GMA_PORT = "192.168.254.213", 2000
        self.REAPER_IP, self.REAPER_PORT = "192.168.254.12", 8000

        # Set up OSC clients
        self.gma_client = udp_client.SimpleUDPClient(self.GMA_IP, self.GMA_PORT)
        self.reaper_client = udp_client.SimpleUDPClient(self.REAPER_IP, self.REAPER_PORT)

        # -------- Window --------
        self.root = tk.Tk()
        self.root.title("AV Control Panel — Sector 536")
        self.root.geometry("1400x840")
        self.root.minsize(1200, 760)

        # Space palette
        self.COLORS = {
            "bg":      "#0b0f1a",  # deep space
            "panel":   "#0f172a",  # slate night
            "panel2":  "#111827",
            "text":    "#e5e7eb",  # light gray
            "muted":   "#94a3b8",
            "neon":    "#22d3ee",  # cyan
            "neon2":   "#a78bfa",  # purple
            "ok":      "#22c55e",
            "warn":    "#f59e0b",
            "danger":  "#ef4444",
            "primary": "#3b82f6",
            "steel":   "#334155"
        }

        self.root.configure(bg=self.COLORS["bg"])

        # -------- ttk Styles --------
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure(
            "Title.TLabel",
            font=("Segoe UI", 22, "bold"),
            background=self.COLORS["bg"],
            foreground=self.COLORS["neon"]
        )
        self.style.configure(
            "Subtitle.TLabel",
            font=("Segoe UI", 12, "bold"),
            background=self.COLORS["panel"],
            foreground=self.COLORS["neon2"]
        )
        self.style.configure(
            "Panel.TFrame",
            background=self.COLORS["panel"]
        )
        self.style.configure(
            "Panel2.TFrame",
            background=self.COLORS["panel2"]
        )
        self.style.configure(
            "TSeparator",
            background=self.COLORS["neon"]
        )
        self.style.configure(
            "Info.TLabel",
            font=("Consolas", 10),
            background=self.COLORS["panel2"],
            foreground=self.COLORS["muted"]
        )

        # -------- REAPER markers and actions --------
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

        # -------- GrandMA3 lighting cue commands --------
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

        # Build UI
        self._build_ui()

        # Optional: subtle starfield in the background
        self._init_starfield()

    # ---------- Layout Builders ----------
    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.COLORS["bg"])
        header.pack(fill=tk.X, padx=18, pady=(16, 10))

        title = ttk.Label(header, text="PROJECT L.U.M.E.N — PRISM CIPHER", style="Title.TLabel")
        title.pack(side=tk.LEFT)

        # Thin neon divider under header
        self._divider(self.root, height=3, pad=(18, 10))

        # Main content grid (single page, divided by panels & separators)
        content = tk.Frame(self.root, bg=self.COLORS["bg"])
        content.pack(fill=tk.BOTH, expand=True, padx=18, pady=10)

        content.grid_columnconfigure(0, weight=1, uniform="col")
        content.grid_columnconfigure(1, weight=1, uniform="col")
        content.grid_rowconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        # Left column: Audio + Lighting
        left_col = ttk.Frame(content, style="Panel.TFrame")
        left_col.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 9), pady=0)
        left_col.grid_rowconfigure(0, weight=1)
        left_col.grid_rowconfigure(2, weight=1)
        left_col.grid_columnconfigure(0, weight=1)

        # Audio Controls Panel
        audio_panel = ttk.Frame(left_col, style="Panel2.TFrame")
        audio_panel.grid(row=0, column=0, sticky="nsew", padx=12, pady=(12, 6))
        self._section_header(audio_panel, "AUDIO — REAPER CONTROLS")

        self._transport_controls(audio_panel)
        self._divider(audio_panel, pad=(12, 10))
        self._reaper_markers(audio_panel)

        # Divider between sections
        self._divider(left_col, pad=(12, 10), neon="neon2")

        # Lighting Controls Panel
        light_panel = ttk.Frame(left_col, style="Panel2.TFrame")
        light_panel.grid(row=2, column=0, sticky="nsew", padx=12, pady=(6, 12))
        self._section_header(light_panel, "LIGHTING — GRANDMA3 CUES")

        self._gma_buttons(light_panel)

        # Right column: Quick Actions + Status
        right_col = ttk.Frame(content, style="Panel.TFrame")
        right_col.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(9, 0), pady=0)
        right_col.grid_rowconfigure(0, weight=0)
        right_col.grid_rowconfigure(2, weight=1)
        right_col.grid_columnconfigure(0, weight=1)

        # Quick Actions panel
        qa_panel = ttk.Frame(right_col, style="Panel2.TFrame")
        qa_panel.grid(row=0, column=0, sticky="new", padx=12, pady=(12, 6))
        self._section_header(qa_panel, "MISSION CONTROLS — QUICK ACTIONS")
        self._quick_actions(qa_panel)

        # Divider
        self._divider(right_col, pad=(12, 10), neon="neon2")

        # Status panel (Network + Log)
        status_panel = ttk.Frame(right_col, style="Panel2.TFrame")
        status_panel.grid(row=2, column=0, sticky="nsew", padx=12, pady=(6, 12))
        self._section_header(status_panel, "TELEMETRY — SYSTEM STATUS")
        self._status_display(status_panel)

    def _section_header(self, parent, text):
        bar = tk.Frame(parent, bg=self.COLORS["panel2"])
        bar.pack(fill=tk.X, padx=12, pady=(12, 8))

        lbl = ttk.Label(bar, text=text, style="Subtitle.TLabel")
        lbl.pack(side=tk.LEFT)

        # Neon accent bar
        accent = tk.Frame(parent, bg=self.COLORS["neon"])
        accent.pack(fill=tk.X, padx=12, pady=(0, 12), ipady=1)

    def _divider(self, parent, height=2, pad=(0, 8), neon="neon"):
        color = self.COLORS[neon] if neon in self.COLORS else self.COLORS["neon"]
        div = tk.Frame(parent, bg=color, height=height)
        # Use the same geometry manager the parent is already using
        try:
            uses_grid = bool(parent.grid_slaves())
        except Exception:
            uses_grid = False

        if uses_grid:
            # Place divider on next available row, spanning all columns
            cols, rows = parent.grid_size()
            cols = max(1, cols)
            try:
                parent.grid_columnconfigure(0, weight=1)
            except Exception:
                pass
            div.grid(row=rows, column=0, columnspan=cols, sticky="ew", padx=pad[0], pady=pad[1])
        else:
            div.pack(fill=tk.X, padx=pad[0], pady=pad[1])

    # ---------- Subsections ----------
    def _transport_controls(self, parent):
        wrap = tk.Frame(parent, bg=self.COLORS["panel2"])
        wrap.pack(padx=12, pady=(6, 8), anchor="w")

        btn_play = self._ghost_button(
            wrap, "▶ PLAY", self.COLORS["ok"],
            lambda: self.trigger_reaper("/action/1007")
        )
        btn_play.pack(side=tk.LEFT, padx=(0, 8), pady=4)

        btn_stop = self._ghost_button(
            wrap, "⏹ STOP", self.COLORS["danger"],
            lambda: self.trigger_reaper("/action/1016")
        )
        btn_stop.pack(side=tk.LEFT, padx=(0, 8), pady=4)

        # Info label
        info = ttk.Label(
            wrap,
            text="Transport sends REAPER actions: /action/1007 (Play), /action/1016 (Stop)",
            style="Info.TLabel"
        )
        info.pack(side=tk.LEFT, padx=8)

    def _reaper_markers(self, parent):
        grid = tk.Frame(parent, bg=self.COLORS["panel2"])
        grid.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        # Create a responsive grid: 4 columns
        cols = 4
        for c in range(cols):
            grid.grid_columnconfigure(c, weight=1)

        r = 0
        c = 0
        for name, address in self.reaper_addresses.items():
            if name in ["Play", "Stop"]:
                continue
            btn = self._chip_button(
                grid, name, self.COLORS["primary"],
                lambda addr=address, n=name: self.trigger_reaper_and_play(addr, n)
            )
            btn.grid(row=r, column=c, padx=6, pady=6, sticky="ew")
            c += 1
            if c >= cols:
                c = 0
                r += 1

    def _gma_buttons(self, parent):
        grid = tk.Frame(parent, bg=self.COLORS["panel2"])
        grid.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        cols = 3
        for c in range(cols):
            grid.grid_columnconfigure(c, weight=1)

        r = 0
        c = 0
        for display_name, command in self.gma_cues.items():
            btn = self._chip_button(
                grid, display_name, self.COLORS["warn"],
                lambda cmd=command: self.trigger_gma(cmd),
                dark=True
            )
            btn.grid(row=r, column=c, padx=6, pady=6, sticky="ew")
            c += 1
            if c >= cols:
                c = 0
                r += 1

        # Add Photography button if not present
        if "phtography" not in self.gma_cues:
            btn = self._chip_button(
                grid, "Photography", self.COLORS["warn"],
                lambda: self.trigger_gma("Go sequence 120 cue 1"),
                dark=True
            )
            btn.grid(row=r, column=c, padx=6, pady=6, sticky="ew")

    def _quick_actions(self, parent):
        grid = tk.Frame(parent, bg=self.COLORS["panel2"])
        grid.pack(fill=tk.X, padx=12, pady=(0, 12))

        buttons = [
            ("Game Startup", self.game_startup, self.COLORS["ok"]),
            ("Win Stage", self.win_stage, self.COLORS["warn"]),
            ("Win Game", self.win_game, self.COLORS["ok"]),
            ("Static + Flash", self.static_and_flash, "#f97316"),  # orange
            ("Emergency Stop", self.emergency_stop, self.COLORS["danger"]),
            ("Reset All", self.reset_all, self.COLORS["steel"])
        ]

        # 2 columns, responsive
        for i in range(2):
            grid.grid_columnconfigure(i, weight=1)

        for i, (label, command, color) in enumerate(buttons):
            btn = self._ghost_button(grid, label, color, command)
            btn.grid(row=i // 2, column=i % 2, padx=6, pady=6, sticky="ew")

    def _status_display(self, parent):
        # Network block
        net_frame = tk.Frame(parent, bg=self.COLORS["panel2"])
        net_frame.pack(fill=tk.X, padx=12, pady=(4, 8))

        net_box = tk.Frame(net_frame, bg=self.COLORS["panel"], bd=0, highlightthickness=1,
                           highlightbackground=self.COLORS["neon2"])
        net_box.pack(fill=tk.X, padx=0, pady=0)

        net_text = (
            f"GMA3 → {self.GMA_IP}:{self.GMA_PORT}    REAPER → {self.REAPER_IP}:{self.REAPER_PORT}\n"
            "All commands are sent via OSC.\n"
            "Sequences auto-play REAPER with /action/1007 after jumps where specified."
        )
        lbl = ttk.Label(net_box, text=net_text, style="Info.TLabel")
        lbl.pack(anchor="w", padx=10, pady=8)

        # Command log
        log_frame = tk.Frame(parent, bg=self.COLORS["panel2"])
        log_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        box = tk.Frame(log_frame, bg=self.COLORS["panel"], bd=0, highlightthickness=1,
                       highlightbackground=self.COLORS["neon"])
        box.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(
            box, height=12, font=("Consolas", 10),
            bg=self.COLORS["panel"], fg=self.COLORS["neon"],
            bd=0, highlightthickness=0, insertbackground=self.COLORS["text"], wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 4))

        controls = tk.Frame(box, bg=self.COLORS["panel"])
        controls.pack(fill=tk.X, padx=8, pady=(0, 8))

        clear_btn = self._chip_button(controls, "Clear Log", self.COLORS["steel"], self.clear_log)
        clear_btn.pack(side=tk.RIGHT, padx=0, pady=0)

    # ---------- Buttons ----------
    def _ghost_button(self, parent, text, color, command):
        # big prominent button
        bg = self.COLORS["panel"]
        frame = tk.Frame(parent, bg=bg)
        btn = tk.Button(
            frame,
            text=text,
            font=("Segoe UI", 12, "bold"),
            bg=bg,
            fg=self.COLORS["text"],
            activebackground=bg,
            activeforeground=self.COLORS["text"],
            relief="flat",
            padx=18, pady=12,
            command=command
        )
        btn.pack(fill=tk.X)

        # neon underline
        underline = tk.Frame(frame, bg=color, height=3)
        underline.pack(fill=tk.X, pady=(6, 0))

        return frame

    def _chip_button(self, parent, text, color, command, dark=False):
        # compact capsule button
        bg = self.COLORS["panel2"] if dark else self.COLORS["panel"]
        frame = tk.Frame(parent, bg=bg)
        btn = tk.Button(
            frame,
            text=text,
            font=("Segoe UI", 10, "bold"),
            bg=bg,
            fg=self.COLORS["text"],
            activebackground=bg,
            activeforeground=self.COLORS["text"],
            relief="flat",
            padx=14, pady=10,
            command=command
        )
        btn.pack(fill=tk.X)
        glow = tk.Frame(frame, bg=color, height=2)
        glow.pack(fill=tk.X, pady=(5, 0))
        return frame

    # ---------- Command helpers ----------
    def trigger_reaper(self, address, msg=1.0):
        try:
            self.reaper_client.send_message(address, msg)
            self.log_command(f"REAPER  {address} → {msg}")
        except Exception as e:
            self.log_command(f"ERROR   REAPER {address} → {str(e)}")
            messagebox.showerror("REAPER Error", f"Failed to send: {address}\n{str(e)}")

    def trigger_reaper_and_play(self, address, name):
        def sequence():
            try:
                self.trigger_reaper(address)
                self.trigger_reaper("/action/1007")
                self.log_command(f"SEQUENCE {name} → Jump + Play")
            except Exception as e:
                self.log_command(f"ERROR   SEQUENCE {name} → {str(e)}")
        threading.Thread(target=sequence, daemon=True).start()

    def trigger_gma(self, command):
        try:
            self.gma_client.send_message("/gma3/cmd", command)
            self.log_command(f"GMA3    {command}")
        except Exception as e:
            self.log_command(f"ERROR   GMA3 {command} → {str(e)}")
            messagebox.showerror("GMA3 Error", f"Failed to send: {command}\n{str(e)}")

    def log_command(self, message):
        timestamp = time.strftime("%H:%M:%S")
        line = f"[{timestamp}] {message}\n"
        print(line, end="")
        if hasattr(self, "log_text"):
            try:
                self.log_text.insert(tk.END, line)
                self.log_text.see(tk.END)
            except tk.TclError:
                # In case UI not constructed yet
                pass

    # ---------- Quick Actions ----------
    def game_startup(self):
        def startup_sequence():
            self.trigger_reaper("/marker/23")
            self.trigger_reaper("/action/1007")
            self.log_command("GAME    Startup sequence completed")
        threading.Thread(target=startup_sequence, daemon=True).start()

    def win_stage(self):
        def win_sequence():
            self.trigger_reaper("/action/1016")
            self.trigger_reaper("/action/41270")
            self.trigger_reaper("/action/1007")
            self.log_command("GAME    Win stage sequence")
        threading.Thread(target=win_sequence, daemon=True).start()

    def win_game(self):
        def win_sequence():
            self.gma_client.send_message("/gma3/cmd", "Go sequence 105 cue 1")
            self.trigger_reaper("/action/1016")
            self.trigger_reaper("/marker/24")
            self.trigger_reaper("/action/1007")
            self.log_command("GAME    Win game sequence with lighting")
        threading.Thread(target=win_sequence, daemon=True).start()

    def static_and_flash(self):
        def static_flash_sequence():
            self.gma_client.send_message("/gma3/cmd", "Go sequence 104 cue 5.1")
            self.trigger_reaper("/action/1016")
            self.trigger_reaper("/marker/24")
            self.trigger_reaper("/action/1007")
            self.log_command("GAME    Static audio + light flash sequence")
        threading.Thread(target=static_flash_sequence, daemon=True).start()

    def emergency_stop(self):
        self.trigger_reaper("/action/1016")
        self.trigger_gma("Off sequence thru please")
        self.log_command("EMERG   Audio stopped and all lights turned off")
        messagebox.showwarning("Emergency Stop", "Audio has been stopped and all lights turned off!")

    def reset_all(self):
        def reset_sequence():
            self.trigger_reaper("/action/1016")
            self.trigger_reaper("/marker/24")
            self.trigger_reaper("/action/1007")
            self.log_command("SYSTEM  Reset to base state")
        threading.Thread(target=reset_sequence, daemon=True).start()

    def clear_log(self):
        try:
            self.log_text.delete("1.0", tk.END)
        except tk.TclError:
            pass

    # ---------- Starfield (optional aesthetic) ----------
    def _init_starfield(self):
        # Draw subtle stars behind everything
        self.bg_canvas = tk.Canvas(self.root, bg=self.COLORS["bg"], highlightthickness=0, bd=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.root.bind("<Configure>", self._redraw_starfield)

        # Send canvas to back (Canvas.lower lowers items, not the widget)
        try:
            self.bg_canvas.tk.call("lower", self.bg_canvas._w)
        except Exception:
            pass

        self.stars = []
        self._redraw_starfield()  # initial draw
        self._twinkle()

    def _redraw_starfield(self, event=None):
        self.bg_canvas.delete("all")
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        # density based on area
        count = max(60, (w * h) // 24000)
        self.stars = []
        for _ in range(count):
            x = random.randint(0, max(1, w))
            y = random.randint(0, max(1, h))
            r = random.choice([1, 1, 1, 2])
            alpha = random.randint(120, 255)
            color = self._hex_with_alpha(self.COLORS["neon"], alpha)
            oid = self.bg_canvas.create_oval(x-r, y-r, x+r, y+r, outline="", fill=color)
            self.stars.append((oid, x, y, r))

    def _twinkle(self):
        # Randomly adjust brightness of a few stars
        if self.stars:
            for oid, *_ in random.sample(self.stars, k=max(1, len(self.stars)//12)):
                alpha = random.randint(80, 255)
                color = self._hex_with_alpha(self.COLORS["neon2"], alpha)
                self.bg_canvas.itemconfig(oid, fill=color)
        self.root.after(350, self._twinkle)

    @staticmethod
    def _hex_with_alpha(hex_color, alpha_0_255):
        # Tkinter doesn't support alpha; we fake it with close shades (kept for stylistic variety)
        # Return the base hex; varying between neon/neon2 gives a twinkle illusion
        return hex_color

    # ---------- Run ----------
    def run(self):
        try:
            self.log_command("SYSTEM  AV Control Panel started")
            self.root.mainloop()
        except KeyboardInterrupt:
            self.log_command("SYSTEM  Shutdown requested")
            self.emergency_stop()
            self.root.quit()

if __name__ == "__main__":
    app = AVControlGUI()
    app.run()
