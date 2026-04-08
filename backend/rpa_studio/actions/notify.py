from __future__ import annotations
from rpa_studio.actions.base import ActionHandler
from rpa_studio.models import ActionType, Step
from rpa_studio.engine.context import ExecutionContext


def _show_windows_toast(title: str, message: str):
    """Show a Windows 10/11 toast notification."""
    try:
        from ctypes import windll, c_int, c_wchar_p, Structure, POINTER, byref
        # Use PowerShell for reliable toast on Windows 10/11
        import subprocess
        ps_script = f'''
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
        $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
        $textNodes = $template.GetElementsByTagName("text")
        $textNodes.Item(0).AppendChild($template.CreateTextNode("{title}")) > $null
        $textNodes.Item(1).AppendChild($template.CreateTextNode("{message}")) > $null
        $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("RPA Studio").Show($toast)
        '''
        subprocess.Popen(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=0x08000000  # CREATE_NO_WINDOW
        )
    except Exception:
        # Fallback: simple MessageBox
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)
        except Exception:
            pass


class NotifyHandler(ActionHandler):
    action_type = ActionType.NOTIFY

    def execute(self, step: Step, context: ExecutionContext):
        message = context.resolve(step.params.get("message", ""))
        title = step.params.get("title", "RPA Studio")
        context.add_log(f"알림: {message}")

        # Windows toast notification
        _show_windows_toast(title, message)

        return {"message": message, "title": title}
