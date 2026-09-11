from __future__ import annotations

import os
import threading
import tkinter as tk

import pygame
import pystray
from PIL import Image
from pystray import MenuItem as item

from utils.path_utils import resource_path


class ApplicationController:
    def __init__(self, app, spawn_controller, background_window):
        self.app = app
        self.spawn_controller = spawn_controller
        self.background_window = background_window
        self.tray_icon = None
        self.cleanup_hotkey = None

    def start_app(self):
        try:
            from pynput import keyboard
            self.cleanup_hotkey = keyboard.GlobalHotKeys({
                "<ctrl>+<shift>+x": self.clear_all
            })
            self.cleanup_hotkey.start()
        except Exception as exc:
            print(f"Failed to start hotkey: {exc}")

        has_gif = bool(self.app.gif_path.get() and os.path.exists(self.app.gif_path.get()))
        has_vid = bool(self.app.vid_enable_var.get() and os.path.exists(self.app.vid_path_var.get()))
        has_bg = bool(self.app.bg_enable_var.get())
        if not has_gif and not has_vid and not has_bg:
            return

        self.app.save_settings()
        if has_gif and not self.spawn_controller.load_images():
            return

        self.app.is_active = True
        self.spawn_controller.tick_counter = 0.0
        self.spawn_controller.video_tick_counter = 0.0

        if has_bg and self.background_window.window is None:
            self.background_window.create(self.spawn_controller._runtime_config())

        self.app.root.withdraw()
        self.create_tray_icon()

    def test_run(self):
        has_gif = bool(self.app.gif_path.get() and os.path.exists(self.app.gif_path.get()))
        has_vid = bool(self.app.vid_enable_var.get() and os.path.exists(self.app.vid_path_var.get()))
        if not has_gif and not has_vid:
            return

        self.app.save_settings()
        if self.app.bg_enable_var.get() and self.background_window.window is None:
            self.background_window.create(self.spawn_controller._runtime_config())

        if has_gif and self.spawn_controller.load_images():
            self.spawn_controller.execute_spawns(is_test=True)
        if has_vid:
            self.spawn_controller.execute_video_spawns(is_test=True)

    def clear_all(self):
        for win in list(self.spawn_controller.active_windows):
            try:
                if hasattr(win, "destroy"):
                    win.destroy()
            except Exception:
                pass
        self.spawn_controller.active_windows.clear()

        for win in list(self.spawn_controller.video_windows):
            try:
                win.destroy()
            except Exception:
                pass
        self.spawn_controller.video_windows.clear()

        self.spawn_controller.active_count = 0
        self.spawn_controller.video_active_count = 0
        self.background_window.remove()
        pygame.mixer.stop()

    def show_window(self, icon=None, tray_item=None):
        self.app.is_active = False
        try:
            if self.tray_icon:
                self.tray_icon.stop()
        except Exception:
            pass
        self.background_window.remove()
        self.app.root.after(0, self.app.root.deiconify)

    def exit_app(self, icon=None, tray_item=None):
        self.exit_app_fully()

    def exit_app_fully(self):
        self.app.save_settings()
        self.background_window.remove()
        try:
            if self.tray_icon:
                self.tray_icon.stop()
        except Exception:
            pass
        try:
            if self.cleanup_hotkey:
                self.cleanup_hotkey.stop()
        except Exception:
            pass
        os._exit(0)

    def create_tray_icon(self):
        try:
            img = Image.open(resource_path("burningToast.ico")).convert("RGBA")
            img.thumbnail((64, 64))
        except Exception:
            img = Image.new("RGB", (64, 64), color=(46, 204, 113))
        menu = pystray.Menu(
            item("⚙️ ตั้งค่า (Settings)", self.show_window),
            item("🗑️ ลบรูปบนจอทั้งหมด (Clear Images)", self.clear_all),
            item("❌ ปิดโปรแกรม (Exit)", self.exit_app),
        )
        self.tray_icon = pystray.Icon("BurningToast", img, "Burning Toast", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
