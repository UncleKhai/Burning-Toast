from __future__ import annotations

import tkinter as tk
from tkinter import ttk, colorchooser

from ui.theme import Theme


class VideoTab:
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent

    def build(self):
        a = self.app
        i18n = a.i18n

        lf7 = Theme.labelframe(self.parent, i18n.t("sec7"), i18n)
        lf7.pack(fill="x", padx=10, pady=5)
        f_en = tk.Frame(lf7, bg=Theme.FRAME); f_en.pack(fill="x", padx=10, pady=2)
        tk.Checkbutton(f_en, text=i18n.t("vid_en"), variable=a.vid_enable_var, font=("Tahoma", 9, "bold"), bg=Theme.FRAME).pack(side="left")

        f_file = tk.Frame(lf7, bg=Theme.FRAME); f_file.pack(fill="x", padx=10, pady=2)
        tk.Label(f_file, text=i18n.t("vid_file"), bg=Theme.FRAME).pack(side="left")
        tk.Entry(f_file, textvariable=a.vid_path_var, width=22).pack(side="left", padx=5)
        tk.Button(
            f_file, text=i18n.t("browse"),
            command=a.browse_video, bg="#FFF"
        ).pack(side="left")
        tk.Button(
            f_file, text=i18n.t("folder"),
            command=a.browse_video_folder, bg="#FFF"
        ).pack(side="left", padx=2)

        container = tk.Frame(lf7, bg=Theme.FRAME); container.pack(fill="x", padx=10, pady=5)
        a.vid_preview_canvas = tk.Canvas(container, bg="#4A3B32", height=150)
        a.vid_preview_canvas.pack(side="top", fill="both", expand=True)
        a.vid_frame_slider = tk.Scale(
            container, from_=0, to=0, variable=a.vid_preview_frame_var,
            orient="horizontal", command=a.change_vid_preview_frame,
            showvalue=False, bg=Theme.FRAME
        )
        a.vid_frame_slider.pack(side="bottom", fill="x", expand=True, padx=5, pady=2)

        f_chroma = tk.Frame(lf7, bg=Theme.FRAME); f_chroma.pack(fill="x", padx=10, pady=2)
        tk.Checkbutton(f_chroma, text="เปิดใช้ Chroma Key", variable=a.vid_use_chroma_var, bg=Theme.FRAME).pack(side="left")
        tk.Label(f_chroma, text=i18n.t("vid_chroma"), bg=Theme.FRAME).pack(side="left", padx=(10, 2))
        tk.Entry(f_chroma, textvariable=a.vid_chroma_var, width=8).pack(side="left")
        tk.Button(
            f_chroma, text="🎨",
            command=lambda: a.vid_chroma_var.set(colorchooser.askcolor()[1] or a.vid_chroma_var.get()),
            bg="#FFF"
        ).pack(side="left", padx=2)

        Theme.add_slider(lf7, i18n.t("vol"), a.vid_volume_var, 0.0, 100.0, res=1.0)
        Theme.add_slider(lf7, "ขนาดวิดีโอ (%):", a.vid_scale_var, 1, 500)
        Theme.add_slider(lf7, "ความโปร่งใสวิดีโอ (%):", a.vid_alpha_var, 10, 100)

        f_dur = tk.Frame(lf7, bg=Theme.FRAME); f_dur.pack(fill="x", padx=10, pady=2)
        tk.Radiobutton(f_dur, text="A: เล่นจนจบ (ตามจำนวน Loop)", variable=a.vid_use_video_duration_var, value=True, bg=Theme.FRAME).pack(side="left")
        tk.Radiobutton(f_dur, text="B: เล่นตามเวลา (วิ):", variable=a.vid_use_video_duration_var, value=False, bg=Theme.FRAME).pack(side="left", padx=(10, 5))
        tk.Entry(f_dur, textvariable=a.vid_duration_var, width=6).pack(side="left")
        f_loop = tk.Frame(lf7, bg=Theme.FRAME); f_loop.pack(fill="x", padx=10, pady=(2, 10))
        tk.Label(f_loop, text="จำนวนรอบที่เล่น (0=วนลูปตลอด):", bg=Theme.FRAME).pack(side="left")
        tk.Entry(f_loop, textvariable=a.vid_loop_count_var, width=5).pack(side="left", padx=5)
        tk.Checkbutton(f_loop, text="เล่นวิดีโอใหม่ตั้งแต่ต้น หากถูก Trigger ซ้ำ", variable=a.vid_replay_on_trigger_var, bg=Theme.FRAME).pack(side="left", padx=(10, 0))

        lf11 = Theme.labelframe(self.parent, " 11 & 12. การตัดวิดีโอ (Trim) และความเร็ว (Speed) ", i18n)
        lf11.pack(fill="x", padx=10, pady=5)
        f_trim = tk.Frame(lf11, bg=Theme.FRAME); f_trim.pack(fill="x", padx=10, pady=2)
        tk.Label(f_trim, text="เริ่มเล่นวิดีโอที่วินาที:", bg=Theme.FRAME).pack(side="left")
        tk.Entry(f_trim, textvariable=a.vid_trim_start_var, width=6).pack(side="left", padx=5)
        tk.Label(f_trim, text="ให้จบลงที่วินาที (0=จบตามคลิป):", bg=Theme.FRAME).pack(side="left", padx=(10, 5))
        tk.Entry(f_trim, textvariable=a.vid_trim_end_var, width=6).pack(side="left")
        f_spd = tk.Frame(lf11, bg=Theme.FRAME); f_spd.pack(fill="x", padx=10, pady=(2, 10))
        tk.Label(f_spd, text="ตัวคูณความเร็ว:", bg=Theme.FRAME).pack(side="left")
        tk.Entry(f_spd, textvariable=a.vid_playback_speed_var, width=5).pack(side="left", padx=5)
        tk.Label(f_spd, text="เร่งสปีดที่:", bg=Theme.FRAME).pack(side="left", padx=(10, 2))
        ttk.Combobox(f_spd, textvariable=a.vid_speed_mode_var, values=("ทั้งคู่ (Both)", "ภาพ (Video)", "เสียง (Audio)"), state="readonly", width=12).pack(side="left")
        tk.Checkbutton(f_spd, text="ปิดเสียง (Mute)", variable=a.vid_mute_var, bg=Theme.FRAME).pack(side="left", padx=(15, 0))

        lf8 = Theme.labelframe(self.parent, i18n.t("sec8"), i18n)
        lf8.pack(fill="x", padx=10, pady=5)
        chaos = tk.Frame(lf8, bg="#FFDAB9"); chaos.pack(fill="x", padx=10, pady=(10, 5))
        tk.Label(chaos, text="[ฟีเจอร์พิเศษา]", font=("Tahoma", 9, "bold"), bg="#FFDAB9", fg="#C0392B").pack(anchor="w", padx=5, pady=2)
        c_row = tk.Frame(chaos, bg="#FFDAB9"); c_row.pack(fill="x", padx=5, pady=2)
        tk.Checkbutton(c_row, text="👻 Jumpscare (เมาส์ชนขยายร่าง)", variable=a.vid_jumpscare_var, bg="#FFDAB9", fg="#8E44AD", font=("Tahoma", 8, "bold")).pack(side="left", padx=5)
        tk.Checkbutton(c_row, text="🍺 เดินเซ (Drunk)", variable=a.vid_drunk_var, bg="#FFDAB9", fg="#D35400", font=("Tahoma", 8, "bold")).pack(side="left", padx=5)
        tk.Checkbutton(c_row, text="🏃‍♂️ วิ่งหนีเมาส์ (Run Away)", variable=a.vid_runaway_var, bg="#FFDAB9", fg="#2980B9", font=("Tahoma", 8, "bold")).pack(side="left", padx=5)
        Theme.add_slider(lf8, "ความเร็วเคลื่อนที่ (px):", a.vid_move_speed_var, 1.0, 100.0)
        phys = tk.Frame(lf8, bg="#FAD7A1"); phys.pack(fill="x", padx=10, pady=5)
        tk.Label(phys, text=i18n.t("physics_title"), font=("Tahoma", 9, "bold"), bg="#FAD7A1", fg="#c0392b").pack(anchor="w", padx=5)
        row1 = tk.Frame(phys, bg="#FAD7A1"); row1.pack(fill="x", padx=5)
        tk.Checkbutton(row1, text=i18n.t("follow_m"), variable=a.vid_follow_mouse_var, bg="#FAD7A1", fg="#2980b9", font=("Tahoma", 9, "bold")).pack(side="left", padx=5)
        tk.Checkbutton(row1, text=i18n.t("dvd"), variable=a.vid_dvd_mode_var, bg="#FAD7A1", fg="#27ae60", font=("Tahoma", 9, "bold")).pack(side="left", padx=5)
        row2 = tk.Frame(phys, bg="#FAD7A1"); row2.pack(fill="x", padx=5)
        tk.Checkbutton(row2, text=i18n.t("grav"), variable=a.vid_gravity_mode_var, bg="#FAD7A1", fg="#d35400", font=("Tahoma", 9, "bold")).pack(side="left", padx=5)

        f_dir = tk.Frame(lf8, bg=Theme.FRAME); f_dir.pack(fill="x", padx=10, pady=5)
        dirs = [
            (i18n.t("ltr"), a.vid_dir_ltr_var, a.vid_flip_ltr_var),
            (i18n.t("rtl"), a.vid_dir_rtl_var, a.vid_flip_rtl_var),
            (i18n.t("ttb"), a.vid_dir_ttb_var, a.vid_flip_ttb_var),
            (i18n.t("btt"), a.vid_dir_btt_var, a.vid_flip_btt_var),
            (i18n.t("cen"), a.vid_dir_center_var, a.vid_flip_center_var),
        ]
        for r, (txt, dvar, fvar) in enumerate(dirs):
            tk.Checkbutton(f_dir, text=txt, variable=dvar, width=15, anchor="w", bg=Theme.FRAME).grid(row=r, column=0, sticky="w", pady=1)
            tk.Checkbutton(f_dir, text=i18n.t("flip_cb"), variable=fvar, bg=Theme.FRAME).grid(row=r, column=1, sticky="w", padx=10, pady=1)
        r = len(dirs)
        tk.Checkbutton(f_dir, text=i18n.t("cus"), variable=a.vid_dir_custom_var, width=15, anchor="w", fg="#2980b9", bg=Theme.FRAME).grid(row=r, column=0, sticky="w", pady=1)
        tools = tk.Frame(f_dir, bg=Theme.FRAME); tools.grid(row=r, column=1, sticky="w", padx=10, pady=1)
        tk.Checkbutton(tools, text=i18n.t("flip_cb"), variable=a.vid_flip_custom_var, bg=Theme.FRAME).pack(side="left")
        tk.Label(tools, text="X:", bg=Theme.FRAME).pack(side="left", padx=(5, 2))
        tk.Entry(tools, textvariable=a.vid_pos_x_var, width=5).pack(side="left")
        tk.Label(tools, text=" Y:", bg=Theme.FRAME).pack(side="left", padx=(5, 2))
        tk.Entry(tools, textvariable=a.vid_pos_y_var, width=5).pack(side="left")

        lf9 = Theme.labelframe(self.parent, i18n.t("sec9"), i18n)
        lf9.pack(fill="x", padx=10, pady=5)
        f_trig = tk.Frame(lf9, bg=Theme.FRAME); f_trig.pack(fill="x", padx=10, pady=2)
        tk.Checkbutton(f_trig, text=i18n.t("enable_trig"), variable=a.vid_enable_trigger_var, font=("Tahoma", 9, "bold"), bg=Theme.FRAME).pack(side="left")
        f_act = tk.Frame(lf9, bg=Theme.FRAME); f_act.pack(fill="x", padx=10, pady=2)
        tk.Label(f_act, text=i18n.t("act"), width=18, anchor="w", bg=Theme.FRAME).pack(side="left")
        ttk.Combobox(f_act, textvariable=a.vid_action_var, values=("กดคีย์บอร์ดเท่านั้น", "คลิกเมาส์เท่านั้น", "ทั้งหมด", "Keyboard Only", "Mouse Only", "All"), state="readonly", width=18).pack(side="left")
        f_spec = tk.Frame(lf9, bg=Theme.FRAME); f_spec.pack(fill="x", padx=10, pady=2)
        tk.Label(f_spec, text=i18n.t("spec_k"), width=22, anchor="w", fg="#8e44ad", bg=Theme.FRAME).pack(side="left")
        tk.Entry(f_spec, textvariable=a.vid_specific_key_var, width=10).pack(side="left")
        tk.Label(f_spec, text=i18n.t("spec_m"), fg="#8e44ad", bg=Theme.FRAME).pack(side="left", padx=5)
        ttk.Combobox(f_spec, textvariable=a.vid_specific_mouse_var, values=("ทั้งหมด", "คลิกซ้าย", "คลิกขวา", "คลิกกลาง", "All", "Left Click", "Right Click", "Middle Click"), state="readonly", width=12).pack(side="left")
        Theme.add_slider(lf9, i18n.t("chance"), a.vid_chance_var, 0.01, 100.0, res=0.01)
        Theme.add_slider(lf9, i18n.t("cd"), a.vid_trigger_cooldown_var, 0.0, 60.0, res=0.1)
        Theme.add_slider(lf9, i18n.t("spawn_delay"), a.vid_trigger_delay_var, 0.0, 60.0, res=0.1)
        Theme.add_slider(lf9, i18n.t("max_ins"), a.vid_max_instances_var, 1, 50, res=1)
        multi = tk.Frame(lf9, bg=Theme.FRAME); multi.pack(fill="x", padx=10, pady=(5, 10))
        tk.Checkbutton(multi, text=i18n.t("multi"), variable=a.vid_multi_spawn_var, font=("Tahoma", 9, "bold"), bg=Theme.FRAME).pack(side="left")
        tk.Entry(multi, textvariable=a.vid_multi_spawn_min_var, width=4).pack(side="left")
        tk.Label(multi, text=i18n.t("to"), bg=Theme.FRAME).pack(side="left", padx=2)
        tk.Entry(multi, textvariable=a.vid_multi_spawn_max_var, width=4).pack(side="left")

        lf10 = Theme.labelframe(self.parent, i18n.t("sec10"), i18n)
        lf10.pack(fill="x", padx=10, pady=5)
        f_auto1 = tk.Frame(lf10, bg=Theme.FRAME); f_auto1.pack(fill="x", padx=10, pady=2)
        tk.Checkbutton(f_auto1, text=i18n.t("auto_en"), variable=a.vid_auto_time_var, font=("Tahoma", 9, "bold"), bg=Theme.FRAME).pack(side="left")
        f_auto2 = tk.Frame(lf10, bg=Theme.FRAME); f_auto2.pack(fill="x", padx=10, pady=2)
        tk.Label(f_auto2, text=i18n.t("every"), bg=Theme.FRAME).pack(side="left")
        tk.Entry(f_auto2, textvariable=a.vid_auto_hr_var, width=3).pack(side="left", padx=2); tk.Label(f_auto2, text=i18n.t("hr"), bg=Theme.FRAME).pack(side="left")
        tk.Entry(f_auto2, textvariable=a.vid_auto_min_var, width=3).pack(side="left", padx=2); tk.Label(f_auto2, text=i18n.t("min"), bg=Theme.FRAME).pack(side="left")
        tk.Entry(f_auto2, textvariable=a.vid_auto_sec_var, width=5).pack(side="left", padx=2); tk.Label(f_auto2, text=i18n.t("sec"), bg=Theme.FRAME).pack(side="left")
        Theme.add_slider(lf10, i18n.t("auto_chance"), a.vid_auto_chance_var, 0.01, 100.0, res=0.01)
        Theme.add_slider(lf10, i18n.t("auto_delay"), a.vid_auto_delay_var, 0.0, 60.0, res=0.1)
