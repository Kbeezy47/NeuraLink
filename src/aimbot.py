# src/aimbot.py

import ctypes
import math
import os
import sys
import time
import threading
import dxcam
import numpy as np
import torch
import win32api
from termcolor import colored
from ultralytics import YOLO

from .pid import PID
from .overlay import Overlay

class Aimbot:
    screensize = {'X': ctypes.windll.user32.GetSystemMetrics(0), 'Y': ctypes.windll.user32.GetSystemMetrics(1)}
    screen_x = int(screensize['X'] / 2)
    screen_y = int(screensize['Y'] / 2)
    mouse_dll = None

    def __init__(self, config):
        self.running = True
        self.aimbot_status = colored("ENABLED", 'green')
        self.config = config

        # --- FIX: Initialize all state attributes BEFORE applying settings ---
        self.locked_target = None
        self.overlay = None
        self.restart_capture_flag = False
        self.frame_count = 0
        self.fps_log_interval = 2.0
        self.mouse_delay = 0.0000001
        # --- END FIX ---

        self.apply_settings(self.config) # Apply initial settings

        self.camera = dxcam.create(output_color="BGR")
        if not self.camera:
            print("[!] Failed to initialize DXcam."), sys.exit()
        
        print("[INFO] Loading model...")
        self.model = YOLO('lib/model/aimbot/bo6/s/best.engine', task='detect')
        
        if torch.cuda.is_available():
            print(colored("CUDA ACCELERATION [ENABLED]", "green"))
        else:
            print(colored("[!] CUDA ACCELERATION IS UNAVAILABLE", "red")), sys.exit()
        
        print("[INFO] Priming model...")
        self.model.predict(source=np.zeros((640, 640, 3), dtype=np.uint8), verbose=False)
        print("[INFO] Model primed.")
        
        dll_path = os.path.abspath("lib/mouse/dd40605x64.dll")
        if not os.path.exists(dll_path):
            print(f"ddxoft DLL not found at {dll_path}"), sys.exit()
        Aimbot.mouse_dll = ctypes.WinDLL(dll_path)
        if Aimbot.mouse_dll.DD_btn(0) == 1:
            print(colored('Loaded ddxoft successfully!', 'green'))
        else:
            print(colored('Failed to initialize ddxoft mouse.', 'red'))

        if self.show_fov_box:
            print("[INFO] Creating overlay window...")
            self.create_overlay()
        print("\n[INFO] PRESS 'F1' TO TOGGLE AIMBOT\n[INFO] PRESS 'F2' TO QUIT")

    def create_overlay(self):
        if self.overlay:
            self.overlay.destroy()
        overlay_left = int(Aimbot.screen_x - self.box_constant // 2)
        overlay_top = int(Aimbot.screen_y - self.box_constant // 2)
        self.overlay = Overlay(overlay_left, overlay_top, self.box_constant, self.box_constant)

    def apply_settings(self, new_settings):
        try:
            self.config.update(new_settings)
            self.show_fov_box = bool(self.config["show_fov_box"])
            self.fov = int(self.config["fov"])
            self.aim_height = int(self.config["aim_height"])
            self.LOCK_RADIUS_PX = int(self.config["lock_radius_px"])
            self.TRACK_TOLERANCE_PX = int(self.config["track_tolerance_px"])
            self.Kp = float(self.config["kp"])
            self.Ki = float(self.config["ki"])
            self.Kd = float(self.config["kd"])
            
            self.pid_x = PID(self.Kp, self.Ki, self.Kd)
            self.pid_y = PID(self.Kp, self.Ki, self.Kd)

            xy_sens = float(self.config["xy_sens"])
            targeting_sens = float(self.config["targeting_sens"])
            self.sens_config = {
                "xy_sens": xy_sens, "targeting_sens": targeting_sens,
                "xy_scale": 10 / xy_sens, "targeting_scale": 10 / (targeting_sens * xy_sens)
            }

            new_fov = int(self.config["fov"])
            # Use hasattr to safely check for 'box_constant' on first run
            if hasattr(self, 'box_constant') and self.box_constant != new_fov:
                self.restart_capture_flag = True
                print(colored("[INFO] FOV changed. Capture region will update.", "yellow"))
            
            self.box_constant = new_fov

            if self.show_fov_box:
                self.create_overlay()
            elif self.overlay:
                self.overlay.destroy()
                self.overlay = None
            
            # This message is more useful when settings are changed via GUI
            # We can skip it on initial load.
            if hasattr(self, 'camera'): # 'camera' is a good proxy for 'initialized'
                 print(colored("[INFO] Settings applied successfully!", "green"))

        except KeyError as e:
            print(colored(f"[!] Error applying settings: A setting key was missing: {e}", "red"))
        except Exception as e:
            print(colored(f"[!] Error applying settings: {e}", "red"))

    def update_status_aimbot(self):
        self.aimbot_status = colored("DISABLED", 'red') if "ENABLED" in self.aimbot_status else colored("ENABLED", 'green')
        sys.stdout.write(f"\033[K[!] AIMBOT IS [{self.aimbot_status}]" + "\r")

    def is_aimbot_enabled(self):
        return "ENABLED" in self.aimbot_status
    
    @staticmethod
    def is_targeted():
        return win32api.GetKeyState(0x01) < 0 or win32api.GetKeyState(0x02) < 0

    def move_crosshair(self, x, y):
        if not self.is_targeted(): return
        if math.hypot(x - self.screen_x, y - self.screen_y) <= self.LOCK_RADIUS_PX:
            self.pid_x.reset(), self.pid_y.reset()
            return

        error_x, error_y = x - self.screen_x, y - self.screen_y
        move_x = -self.pid_x.update(error_x) * self.sens_config["targeting_scale"]
        move_y = -self.pid_y.update(error_y) * self.sens_config["targeting_scale"]
        Aimbot.mouse_dll.DD_movR(round(move_x), round(move_y))
        time.sleep(self.mouse_delay)

    def _log_fps(self):
        last_frame_count = 0
        last_log_time = time.perf_counter()
        while self.running:
            time.sleep(self.fps_log_interval)
            current_time = time.perf_counter()
            current_frames = self.frame_count
            elapsed_time = current_time - last_log_time
            frames_processed = current_frames - last_frame_count
            if elapsed_time > 0:
                fps = frames_processed / elapsed_time
                sys.stdout.write(f"\033[K[PERFORMANCE] FPS: {fps:.1f}\n")
                print(f"[!] AIMBOT IS [{self.aimbot_status}]", end="\r")
            last_log_time = current_time
            last_frame_count = current_frames

    def start_processing_loop(self):
        print("[INFO] Beginning screen capture")
        left, top = int(self.screen_x - self.box_constant / 2), int(self.screen_y - self.box_constant / 2)
        region = (left, top, left + self.box_constant, top + self.box_constant)
        self.camera.start(region=region, target_fps=240)

        fps_thread = threading.Thread(target=self._log_fps, daemon=True)
        fps_thread.start()

        while self.running:
            if self.restart_capture_flag:
                self.camera.stop()
                left, top = int(self.screen_x - self.box_constant / 2), int(self.screen_y - self.box_constant / 2)
                region = (left, top, left + self.box_constant, top + self.box_constant)
                self.camera.start(region=region, target_fps=240)
                self.restart_capture_flag = False

            frame = self.camera.get_latest_frame()
            if frame is None: continue

            results = self.model.predict(source=frame, verbose=False)
            self.frame_count += 1
            if not results or len(results[0].boxes) == 0:
                if self.locked_target: self.locked_target = None; self.pid_x.reset(); self.pid_y.reset()
                continue
            
            boxes, confs = results[0].boxes.xyxy.cpu().numpy(), results[0].boxes.conf.cpu().numpy()
            candidates = []
            for i, box in enumerate(boxes):
                if confs[i] > 0.65:
                    x1, y1, x2, y2 = box
                    center_x = (int(x1) + left + int(x2) + left) // 2
                    aim_y = (int(y1) + top) + int((int(y2) - int(y1)) * (self.aim_height / 100.0))
                    candidates.append({"abs_center": (center_x, aim_y), "dist_center": math.hypot(center_x - self.screen_x, aim_y - self.screen_y)})
            
            chosen = None
            if self.locked_target and candidates:
                best_match = min(candidates, key=lambda c: math.hypot(c["abs_center"][0] - self.locked_target["abs_center"][0], c["abs_center"][1] - self.locked_target["abs_center"][1]))
                if math.hypot(best_match["abs_center"][0] - self.locked_target["abs_center"][0], best_match["abs_center"][1] - self.locked_target["abs_center"][1]) < self.TRACK_TOLERANCE_PX:
                    chosen = self.locked_target = best_match
                else: self.locked_target = None
            if not self.locked_target and candidates:
                chosen = self.locked_target = min(candidates, key=lambda c: c["dist_center"])
            if chosen and self.is_aimbot_enabled() and self.is_targeted():
                self.move_crosshair(*chosen["abs_center"])

    def clean_up(self):
        print("\n[INFO] F2 WAS PRESSED. QUITTING...")
        self.running = False
        if self.overlay: self.overlay.destroy()
        if self.camera: self.camera.stop()
        time.sleep(0.5)
        os._exit(0)