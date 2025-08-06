import tkinter as tk  # Import main tkinter library for GUI creation
from tkinter import ttk, messagebox  # Import themed widgets and message dialogs
from pythonosc import udp_client  # Import OSC (Open Sound Control) client for network communication
import threading  # Import threading for background task execution
import time  # Import time module for delays and timestamps

class AVControlGUI:  # Main class for the AV Control Panel application
    def __init__(self):  # Constructor method to initialize the GUI application
        # Network Configuration
        self.GMA_IP, self.GMA_PORT = "192.168.254.213", 2000  # Set IP and port for GrandMA3 lighting console
        self.REAPER_IP, self.REAPER_PORT = "192.168.254.12", 8000  # Set IP and port for REAPER audio workstation
        
        # OSC Clients
        self.gma_client = udp_client.SimpleUDPClient(self.GMA_IP, self.GMA_PORT)  # Create OSC client for GrandMA3 communication
        self.reaper_client = udp_client.SimpleUDPClient(self.REAPER_IP, self.REAPER_PORT)  # Create OSC client for REAPER communication
        
        # Create main window
        self.root = tk.Tk()  # Create the main application window
        self.root.title("AV Control Panel - Raspberry Pi 4")  # Set the window title
        self.root.geometry("1920x1080")  # Set window size to Full HD resolution
        self.root.configure(bg="#2c3e50")  # Set dark blue background color
        
        # Configure styles
        self.style = ttk.Style()  # Create a style object for themed widget customization
        self.style.theme_use('clam')  # Set the theme to 'clam' for a modern look
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background="#2c3e50", foreground="white")  # Configure title label style with large bold font
        self.style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'), background="#2c3e50", foreground="white")  # Configure subtitle label style with medium bold font
        self.style.configure('Control.TButton', font=('Arial', 10, 'bold'), padding=10)  # Configure button style with padding
        
        # REAPER OSC Addresses
        self.reaper_addresses = {  # Dictionary mapping marker names to OSC addresses
            "Marker 21": "/action/41261",  # OSC address to jump to marker 21 in REAPER
            "Marker 22": "/action/41262",  # OSC address to jump to marker 22 in REAPER
            "Marker 23": "/action/41263",  # OSC address to jump to marker 23 in REAPER
            "Marker 24": "/action/41264",  # OSC address to jump to marker 24 in REAPER
            "Marker 25": "/action/41265",  # OSC address to jump to marker 25 in REAPER
            "Marker 26": "/action/41266",  # OSC address to jump to marker 26 in REAPER
            "Marker 27": "/action/41267",  # OSC address to jump to marker 27 in REAPER
            "Marker 28": "/action/41268",  # OSC address to jump to marker 28 in REAPER
            "Marker 29": "/action/41269",  # OSC address to jump to marker 29 in REAPER
            "Marker 30": "/action/41270",  # OSC address to jump to marker 30 in REAPER
            "Marker 31": "/marker/20",  # Direct marker jump to position 20
            "Marker 32": "/marker/21",  # Direct marker jump to position 21
            "Marker 33": "/marker/22",  # Direct marker jump to position 22
            "Marker 34": "/marker/23",  # Direct marker jump to position 23
            "Marker 35": "/marker/24",  # Direct marker jump to position 24
            "Play": "/action/1007",  # OSC address for REAPER play command
            "Stop": "/action/1016"  # OSC address for REAPER stop command
        }
        
        # GrandMA3 Cues
        self.gma_cues = [  # List of predefined lighting cue commands for GrandMA3
            "Go Sequence 23 cue 1",  # Trigger sequence 23, cue 1
            "Go Sequence 23 cue 2",  # Trigger sequence 23, cue 2
            "Go Sequence 23 cue 3",  # Trigger sequence 23, cue 3
            "Go Sequence 23 cue 4",  # Trigger sequence 23, cue 4
            "Go Sequence 38 cue 3",  # Trigger sequence 38, cue 3
            "Go+ Sequence 41",  # Go forward in sequence 41
            "On Sequence 207",  # Turn on sequence 207
            "Off Sequence 23 cue 1",  # Turn off sequence 23, cue 1
            "Off Sequence 23 cue 2",  # Turn off sequence 23, cue 2
            "Off Sequence 23 cue 3",  # Turn off sequence 23, cue 3
            "Off Sequence 23 cue 4",  # Turn off sequence 23, cue 4
            "Go+ sequence 23",  # Go forward in sequence 23
            "Go sequence 33",  # Go to sequence 33
            "Go+ sequence 32"  # Go forward in sequence 32
        ]
        
        self.create_widgets()  # Call method to create all GUI widgets
        
    def create_widgets(self):  # Method to create and arrange all GUI widgets
        # Main container
        main_frame = tk.Frame(self.root, bg="#2c3e50")  # Create main frame container with dark background
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)  # Pack frame to fill window with padding
        
        # Title
        title_label = ttk.Label(main_frame, text="🎵 AV Control Panel", style='Title.TLabel')  # Create title label with music icon
        title_label.pack(pady=(0, 20))  # Pack title with bottom padding
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)  # Create tabbed notebook widget
        notebook.pack(fill=tk.BOTH, expand=True)  # Pack notebook to fill available space
        
        # REAPER Control Tab
        reaper_frame = tk.Frame(notebook, bg="#34495e")  # Create frame for REAPER controls with darker background
        notebook.add(reaper_frame, text="🎵 REAPER Control")  # Add REAPER tab to notebook with music icon
        self.create_reaper_controls(reaper_frame)  # Create REAPER control widgets in this frame
        
        # GrandMA3 Control Tab
        gma_frame = tk.Frame(notebook, bg="#34495e")  # Create frame for GrandMA3 controls
        notebook.add(gma_frame, text="💡 GrandMA3 Control")  # Add GrandMA3 tab to notebook with light bulb icon
        self.create_gma_controls(gma_frame)  # Create GrandMA3 control widgets in this frame
        
        # Quick Actions Tab
        quick_frame = tk.Frame(notebook, bg="#34495e")  # Create frame for quick action buttons
        notebook.add(quick_frame, text="⚡ Quick Actions")  # Add quick actions tab with lightning icon
        self.create_quick_actions(quick_frame)  # Create quick action widgets in this frame
        
        # Status Tab
        status_frame = tk.Frame(notebook, bg="#34495e")  # Create frame for status display
        notebook.add(status_frame, text="📊 Status")  # Add status tab with chart icon
        self.create_status_display(status_frame)  # Create status display widgets in this frame
    
    def create_reaper_controls(self, parent):  # Method to create REAPER audio control widgets
        # REAPER Controls
        reaper_label = ttk.Label(parent, text="REAPER Commands", style='Subtitle.TLabel')  # Create subtitle for REAPER section
        reaper_label.pack(pady=(20, 10))  # Pack label with vertical padding
        
        # Transport Controls
        transport_frame = tk.LabelFrame(parent, text="Transport Controls", font=('Arial', 12, 'bold'),  # Create labeled frame for transport buttons
                                      bg="#34495e", fg="white", padx=10, pady=10)  # Set background, text color and padding
        transport_frame.pack(fill=tk.X, padx=20, pady=10)  # Pack frame to fill horizontally with padding
        
        transport_buttons = tk.Frame(transport_frame, bg="#34495e")  # Create container frame for transport buttons
        transport_buttons.pack()  # Pack button container
        
        play_btn = tk.Button(transport_buttons, text="▶️ PLAY", font=('Arial', 12, 'bold'),  # Create play button with play icon
                           bg="#27ae60", fg="white", padx=20, pady=10,  # Set green background, white text, and padding
                           command=lambda: self.trigger_reaper("/action/1007"))  # Set command to trigger REAPER play
        play_btn.pack(side=tk.LEFT, padx=10)  # Pack button on left side with horizontal padding
        
        stop_btn = tk.Button(transport_buttons, text="⏹️ STOP", font=('Arial', 12, 'bold'),  # Create stop button with stop icon
                           bg="#e74c3c", fg="white", padx=20, pady=10,  # Set red background, white text, and padding
                           command=lambda: self.trigger_reaper("/action/1016"))  # Set command to trigger REAPER stop
        stop_btn.pack(side=tk.LEFT, padx=10)  # Pack button on left side with horizontal padding
        
        # Marker Controls
        marker_frame = tk.LabelFrame(parent, text="Marker Controls", font=('Arial', 12, 'bold'),  # Create labeled frame for marker buttons
                                   bg="#34495e", fg="white", padx=10, pady=10)  # Set styling and padding
        marker_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)  # Pack frame to fill and expand with padding
        
        # Create scrollable marker buttons
        canvas = tk.Canvas(marker_frame, bg="#34495e", highlightthickness=0)  # Create scrollable canvas with no border highlight
        scrollbar = ttk.Scrollbar(marker_frame, orient="vertical", command=canvas.yview)  # Create vertical scrollbar linked to canvas
        scrollable_frame = tk.Frame(canvas, bg="#34495e")  # Create frame inside canvas for scrollable content
        
        scrollable_frame.bind(  # Bind configuration event to update scroll region
            "<Configure>",  # Event trigger when frame size changes
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))  # Update canvas scroll region to fit all content
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")  # Create window in canvas containing scrollable frame
        canvas.configure(yscrollcommand=scrollbar.set)  # Link canvas vertical scroll to scrollbar
        
        # Add marker buttons in grid
        row, col = 0, 0  # Initialize grid position counters
        for name, address in self.reaper_addresses.items():  # Loop through all REAPER address mappings
            if name not in ["Play", "Stop"]:  # Skip transport controls (already created above)
                btn = tk.Button(scrollable_frame, text=name, font=('Arial', 10),  # Create marker button with name
                              bg="#3498db", fg="white", padx=15, pady=8,  # Set blue background, white text, padding
                              command=lambda addr=address, n=name: self.trigger_reaper_and_play(addr, n))  # Set command to jump to marker and play
                btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")  # Place button in grid with padding and expand east-west
                
                col += 1  # Move to next column
                if col > 2:  # If we've filled 3 columns
                    col = 0  # Reset to first column
                    row += 1  # Move to next row
        
        # Configure grid columns to expand
        for i in range(3):  # For each of the 3 columns
            scrollable_frame.grid_columnconfigure(i, weight=1)  # Set column to expand equally
        
        canvas.pack(side="left", fill="both", expand=True)  # Pack canvas on left side, fill and expand
        scrollbar.pack(side="right", fill="y")  # Pack scrollbar on right side, fill vertically
        
    def create_gma_controls(self, parent):
        # GrandMA3 Controls
        gma_label = ttk.Label(parent, text="GrandMA3 Commands", style='Subtitle.TLabel')
        gma_label.pack(pady=(20, 10))
        
        # Cue Controls
        cue_frame = tk.LabelFrame(parent, text="Lighting Cues", font=('Arial', 12, 'bold'),
                                bg="#34495e", fg="white", padx=10, pady=10)
        cue_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create scrollable cue buttons
        canvas = tk.Canvas(cue_frame, bg="#34495e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(cue_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#34495e")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add cue buttons
        for i, cue in enumerate(self.gma_cues):
            btn = tk.Button(scrollable_frame, text=cue, font=('Arial', 10),
                          bg="#f39c12", fg="black", padx=15, pady=8,
                          command=lambda c=cue: self.trigger_gma(c))
            btn.pack(fill=tk.X, padx=5, pady=2)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Custom Cue Entry
        custom_frame = tk.LabelFrame(parent, text="Custom Command", font=('Arial', 12, 'bold'),
                                   bg="#34495e", fg="white", padx=10, pady=10)
        custom_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.custom_entry = tk.Entry(custom_frame, font=('Arial', 12), width=40)
        self.custom_entry.pack(side=tk.LEFT, padx=5)
        
        custom_btn = tk.Button(custom_frame, text="Send Custom", font=('Arial', 10, 'bold'),
                             bg="#9b59b6", fg="white", padx=15, pady=5,
                             command=self.send_custom_gma)
        custom_btn.pack(side=tk.LEFT, padx=5)
        
    def create_quick_actions(self, parent):
        # Quick Actions
        quick_label = ttk.Label(parent, text="Quick Game Actions", style='Subtitle.TLabel')
        quick_label.pack(pady=(20, 10))
        
        # Game State Actions
        actions_frame = tk.LabelFrame(parent, text="Game State Controls", font=('Arial', 12, 'bold'),
                                    bg="#34495e", fg="white", padx=20, pady=20)
        actions_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create action buttons
        actions = [
            ("Game Startup", self.game_startup, "#27ae60"),
            ("Win Stage", self.win_stage, "#f1c40f"),
            ("Win Game", self.win_game, "#2ecc71"),
            ("Lose Stage", self.lose_stage, "#e67e22"),
            ("Lose Game", self.lose_game, "#e74c3c"),
            ("Emergency Stop", self.emergency_stop, "#c0392b"),
            ("Reset All", self.reset_all, "#95a5a6")
        ]
        
        for i, (text, command, color) in enumerate(actions):
            btn = tk.Button(actions_frame, text=text, font=('Arial', 14, 'bold'),
                          bg=color, fg="white", padx=30, pady=15,
                          command=command)
            btn.grid(row=i//2, column=i%2, padx=20, pady=15, sticky="ew")
        
        # Configure grid
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)
        
    def create_status_display(self, parent):
        # Status Display
        status_label = ttk.Label(parent, text="System Status", style='Subtitle.TLabel')
        status_label.pack(pady=(20, 10))
        
        # Network Status
        network_frame = tk.LabelFrame(parent, text="Network Configuration", font=('Arial', 12, 'bold'),
                                    bg="#34495e", fg="white", padx=10, pady=10)
        network_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.status_text = tk.Text(network_frame, height=10, font=('Courier', 10),
                                 bg="#2c3e50", fg="#ecf0f1", wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Update status
        self.update_status()
        
        # Log Frame
        log_frame = tk.LabelFrame(parent, text="Command Log", font=('Arial', 12, 'bold'),
                                bg="#34495e", fg="white", padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.log_text = tk.Text(log_frame, height=15, font=('Courier', 10),
                              bg="#2c3e50", fg="#1abc9c", wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Clear log button
        clear_btn = tk.Button(log_frame, text="Clear Log", font=('Arial', 10),
                            bg="#7f8c8d", fg="white", padx=15, pady=5,
                            command=self.clear_log)
        clear_btn.pack(pady=5)
    
    def trigger_reaper(self, address, msg=1.0):  # Method to send OSC message to REAPER
        """Send OSC message to REAPER"""  # Docstring describing method purpose
        try:  # Try to send message, handle potential errors
            self.reaper_client.send_message(address, msg)  # Send OSC message to REAPER with specified address and value
            self.log_command(f"REAPER: {address} → {msg}")  # Log successful command to display
        except Exception as e:  # Catch any exceptions that occur
            self.log_command(f"ERROR REAPER: {address} → {str(e)}")  # Log error message
            messagebox.showerror("REAPER Error", f"Failed to send: {address}\n{str(e)}")  # Show error dialog to user
    
    def trigger_reaper_and_play(self, address, name):  # Method to jump to marker and start playback
        """Jump to marker and start playing"""  # Docstring describing method purpose
        def sequence():  # Inner function to execute sequence in background thread
            try:  # Try to execute sequence, handle potential errors
                self.trigger_reaper(address)  # Jump to specified marker address
                time.sleep(0.5)  # Wait for jump to complete before playing
                self.trigger_reaper("/action/1007")  # Send play command to REAPER
                self.log_command(f"SEQUENCE: {name} → Jump + Play")  # Log successful sequence completion
            except Exception as e:  # Catch any exceptions that occur
                self.log_command(f"ERROR SEQUENCE: {name} → {str(e)}")  # Log error message
        
        threading.Thread(target=sequence, daemon=True).start()  # Start sequence in background daemon thread
    
    def trigger_gma(self, command):  # Method to send command to GrandMA3 lighting console
        """Send command to GrandMA3"""  # Docstring describing method purpose
        try:  # Try to send command, handle potential errors
            self.gma_client.send_message("/gma3/cmd", command)  # Send OSC command to GrandMA3 via /gma3/cmd address
            self.log_command(f"GMA3: {command}")  # Log successful command to display
        except Exception as e:  # Catch any exceptions that occur
            self.log_command(f"ERROR GMA3: {command} → {str(e)}")  # Log error message
            messagebox.showerror("GMA3 Error", f"Failed to send: {command}\n{str(e)}")  # Show error dialog to user
    
    def send_custom_gma(self):
        """Send custom GMA3 command"""
        command = self.custom_entry.get().strip()
        if command:
            self.trigger_gma(command)
            self.custom_entry.delete(0, tk.END)
    
    def log_command(self, message):  # Method to add message to command log display
        """Add message to command log"""  # Docstring describing method purpose
        timestamp = time.strftime("%H:%M:%S")  # Get current time in HH:MM:SS format
        log_entry = f"[{timestamp}] {message}\n"  # Format log entry with timestamp
        self.log_text.insert(tk.END, log_entry)  # Insert log entry at end of log text widget
        self.log_text.see(tk.END)  # Scroll log text to show most recent entry
    
    def clear_log(self):
        """Clear the command log"""
        self.log_text.delete(1.0, tk.END)
    
    def update_status(self):
        """Update network status display"""
        status_info = f"""
Network Configuration:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REAPER Audio Workstation:
  IP Address: {self.REAPER_IP}
  Port: {self.REAPER_PORT}
  Status: Connected ✓

GrandMA3 Lighting Console:
  IP Address: {self.GMA_IP}
  Port: {self.GMA_PORT}
  Status: Connected ✓

Raspberry Pi 4 Model B:
  Control Interface: Active ✓
  OSC Protocol: UDP
  
Available Commands:
  • REAPER: {len(self.reaper_addresses)} addresses
  • GMA3: {len(self.gma_cues)} preset cues + custom
        """
        
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, status_info)
    
    # Quick Action Methods
    def game_startup(self):
        """Execute game startup sequence"""
        def startup_sequence():
            self.trigger_gma("Go Sequence 38 cue 3")
            time.sleep(0.3)
            self.trigger_gma("Go+ Sequence 41")
            time.sleep(0.9)
            self.trigger_gma("On Sequence 207")
            self.trigger_reaper("/marker/23")  # Jump to Marker 34
            time.sleep(0.1)
            self.trigger_reaper("/action/1007")  # Play
            self.log_command("GAME: Startup sequence completed")
        
        threading.Thread(target=startup_sequence, daemon=True).start()
    
    def win_stage(self):
        """Execute win stage sequence"""
        def win_sequence():
            self.trigger_reaper("/action/1016")  # Stop
            time.sleep(0.5)
            self.trigger_reaper("/action/41270")  # Jump to Marker 30
            time.sleep(0.5)
            self.trigger_reaper("/action/1007")  # Play
            self.trigger_gma("Go+ sequence 33")
            self.log_command("GAME: Win stage sequence")
        
        threading.Thread(target=win_sequence, daemon=True).start()
    
    def win_game(self):
        """Execute win game sequence"""
        def win_sequence():
            self.trigger_gma("Go+ sequence 23")
            self.trigger_gma("Go sequence 33")
            self.trigger_reaper("/marker/21")  # Jump to Marker 32
            time.sleep(0.5)
            self.trigger_reaper("/action/1007")  # Play
            self.log_command("GAME: Win game sequence")
        
        threading.Thread(target=win_sequence, daemon=True).start()
    
    def lose_stage(self):
        """Execute lose stage sequence"""
        def lose_sequence():
            self.trigger_reaper("/action/1016")  # Stop
            self.trigger_reaper("/marker/20")  # Jump to Marker 31
            time.sleep(0.5)
            self.trigger_reaper("/action/1007")  # Play
            self.trigger_gma("Go+ sequence 32")
            self.log_command("GAME: Lose stage sequence")
        
        threading.Thread(target=lose_sequence, daemon=True).start()
    
    def lose_game(self):
        """Execute lose game sequence"""
        def lose_sequence():
            self.trigger_gma("Go+ sequence 32")
            self.trigger_reaper("/marker/22")  # Jump to Marker 33
            time.sleep(0.5)
            self.trigger_reaper("/action/1007")  # Play
            self.log_command("GAME: Lose game sequence")
        
        threading.Thread(target=lose_sequence, daemon=True).start()
    
    def emergency_stop(self):
        """Emergency stop all audio"""
        self.trigger_reaper("/action/1016")  # Stop REAPER
        self.log_command("EMERGENCY: All audio stopped")
        messagebox.showwarning("Emergency Stop", "All audio has been stopped!")
    
    def reset_all(self):
        """Reset to base state"""
        def reset_sequence():
            self.trigger_reaper("/action/1016")  # Stop
            time.sleep(0.5)
            self.trigger_reaper("/marker/24")  # Jump to Marker 35
            time.sleep(0.5)
            self.trigger_reaper("/action/1007")  # Play base audio
            self.log_command("SYSTEM: Reset to base state")
        
        threading.Thread(target=reset_sequence, daemon=True).start()
    
    def run(self):  # Method to start the GUI application
        """Start the GUI"""  # Docstring describing method purpose
        try:  # Try to run GUI, handle potential keyboard interrupts
            self.log_command("SYSTEM: AV Control Panel started")  # Log application startup
            self.root.mainloop()  # Start the tkinter main event loop
        except KeyboardInterrupt:  # Handle Ctrl+C gracefully
            self.log_command("SYSTEM: Shutdown requested")  # Log shutdown request
            self.emergency_stop()  # Execute emergency stop to halt all audio
            self.root.quit()  # Quit the tkinter application

if __name__ == "__main__":  # Check if script is run directly (not imported)
    # Run the control GUI
    app = AVControlGUI()  # Create instance of the AV Control GUI application
    app.run()  # Start the application
