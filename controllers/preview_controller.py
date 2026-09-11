from __future__ import annotations

import glob
import os

import cv2
from PIL import Image, ImageTk, ImageOps, ImageSequence


class PreviewController:
    def __init__(self, app):
        self.app = app
        self.vid_cap = None

    def update_image_preview(self, *args):
        path = self.app.gif_path.get()
        if not path or not os.path.exists(path):
            return

        target_file = path
        if os.path.isdir(path):
            target_file = None
            for ext in ("*.gif", "*.png", "*.jpg", "*.jpeg"):
                files = glob.glob(os.path.join(path, ext))
                if files:
                    target_file = files[0]
                    break
        if not target_file:
            return

        try:
            img = Image.open(target_file)
            self.app.preview_all_frames = []
            zoom = self.app.preview_zoom_var.get() / 100.0
            resample = getattr(Image, "Resampling", Image).LANCZOS
            for frame in ImageSequence.Iterator(img):
                f = frame.convert("RGBA")
                if self.app.manual_flip_var.get():
                    f = ImageOps.mirror(f)
                f = f.resize(
                    (max(1, int(f.width * zoom)), max(1, int(f.height * zoom))),
                    resample
                )
                self.app.preview_all_frames.append(f)

            if self.app.preview_all_frames:
                self.app.frame_slider.config(to=len(self.app.preview_all_frames) - 1)
                self.app.preview_frame_var.set(0)
                self.change_image_frame(0)
        except Exception:
            pass

    def change_image_frame(self, value):
        if self.app.preview_all_frames:
            idx = int(self.app.preview_frame_var.get())
            if idx < len(self.app.preview_all_frames):
                self.app.preview_tk = ImageTk.PhotoImage(self.app.preview_all_frames[idx])
                self.app.preview_canvas.delete("all")
                self.app.preview_canvas.create_image(0, 0, image=self.app.preview_tk, anchor="nw")
                self.app.preview_canvas.config(scrollregion=self.app.preview_canvas.bbox("all"))

    def update_video_preview(self, *args):
        path = self.app.vid_path_var.get()
        if not path or not os.path.exists(path):
            return

        target_file = path
        if os.path.isdir(path):
            target_file = None
            for ext in ("*.mp4", "*.avi", "*.mov", "*.mkv", "*.webm"):
                files = glob.glob(os.path.join(path, ext))
                if files:
                    target_file = files[0]
                    break
        if not target_file:
            return

        try:
            if self.vid_cap is not None:
                self.vid_cap.release()
            self.vid_cap = cv2.VideoCapture(target_file)
            total = int(self.vid_cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.app.vid_frame_slider.config(to=max(0, total - 1))
            self.app.vid_preview_frame_var.set(0)
            self.change_video_frame(0)
        except Exception:
            pass

    def change_video_frame(self, value):
        if self.vid_cap is None or not self.vid_cap.isOpened():
            return
        try:
            frame_idx = int(float(value))
            self.vid_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = self.vid_cap.read()
            if not ret:
                return
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            h = 150
            w = int((h / img.height) * img.width)
            img = img.resize((max(1, w), h), getattr(Image, "Resampling", Image).LANCZOS)
            self.app.vid_preview_tk = ImageTk.PhotoImage(img)
            self.app.vid_preview_canvas.delete("all")
            self.app.vid_preview_canvas.create_image(0, 0, image=self.app.vid_preview_tk, anchor="nw")
            self.app.vid_preview_canvas.config(scrollregion=self.app.vid_preview_canvas.bbox("all"))
        except Exception:
            pass
