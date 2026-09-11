import tkinter as tk


class Theme:
    BG = "#FDF4E3"
    FRAME = "#FDEBD0"
    TEXT = "#5C3A21"
    BUTTON = "#E67E22"
    BUTTON_HOVER = "#D35400"

    @classmethod
    def labelframe(cls, parent, text, i18n):
        return tk.LabelFrame(
            parent, text=text, font=("Tahoma", 10, "bold"),
            fg=cls.TEXT, bg=cls.FRAME, bd=2, relief="groove"
        )

    @classmethod
    def button(cls, parent, text, command, bg_color=None):
        btn = tk.Button(
            parent, text=text, bg=bg_color or cls.BUTTON, fg="white",
            font=("Tahoma", 9, "bold"), command=command, relief="flat",
            activebackground=cls.BUTTON_HOVER,
        )
        return btn

    @classmethod
    def add_slider(cls, parent, label, var, min_v, max_v, res=1.0):
        frame = tk.Frame(parent, bg=cls.FRAME)
        frame.pack(fill="x", padx=10, pady=2)
        tk.Label(frame, text=label, width=22, anchor="w", bg=cls.FRAME).pack(side="left")
        tk.Entry(frame, textvariable=var, width=6).pack(side="right")
        tk.Scale(
            frame, from_=min_v, to=max_v, resolution=res, variable=var,
            orient="horizontal", showvalue=False, bg=cls.FRAME
        ).pack(side="right", expand=True, fill="x", padx=5)
