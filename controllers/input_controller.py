from __future__ import annotations

from pynput import keyboard, mouse


class InputController:
    def __init__(self, root, on_input):
        self.root = root
        self.on_input = on_input
        self.keyboard_listener = None
        self.mouse_listener = None

    def start(self):
        def on_key(key):
            try:
                key_name = key.char.lower() if hasattr(key, "char") and key.char else key.name.lower()
            except Exception:
                key_name = ""
            self.root.after_idle(lambda: self.on_input("keyboard", key_name))

        def on_click(x, y, button, pressed):
            if not pressed:
                return
            if button == mouse.Button.left:
                name = "คลิกซ้าย"
            elif button == mouse.Button.right:
                name = "คลิกขวา"
            elif button == mouse.Button.middle:
                name = "คลิกกลาง"
            else:
                name = "อื่นๆ"
            self.root.after_idle(lambda: self.on_input("mouse", name))

        self.keyboard_listener = keyboard.Listener(on_press=on_key, daemon=True)
        self.mouse_listener = mouse.Listener(on_click=on_click, daemon=True)
        self.keyboard_listener.start()
        self.mouse_listener.start()

    def stop(self):
        for listener in (self.keyboard_listener, self.mouse_listener):
            try:
                if listener:
                    listener.stop()
            except Exception:
                pass
