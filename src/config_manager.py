# src/config_manager.py

import json
import os

class ConfigManager:
    """Manages loading and saving of application settings."""
    def __init__(self, config_path="lib/config/config.json"):
        self.config_path = config_path
        self.default_settings = {
            "show_fov_box": True,
            "fov": 400,
            "aim_height": 40,
            "lock_radius_px": 2,
            "track_tolerance_px": 25,
            "kp": 0.40,
            "ki": 0.04,
            "kd": 0.35,
            "xy_sens": 5.0,
            "targeting_sens": 0.8
        }
        self.settings = self.load_settings()

    def load_settings(self):
        """Loads settings from the JSON file, using defaults if not found or invalid."""
        try:
            if not os.path.exists("lib/config"):
                os.makedirs("lib/config")
            with open(self.config_path) as f:
                config = json.load(f)
                # Ensure all keys are present, add defaults for missing ones
                for key, value in self.default_settings.items():
                    if key not in config:
                        config[key] = value
                return config
        except (FileNotFoundError, json.JSONDecodeError):
            print("[!] config.json not found or invalid. Using default values.")
            return self.default_settings

    def save_settings(self, settings_dict):
        """Saves the provided settings dictionary to the JSON file."""
        self.settings.update(settings_dict)
        with open(self.config_path, 'w') as f:
            json.dump(self.settings, f, indent=4)