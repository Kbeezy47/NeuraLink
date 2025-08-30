# src/gui.py

import tkinter as tk
from tkinter import ttk
from termcolor import colored

class SettingsGUI:
    def __init__(self, master, aimbot_instance, config_manager):
        self.master = master
        self.aimbot = aimbot_instance
        self.config_manager = config_manager
        
        master.title("Aimbot Settings")
        master.geometry("600x550")
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text='Aimbot')
        self.notebook.add(self.tab2, text='PID & Sensitivity')
        
        self.create_aimbot_tab()
        self.create_pid_sens_tab()
        
        self.apply_button = ttk.Button(master, text="Save & Apply", command=self.apply_and_save_settings)
        self.apply_button.pack(pady=10)
        
        self.load_initial_values()

    def create_slider(self, parent, text, from_, to, var, resolution=1):
        frame = ttk.Frame(parent)
        label = ttk.Label(frame, text=text, width=25)
        label.pack(side=tk.LEFT, padx=5, pady=5)
        entry = ttk.Entry(frame, textvariable=var, width=10)
        entry.pack(side=tk.LEFT, padx=5)
        command = lambda val: var.set(int(float(val))) if resolution == 1 else var.set(round(float(val), 2))
        slider = ttk.Scale(frame, from_=from_, to=to, orient=tk.HORIZONTAL, variable=var, command=command)
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        frame.pack(fill=tk.X, padx=10, pady=5)

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
        pid_frame.pack(fill=tk.X, padx=10, pady=10)
        self.kp_var = tk.DoubleVar()
        self.ki_var = tk.DoubleVar()
        self.kd_var = tk.DoubleVar()
        self.create_slider(pid_frame, "Kp (Proportional):", 0.0, 2.0, self.kp_var, 0.01)
        self.create_slider(pid_frame, "Ki (Integral):", 0.0, 1.0, self.ki_var, 0.01)
        self.create_slider(pid_frame, "Kd (Derivative):", 0.0, 2.0, self.kd_var, 0.01)
        ttk.Label(pid_frame, text="NOTE: Lower FOV requires lower Kp/Kd values to prevent instability.", foreground="blue").pack(pady=5)
        
        sens_frame = ttk.LabelFrame(self.tab2, text="In-Game Sensitivity")
        sens_frame.pack(fill=tk.X, padx=10, pady=10)
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