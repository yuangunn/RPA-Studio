from __future__ import annotations
from rpa_studio.actions.base import ActionHandler
from rpa_studio.models import ActionType, Step
from rpa_studio.engine.context import ExecutionContext


def _connect_window(window_title: str):
    """Connect to a window by title. Raises clear error if title is empty."""
    import pywinauto

    if not window_title or not window_title.strip():
        raise RuntimeError(
            "대상 앱 창 제목이 비어있어요. "
            "속성 패널에서 '대상 앱 창 제목' 또는 '창 선택'을 설정해주세요."
        )

    try:
        app = pywinauto.Application(backend="uia").connect(
            title_re=f".*{window_title}.*", timeout=5
        )
        return app.top_window()
    except Exception as e:
        if "no windows" in str(e).lower() or "could not find" in str(e).lower():
            raise RuntimeError(f"'{window_title}' 창을 찾을 수 없어요. 앱이 실행 중인지 확인해주세요.")
        raise RuntimeError(f"창 연결 실패: {e}")


def _find_element(window, info: dict):
    """Find UI element with 3-tier fallback strategy."""
    if not info:
        raise RuntimeError("요소 정보가 없어요. '🎯 요소 선택하기'로 요소를 먼저 선택해주세요.")

    # Tier 1: AutomationId
    auto_id = info.get("automation_id", "")
    if auto_id:
        try:
            return window.child_window(auto_id=auto_id).wrapper_object()
        except Exception:
            pass

    # Tier 2: Name + ControlType
    name = info.get("name", "")
    ctrl = info.get("control_type", "")
    if name:
        try:
            kwargs = {"title": name}
            if ctrl:
                kwargs["control_type"] = ctrl
            return window.child_window(**kwargs).wrapper_object()
        except Exception:
            pass

    # Tier 3: Name only (looser match)
    if name:
        try:
            return window.child_window(title_re=f".*{name}.*").wrapper_object()
        except Exception:
            pass

    raise RuntimeError(
        f"요소를 찾을 수 없어요: {info.get('name', '(이름 없음)')}. "
        f"앱 화면이 바뀌었을 수 있습니다. 요소를 다시 선택해주세요."
    )


class UIClickHandler(ActionHandler):
    action_type = ActionType.UI_CLICK

    def execute(self, step: Step, context: ExecutionContext):
        element_info = step.params.get("element_info", {})
        window_title = context.resolve(step.params.get("window_title", ""))
        click_type = step.params.get("click_type", "left")
        element_path = step.params.get("element_path", "")

        context.add_log(f"UI 요소 클릭: {element_path}")

        win = _connect_window(window_title)
        element = _find_element(win, element_info)

        if click_type == "left":
            element.click_input()
        elif click_type == "right":
            element.click_input(button="right")
        elif click_type == "double":
            element.double_click_input()

        return {"clicked": True, "element": element_path}


class UITypeHandler(ActionHandler):
    action_type = ActionType.UI_TYPE

    def execute(self, step: Step, context: ExecutionContext):
        text = context.resolve(step.params.get("text", ""))
        window_title = context.resolve(step.params.get("window_title", ""))
        element_info = step.params.get("element_info", {})

        context.add_log(f"텍스트 입력: {text[:20]}...")

        win = _connect_window(window_title)
        element = _find_element(win, element_info)
        element.set_text(text)

        return {"typed": text}
