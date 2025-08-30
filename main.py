# main.py
import os
import threading
import tkinter as tk

from src.aimbot import Aimbot
from src.gui import SettingsGUI
from src.config_manager import ConfigManager
from src.input_handler import InputHandler

def main():
    """Initializes and runs the application components."""
    os.system('cls' if os.name == 'nt' else 'clear')

    # 1. Initialize components
    config_manager = ConfigManager()
    aimbot_instance = Aimbot(config=config_manager.settings)
    input_handler = InputHandler(aimbot_instance=aimbot_instance)

    # 2. Start background services
    input_handler.start()
    aimbot_thread = threading.Thread(target=aimbot_instance.start_processing_loop, daemon=True)
    aimbot_thread.start()

    # 3. Set up and run the GUI
    root = tk.Tk()
    gui = SettingsGUI(root, aimbot_instance, config_manager)

    def overlay_update_loop():
        """Periodically update the overlay window to keep it from freezing."""
        if aimbot_instance and aimbot_instance.overlay:
            aimbot_instance.overlay.update()
        root.after(16, overlay_update_loop) # ~60 FPS update rate

    overlay_update_loop()
    root.mainloop()

if __name__ == "__main__":
    main()