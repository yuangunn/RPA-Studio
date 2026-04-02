from __future__ import annotations
import subprocess
import psutil
from rpa_studio.actions.base import ActionHandler
from rpa_studio.models import ActionType, Step
from rpa_studio.engine.context import ExecutionContext

APP_NAME_MAP = {
    "microsoft teams": "Teams.exe",
    "teams": "Teams.exe",
    "메모장": "notepad.exe",
    "notepad": "notepad.exe",
    "계산기": "calc.exe",
    "calculator": "calc.exe",
    "excel": "EXCEL.EXE",
    "엑셀": "EXCEL.EXE",
    "word": "WINWORD.EXE",
    "워드": "WINWORD.EXE",
    "chrome": "chrome.exe",
    "크롬": "chrome.exe",
    "edge": "msedge.exe",
}

class AppOpenHandler(ActionHandler):
    action_type = ActionType.APP_OPEN
    def execute(self, step: Step, context: ExecutionContext):
        app_input = context.resolve(step.params.get("app_path", step.params.get("app_name", "")))
        app = APP_NAME_MAP.get(app_input.lower(), app_input)
        context.add_log(f"앱 열기: {app}")
        try:
            subprocess.Popen(app)
        except FileNotFoundError:
            subprocess.Popen(["cmd", "/c", "start", "", app])
        return {"app": app}

class AppCloseHandler(ActionHandler):
    action_type = ActionType.APP_CLOSE
    def execute(self, step: Step, context: ExecutionContext):
        app_name = context.resolve(step.params.get("app_name", ""))
        context.add_log(f"앱 닫기: {app_name}")
        for proc in psutil.process_iter(["name"]):
            if app_name.lower() in proc.info["name"].lower():
                proc.terminate()
                return {"terminated": proc.info["name"]}
        return {"terminated": None}

class WindowFocusHandler(ActionHandler):
    action_type = ActionType.WINDOW_FOCUS
    def execute(self, step: Step, context: ExecutionContext):
        import pywinauto
        title = context.resolve(step.params.get("window_title", ""))
        context.add_log(f"창 전환: {title}")
        app = pywinauto.Application(backend="uia").connect(title_re=f".*{title}.*")
        win = app.top_window()
        win.set_focus()
        return {"focused": title}

class WindowResizeHandler(ActionHandler):
    action_type = ActionType.WINDOW_RESIZE
    def execute(self, step: Step, context: ExecutionContext):
        import pywinauto
        title = context.resolve(step.params.get("window_title", ""))
        action = step.params.get("action", "maximize")
        context.add_log(f"창 크기 조절: {title} → {action}")
        app = pywinauto.Application(backend="uia").connect(title_re=f".*{title}.*")
        win = app.top_window()
        if action == "maximize": win.maximize()
        elif action == "minimize": win.minimize()
        elif action == "restore": win.restore()
        return {"action": action}
