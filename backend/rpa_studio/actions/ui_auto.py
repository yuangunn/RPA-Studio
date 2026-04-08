from __future__ import annotations
from rpa_studio.actions.base import ActionHandler
from rpa_studio.models import ActionType, Step
from rpa_studio.engine.context import ExecutionContext

class UIClickHandler(ActionHandler):
    action_type = ActionType.UI_CLICK
    def execute(self, step: Step, context: ExecutionContext):
        import pywinauto
        element_info = step.params.get("element_info", {})
        window_title = context.resolve(step.params.get("window_title", ""))
        click_type = step.params.get("click_type", "left")
        context.add_log(f"UI 요소 클릭: {step.params.get('element_path', '')}")
        app = pywinauto.Application(backend="uia").connect(title_re=f".*{window_title}.*")
        win = app.top_window()
        element = self._find_element(win, element_info)
        if click_type == "left": element.click_input()
        elif click_type == "right": element.click_input(button="right")
        elif click_type == "double": element.double_click_input()
        return {"clicked": True}

    def _find_element(self, window, info: dict):
        auto_id = info.get("automation_id", "")
        if auto_id:
            try:
                return window.child_window(auto_id=auto_id).wrapper_object()
            except Exception:
                pass
        name = info.get("name", "")
        ctrl = info.get("control_type", "")
        if name:
            try:
                return window.child_window(title=name, control_type=ctrl).wrapper_object()
            except Exception:
                pass
        raise RuntimeError(f"요소를 찾을 수 없어요: {info}")

class UITypeHandler(ActionHandler):
    action_type = ActionType.UI_TYPE
    def execute(self, step: Step, context: ExecutionContext):
        import pywinauto
        text = context.resolve(step.params.get("text", ""))
        window_title = context.resolve(step.params.get("window_title", ""))
        element_info = step.params.get("element_info", {})
        context.add_log(f"텍스트 입력: {text[:20]}...")
        app = pywinauto.Application(backend="uia").connect(title_re=f".*{window_title}.*")
        win = app.top_window()
        handler = UIClickHandler()
        element = handler._find_element(win, element_info)
        element.set_text(text)
        return {"typed": text}
