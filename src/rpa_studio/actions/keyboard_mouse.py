from __future__ import annotations
from rpa_studio.actions.base import ActionHandler
from rpa_studio.models import ActionType, Step
from rpa_studio.engine.context import ExecutionContext

class HotkeyHandler(ActionHandler):
    action_type = ActionType.HOTKEY
    def execute(self, step: Step, context: ExecutionContext):
        import pyautogui
        keys = step.params.get("keys", "")
        context.add_log(f"단축키: {keys}")
        parts = [k.strip().lower() for k in keys.split("+")]
        pyautogui.hotkey(*parts)
        return {"keys": keys}

class MouseMoveHandler(ActionHandler):
    action_type = ActionType.MOUSE_MOVE
    def execute(self, step: Step, context: ExecutionContext):
        import pyautogui
        x = int(step.params.get("x", 0))
        y = int(step.params.get("y", 0))
        context.add_log(f"마우스 이동: ({x}, {y})")
        pyautogui.moveTo(x, y)
        return {"x": x, "y": y}
