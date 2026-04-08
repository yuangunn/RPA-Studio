from __future__ import annotations
import time
import threading
from typing import Optional
from pynput import mouse, keyboard
from rpa_studio.models import Step, ActionType

try:
    import pywinauto
    from pywinauto import Desktop
    HAS_PYWINAUTO = True
except ImportError:
    HAS_PYWINAUTO = False


class RecorderEngine:
    """Records mouse/keyboard events and converts them to Steps."""

    def __init__(self):
        self._steps: list[Step] = []
        self._running = False
        self._paused = False
        self._last_action_time: float = 0
        self._mouse_listener: Optional[mouse.Listener] = None
        self._key_listener: Optional[keyboard.Listener] = None
        self._key_buffer: list[str] = []
        self._key_timer: Optional[threading.Timer] = None
        self._callbacks: list = []

    def start(self):
        self._steps = []
        self._running = True
        self._paused = False
        self._last_action_time = time.time()

        self._mouse_listener = mouse.Listener(on_click=self._on_mouse_click)
        self._key_listener = keyboard.Listener(on_press=self._on_key_press)
        self._mouse_listener.start()
        self._key_listener.start()

    def stop(self) -> list[Step]:
        self._running = False
        if self._mouse_listener:
            self._mouse_listener.stop()
        if self._key_listener:
            self._key_listener.stop()
        self._flush_key_buffer()
        return list(self._steps)

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False
        self._last_action_time = time.time()

    @property
    def is_running(self) -> bool:
        return self._running

    def _check_idle_gap(self):
        """Insert a wait step if idle for > 3 seconds."""
        now = time.time()
        gap = now - self._last_action_time
        if gap > 3.0:
            self._steps.append(Step(
                type=ActionType.WAIT,
                params={"seconds": round(gap, 1)},
            ))
        self._last_action_time = now

    def _on_mouse_click(self, x, y, button, pressed):
        if not self._running or self._paused or not pressed:
            return

        self._flush_key_buffer()
        self._check_idle_gap()

        # Try to identify UI element at click position
        element_info = {}
        element_path = f"({x}, {y})"
        if HAS_PYWINAUTO:
            try:
                desktop = Desktop(backend="uia")
                element = desktop.from_point(x, y)
                if element:
                    element_info = {
                        "name": element.element_info.name or "",
                        "control_type": element.element_info.control_type or "",
                        "automation_id": element.element_info.automation_id or "",
                        "class_name": element.element_info.class_name or "",
                    }
                    element_path = element.element_info.name or element_path
            except Exception:
                pass

        click_type = "left" if button == mouse.Button.left else "right"
        self._steps.append(Step(
            type=ActionType.UI_CLICK,
            params={
                "element_info": element_info,
                "element_path": element_path,
                "click_type": click_type,
                "x": x,
                "y": y,
            },
            wait_after=0.5,
        ))

    def _on_key_press(self, key):
        if not self._running or self._paused:
            return

        try:
            char = key.char
            if char:
                self._key_buffer.append(char)
                self._reset_key_timer()
                return
        except AttributeError:
            pass

        # Special key
        self._flush_key_buffer()
        self._check_idle_gap()

        key_name = str(key).replace("Key.", "")
        # Check for modifier combos
        if hasattr(key, 'name'):
            key_name = key.name

        self._steps.append(Step(
            type=ActionType.HOTKEY,
            params={"keys": key_name},
        ))

    def _reset_key_timer(self):
        if self._key_timer:
            self._key_timer.cancel()
        self._key_timer = threading.Timer(1.0, self._flush_key_buffer)
        self._key_timer.start()

    def _flush_key_buffer(self):
        if self._key_buffer:
            text = "".join(self._key_buffer)
            self._check_idle_gap()
            self._steps.append(Step(
                type=ActionType.UI_TYPE,
                params={"text": text},
            ))
            self._key_buffer.clear()
        if self._key_timer:
            self._key_timer.cancel()
            self._key_timer = None
