from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ui.theme import Theme


class BackgroundTab:
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent

    def build(self):
        a = self.app
        i18n = a.i18n

        lf = Theme.labelframe(self.parent, i18n.t("sec6"), i18n)
        lf.pack(fill="x", padx=10, pady=5)

        row = tk.Frame(lf, bg=Theme.FRAME); row.pack(fill="x", padx=10, pady=2)
        tk.Checkbutton(row, text=i18n.t("bg_en"), variable=a.bg_enable_var, font=("Tahoma", 9, "bold"), bg=Theme.FRAME).pack(side="left")
        tk.Label(row, text=" เลเยอร์:", bg=Theme.FRAME).pack(side="left", padx=(10, 2))
        ttk.Combobox(
            row, textvariable=a.bg_layer_var,
            values=("อยู่หลังสุด (Background)", "บังทุกอย่าง (Foreground)"),
            state="readonly", width=25
        ).pack(side="left")

        row_type = tk.Frame(lf, bg=Theme.FRAME); row_type.pack(fill="x", padx=10, pady=2)
        tk.Radiobutton(row_type, text=i18n.t("bg_col"), variable=a.bg_type_var, value="color", bg=Theme.FRAME).pack(side="left")
        tk.Button(row_type, text="🎨", command=a.choose_bg_color, bg="#FFF").pack(side="left", padx=5)
        tk.Radiobutton(row_type, text=i18n.t("bg_img"), variable=a.bg_type_var, value="image", bg=Theme.FRAME).pack(side="left", padx=(10, 0))
        tk.Entry(row_type, textvariable=a.bg_image_path_var, width=15).pack(side="left", padx=5)
        tk.Button(row_type, text=i18n.t("browse"), command=a.browse_bg_image, bg="#FFF").pack(side="left")

        Theme.add_slider(lf, i18n.t("bg_alpha"), a.bg_alpha_var, 0.0, 100.0, res=1.0)

        row_text = tk.Frame(lf, bg=Theme.FRAME); row_text.pack(fill="x", padx=10, pady=5)
        tk.Label(row_text, text=i18n.t("bg_text"), bg=Theme.FRAME).pack(side="left")
        tk.Entry(row_text, textvariable=a.bg_text_var, width=25).pack(side="left", padx=5)
        tk.Label(row_text, text=i18n.t("pos"), bg=Theme.FRAME).pack(side="left", padx=(5, 2))
        ttk.Combobox(row_text, textvariable=a.bg_text_pos_var, values=("top", "bottom"), state="readonly", width=8).pack(side="left")
