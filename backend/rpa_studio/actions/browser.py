from __future__ import annotations
import subprocess
import webbrowser
from rpa_studio.actions.base import ActionHandler
from rpa_studio.models import ActionType, Step
from rpa_studio.engine.context import ExecutionContext


class BrowserOpenHandler(ActionHandler):
    action_type = ActionType.BROWSER_OPEN
    def execute(self, step: Step, context: ExecutionContext):
        browser = step.params.get("browser", "chrome")
        context.add_log(f"브라우저 열기: {browser}")
        if browser == "chrome":
            try:
                subprocess.Popen(["chrome.exe"])
            except FileNotFoundError:
                try:
                    subprocess.Popen([r"C:\Program Files\Google\Chrome\Application\chrome.exe"])
                except FileNotFoundError:
                    webbrowser.open("")
        elif browser == "edge":
            subprocess.Popen(["msedge.exe"])
        else:
            webbrowser.open("")
        return {"browser": browser}


class BrowserURLHandler(ActionHandler):
    action_type = ActionType.BROWSER_URL
    def execute(self, step: Step, context: ExecutionContext):
        url = context.resolve(step.params.get("url", ""))
        browser = step.params.get("browser", "chrome")
        context.add_log(f"웹사이트 열기: {url} ({browser})")
        if browser == "chrome":
            try:
                subprocess.Popen(["chrome.exe", url])
            except FileNotFoundError:
                try:
                    subprocess.Popen([r"C:\Program Files\Google\Chrome\Application\chrome.exe", url])
                except FileNotFoundError:
                    webbrowser.open(url)
        elif browser == "edge":
            subprocess.Popen(["msedge.exe", url])
        else:
            webbrowser.open(url)
        return {"url": url, "browser": browser}
