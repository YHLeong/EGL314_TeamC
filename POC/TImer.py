import tkinter as tk
import time
import threading

# Timer durations in seconds
DURATIONS = {
    "30s": 30,
    "1min": 60,
    "1min 30s": 90
}

class CountdownTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Selectable Timer")
        
        self.time_left = 0
        self.running = False

        self.label = tk.Label(root, text="Select a timer duration", font=("Arial", 24))
        self.label.pack(pady=20)

        self.time_display = tk.Label(root, text="", font=("Arial", 32), fg="blue")
        self.time_display.pack()

        # Buttons
        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.pack(pady=10)

        for name, seconds in DURATIONS.items():
            btn = tk.Button(self.buttons_frame, text=name, width=10, font=("Arial", 14),
                            command=lambda s=seconds: self.start_timer(s))
            btn.pack(side=tk.LEFT, padx=5)

    def start_timer(self, duration):
        if self.running:
            return  # Ignore if timer is already running
        self.time_left = duration
        self.running = True
        threading.Thread(target=self.run_timer, daemon=True).start()

    def run_timer(self):
        while self.time_left > 0 and self.running:
            mins, secs = divmod(self.time_left, 60)
            time_str = f"{mins:02d}:{secs:02d}"
            self.time_display.config(text=time_str)
            time.sleep(1)
            self.time_left -= 1
        if self.running:
            self.time_display.config(text="Time's up!", fg="red")
        self.running = False

if __name__ == "__main__":
    root = tk.Tk()
    timer = CountdownTimer(root)
    root.mainloop()