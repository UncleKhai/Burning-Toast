from __future__ import annotations

import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, ttk
import pygame

try:
    from tkinterdnd2 import TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    print("Warning: tkinterdnd2 is not installed. Drag & Drop will be disabled.")

from utils.config_manager import ConfigManager
from utils.i18n import I18n
from utils.path_utils import resource_path
from ui.theme import Theme
from ui.background_window import BackgroundWindow
from tabs.tab_image import ImageTab
from tabs.tab_video import VideoTab
from tabs.tab_background import BackgroundTab
from core.image_loader import ImageLoader
from controllers.preview_controller import PreviewController
from controllers.spawn_controller import SpawnController
from controllers.input_controller import InputController
from controllers.application_controller import ApplicationController


class OverlayApp:
    """UI coordinator/state holder. Business logic lives in controllers/core modules."""

    def __init__(self):
        try:
            pygame.mixer.init()
        except Exception as exc:
            print(f"Audio system warning: {exc}")

        self.root = TkinterDnD.Tk() if DND_AVAILABLE else tk.Tk()
        self.root.title("🍞 Burning Toast")

        window_w, window_h = 620, 700
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(
            f"{window_w}x{window_h}+{int(sw/2-window_w/2)}+{int(sh/2-window_h/2)}"
        )

        self.t_bg = Theme.BG
        self.t_frame = Theme.FRAME
        self.t_text = Theme.TEXT
        self.t_btn = Theme.BUTTON
        self.t_btn_hover = Theme.BUTTON_HOVER
        self.root.configure(bg=self.t_bg)

        self.settings_file = "skeleton_settings.json"
        icon_path = resource_path("burningToast.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception as exc:
                print(f"Icon load error: {exc}")

        self.lang_var = tk.StringVar(value="TH")
        self.i18n = I18n("TH")
        self._create_variables()

        self.config_manager = ConfigManager(self.settings_file)
        self.apply_settings(self.config_manager.load_settings())

        self.image_loader = ImageLoader()
        self.background_window = BackgroundWindow(self.root)
        self.preview_controller = PreviewController(self)
        self.spawn_controller = SpawnController(self, self.image_loader, self.background_window)
        self.input_controller = InputController(self.root, self.spawn_controller.handle_input)
        self.application_controller = ApplicationController(
            self, self.spawn_controller, self.background_window
        )

        self.build_ui()
        self.input_controller.start()
        self.tick_loop()

        if self.gif_path.get():
            self.update_preview()
        if self.vid_path_var.get():
            self.update_vid_preview()

    def _create_variables(self):
        self.gif_path = tk.StringVar()
        self.sound_path = tk.StringVar()
        self.scale_var = tk.DoubleVar(value=100.0)
        self.alpha_var = tk.DoubleVar(value=100.0)
        self.volume_var = tk.DoubleVar(value=100.0)
        self.frame_delay_var = tk.DoubleVar(value=30.0)
        self.use_default_delay_var = tk.BooleanVar(value=False)
        self.speed_var = tk.DoubleVar(value=15.0)
        self.manual_flip_var = tk.BooleanVar(value=False)
        self.preview_zoom_var = tk.DoubleVar(value=100.0)
        self.stop_sound_var = tk.BooleanVar(value=True)
        self.audio_fade_in_var = tk.IntVar(value=0)
        self.audio_fade_out_var = tk.IntVar(value=300)

        self.dir_ltr_var = tk.BooleanVar(value=True)
        self.flip_ltr_var = tk.BooleanVar(value=False)
        self.dir_rtl_var = tk.BooleanVar(value=False)
        self.flip_rtl_var = tk.BooleanVar(value=True)
        self.dir_ttb_var = tk.BooleanVar(value=False)
        self.flip_ttb_var = tk.BooleanVar(value=False)
        self.dir_btt_var = tk.BooleanVar(value=False)
        self.flip_btt_var = tk.BooleanVar(value=False)
        self.dir_center_var = tk.BooleanVar(value=False)
        self.flip_center_var = tk.BooleanVar(value=False)
        self.dir_custom_var = tk.BooleanVar(value=False)
        self.flip_custom_var = tk.BooleanVar(value=False)
        self.custom_x_var = tk.IntVar(value=100)
        self.custom_y_var = tk.IntVar(value=100)
        self.dvd_mode_var = tk.BooleanVar(value=False)
        self.follow_mouse_var = tk.BooleanVar(value=False)
        self.gravity_mode_var = tk.BooleanVar(value=False)
        self.use_duration_var = tk.BooleanVar(value=False)
        self.all_duration_var = tk.DoubleVar(value=3.0)
        self.end_on_loop_var = tk.BooleanVar(value=False)

        self.enable_trigger_var = tk.BooleanVar(value=True)
        self.action_var = tk.StringVar(value="ทั้งหมด")
        self.specific_key_var = tk.StringVar(value="")
        self.specific_mouse_var = tk.StringVar(value="ทั้งหมด")
        self.chance_var = tk.DoubleVar(value=10.0)
        self.max_instances_var = tk.IntVar(value=3)
        self.trigger_cooldown_var = tk.DoubleVar(value=0.0)
        self.trigger_delay_var = tk.DoubleVar(value=0.0)
        self.multi_spawn_var = tk.BooleanVar(value=False)
        self.multi_spawn_min_var = tk.IntVar(value=1)
        self.multi_spawn_max_var = tk.IntVar(value=3)

        self.auto_time_var = tk.BooleanVar(value=False)
        self.auto_hr_var = tk.IntVar(value=0)
        self.auto_min_var = tk.IntVar(value=0)
        self.auto_sec_var = tk.DoubleVar(value=5.0)
        self.auto_chance_var = tk.DoubleVar(value=100.0)
        self.auto_delay_var = tk.DoubleVar(value=0.0)

        self.bg_enable_var = tk.BooleanVar(value=False)
        self.bg_layer_var = tk.StringVar(value="อยู่หลังสุด (Background)")
        self.bg_type_var = tk.StringVar(value="color")
        self.bg_color_var = tk.StringVar(value="#000000")
        self.bg_image_path_var = tk.StringVar(value="")
        self.bg_alpha_var = tk.DoubleVar(value=50.0)
        self.bg_text_var = tk.StringVar(value="")
        self.bg_text_pos_var = tk.StringVar(value="top")

        self.vid_enable_var = tk.BooleanVar(value=False)
        self.vid_path_var = tk.StringVar(value="")
        self.vid_use_chroma_var = tk.BooleanVar(value=True)
        self.vid_use_default_speed_var = tk.BooleanVar(value=True)
        self.vid_chroma_var = tk.StringVar(value="#00FF00")
        self.vid_volume_var = tk.DoubleVar(value=100.0)
        self.vid_speed_var = tk.DoubleVar(value=33.0)
        self.vid_duration_var = tk.DoubleVar(value=0.0)
        self.vid_scale_var = tk.DoubleVar(value=100.0)
        self.vid_alpha_var = tk.DoubleVar(value=100.0)
        self.vid_pos_x_var = tk.IntVar(value=0)
        self.vid_pos_y_var = tk.IntVar(value=0)
        self.vid_move_speed_var = tk.DoubleVar(value=15.0)
        self.vid_dvd_mode_var = tk.BooleanVar(value=False)
        self.vid_gravity_mode_var = tk.BooleanVar(value=False)
        self.vid_follow_mouse_var = tk.BooleanVar(value=False)
        self.vid_dir_ltr_var = tk.BooleanVar(value=True)
        self.vid_flip_ltr_var = tk.BooleanVar(value=False)
        self.vid_dir_rtl_var = tk.BooleanVar(value=False)
        self.vid_flip_rtl_var = tk.BooleanVar(value=True)
        self.vid_dir_ttb_var = tk.BooleanVar(value=False)
        self.vid_flip_ttb_var = tk.BooleanVar(value=False)
        self.vid_dir_btt_var = tk.BooleanVar(value=False)
        self.vid_flip_btt_var = tk.BooleanVar(value=False)
        self.vid_dir_center_var = tk.BooleanVar(value=False)
        self.vid_flip_center_var = tk.BooleanVar(value=False)
        self.vid_dir_custom_var = tk.BooleanVar(value=False)
        self.vid_flip_custom_var = tk.BooleanVar(value=False)

        self.vid_enable_trigger_var = tk.BooleanVar(value=False)
        self.vid_action_var = tk.StringVar(value="ทั้งหมด")
        self.vid_specific_key_var = tk.StringVar(value="")
        self.vid_specific_mouse_var = tk.StringVar(value="ทั้งหมด")
        self.vid_chance_var = tk.DoubleVar(value=10.0)
        self.vid_max_instances_var = tk.IntVar(value=1)
        self.vid_trigger_cooldown_var = tk.DoubleVar(value=0.0)
        self.vid_trigger_delay_var = tk.DoubleVar(value=0.0)
        self.vid_multi_spawn_var = tk.BooleanVar(value=False)
        self.vid_multi_spawn_min_var = tk.IntVar(value=1)
        self.vid_multi_spawn_max_var = tk.IntVar(value=1)

        self.vid_auto_time_var = tk.BooleanVar(value=False)
        self.vid_auto_hr_var = tk.IntVar(value=0)
        self.vid_auto_min_var = tk.IntVar(value=0)
        self.vid_auto_sec_var = tk.DoubleVar(value=5.0)
        self.vid_auto_chance_var = tk.DoubleVar(value=100.0)
        self.vid_auto_delay_var = tk.DoubleVar(value=0.0)

        self.vid_use_video_duration_var = tk.BooleanVar(value=True)
        self.vid_loop_count_var = tk.IntVar(value=0)
        self.vid_replay_on_trigger_var = tk.BooleanVar(value=False)
        self.vid_trim_start_var = tk.DoubleVar(value=0.0)
        self.vid_trim_end_var = tk.DoubleVar(value=0.0)
        self.vid_playback_speed_var = tk.DoubleVar(value=1.0)
        self.vid_speed_mode_var = tk.StringVar(value="ทั้งคู่ (Both)")
        self.vid_mute_var = tk.BooleanVar(value=False)

        # Video-only chaotic effects were not serialized in the original file.
        self.vid_jumpscare_var = tk.BooleanVar(value=False)
        self.vid_drunk_var = tk.BooleanVar(value=False)
        self.vid_runaway_var = tk.BooleanVar(value=False)

        self.preview_frame_var = tk.IntVar(value=0)
        self.preview_all_frames = []
        self.preview_tk = None
        self.vid_preview_frame_var = tk.DoubleVar(value=0.0)
        self.vid_preview_tk = None
        self.is_active = False
        self.test_menu = None
        self.btn_test = None

    def _var_for_key(self, key):
        return self.lang_var if key == "language" else getattr(self, f"{key}_var", None)

    def apply_settings(self, data):
        for key, value in data.items():
            var = self._var_for_key(key)
            if var is not None:
                try:
                    var.set(value)
                except Exception:
                    pass
        self.i18n.set_language(self.lang_var.get())

    def get_settings_data(self):
        data = {}
        for key in self.config_manager.load_settings().keys():
            var = self._var_for_key(key)
            if var is not None:
                try:
                    data[key] = var.get()
                except Exception:
                    pass
        return data

    def load_settings(self, filename):
        self.apply_settings(self.config_manager.load_settings(filename))

    def save_settings(self, filename=None):
        return self.config_manager.save_settings(self.get_settings_data(), filename or self.settings_file)

    def t(self, key):
        return self.i18n.t(key)

    def build_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        rainbow_frame = tk.Frame(self.root, height=6)
        rainbow_frame.pack(fill="x", side="top")
        for color in ["#FF595E", "#FFCA3A", "#8AC926", "#1982C4", "#6A4C93"]:
            tk.Frame(rainbow_frame, bg=color, height=6).pack(side="left", expand=True, fill="x")

        lang_frame = tk.Frame(self.root, bg=self.t_bg)
        lang_frame.pack(fill="x", side="top", padx=10, pady=(5, 0))
        tk.Label(lang_frame, text="🍞 Burning Toast", font=("Impact", 14), fg=self.t_btn, bg=self.t_bg).pack(side="left")
        tk.Radiobutton(lang_frame, text="EN", variable=self.lang_var, value="EN", bg=self.t_bg, command=self.switch_language).pack(side="right")
        tk.Radiobutton(lang_frame, text="TH", variable=self.lang_var, value="TH", bg=self.t_bg, command=self.switch_language).pack(side="right")

        self.canvas = tk.Canvas(self.root, borderwidth=0, highlightthickness=0, bg=self.t_bg)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=self.t_bg)
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", tags="scroll_frame_tag")
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig("scroll_frame_tag", width=e.width))
        self.root.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        bottom_frame = tk.Frame(self.root, bg=self.t_bg)
        bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        row1 = tk.Frame(bottom_frame, bg=self.t_bg); row1.pack(fill="x", pady=2)
        Theme.button(row1, self.t("l_profile"), self.load_profile_dialog, "#8e44ad").pack(side="left", expand=True, fill="x", padx=2)
        Theme.button(row1, self.t("s_profile"), self.save_profile_dialog, "#9b59b6").pack(side="left", expand=True, fill="x", padx=2)
        self.btn_test = Theme.button(row1, self.t("test"), self.show_test_menu, "#f39c12")
        self.btn_test.pack(side="left", expand=True, fill="x", padx=2)
        self.test_menu = tk.Menu(self.root, tearoff=0, font=("Tahoma", 10))
        self.test_menu.add_command(label="🖼️ ทดสอบเฉพาะรูปภาพ (Image)", command=lambda: self.execute_spawns(True))
        self.test_menu.add_command(label="🎬 ทดสอบเฉพาะวิดีโอ (Video)", command=lambda: self.execute_vid_spawns(True))
        self.test_menu.add_command(label="✨ ทดสอบทั้งคู่ (Both)", command=self.test_both)

        row2 = tk.Frame(bottom_frame, bg=self.t_bg); row2.pack(fill="x", pady=2)
        Theme.button(row2, self.t("run"), self.start_app, "#2ecc71").pack(side="left", expand=True, fill="x", padx=2)
        Theme.button(row2, self.t("clear"), self.clear_all_images, "#e74c3c").pack(side="left", expand=True, fill="x", padx=2)
        Theme.button(row2, self.t("exit"), self.exit_app_fully, "#34495e").pack(side="left", expand=True, fill="x", padx=2)

        self.canvas.pack(side="left", fill="both", expand=True, pady=5)
        self.scrollbar.pack(side="right", fill="y")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook.Tab", font=("Tahoma", 10, "bold"), padding=[10, 5])

        self.notebook = ttk.Notebook(self.scroll_frame)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        self.tab_img = tk.Frame(self.notebook, bg=self.t_bg)
        self.tab_vid = tk.Frame(self.notebook, bg=self.t_bg)
        self.tab_bg = tk.Frame(self.notebook, bg=self.t_bg)
        self.notebook.add(self.tab_img, text=" 🖼️ ตั้งค่ารูปภาพ ")
        self.notebook.add(self.tab_vid, text=" 🎬 ตั้งค่าวิดีโอ ")
        self.notebook.add(self.tab_bg, text=" ⚙️ ตั้งค่าระบบแบคกราวด์ ")

        ImageTab(self, self.tab_img).build()
        VideoTab(self, self.tab_vid).build()
        BackgroundTab(self, self.tab_bg).build()

        self.root.protocol("WM_DELETE_WINDOW", self.start_app)

    # ---- Settings/profile actions ----
    def load_profile_dialog(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Profile", "*.json")], title="Load Profile")
        if path:
            self.load_settings(path)
            self.build_ui()
            self.update_preview()
            self.update_vid_preview()
            messagebox.showinfo("Success", f"Loaded: {os.path.basename(path)}")

    def save_profile_dialog(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON Profile", "*.json")]
        )
        if path:
            self.save_settings(path)
            messagebox.showinfo("Success", f"Saved: {os.path.basename(path)}")

    def switch_language(self):
        self.i18n.set_language(self.lang_var.get())
        self.build_ui()
        if self.gif_path.get():
            self.update_preview()
        if self.vid_path_var.get():
            self.update_vid_preview()

    # ---- Thin UI callbacks ----
    def toggle_vid_speed_ui(self):
        state = "disabled" if self.vid_use_default_speed_var.get() else "normal"
        self.vid_speed_entry.config(state=state)
        self.vid_speed_scale.config(state=state)

    def toggle_delay_ui(self):
        state = "disabled" if self.use_default_delay_var.get() else "normal"
        self.delay_entry.config(state=state)

    def handle_drop(self, event, string_var, callback=None):
        path = event.data.strip("{}")
        string_var.set(path)
        if callback:
            callback()

    def browse_gif(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.gif *.png *.jpg")])
        if path:
            self.gif_path.set(path)
            self.update_preview()

    def browse_gif_folder(self):
        path = filedialog.askdirectory(title="Select Folder")
        if path:
            self.gif_path.set(path)
            self.update_preview()

    def browse_sound(self):
        path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")])
        if path:
            self.sound_path.set(path)

    def browse_sound_folder(self):
        path = filedialog.askdirectory(title="Select Folder")
        if path:
            self.sound_path.set(path)

    def browse_video(self):
        path = filedialog.askopenfilename(
            filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv *.webm")]
        )
        if path:
            self.vid_path_var.set(path)
            self.update_vid_preview()

    def browse_video_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.vid_path_var.set(path)
            self.update_vid_preview()

    def test_sound(self):
        path = self.sound_path.get()
        if path and os.path.exists(path):
            chosen = None
            if os.path.isdir(path):
                files = []
                import glob
                for ext in ("*.mp3", "*.wav", "*.ogg"):
                    files.extend(glob.glob(os.path.join(path, ext)))
                if files:
                    chosen = random.choice(files)
            else:
                chosen = path
            if chosen:
                try:
                    pygame.mixer.stop()
                    snd = pygame.mixer.Sound(chosen)
                    snd.set_volume(max(0.0, min(1.0, self.volume_var.get() / 100.0)))
                    snd.play(fade_ms=max(0, int(self.audio_fade_in_var.get())))
                except Exception:
                    pass

    def choose_bg_color(self):
        color = colorchooser.askcolor(title="Select Background Color")[1]
        if color:
            self.bg_color_var.set(color)

    def browse_bg_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if path:
            self.bg_image_path_var.set(path)

    # ---- Preview facade ----
    def update_preview(self, *args):
        self.preview_controller.update_image_preview(*args)

    def change_preview_frame(self, val):
        self.preview_controller.change_image_frame(val)

    def update_vid_preview(self, *args):
        self.preview_controller.update_video_preview(*args)

    def change_vid_preview_frame(self, val):
        self.preview_controller.change_video_frame(val)

    # ---- Controllers facade ----
    def tick_loop(self):
        self.spawn_controller.tick()

    def start_listeners(self):
        self.input_controller.start()

    def check_trigger(self, input_type, key_or_btn=""):
        self.spawn_controller.handle_input(input_type, key_or_btn)

    def execute_spawns(self, is_test=False):
        self.spawn_controller.execute_spawns(is_test)

    def execute_vid_spawns(self, is_test=False):
        self.spawn_controller.execute_video_spawns(is_test)

    def start_app(self):
        self.application_controller.start_app()

    def test_run(self):
        self.application_controller.test_run()

    def clear_all_images(self):
        self.application_controller.clear_all()

    def exit_app_fully(self):
        self.application_controller.exit_app_fully()

    # ---- Test menu ----
    def show_test_menu(self):
        try:
            x = self.btn_test.winfo_rootx()
            y = self.btn_test.winfo_rooty() - self.test_menu.winfo_reqheight()
            self.test_menu.post(x, y)
        except Exception:
            pass

    def test_both(self):
        self.image_loader.load_and_cache(self.gif_path.get(), self.scale_var.get(), self.manual_flip_var.get())
        self.execute_spawns(True)
        self.execute_vid_spawns(True)


if __name__ == "__main__":
    OverlayApp().root.mainloop()
