from __future__ import annotations

import ctypes
import math
import os
import random
import tempfile
import threading
import time

import cv2
import pygame
import tkinter as tk
from PIL import Image, ImageTk

try:
    from moviepy import VideoFileClip, vfx
    MOVIEPY_AVAILABLE = True
except ImportError:
    try:
        from moviepy.editor import VideoFileClip, vfx
        MOVIEPY_AVAILABLE = True
    except ImportError:
        MOVIEPY_AVAILABLE = False
        print("Warning: moviepy is not installed. Video audio and speed features will not work.")


class VideoPlayer:
    """Video rendering core. It receives a plain config dictionary and never reads Tk variables."""

    def __init__(self, win, label, video_path, config, on_destroy=None):
        self.win = win
        self.label = label
        self.video_path = video_path
        self.config = dict(config)
        self.on_destroy = on_destroy
        self.target_alpha = max(0.0, min(1.0, float(self.config.get("vid_alpha", 100.0)) / 100.0))
        self.win.attributes("-alpha", 0.0)

        self.chroma_key = self.config.get("vid_chroma", "#00FF00")
        self.use_chroma = self.config.get("vid_use_chroma", True)

        self.cap = cv2.VideoCapture(self.video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        if not self.fps or self.fps <= 0 or math.isnan(self.fps):
            self.fps = 30.0
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        self.start_frame = int(float(self.config.get("vid_trim_start", 0.0)) * self.fps)
        trim_end = float(self.config.get("vid_trim_end", 0.0))
        self.end_frame = int(trim_end * self.fps) if trim_end > 0 else self.total_frames
        self.end_frame = min(self.end_frame, self.total_frames)

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
        self.current_loop = 1

        if self.use_chroma:
            try:
                self.win.wm_attributes("-transparentcolor", self.chroma_key)
                self.label.config(bg=self.chroma_key)
                self.win.config(bg=self.chroma_key)
            except tk.TclError:
                pass
        else:
            self.label.config(bg="black")
            self.win.config(bg="black")

        self.win.attributes("-alpha", self.target_alpha)

        sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
        scale = float(self.config.get("vid_scale", 100.0)) / 100.0
        orig_w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640
        orig_h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480
        if math.isnan(orig_w):
            orig_w = 640
        if math.isnan(orig_h):
            orig_h = 480
        w_img = max(1, int(orig_w * scale))
        h_img = max(1, int(orig_h * scale))

        speed = float(self.config.get("vid_move_speed", 15.0))
        active_dirs = []
        for key, direction in (
            ("vid_dir_ltr", "LTR"), ("vid_dir_rtl", "RTL"), ("vid_dir_ttb", "TTB"),
            ("vid_dir_btt", "BTT"), ("vid_dir_center", "CENTER"), ("vid_dir_custom", "CUSTOM")
        ):
            if self.config.get(key):
                active_dirs.append(direction)
        self.direction = random.choice(active_dirs) if active_dirs else "LTR"

        flip_key = {
            "LTR": "vid_flip_ltr", "RTL": "vid_flip_rtl", "TTB": "vid_flip_ttb",
            "BTT": "vid_flip_btt", "CENTER": "vid_flip_center", "CUSTOM": "vid_flip_custom"
        }[self.direction]
        self.use_flip = bool(self.config.get(flip_key, False))

        if self.direction == "LTR":
            self.x, self.y, self.dx, self.dy = -float(w_img), random.randint(50, max(51, sh - h_img - 50)), speed, 0.0
        elif self.direction == "RTL":
            self.x, self.y, self.dx, self.dy = float(sw), random.randint(50, max(51, sh - h_img - 50)), -speed, 0.0
        elif self.direction == "TTB":
            self.x, self.y, self.dx, self.dy = random.randint(50, max(51, sw - w_img - 50)), -float(h_img), 0.0, speed
        elif self.direction == "BTT":
            self.x, self.y, self.dx, self.dy = random.randint(50, max(51, sw - w_img - 50)), float(sh), 0.0, -speed
        elif self.direction == "CENTER":
            self.x, self.y, self.dx, self.dy = (sw - w_img) / 2.0, (sh - h_img) / 2.0, 0.0, 0.0
        else:
            self.x, self.y, self.dx, self.dy = float(self.config.get("vid_pos_x", 0)), float(self.config.get("vid_pos_y", 0)), 0.0, 0.0

        if self.config.get("vid_dvd_mode") and self.dx == 0 and self.dy == 0:
            self.dx = random.choice([-speed, speed])
            self.dy = random.choice([-speed, speed])

        self.win.geometry(f"+{int(self.x)}+{int(self.y)}")
        self.audio_file = None
        self.audio_channel = None
        self.is_playing = True
        self.audio_ready = False
        self.start_time = time.time()
        self.init_time = time.time()

        if MOVIEPY_AVAILABLE:
            threading.Thread(target=self.extract_and_play_audio, daemon=True).start()
        else:
            self.audio_ready = True

        self.update_frame()

    def _cleanup(self):
        self.stop()
        try:
            if self.on_destroy:
                self.on_destroy(self.win)
        finally:
            try:
                self.win.destroy()
            except Exception:
                pass

    def destroy_player(self):
        self._cleanup()

    def extract_and_play_audio(self):
        try:
            if self.config.get("vid_mute", False):
                self.start_time = time.time()
                self.audio_ready = True
                return

            clip = VideoFileClip(self.video_path)
            start_t = float(self.config.get("vid_trim_start", 0.0))
            end_t = float(self.config.get("vid_trim_end", 0.0))

            if hasattr(clip, "subclipped"):
                if end_t > 0 and end_t > start_t:
                    clip = clip.subclipped(start_t, end_t)
                elif start_t > 0:
                    clip = clip.subclipped(start_t)
            else:
                if end_t > 0 and end_t > start_t:
                    clip = clip.subclip(start_t, end_t)
                elif start_t > 0:
                    clip = clip.subclip(start_t)

            speed_mode = self.config.get("vid_speed_mode", "ทั้งคู่ (Both)")
            speed = (
                float(self.config.get("vid_playback_speed", 1.0))
                if speed_mode in ["ทั้งคู่ (Both)", "เสียง (Audio)"] else 1.0
            )
            if speed != 1.0:
                try:
                    clip = clip.fx(vfx.speedx, speed)
                except AttributeError:
                    if hasattr(clip, "multiply_speed"):
                        clip = clip.multiply_speed(speed)

            if clip.audio:
                temp_dir = tempfile.gettempdir()
                filename = f"temp_vid_{abs(hash(self.video_path))}_{time.time()}.mp3"
                self.audio_file = os.path.join(temp_dir, filename)
                clip.audio.write_audiofile(self.audio_file, logger=None)
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                sound = pygame.mixer.Sound(self.audio_file)
                sound.set_volume(max(0.0, min(1.0, float(self.config.get("vid_volume", 100.0)) / 100.0)))
                self.audio_channel = sound.play()
            clip.close()
        except Exception as exc:
            print(f"Audio extraction error: {exc}")
        finally:
            self.start_time = time.time()
            self.audio_ready = True

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

    def update_frame(self):
        if not self.is_playing:
            return
        active = self.config.get("is_active", True)
        active = active() if callable(active) else active
        if not active and not self.config.get("is_test", False):
            self.destroy_player()
            return

        if MOVIEPY_AVAILABLE and not self.audio_ready:
            self.win.after(10, self.update_frame)
            return

        if self.win.attributes("-alpha") == 0.0:
            self.win.attributes("-alpha", getattr(self, "target_alpha", 1.0))

        if not self.config.get("vid_use_video_duration", True):
            duration = float(self.config.get("vid_duration", 0.0))
            if duration > 0 and (time.time() - self.init_time) >= duration:
                self.destroy_player()
                return

        use_default_speed = self.config.get("vid_use_default_speed", True)
        speed_mode = self.config.get("vid_speed_mode", "ทั้งคู่ (Both)")
        speed_mult = float(self.config.get("vid_playback_speed", 1.0)) if speed_mode in ["ทั้งคู่ (Both)", "ภาพ (Video)"] else 1.0

        if use_default_speed:
            elapsed = (time.time() - self.start_time) * speed_mult
            target_frame = self.start_frame + int(elapsed * self.fps)
            if target_frame >= self.end_frame:
                self.current_loop += 1
                max_loops = int(self.config.get("vid_loop_count", 0))
                if max_loops > 0 and self.current_loop > max_loops:
                    self.destroy_player()
                    return
                self.start_time = time.time()
                target_frame = self.start_frame
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
                self._restart_audio()
            current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            if abs(target_frame - current_frame) > 2:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        else:
            current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            if current_frame >= self.end_frame:
                self.current_loop += 1
                max_loops = int(self.config.get("vid_loop_count", 0))
                if max_loops > 0 and self.current_loop > max_loops:
                    self.destroy_player()
                    return
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
                self._restart_audio()

        ret, frame = self.cap.read()
        if ret:
            if self.use_flip:
                frame = cv2.flip(frame, 1)

            scale = float(self.config.get("vid_scale", 100.0)) / 100.0

            if self.config.get("vid_jumpscare", False):
                mx, my = self._cursor_pos()
                cx = self.x + (frame.shape[1] * scale) / 2
                cy = self.y + (frame.shape[0] * scale) / 2
                if math.hypot(mx - cx, my - cy) < 100:
                    scale *= 3.0

            if scale != 1.0:
                frame = cv2.resize(
                    frame,
                    (max(1, int(frame.shape[1] * scale)), max(1, int(frame.shape[0] * scale))),
                    interpolation=cv2.INTER_AREA,
                )

            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)

            speed = float(self.config.get("vid_move_speed", 15.0))
            sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
            w_img, h_img = cv2image.shape[1], cv2image.shape[0]

            if self.config.get("vid_follow_mouse", False):
                mx, my = self._cursor_pos()
                cx, cy = self.x + w_img / 2, self.y + h_img / 2
                dist = math.hypot(mx - cx, my - cy)
                if dist > 0:
                    self.dx = ((mx - cx) / dist) * speed
                    self.dy = ((my - cy) / dist) * speed

            if self.config.get("vid_drunk", False):
                self.dy += math.sin(time.time() * 8.0) * 4.0

            if self.config.get("vid_runaway", False):
                mx, my = self._cursor_pos()
                cx, cy = self.x + w_img / 2, self.y + h_img / 2
                dist = math.hypot(mx - cx, my - cy)
                if 0 < dist < 150:
                    self.dx = ((cx - mx) / dist) * (speed * 4)
                    self.dy = ((cy - my) / dist) * (speed * 4)

            if self.config.get("vid_gravity_mode", False):
                self.dy += 0.5

            next_x, next_y = self.x + self.dx, self.y + self.dy

            if self.config.get("vid_dvd_mode", False):
                if next_x <= 0 or next_x + w_img >= sw:
                    self.dx = -self.dx
                    next_x = max(0, min(sw - w_img, next_x))
                if next_y <= 0 or next_y + h_img >= sh:
                    if self.config.get("vid_gravity_mode", False) and next_y + h_img >= sh:
                        self.dy = -self.dy * 0.7
                        if abs(self.dy) < 1.0:
                            self.dy = 0
                    else:
                        self.dy = -self.dy
                    next_y = max(0, min(sh - h_img, next_y))
            else:
                if self.config.get("vid_gravity_mode", False) and next_y + h_img >= sh:
                    self.dy = -self.dy * 0.7
                    next_y = sh - h_img
                    if abs(self.dy) < 1.0:
                        self.dy = 0

            if not self.config.get("vid_dvd_mode", False):
                if self.direction == "LTR" and next_x > sw:
                    self.destroy_player(); return
                if self.direction == "RTL" and next_x < -w_img:
                    self.destroy_player(); return
                if self.direction == "TTB" and next_y > sh:
                    self.destroy_player(); return
                if self.direction == "BTT" and next_y < -h_img:
                    self.destroy_player(); return

            self.x, self.y = next_x, next_y
            self.win.geometry(f"+{int(self.x)}+{int(self.y)}")

        base_delay_ms = (1000 / self.fps) if use_default_speed else float(self.config.get("vid_speed", 33.0))
        delay_ms = max(1, int(base_delay_ms / speed_mult))
        self.win.after(delay_ms, self.update_frame)

    def _restart_audio(self):
        if self.audio_channel and self.audio_file:
            try:
                self.audio_channel.stop()
                sound = pygame.mixer.Sound(self.audio_file)
                sound.set_volume(max(0.0, min(1.0, float(self.config.get("vid_volume", 100.0)) / 100.0)))
                self.audio_channel = sound.play()
            except Exception:
                pass

    def stop(self):
        self.is_playing = False
        try:
            if self.cap.isOpened():
                self.cap.release()
        except Exception:
            pass
        if self.audio_channel:
            try:
                self.audio_channel.stop()
            except Exception:
                pass
        if self.audio_file and os.path.exists(self.audio_file):
            try:
                os.remove(self.audio_file)
            except Exception:
                pass

    def restart_video(self):
        self.start_time = time.time()
        self.init_time = time.time()
        self.current_loop = 1
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
        self._restart_audio()
