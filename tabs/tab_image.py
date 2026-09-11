from __future__ import annotations

import tkinter as tk
from tkinter import ttk

try:
    from tkinterdnd2 import DND_FILES
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

from ui.theme import Theme


class ImageTab:
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent

    def build(self):
        a = self.app
        i18n = a.i18n

        lf1 = Theme.labelframe(self.parent, i18n.t("sec1"), i18n)
        lf1.pack(fill="x", padx=10, pady=5)
        tk.Label(lf1, text=i18n.t("drag"), fg="#7f8c8d", bg=Theme.FRAME, font=("Tahoma", 8)).pack(anchor="w", padx=10)

        f_img = tk.Frame(lf1, bg=Theme.FRAME)
        f_img.pack(fill="x", padx=10, pady=2)
        tk.Label(f_img, text=i18n.t("img"), bg=Theme.FRAME).pack(side="left")
        a.entry_img = tk.Entry(f_img, textvariable=a.gif_path)
        a.entry_img.pack(side="left", expand=True, fill="x", padx=5)
        tk.Button(f_img, text=i18n.t("browse"), command=a.browse_gif, bg="#FFF").pack(side="right")
        tk.Button(f_img, text=i18n.t("folder"), command=a.browse_gif_folder, bg="#FFF").pack(side="right", padx=2)

        preview_container = tk.Frame(lf1, bg=Theme.FRAME)
        preview_container.pack(fill="x", padx=10, pady=5)
        a.pv_vbar = ttk.Scrollbar(preview_container, orient="vertical")
        a.pv_vbar.pack(side="right", fill="y")
        a.pv_hbar = ttk.Scrollbar(preview_container, orient="horizontal")
        a.pv_hbar.pack(side="bottom", fill="x")
        a.preview_canvas = tk.Canvas(
            preview_container, bg="#4A3B32", height=150,
            yscrollcommand=a.pv_vbar.set, xscrollcommand=a.pv_hbar.set
        )
        a.preview_canvas.pack(side="left", fill="both", expand=True)
        a.pv_vbar.config(command=a.preview_canvas.yview)
        a.pv_hbar.config(command=a.preview_canvas.xview)

        f_pv_tools = tk.Frame(lf1, bg=Theme.FRAME)
        f_pv_tools.pack(fill="x", padx=10, pady=2)
        tk.Checkbutton(
            f_pv_tools, text=i18n.t("flip"), variable=a.manual_flip_var,
            command=a.update_preview, bg=Theme.FRAME
        ).pack(side="left")
        a.frame_slider = tk.Scale(
            f_pv_tools, from_=0, to=0, variable=a.preview_frame_var,
            orient="horizontal", command=a.change_preview_frame,
            showvalue=False, bg=Theme.FRAME
        )
        a.frame_slider.pack(side="left", fill="x", expand=True, padx=5)
        tk.Scale(
            f_pv_tools, from_=10, to=400, variable=a.preview_zoom_var,
            orient="horizontal", showvalue=False, command=a.update_preview, bg=Theme.FRAME
        ).pack(side="right", expand=True, fill="x")
        tk.Label(f_pv_tools, text=i18n.t("zoom"), bg=Theme.FRAME).pack(side="right")

        f_snd = tk.Frame(lf1, bg=Theme.FRAME)
        f_snd.pack(fill="x", padx=10, pady=(5, 10))
        tk.Label(f_snd, text=i18n.t("snd"), bg=Theme.FRAME).pack(side="left")
        a.entry_snd = tk.Entry(f_snd, textvariable=a.sound_path)
        a.entry_snd.pack(side="left", expand=True, fill="x", padx=5)
        tk.Button(f_snd, text=i18n.t("play"), command=a.test_sound, bg="#FFF").pack(side="right")
        tk.Button(f_snd, text=i18n.t("browse"), command=a.browse_sound, bg="#FFF").pack(side="right", padx=2)
        tk.Button(f_snd, text=i18n.t("folder"), command=a.browse_sound_folder, bg="#FFF").pack(side="right", padx=2)

        if DND_AVAILABLE:
            a.entry_img.drop_target_register(DND_FILES)
            a.entry_img.dnd_bind("<<Drop>>", lambda e: a.handle_drop(e, a.gif_path, a.update_preview))
            a.entry_snd.drop_target_register(DND_FILES)
            a.entry_snd.dnd_bind("<<Drop>>", lambda e: a.handle_drop(e, a.sound_path, None))

        lf2 = Theme.labelframe(self.parent, i18n.t("sec2"), i18n)
        lf2.pack(fill="x", padx=10, pady=5)
        Theme.add_slider(lf2, i18n.t("scale"), a.scale_var, 1, 5000)
        Theme.add_slider(lf2, i18n.t("alpha"), a.alpha_var, 10, 100)
        Theme.add_slider(lf2, i18n.t("vol"), a.volume_var, 0, 100)

        f_fade = tk.Frame(lf2, bg=Theme.FRAME)
        f_fade.pack(fill="x", padx=10, pady=2)
        tk.Checkbutton(f_fade, text=i18n.t("stop_snd"), variable=a.stop_sound_var, bg=Theme.FRAME).pack(side="left")
        tk.Label(f_fade, text=i18n.t("fade_in"), bg=Theme.FRAME).pack(side="left", padx=(5, 2))
        tk.Entry(f_fade, textvariable=a.audio_fade_in_var, width=5).pack(side="left")
        tk.Label(f_fade, text=i18n.t("fade_out"), bg=Theme.FRAME).pack(side="left", padx=(5, 2))
        tk.Entry(f_fade, textvariable=a.audio_fade_out_var, width=5).pack(side="left")

        f_speed = tk.Frame(lf2, bg=Theme.FRAME)
        f_speed.pack(fill="x", padx=10, pady=5)
        tk.Label(f_speed, text=i18n.t("speed"), width=20, anchor="w", bg=Theme.FRAME).pack(side="left")
        tk.Entry(f_speed, textvariable=a.speed_var, width=10).pack(side="left")

        f_delay = tk.Frame(lf2, bg=Theme.FRAME)
        f_delay.pack(fill="x", padx=10, pady=2)
        tk.Label(f_delay, text=i18n.t("delay"), width=20, anchor="w", bg=Theme.FRAME).pack(side="left")
        a.delay_entry = tk.Entry(f_delay, textvariable=a.frame_delay_var, width=6)
        a.delay_entry.pack(side="left")
        tk.Checkbutton(
            f_delay, text=i18n.t("use_def_delay"), variable=a.use_default_delay_var,
            command=a.toggle_delay_ui, bg=Theme.FRAME
        ).pack(side="left", padx=10)
        a.toggle_delay_ui()

        lf3 = Theme.labelframe(self.parent, i18n.t("sec3"), i18n)
        lf3.pack(fill="x", padx=10, pady=5)
        f_physics = tk.Frame(lf3, bg="#FAD7A1")
        f_physics.pack(fill="x", padx=10, pady=5)
        tk.Label(f_physics, text=i18n.t("physics_title"), font=("Tahoma", 9, "bold"), bg="#FAD7A1", fg="#c0392b").pack(anchor="w", padx=5)

        p_row1 = tk.Frame(f_physics, bg="#FAD7A1")
        p_row1.pack(fill="x", padx=5)
        tk.Checkbutton(p_row1, text=i18n.t("follow_m"), variable=a.follow_mouse_var, bg="#FAD7A1", fg="#2980b9", font=("Tahoma", 9, "bold")).pack(side="left", padx=5)
        tk.Checkbutton(p_row1, text=i18n.t("dvd"), variable=a.dvd_mode_var, bg="#FAD7A1", fg="#27ae60", font=("Tahoma", 9, "bold")).pack(side="left", padx=5)
        p_row2 = tk.Frame(f_physics, bg="#FAD7A1")
        p_row2.pack(fill="x", padx=5)
        tk.Checkbutton(p_row2, text=i18n.t("grav"), variable=a.gravity_mode_var, bg="#FAD7A1", fg="#d35400", font=("Tahoma", 9, "bold")).pack(side="left", padx=5)

        f_dir_grid = tk.Frame(lf3, bg=Theme.FRAME)
        f_dir_grid.pack(fill="x", padx=10, pady=5)
        dirs_config = [
            (i18n.t("ltr"), a.dir_ltr_var, a.flip_ltr_var),
            (i18n.t("rtl"), a.dir_rtl_var, a.flip_rtl_var),
            (i18n.t("ttb"), a.dir_ttb_var, a.flip_ttb_var),
            (i18n.t("btt"), a.dir_btt_var, a.flip_btt_var),
            (i18n.t("cen"), a.dir_center_var, a.flip_center_var),
        ]
        for r, (text, dir_var, flip_var) in enumerate(dirs_config):
            tk.Checkbutton(f_dir_grid, text=text, variable=dir_var, width=15, anchor="w", bg=Theme.FRAME).grid(row=r, column=0, sticky="w", pady=1)
            tk.Checkbutton(f_dir_grid, text=i18n.t("flip_cb"), variable=flip_var, bg=Theme.FRAME).grid(row=r, column=1, sticky="w", padx=10, pady=1)

        r_custom = len(dirs_config)
        tk.Checkbutton(f_dir_grid, text=i18n.t("cus"), variable=a.dir_custom_var, width=15, anchor="w", fg="#2980b9", bg=Theme.FRAME).grid(row=r_custom, column=0, sticky="w", pady=1)
        f_cus_tools = tk.Frame(f_dir_grid, bg=Theme.FRAME)
        f_cus_tools.grid(row=r_custom, column=1, sticky="w", padx=10, pady=1)
        tk.Checkbutton(f_cus_tools, text=i18n.t("flip_cb"), variable=a.flip_custom_var, bg=Theme.FRAME).pack(side="left")
        tk.Label(f_cus_tools, text="X:", bg=Theme.FRAME).pack(side="left", padx=(5, 2))
        tk.Entry(f_cus_tools, textvariable=a.custom_x_var, width=5).pack(side="left")
        tk.Label(f_cus_tools, text=" Y:", bg=Theme.FRAME).pack(side="left", padx=(5, 2))
        tk.Entry(f_cus_tools, textvariable=a.custom_y_var, width=5).pack(side="left")
        f_all_dur = tk.Frame(lf3, bg=Theme.FRAME)
        f_all_dur.pack(fill="x", padx=10, pady=2)
        tk.Checkbutton(f_all_dur, text=i18n.t("dur"), variable=a.use_duration_var, bg=Theme.FRAME).pack(side="left")
        tk.Entry(f_all_dur, textvariable=a.all_duration_var, width=5).pack(side="left", padx=5)
        f_end = tk.Frame(lf3, bg=Theme.FRAME)
        f_end.pack(fill="x", padx=10, pady=(2, 10))
        tk.Checkbutton(f_end, text=i18n.t("end_loop"), variable=a.end_on_loop_var, bg=Theme.FRAME).pack(side="left")

        lf4 = Theme.labelframe(self.parent, i18n.t("sec4"), i18n)
        lf4.pack(fill="x", padx=10, pady=5)
        f_trigger = tk.Frame(lf4, bg=Theme.FRAME); f_trigger.pack(fill="x", padx=10, pady=2)
        tk.Checkbutton(f_trigger, text=i18n.t("enable_trig"), variable=a.enable_trigger_var, font=("Tahoma", 9, "bold"), bg=Theme.FRAME).pack(side="left")
        f_act = tk.Frame(lf4, bg=Theme.FRAME); f_act.pack(fill="x", padx=10, pady=2)
        tk.Label(f_act, text=i18n.t("act"), width=18, anchor="w", bg=Theme.FRAME).pack(side="left")
        ttk.Combobox(f_act, textvariable=a.action_var, values=("กดคีย์บอร์ดเท่านั้น", "คลิกเมาส์เท่านั้น", "ทั้งหมด", "Keyboard Only", "Mouse Only", "All"), state="readonly", width=18).pack(side="left")
        f_spec = tk.Frame(lf4, bg=Theme.FRAME); f_spec.pack(fill="x", padx=10, pady=2)
        tk.Label(f_spec, text=i18n.t("spec_k"), width=22, anchor="w", fg="#8e44ad", bg=Theme.FRAME).pack(side="left")
        tk.Entry(f_spec, textvariable=a.specific_key_var, width=10).pack(side="left")
        tk.Label(f_spec, text=i18n.t("spec_m"), fg="#8e44ad", bg=Theme.FRAME).pack(side="left", padx=5)
        ttk.Combobox(f_spec, textvariable=a.specific_mouse_var, values=("ทั้งหมด", "คลิกซ้าย", "คลิกขวา", "คลิกกลาง", "All", "Left Click", "Right Click", "Middle Click"), state="readonly", width=12).pack(side="left")
        Theme.add_slider(lf4, i18n.t("chance"), a.chance_var, 0.01, 100.0, res=0.01)
        Theme.add_slider(lf4, i18n.t("cd"), a.trigger_cooldown_var, 0.0, 60.0, res=0.1)
        Theme.add_slider(lf4, i18n.t("spawn_delay"), a.trigger_delay_var, 0.0, 60.0, res=0.1)
        Theme.add_slider(lf4, i18n.t("max_ins"), a.max_instances_var, 1, 50, res=1)
        f_multi = tk.Frame(lf4, bg=Theme.FRAME); f_multi.pack(fill="x", padx=10, pady=(5, 10))
        tk.Checkbutton(f_multi, text=i18n.t("multi"), variable=a.multi_spawn_var, font=("Tahoma", 9, "bold"), bg=Theme.FRAME).pack(side="left")
        tk.Entry(f_multi, textvariable=a.multi_spawn_min_var, width=4).pack(side="left")
        tk.Label(f_multi, text=i18n.t("to"), bg=Theme.FRAME).pack(side="left", padx=2)
        tk.Entry(f_multi, textvariable=a.multi_spawn_max_var, width=4).pack(side="left")

        lf5 = Theme.labelframe(self.parent, i18n.t("sec5"), i18n)
        lf5.pack(fill="x", padx=10, pady=5)
        f_auto1 = tk.Frame(lf5, bg=Theme.FRAME); f_auto1.pack(fill="x", padx=10, pady=2)
        tk.Checkbutton(f_auto1, text=i18n.t("auto_en"), variable=a.auto_time_var, font=("Tahoma", 9, "bold"), bg=Theme.FRAME).pack(side="left")
        f_auto2 = tk.Frame(lf5, bg=Theme.FRAME); f_auto2.pack(fill="x", padx=10, pady=2)
        tk.Label(f_auto2, text=i18n.t("every"), bg=Theme.FRAME).pack(side="left")
        tk.Entry(f_auto2, textvariable=a.auto_hr_var, width=3).pack(side="left", padx=2)
        tk.Label(f_auto2, text=i18n.t("hr"), bg=Theme.FRAME).pack(side="left")
        tk.Entry(f_auto2, textvariable=a.auto_min_var, width=3).pack(side="left", padx=2)
        tk.Label(f_auto2, text=i18n.t("min"), bg=Theme.FRAME).pack(side="left")
        tk.Entry(f_auto2, textvariable=a.auto_sec_var, width=5).pack(side="left", padx=2)
        tk.Label(f_auto2, text=i18n.t("sec"), bg=Theme.FRAME).pack(side="left")
        Theme.add_slider(lf5, i18n.t("auto_chance"), a.auto_chance_var, 0.01, 100.0, res=0.01)
        Theme.add_slider(lf5, i18n.t("auto_delay"), a.auto_delay_var, 0.0, 60.0, res=0.1)
