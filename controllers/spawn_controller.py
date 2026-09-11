from __future__ import annotations

import glob
import os
import random
import time
import tkinter as tk

from core.image_animator import ImageAnimator
from core.video_player import VideoPlayer


class SpawnController:
    def __init__(self, app, image_loader, background_window):
        self.app = app
        self.root = app.root
        self.image_loader = image_loader
        self.background_window = background_window
        self.active_windows = []
        self.video_windows = []
        self.active_count = 0
        self.video_active_count = 0
        self.last_trigger_time = 0.0
        self.video_last_trigger_time = 0.0
        self.tick_counter = 0.0
        self.video_tick_counter = 0.0

    def config(self):
        return self.app.get_settings_data()

    def _runtime_config(self):
        data = self.config()
        data["is_active"] = lambda: self.app.is_active
        data["vid_jumpscare"] = self.app.vid_jumpscare_var.get()
        data["vid_drunk"] = self.app.vid_drunk_var.get()
        data["vid_runaway"] = self.app.vid_runaway_var.get()
        data["bg_layer"] = self.app.bg_layer_var.get()
        return data

    def _on_image_destroy(self, win):
        if win in self.active_windows:
            self.active_windows.remove(win)
        self.active_count = max(0, self.active_count - 1)
        if self.active_count == 0:
            self.background_window.remove()

    def _background_callback(self):
        cfg = self._runtime_config()
        if cfg.get("bg_enable") and self.background_window.window is None:
            self.background_window.create(cfg)

    def _on_video_destroy(self, win):
        if win in self.video_windows:
            self.video_windows.remove(win)
        self.video_active_count = max(0, self.video_active_count - 1)

    def load_images(self):
        return self.image_loader.load_and_cache(
            self.app.gif_path.get(),
            self.app.scale_var.get(),
            self.app.manual_flip_var.get(),
        )

    def execute_spawns(self, is_test=False):
        spawn_count = 1
        if self.app.multi_spawn_var.get():
            min_c = max(1, self.app.multi_spawn_min_var.get())
            max_c = max(min_c, self.app.multi_spawn_max_var.get())
            spawn_count = random.randint(min_c, max_c)

        for _ in range(spawn_count):
            if self.active_count < self.app.max_instances_var.get():
                self.active_count += 1
                self.root.after(0, lambda test=is_test: self.spawn_image(test))

    def spawn_image(self, is_test=False):
        if not self.image_loader.cached_media:
            self.active_count = max(0, self.active_count - 1)
            return

        config = self._runtime_config()
        animator = ImageAnimator(
            self.root, self.image_loader.cached_media, config,
            on_destroy=self._on_image_destroy,
            background_callback=self._background_callback,
        )
        animator.start(is_test=is_test)
        self.active_windows.append(animator.window)

    @staticmethod
    def _choose_video_file(source):
        if not source or not os.path.exists(source):
            return None
        if not os.path.isdir(source):
            return source
        files = []
        for ext in ("*.mp4", "*.avi", "*.mov", "*.mkv", "*.webm"):
            files.extend(glob.glob(os.path.join(source, ext)))
        return random.choice(files) if files else None

    def execute_video_spawns(self, is_test=False):
        spawn_count = 1
        if self.app.vid_multi_spawn_var.get():
            min_c = max(1, self.app.vid_multi_spawn_min_var.get())
            max_c = max(min_c, self.app.vid_multi_spawn_max_var.get())
            spawn_count = random.randint(min_c, max_c)

        for _ in range(spawn_count):
            if self.video_active_count < self.app.vid_max_instances_var.get():
                self.video_active_count += 1
                self.root.after(0, lambda test=is_test: self.spawn_video(test))
            elif self.app.vid_replay_on_trigger_var.get() and self.video_windows:
                win = self.video_windows[0]
                vp = getattr(win, "vp", None)
                if vp:
                    self.root.after(0, vp.restart_video)

    def spawn_video(self, is_test=False):
        if not self.app.vid_enable_var.get():
            self.video_active_count = max(0, self.video_active_count - 1)
            return

        target_file = self._choose_video_file(self.app.vid_path_var.get())
        if not target_file:
            self.video_active_count = max(0, self.video_active_count - 1)
            return

        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        label = tk.Label(win)
        label.pack()

        video_config = self._runtime_config()
        video_config["is_test"] = is_test
        vp = VideoPlayer(
            win, label, target_file, video_config,
            on_destroy=self._on_video_destroy,
        )
        win.vp = vp
        win.update()

        try:
            import ctypes
            hwnd = ctypes.windll.user32.GetParent(win.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style | 0x08080020)
        except Exception:
            pass

        self.video_windows.append(win)

    def check_image_trigger(self):
        if not self.app.is_active or self.active_count >= self.app.max_instances_var.get():
            return
        now = time.time()
        if now - self.last_trigger_time < self.app.trigger_cooldown_var.get():
            return
        if random.random() < float(self.app.chance_var.get()) / 100.0:
            self.last_trigger_time = now
            delay = self.app.trigger_delay_var.get()
            if delay > 0:
                self.root.after(int(delay * 1000), lambda: self.execute_spawns(False))
            else:
                self.execute_spawns(False)

    def check_video_trigger(self):
        if not self.app.is_active or self.video_active_count >= self.app.vid_max_instances_var.get():
            return
        now = time.time()
        if now - self.video_last_trigger_time < self.app.vid_trigger_cooldown_var.get():
            return
        if random.random() < float(self.app.vid_chance_var.get()) / 100.0:
            self.video_last_trigger_time = now
            delay = self.app.vid_trigger_delay_var.get()
            if delay > 0:
                self.root.after(int(delay * 1000), lambda: self.execute_video_spawns(False))
            else:
                self.execute_video_spawns(False)

    def handle_input(self, input_type, key_or_btn=""):
        if not self.app.is_active:
            return

        mouse_map = {
            "คลิกซ้าย": "Left Click", "Left Click": "คลิกซ้าย",
            "คลิกขวา": "Right Click", "Right Click": "คลิกขวา",
            "คลิกกลาง": "Middle Click", "Middle Click": "คลิกกลาง",
            "ทั้งหมด": "All", "All": "ทั้งหมด",
        }

        if self.app.enable_trigger_var.get():
            act = self.app.action_var.get()
            ok = False
            if input_type == "keyboard" and act in ["กดคีย์บอร์ดเท่านั้น", "Keyboard Only", "ทั้งหมด", "All"]:
                req = self.app.specific_key_var.get().strip().lower()
                ok = not req or key_or_btn == req
            elif input_type == "mouse" and act in ["คลิกเมาส์เท่านั้น", "Mouse Only", "ทั้งหมด", "All"]:
                req = self.app.specific_mouse_var.get()
                ok = req in ["ทั้งหมด", "All"] or key_or_btn == req or key_or_btn == mouse_map.get(req)
            if ok:
                self.check_image_trigger()

        if self.app.vid_enable_var.get() and self.app.vid_enable_trigger_var.get():
            act = self.app.vid_action_var.get()
            ok = False
            if input_type == "keyboard" and act in ["กดคีย์บอร์ดเท่านั้น", "Keyboard Only", "ทั้งหมด", "All"]:
                req = self.app.vid_specific_key_var.get().strip().lower()
                ok = not req or key_or_btn == req
            elif input_type == "mouse" and act in ["คลิกเมาส์เท่านั้น", "Mouse Only", "ทั้งหมด", "All"]:
                req = self.app.vid_specific_mouse_var.get()
                ok = req in ["ทั้งหมด", "All"] or key_or_btn == req or key_or_btn == mouse_map.get(req)
            if ok:
                self.check_video_trigger()

    def tick(self):
        try:
            if self.app.is_active:
                if self.app.auto_time_var.get():
                    interval = max(0.1, float(
                        self.app.auto_hr_var.get() * 3600
                        + self.app.auto_min_var.get() * 60
                        + self.app.auto_sec_var.get()
                    ))
                    self.tick_counter += 0.1
                    if self.tick_counter >= interval:
                        self.tick_counter = 0.0
                        if random.random() < float(self.app.auto_chance_var.get()) / 100.0:
                            delay = self.app.auto_delay_var.get()
                            if delay > 0:
                                self.root.after(int(delay * 1000), lambda: self.execute_spawns(False))
                            else:
                                self.execute_spawns(False)

                if self.app.vid_enable_var.get() and self.app.vid_auto_time_var.get():
                    interval = max(0.1, float(
                        self.app.vid_auto_hr_var.get() * 3600
                        + self.app.vid_auto_min_var.get() * 60
                        + self.app.vid_auto_sec_var.get()
                    ))
                    self.video_tick_counter += 0.1
                    if self.video_tick_counter >= interval:
                        self.video_tick_counter = 0.0
                        if random.random() < float(self.app.vid_auto_chance_var.get()) / 100.0:
                            delay = self.app.vid_auto_delay_var.get()
                            if delay > 0:
                                self.root.after(int(delay * 1000), lambda: self.execute_video_spawns(False))
                            else:
                                self.execute_video_spawns(False)
        except Exception:
            pass
        finally:
            self.root.after(100, self.tick)
