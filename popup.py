import ctypes
import math
import tkinter as tk


class VoicePopup:
    def __init__(self, root, get_audio_level):
        self.root = root
        self.get_audio_level = get_audio_level

        self.state = "IDLE"
        self.frame = 0
        self.bars = []

        self.window = tk.Toplevel(root)
        self.window.withdraw()
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#111827")

        width, height = 230, 66
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        self.window.geometry(
            f"{width}x{height}+"
            f"{screen_width - width - 30}+"
            f"{screen_height - height - 100}"
        )

        self.status = tk.Label(
            self.window,
            text="",
            bg="#111827",
            fg="#4ADE80",
            font=("Segoe UI", 10, "bold"),
        )
        self.status.pack(pady=(7, 0))

        self.canvas = tk.Canvas(
            self.window,
            width=200,
            height=30,
            bg="#111827",
            highlightthickness=0,
        )
        self.canvas.pack()

        for i in range(25):
            x = 8 + i * 7

            bar = self.canvas.create_rectangle(
                x,
                13,
                x + 3,
                17,
                fill="#4ADE80",
                outline="",
            )

            self.bars.append(bar)

    def keep_above_without_activation(self):
        hwnd = self.window.winfo_id()

        HWND_TOPMOST = -1
        SWP_NOSIZE = 0x0001
        SWP_NOMOVE = 0x0002
        SWP_NOACTIVATE = 0x0010

        ctypes.windll.user32.SetWindowPos(
            hwnd,
            HWND_TOPMOST,
            0,
            0,
            0,
            0,
            SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE,
        )

    def set_state(self, state, message, color):
        self.state = state
        self.status.configure(text=message, fg=color)

        if state == "IDLE":
            self.window.withdraw()
            return

        self.window.deiconify()
        self.keep_above_without_activation()

        if state == "LISTENING":
            self.animate()

    def animate(self):
        if self.state != "LISTENING":
            return

        try:
            level = self.get_audio_level()
        except Exception:
            level = 0.0

        strength = min(1.0, max(0.0, level * 30))

        self.frame += 1

        for i, bar in enumerate(self.bars):
            phase = self.frame * 0.3 + i * 0.6
            movement = abs(math.sin(phase))

            height = 3 + int(17 * strength * movement)
            x = 8 + i * 7

            self.canvas.coords(
                bar,
                x,
                15 - height / 2,
                x + 3,
                15 + height / 2,
            )

        self.root.after(60, self.animate)