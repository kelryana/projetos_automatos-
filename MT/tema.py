class TemaManager:
    def __init__(self, root):
        self.root = root
        self.dark = False
        self._apply_light()

    def toggle(self):
        if self.dark:
            self._apply_light()
        else:
            self._apply_dark()
        self.dark = not self.dark

    def _apply_light(self):
        self.root.configure(bg="#f3f4f6")
        style = self._get_style()
        style.theme_use("clam")

        # Cores claras
        style.configure("TFrame", background="#f3f4f6")
        style.configure("TLabel", background="#f3f4f6", foreground="#111827")
        style.configure("TButton", background="#e5e7eb", foreground="#111827")
        style.map("TButton", background=[("active", "#d1d5db")])
        style.configure("TEntry", fieldbackground="#ffffff", foreground="#111827")
        style.configure("TCombobox", fieldbackground="#ffffff", foreground="#111827")
        style.configure("TCheckbutton", background="#f3f4f6", foreground="#111827")
        style.configure("TLabelframe", background="#f3f4f6", foreground="#111827")
        style.configure("TLabelframe.Label", background="#f3f4f6", foreground="#111827")

    def _apply_dark(self):
        self.root.configure(bg="#1f2937")
        style = self._get_style()
        style.theme_use("clam")

        # Cores escuras
        style.configure("TFrame", background="#1f2937")
        style.configure("TLabel", background="#1f2937", foreground="#f9fafb")
        style.configure("TButton", background="#2563eb", foreground="#ffffff")
        style.configure("Rounded.TButton", relief="flat", borderwidth=0, padding=6)
        style.configure("TEntry", fieldbackground="#374151", foreground="#f9fafb")
        style.configure("TCombobox", fieldbackground="#374151", foreground="#f9fafb")
        style.configure("TCheckbutton", background="#1f2937", foreground="#f9fafb")
        style.configure("TLabelframe", background="#1f2937", foreground="#f9fafb")
        style.configure("TLabelframe.Label", background="#1f2937", foreground="#f9fafb")
        style.configure("Rounded.TButton",
            relief="flat",
            borderwidth=1,
            padding=6,
            font=("Segoe UI", 10),
            focuscolor=style.configure(".")["background"]
        )
        style.map("Rounded.TButton",
            background=[("active", "#1d4ed8"), ("!active", "#2563eb")],
            foreground=[("!disabled", "#ffffff")]
        )


        # Aplicar diretamente em widgets visuais (se necessário)
        try:
            self.root.tape_canvas.configure(bg="#374151")
            self.root.txt_console.configure(bg="#111827", fg="#f9fafb")
            self.root.fig.patch.set_facecolor("#1f2937")
            self.root.ax.set_facecolor("#1f2937")
        except Exception:
            pass

    def _get_style(self):
        import tkinter.ttk as ttk
        return ttk.Style()
