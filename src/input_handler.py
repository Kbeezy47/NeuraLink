# src/input_handler.py

from pynput import keyboard

class InputHandler:
    def __init__(self, aimbot_instance):
        self.aimbot = aimbot_instance
        self.listener = keyboard.Listener(on_release=self._on_release)

    def _on_release(self, key):
        if key == keyboard.Key.f1:
            self.aimbot.update_status_aimbot()
        if key == keyboard.Key.f2:
            self.aimbot.clean_up()

    def start(self):
        self.listener.start()

    def stop(self):
        self.listener.stop()