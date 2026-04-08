from __future__ import annotations
import threading
import psutil
from pathlib import Path
from typing import Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent


class AppTrigger:
    """Poll process list to detect when a specific app starts."""

    def __init__(self, process_name: str, callback: Callable, poll_interval: float = 5.0):
        self._process_name = process_name.lower()
        self._callback = callback
        self._poll_interval = poll_interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._was_running = False

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=self._poll_interval + 1)

    def _poll_loop(self):
        import time
        while self._running:
            is_running = self._check_process()
            if is_running and not self._was_running:
                self._callback()
            self._was_running = is_running
            time.sleep(self._poll_interval)

    def _check_process(self) -> bool:
        for proc in psutil.process_iter(["name"]):
            try:
                if self._process_name in proc.info["name"].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False


class _FileCreatedHandler(FileSystemEventHandler):
    def __init__(self, pattern: str, callback: Callable):
        self._pattern = pattern.lower()
        self._callback = callback

    def on_created(self, event):
        if isinstance(event, FileCreatedEvent):
            if self._pattern in event.src_path.lower():
                self._callback(event.src_path)


class FileTrigger:
    """Watch a directory for new files matching a pattern."""

    def __init__(self, watch_dir: str, pattern: str, callback: Callable):
        self._watch_dir = watch_dir
        self._handler = _FileCreatedHandler(pattern, callback)
        self._observer = Observer()

    def start(self):
        self._observer.schedule(self._handler, self._watch_dir, recursive=False)
        self._observer.start()

    def stop(self):
        self._observer.stop()
        self._observer.join(timeout=5)


class TriggerManager:
    """Manages all active triggers."""

    def __init__(self):
        self._triggers: dict[str, AppTrigger | FileTrigger] = {}

    def add_app_trigger(self, trigger_id: str, process_name: str, callback: Callable,
                        poll_interval: float = 5.0) -> None:
        self.remove_trigger(trigger_id)
        t = AppTrigger(process_name, callback, poll_interval)
        self._triggers[trigger_id] = t
        t.start()

    def add_file_trigger(self, trigger_id: str, watch_dir: str, pattern: str,
                         callback: Callable) -> None:
        self.remove_trigger(trigger_id)
        t = FileTrigger(watch_dir, pattern, callback)
        self._triggers[trigger_id] = t
        t.start()

    def remove_trigger(self, trigger_id: str) -> None:
        t = self._triggers.pop(trigger_id, None)
        if t:
            t.stop()

    def stop_all(self) -> None:
        for t in self._triggers.values():
            t.stop()
        self._triggers.clear()
