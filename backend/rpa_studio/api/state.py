"""Application state singleton.

Holds references to the execution engine, recorder, scheduler,
and manages the lifecycle of running executions.
"""
from __future__ import annotations

import asyncio
import threading
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from rpa_studio.engine.executor import StepExecutor
from rpa_studio.engine.context import ExecutionContext
from rpa_studio.engine.recorder import RecorderEngine
from rpa_studio.scheduler.cron import ScheduleManager
from rpa_studio.scheduler.triggers import TriggerManager
from rpa_studio.models import Project


PROJECTS_DIR = Path.home() / ".rpa_studio" / "projects"


@dataclass
class ExecutionInfo:
    execution_id: str
    project_name: str
    executor: StepExecutor
    context: ExecutionContext
    thread: threading.Thread
    queue: asyncio.Queue  # bridges sync callbacks → async WebSocket


class AppState:
    """Singleton holding all application state."""

    def __init__(self):
        self.executions: dict[str, ExecutionInfo] = {}
        self.recorder: RecorderEngine = RecorderEngine()
        self.schedule_manager: ScheduleManager = ScheduleManager()
        self.trigger_manager: TriggerManager = TriggerManager()
        self._lock = threading.Lock()

        # Ensure projects directory exists
        PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

    def start_execution(self, project: Project, loop: asyncio.AbstractEventLoop) -> str:
        """Start executing a project in a background thread.

        Returns execution_id. Callbacks push messages to an asyncio.Queue
        that the WebSocket handler reads from.
        """
        exec_id = uuid.uuid4().hex[:12]
        queue: asyncio.Queue = asyncio.Queue()
        executor = StepExecutor()
        context = ExecutionContext(variables=dict(project.variables))

        def _send(msg: dict):
            """Thread-safe push to async queue."""
            loop.call_soon_threadsafe(queue.put_nowait, msg)

        executor.on_step_enter = lambda s: _send({
            "type": "step_enter",
            "step_id": s.id,
            "step_label": s.label,
        })
        executor.on_step_exit = lambda s, r: _send({
            "type": "step_exit",
            "step_id": s.id,
            "result": str(r) if r else None,
        })
        executor.on_log = lambda msg: _send({
            "type": "log",
            "message": msg,
        })
        executor.on_error = lambda msg: _send({
            "type": "error",
            "message": msg,
        })

        def _run():
            # Import action handlers to register them
            import rpa_studio.actions.app_control
            import rpa_studio.actions.ui_auto
            import rpa_studio.actions.keyboard_mouse
            import rpa_studio.actions.file_ops
            import rpa_studio.actions.excel_ops
            import rpa_studio.actions.browser
            import rpa_studio.actions.image_match
            import rpa_studio.actions.ocr
            import rpa_studio.actions.notify
            import rpa_studio.actions.web_auto

            executor.run(project, context)
            _send({"type": "execution_complete", "success": context.error is None})

        thread = threading.Thread(target=_run, daemon=True)

        info = ExecutionInfo(
            execution_id=exec_id,
            project_name=project.name,
            executor=executor,
            context=context,
            thread=thread,
            queue=queue,
        )

        with self._lock:
            self.executions[exec_id] = info

        thread.start()
        return exec_id

    def stop_execution(self, exec_id: str) -> bool:
        with self._lock:
            info = self.executions.get(exec_id)
        if not info:
            return False
        info.executor.stop()
        return True

    def get_execution(self, exec_id: str) -> Optional[ExecutionInfo]:
        with self._lock:
            return self.executions.get(exec_id)

    def cleanup_execution(self, exec_id: str):
        with self._lock:
            self.executions.pop(exec_id, None)

    def shutdown(self):
        """Clean shutdown of all subsystems."""
        for info in list(self.executions.values()):
            info.executor.stop()
        self.schedule_manager.shutdown()
        self.trigger_manager.stop_all()


# Module-level singleton
app_state = AppState()
