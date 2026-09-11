from __future__ import annotations

import ctypes
import math
import os
import random
import time
import glob
import tkinter as tk
import pygame


class ImageAnimator:
    def __init__(self, root, media_cache, config, on_destroy=None, background_callback=None):
        self.root = root
        self.media_cache = media_cache
        self.config = config
        self.on_destroy = on_destroy
        self.background_callback = background_callback
        self.window = None
        self.channel = None
        self._destroyed = False

    @staticmethod
    def _cursor_pos():
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        pt = POINT()
        try:
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
            return pt.x, pt.y
        except Exception:
            return 0, 0

    def _cleanup(self):
        if self._destroyed:
            return
        self._destroyed = True
        try:
            if self.config.get("stop_sound", True) and self.channel is not None:
                if self.channel.get_busy():
                    self.channel.fadeout(max(0, int(self.config.get("audio_fade_out", 300))))
        except Exception:
            pass
        if self.window is not None:
            try:
                self.window.destroy()
            except Exception:
                pass
        if self.on_destroy:
            self.on_destroy(self.window)

    def start(self, is_test=False):
        if not self.media_cache:
            if self.on_destroy:
                self.on_destroy(None)
            return

        if self.config.get("bg_enable") and self.background_callback:
            self.background_callback()

        media = random.choice(self.media_cache)
        cached_normal, cached_flipped, gif_default_delay = (
            media["normal"], media["flipped"], media["delay"]
        )

        s_path = self.config.get("sound_path", "")
        if s_path and os.path.exists(s_path):
            chosen_snd = None
            if os.path.isdir(s_path):
                s_files = []
                for ext in ("*.mp3", "*.wav", "*.ogg"):
                    s_files.extend(glob.glob(os.path.join(s_path, ext)))
                if s_files:
                    chosen_snd = random.choice(s_files)
            else:
                chosen_snd = s_path

            if chosen_snd:
                try:
                    vol = max(0.0, min(1.0, float(self.config.get("volume", 100.0)) / 100.0))
                    snd = pygame.mixer.Sound(chosen_snd)
                    snd.set_volume(vol)
                    self.channel = snd.play(
                        fade_ms=max(0, int(self.config.get("audio_fade_in", 0)))
                    )
                except Exception:
                    pass

        win = tk.Toplevel(self.root)
        self.window = win
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.config(bg="#f0f0f0")
        win.attributes("-alpha", max(0.0, min(1.0, self.config.get("alpha", 100.0) / 100.0)))
        try:
            win.wm_attributes("-transparentcolor", "#f0f0f0")
        except tk.TclError:
            pass

        win.update()
        try:
            hwnd = ctypes.windll.user32.GetParent(win.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x08080020)
        except Exception:
            pass

        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        speed = float(self.config.get("speed", 15.0))
        delay_ms = (
            max(35, int(gif_default_delay))
            if self.config.get("use_default_delay", False)
            else max(35, int(self.config.get("frame_delay", 30.0)))
        )

        active_dirs = []
        for key, direction in (
            ("dir_ltr", "LTR"), ("dir_rtl", "RTL"), ("dir_ttb", "TTB"),
            ("dir_btt", "BTT"), ("dir_center", "CENTER"), ("dir_custom", "CUSTOM")
        ):
            if self.config.get(key):
                active_dirs.append(direction)

        direction = random.choice(active_dirs) if active_dirs else "LTR"
        flip_key = {
            "LTR": "flip_ltr", "RTL": "flip_rtl", "TTB": "flip_ttb",
            "BTT": "flip_btt", "CENTER": "flip_center", "CUSTOM": "flip_custom"
        }[direction]
        frames = cached_flipped if self.config.get(flip_key, False) else cached_normal

        label = tk.Label(win, bg="#f0f0f0")
        label.pack()
        w_img, h_img = frames[0].width(), frames[0].height()

        if direction == "LTR":
            x, y, dx, dy = -w_img, random.randint(50, max(51, sh - h_img - 50)), speed, 0.0
        elif direction == "RTL":
            x, y, dx, dy = sw, random.randint(50, max(51, sh - h_img - 50)), -speed, 0.0
        elif direction == "TTB":
            x, y, dx, dy = random.randint(50, max(51, sw - w_img - 50)), -h_img, 0.0, speed
        elif direction == "BTT":
            x, y, dx, dy = random.randint(50, max(51, sw - w_img - 50)), sh, 0.0, -speed
        elif direction == "CENTER":
            x, y, dx, dy = (sw - w_img) / 2.0, (sh - h_img) / 2.0, 0.0, 0.0
        else:
            x, y, dx, dy = self.config.get("custom_x", 100), self.config.get("custom_y", 100), 0.0, 0.0

        if self.config.get("dvd_mode") and dx == 0 and dy == 0:
            dx, dy = random.choice([-speed, speed]), random.choice([-speed, speed])

        frame_idx, time_timer = 0, 0

        def animate():
            nonlocal x, y, dx, dy, frame_idx, time_timer
            if self._destroyed:
                return
            active = self.config.get("is_active", True)
            active = active() if callable(active) else active
            if not active and not is_test:
                self._cleanup()
                return

            out_of_bounds = False
            time_timer += 1

            if self.config.get("follow_mouse"):
                mx, my = self._cursor_pos()
                cx, cy = x + w_img / 2, y + h_img / 2
                vec_x, vec_y = mx - cx, my - cy
                dist = math.hypot(vec_x, vec_y)
                if dist > 0:
                    dx, dy = (vec_x / dist) * speed, (vec_y / dist) * speed

            if self.config.get("gravity_mode"):
                dy += 0.5

            next_x, next_y = x + dx, y + dy

            if self.config.get("dvd_mode"):
                if next_x <= 0 or next_x + w_img >= sw:
                    dx = -dx
                    next_x = max(0, min(sw - w_img, next_x))
                if next_y <= 0 or next_y + h_img >= sh:
                    if self.config.get("gravity_mode") and next_y + h_img >= sh:
                        dy = -dy * 0.7
                        if abs(dy) < 1.0:
                            dy = 0
                    else:
                        dy = -dy
                    next_y = max(0, min(sh - h_img, next_y))
            else:
                if self.config.get("gravity_mode") and next_y + h_img >= sh:
                    dy = -dy * 0.7
                    next_y = sh - h_img
                    if abs(dy) < 1.0:
                        dy = 0

            x, y = next_x, next_y

            if self.config.get("end_on_loop"):
                if frame_idx == len(frames) - 1 and time_timer >= len(frames):
                    out_of_bounds = True
            elif self.config.get("use_duration") or (
                direction in ("CENTER", "CUSTOM")
                and not self.config.get("dvd_mode")
                and not self.config.get("follow_mouse")
            ):
                dur = float(self.config.get("all_duration", 3.0)) if self.config.get("use_duration") else 3.0
                if time_timer > int((dur * 1000) / delay_ms):
                    out_of_bounds = True
            elif not self.config.get("dvd_mode"):
                if direction == "LTR" and x > sw:
                    out_of_bounds = True
                elif direction == "RTL" and x < -w_img:
                    out_of_bounds = True
                elif direction == "TTB" and y > sh:
                    out_of_bounds = True
                elif direction == "BTT" and y < -h_img:
                    out_of_bounds = True

            if not out_of_bounds:
                win.geometry(f"+{int(x)}+{int(y)}")
                label.config(image=frames[frame_idx])
                frame_idx = (frame_idx + 1) % len(frames)
                win.after(delay_ms, animate)
            else:
                self._cleanup()

        animate()
