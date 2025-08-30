# src/gui.py

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from termcolor import colored

class SettingsGUI:
    def __init__(self, master, aimbot_instance, config_manager):
        self.master = master
        self.aimbot = aimbot_instance
        self.config_manager = config_manager
        
        # Apply dark theme before creating widgets
        self._apply_dark_theme(master)

        master.title("Aimbot Settings")
        master.geometry("640x580")
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.tab1 = ttk.Frame(self.notebook, padding=10)
        self.tab2 = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab1, text='Aimbot')
        self.notebook.add(self.tab2, text='PID & Sensitivity')
        
        self.create_aimbot_tab()
        self.create_pid_sens_tab()
        
        self.apply_button = ttk.Button(master, text="Save & Apply", command=self.apply_and_save_settings, style="Accent.TButton")
        self.apply_button.pack(pady=10)
        
        self.load_initial_values()

    def _apply_dark_theme(self, root: tk.Tk) -> None:
        """Configure a modern dark theme for ttk widgets."""
        colors = {
            "bg": "#121212",
            "panel": "#1E1E1E",
            "elev": "#252526",
            "stroke": "#2D2D2D",
            "muted": "#9AA0A6",
            "fg": "#E5E5E5",
            "accent": "#5B8DEF",
            "accent_hover": "#6C9BFF",
            "accent_active": "#3D6ED6",
        }

        # Base window background and fonts
        root.configure(bg=colors["bg"])
        try:
            base = tkfont.nametofont("TkDefaultFont")
            base.configure(family="Segoe UI", size=10)
            text = tkfont.nametofont("TkTextFont")
            text.configure(family="Segoe UI", size=10)
            heading = tkfont.nametofont("TkHeadingFont")
            heading.configure(family="Segoe UI", size=10, weight="bold")
        except tk.TclError:
            pass

        style = ttk.Style(root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Frames and labels
        style.configure("TFrame", background=colors["bg"])
        style.configure("TLabel", background=colors["bg"], foreground=colors["fg"])
        style.configure("Muted.TLabel", background=colors["bg"], foreground=colors["muted"])

        # Inputs
        style.configure("TEntry",
                        fieldbackground=colors["panel"],
                        foreground=colors["fg"],
                        background=colors["panel"],
                        insertcolor=colors["fg"])
        style.configure("TCheckbutton", background=colors["bg"], foreground=colors["fg"])

        # Buttons
        style.configure("TButton", background=colors["elev"], foreground=colors["fg"], padding=(12, 8), borderwidth=0)
        style.map("TButton", background=[("active", colors["elev"])])
        style.configure("Accent.TButton", background=colors["accent"], foreground="#FFFFFF", padding=(14, 9), borderwidth=0)
        style.map("Accent.TButton",
                  background=[("active", colors["accent_hover"]), ("pressed", colors["accent_active"])])

        # Group boxes
        style.configure("TLabelframe", background=colors["panel"], foreground=colors["fg"], borderwidth=0.5, relief="solid")
        style.configure("TLabelframe.Label", background=colors["panel"], foreground=colors["muted"], padding=(2, 0))

        # Tabs
        style.configure("TNotebook", background=colors["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background=colors["panel"], foreground=colors["muted"], padding=(2, 5))
        style.map("TNotebook.Tab",
                  background=[("selected", colors["elev"]), ("active", colors["elev"])],
                  foreground=[("selected", colors["fg"])])

        # Sliders
        style.configure("TScale", background=colors["panel"], troughcolor=colors["stroke"]) 

    def create_slider(self, parent, text, from_, to, var, resolution=1):
        frame = ttk.Frame(parent)
        label = ttk.Label(frame, text=text, width=25)
        label.pack(side=tk.LEFT, padx=6, pady=8)
        entry = ttk.Entry(frame, textvariable=var, width=10)
        entry.pack(side=tk.LEFT, padx=8)
        command = lambda val: var.set(int(float(val))) if resolution == 1 else var.set(round(float(val), 2))
        slider = ttk.Scale(frame, from_=from_, to=to, orient=tk.HORIZONTAL, variable=var, command=command)
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        frame.pack(fill=tk.X, padx=12, pady=4)

    def create_aimbot_tab(self):
        self.show_fov_box_var = tk.BooleanVar()
        self.fov_var = tk.IntVar()
        self.aim_height_var = tk.IntVar()
        self.lock_radius_var = tk.IntVar()
        self.track_tolerance_var = tk.IntVar()
        
        self.create_slider(self.tab1, "FOV (Detection Box Size):", 100, 1000, self.fov_var)
        self.create_slider(self.tab1, "Aim Height (% from top):", 0, 100, self.aim_height_var)
        self.create_slider(self.tab1, "Lock Radius (px):", 0, 50, self.lock_radius_var)
        self.create_slider(self.tab1, "Track Tolerance (px):", 0, 100, self.track_tolerance_var)
        
        check_frame = ttk.Frame(self.tab1)
        ttk.Checkbutton(check_frame, text="Show FOV Box", variable=self.show_fov_box_var).pack(pady=10)
        check_frame.pack()

    def create_pid_sens_tab(self):
        pid_frame = ttk.LabelFrame(self.tab2, text="PID Controller Gains")
        pid_frame.pack(fill=tk.X, padx=6, pady=8)
        self.kp_var = tk.DoubleVar()
        self.ki_var = tk.DoubleVar()
        self.kd_var = tk.DoubleVar()
        self.create_slider(pid_frame, "Kp (Proportional):", 0.0, 2.0, self.kp_var, 0.01)
        self.create_slider(pid_frame, "Ki (Integral):", 0.0, 1.0, self.ki_var, 0.01)
        self.create_slider(pid_frame, "Kd (Derivative):", 0.0, 2.0, self.kd_var, 0.01)
        ttk.Label(pid_frame, text="NOTE: Lower FOV requires lower Kp/Kd values to prevent instability.", style="Muted.TLabel").pack(pady=5)
        
        sens_frame = ttk.LabelFrame(self.tab2, text="In-Game Sensitivity")
        sens_frame.pack(fill=tk.X, padx=6, pady=8)
        self.xy_sens_var = tk.DoubleVar()
        self.targeting_sens_var = tk.DoubleVar()
        self.create_slider(sens_frame, "X/Y Sensitivity:", 1.0, 20.0, self.xy_sens_var, 0.1)
        self.create_slider(sens_frame, "Targeting Sensitivity:", 0.1, 2.0, self.targeting_sens_var, 0.1)

    def load_initial_values(self):
        config = self.aimbot.config
        self.show_fov_box_var.set(config["show_fov_box"])
        self.fov_var.set(config["fov"])
        self.aim_height_var.set(config["aim_height"])
        self.lock_radius_var.set(config["lock_radius_px"])
        self.track_tolerance_var.set(config["track_tolerance_px"])
        self.kp_var.set(config["kp"])
        self.ki_var.set(config["ki"])
        self.kd_var.set(config["kd"])
        self.xy_sens_var.set(config["xy_sens"])
        self.targeting_sens_var.set(config["targeting_sens"])

    def apply_and_save_settings(self):
        settings = {
            "show_fov_box": self.show_fov_box_var.get(),
            "fov": self.fov_var.get(),
            "aim_height": self.aim_height_var.get(),
            "lock_radius_px": self.lock_radius_var.get(),
            "track_tolerance_px": self.track_tolerance_var.get(),
            "kp": self.kp_var.get(),
            "ki": self.ki_var.get(),
            "kd": self.kd_var.get(),
            "xy_sens": self.xy_sens_var.get(),
            "targeting_sens": self.targeting_sens_var.get()
        }
        if self.aimbot:
            self.aimbot.apply_settings(settings)
            self.config_manager.save_settings(settings)
            print(colored("[INFO] Settings saved to config.json!", "green"))
