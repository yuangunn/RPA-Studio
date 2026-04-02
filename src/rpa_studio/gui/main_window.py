from __future__ import annotations

from PyQt6.QtWidgets import (
    QMainWindow, QToolBar, QPushButton, QWidget, QLabel,
    QDockWidget, QVBoxLayout, QFileDialog, QMessageBox,
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence, QUndoStack

from rpa_studio.gui.style import DARK_THEME
from rpa_studio.gui.action_palette import ActionPalette
from rpa_studio.gui.step_editor import StepEditor
from rpa_studio.gui.log_panel import LogPanel
from rpa_studio.gui.property_panel import PropertyPanel
from rpa_studio.gui.execution_thread import ExecutionThread
from rpa_studio.locale_kr import LABELS
from rpa_studio.models import Project


class MainWindow(QMainWindow):
    mode_changed = pyqtSignal(bool)  # True = advanced

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🤖 RPA Studio")
        self.setMinimumSize(1100, 700)
        self.setStyleSheet(DARK_THEME)

        self._undo_stack = QUndoStack(self)
        self._advanced_mode = False
        self._project = Project(name="새 프로젝트")
        self._project_path = None
        self._exec_thread: ExecutionThread | None = None

        self._setup_toolbar()
        self._setup_central()
        self._setup_docks()
        self._setup_shortcuts()

    def _setup_toolbar(self):
        tb = QToolBar("Main")
        tb.setMovable(False)
        tb.setIconSize(QSize(16, 16))
        self.addToolBar(tb)

        self._run_btn = QPushButton(LABELS["run"])
        self._run_btn.setObjectName("runBtn")
        self._run_btn.clicked.connect(self._on_run)
        self._stop_btn = QPushButton(LABELS["stop"])
        self._stop_btn.setObjectName("stopBtn")
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self._on_stop)
        self._record_btn = QPushButton(LABELS["record"])
        self._record_btn.setObjectName("recordBtn")
        self._record_btn.clicked.connect(self._on_record)

        tb.addWidget(self._run_btn)
        tb.addWidget(self._stop_btn)
        tb.addWidget(self._record_btn)
        tb.addSeparator()

        self._mode_btn = QPushButton(LABELS["mode_basic"])
        self._mode_btn.setCheckable(True)
        self._mode_btn.toggled.connect(self._on_mode_toggle)
        tb.addWidget(self._mode_btn)

    def _setup_central(self):
        self._step_editor = StepEditor()
        self.setCentralWidget(self._step_editor)

    def _setup_docks(self):
        # Left: Action Palette
        self._palette_dock = QDockWidget("작업 추가", self)
        self._palette = ActionPalette()
        self._palette_dock.setWidget(self._palette)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._palette_dock)

        # Right: Property Panel
        self._property_dock = QDockWidget(LABELS["prop_title"], self)
        self._property_panel = PropertyPanel()
        self._property_dock.setWidget(self._property_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._property_dock)

        # Connect step selection to property panel
        self._step_editor.step_selected.connect(self._on_step_selected)

        # Bottom: Log Panel
        self._log_dock = QDockWidget(LABELS["log_title"], self)
        self._log_panel = LogPanel()
        self._log_dock.setWidget(self._log_panel)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self._log_dock)

    def _setup_shortcuts(self):
        for text, key, slot in [
            ("Run", "F5", self._on_run),
            ("Stop", "F6", self._on_stop),
            ("Record", "F9", self._on_record),
            ("Save", QKeySequence.StandardKey.Save, self._on_save),
            ("New", QKeySequence.StandardKey.New, self._on_new),
        ]:
            if isinstance(key, str):
                a = QAction(text, self, shortcut=QKeySequence(key), triggered=slot)
            else:
                a = QAction(text, self, shortcut=key, triggered=slot)
            self.addAction(a)

        undo_action = QAction("Undo", self, shortcut=QKeySequence.StandardKey.Undo,
                              triggered=self._undo_stack.undo)
        redo_action = QAction("Redo", self, shortcut=QKeySequence.StandardKey.Redo,
                              triggered=self._undo_stack.redo)
        self.addAction(undo_action)
        self.addAction(redo_action)

    # --- Slots ---

    def _on_run(self):
        self._project.steps = self._step_editor.get_steps()
        if not self._project.steps:
            self._log_panel.append_log("실행할 단계가 없습니다.")
            return

        self._exec_thread = ExecutionThread(self._project, parent=self)
        self._exec_thread.log_message.connect(self._log_panel.append_log)
        self._exec_thread.error_occurred.connect(self._log_panel.append_log)
        self._exec_thread.step_entered.connect(
            lambda sid: self._log_panel.append_log(f"▶ 단계 시작: {sid}")
        )
        self._exec_thread.step_exited.connect(
            lambda sid: self._log_panel.append_log(f"✔ 단계 완료: {sid}")
        )
        self._exec_thread.execution_finished.connect(self._on_execution_finished)

        self._run_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._log_panel.append_log("--- 실행 시작 ---")
        self._exec_thread.start()

    def _on_stop(self):
        if self._exec_thread is not None:
            self._exec_thread.stop()

    def _on_execution_finished(self):
        self._run_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._log_panel.append_log("--- 완료! ---")

    def _on_record(self):
        pass  # Wired in Task 10

    def _on_save(self):
        if not self._project_path:
            path, _ = QFileDialog.getSaveFileName(
                self, "프로젝트 저장", "", "RPA 프로젝트 (*.json)"
            )
            if not path:
                return
            self._project_path = path

        self._project.steps = self._step_editor.get_steps()
        from rpa_studio.project.project_file import save_project
        from pathlib import Path
        save_project(self._project, Path(self._project_path))
        self.statusBar().showMessage("저장 완료!", 3000)

    def _on_new(self):
        self._project = Project(name="새 프로젝트")
        self._project_path = None
        self._step_editor.set_steps([])
        self.setWindowTitle("🤖 RPA Studio — 새 프로젝트")
        self.statusBar().showMessage("새 프로젝트 생성", 3000)

    def _on_step_selected(self, step_id: str):
        step = self._step_editor.get_selected_step()
        self._property_panel.set_step(step)

    def _on_mode_toggle(self, checked: bool):
        self._advanced_mode = checked
        self._mode_btn.setText(
            LABELS["mode_advanced"] if checked else LABELS["mode_basic"]
        )
        self.mode_changed.emit(checked)
