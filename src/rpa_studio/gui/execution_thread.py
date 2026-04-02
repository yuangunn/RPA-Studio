from __future__ import annotations
from PyQt6.QtCore import QThread, pyqtSignal
from rpa_studio.models import Project, Step
from rpa_studio.engine.executor import StepExecutor
from rpa_studio.engine.context import ExecutionContext
# Import all action modules to register handlers
import rpa_studio.actions.app_control
import rpa_studio.actions.ui_auto
import rpa_studio.actions.keyboard_mouse
import rpa_studio.actions.file_ops
import rpa_studio.actions.excel_ops
import rpa_studio.actions.notify


class ExecutionThread(QThread):
    step_entered = pyqtSignal(str)  # step.id
    step_exited = pyqtSignal(str)   # step.id
    log_message = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    execution_finished = pyqtSignal()

    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self._project = project
        self._executor = StepExecutor()
        self._context = ExecutionContext()

        self._executor.on_step_enter = lambda s: self.step_entered.emit(s.id)
        self._executor.on_step_exit = lambda s, r: self.step_exited.emit(s.id)
        self._executor.on_log = lambda msg: self.log_message.emit(msg)
        self._executor.on_error = lambda msg: self.error_occurred.emit(msg)

    def run(self):
        self._executor.run(self._project, self._context)
        self.execution_finished.emit()

    def stop(self):
        self._executor.stop()

    @property
    def context(self) -> ExecutionContext:
        return self._context
