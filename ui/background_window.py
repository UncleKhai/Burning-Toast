from __future__ import annotations

import ctypes
import os
import tkinter as tk
from PIL import Image, ImageTk


class BackgroundWindow:
    def __init__(self, root):
        self.root = root
        self.window = None
        self.tk_img = None

    def create(self, config):
        if self.window is not None:
            return
        self.window = tk.Toplevel(self.root)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)

        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        self.window.geometry(f"{sw}x{sh}+0+0")
        self.window.attributes("-alpha", max(0.0, min(1.0, float(config.get("bg_alpha", 50.0)) / 100.0)))
        self.window.update()

        try:
            hwnd = ctypes.windll.user32.GetParent(self.window.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x08080020)
        except Exception:
            pass

        canvas = tk.Canvas(self.window, width=sw, height=sh, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        if config.get("bg_type", "color") == "color":
            canvas.config(bg=config.get("bg_color", "#000000"))
        else:
            path = config.get("bg_image_path", "")
            if path and os.path.exists(path):
                img = Image.open(path).resize((sw, sh))
                self.tk_img = ImageTk.PhotoImage(img)
                canvas.create_image(0, 0, image=self.tk_img, anchor="nw")
            else:
                canvas.config(bg="#000000")

        overlay_text = config.get("bg_text", "")
        if overlay_text.strip():
            y_pos = 100 if config.get("bg_text_pos", "top") == "top" else sh - 100
            canvas.create_text(
                sw / 2, y_pos, text=overlay_text, fill="white",
                font=("Tahoma", 40, "bold"), anchor="center"
            )

        if config.get("bg_layer") == "บังทุกอย่าง (Foreground)":
            self.window.attributes("-topmost", True)
        else:
            self.window.attributes("-topmost", False)
            self.window.lower()

    def remove(self):
        if self.window is not None:
            try:
                self.window.destroy()
            except Exception:
                pass
            self.window = None
