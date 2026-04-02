from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from rpa_studio.models import Step, ActionType, LOCKED_ACTIONS
from rpa_studio.gui.step_widgets import StepWidget
from rpa_studio.locale_kr import LABELS


class StepEditor(QWidget):
    step_selected = pyqtSignal(str)
    steps_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._steps: list[Step] = []
        self._widgets: list[StepWidget] = []
        self._selected_id: str | None = None
        self._drag_source_id: str | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)

        self._header = QLabel("\U0001f4cb \uc0c8 \ud504\ub85c\uc81d\ud2b8")
        self._header.setStyleSheet("color: #c9d1d9; font-size: 14px; font-weight: bold;")
        layout.addWidget(self._header)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self._scroll.setAcceptDrops(True)
        self._step_container = QWidget()
        self._step_container.setAcceptDrops(True)
        self._step_layout = QVBoxLayout(self._step_container)
        self._step_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._step_layout.setSpacing(4)
        self._scroll.setWidget(self._step_container)
        layout.addWidget(self._scroll, stretch=1)

        # Override scroll area drag/drop to forward to us
        self._scroll.dragEnterEvent = self.dragEnterEvent
        self._scroll.dropEvent = self.dropEvent
        self._step_container.dragEnterEvent = self.dragEnterEvent
        self._step_container.dropEvent = self.dropEvent

        add_btn = QPushButton(LABELS["add_step"])
        add_btn.setStyleSheet("QPushButton { border: 2px dashed #30363d; padding: 12px; color: #484f58; }")
        layout.addWidget(add_btn)

        self.setAcceptDrops(True)

    def set_project_name(self, name: str):
        self._header.setText(f"\U0001f4cb {name}")

    def set_steps(self, steps: list[Step]):
        self._steps = steps
        self._rebuild()

    def add_step(self, step: Step, index: int | None = None):
        if index is None:
            self._steps.append(step)
        else:
            self._steps.insert(index, step)
        self._rebuild()
        self.steps_changed.emit()

    def remove_step(self, step_id: str):
        self._steps = [s for s in self._steps if s.id != step_id]
        self._rebuild()
        self.steps_changed.emit()

    def move_step(self, step_id: str, direction: int):
        for i, s in enumerate(self._steps):
            if s.id == step_id:
                new_i = i + direction
                if 0 <= new_i < len(self._steps):
                    self._steps[i], self._steps[new_i] = self._steps[new_i], self._steps[i]
                    self._rebuild()
                    self.steps_changed.emit()
                return

    def get_steps(self) -> list[Step]:
        return list(self._steps)

    def get_selected_step(self) -> Step | None:
        for s in self._steps:
            if s.id == self._selected_id:
                return s
            for c in s.children:
                if c.id == self._selected_id:
                    return c
        return None

    def _rebuild(self):
        for w in self._widgets:
            self._step_layout.removeWidget(w)
            w.deleteLater()
        self._widgets.clear()

        idx = 1
        for step in self._steps:
            self._add_step_widget(step, idx, indent=0)
            idx += 1
            for ci, child in enumerate(step.children):
                self._add_step_widget(child, f"{idx-1}-{ci+1}", indent=1)

    def _add_step_widget(self, step: Step, index, indent: int):
        w = StepWidget(step, index, indent=indent)
        w.clicked.connect(self._on_step_clicked)
        if step.id == self._selected_id:
            w.set_selected(True)
        self._step_layout.addWidget(w)
        self._widgets.append(w)

    def _on_step_clicked(self, step_id: str):
        self._selected_id = step_id
        for w in self._widgets:
            w.set_selected(w.step.id == step_id)
        self.step_selected.emit(step_id)

    def keyPressEvent(self, event):
        if self._selected_id:
            if event.key() == Qt.Key.Key_Delete:
                self.remove_step(self._selected_id)
                return
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                if event.key() == Qt.Key.Key_Up:
                    self.move_step(self._selected_id, -1)
                    return
                if event.key() == Qt.Key.Key_Down:
                    self.move_step(self._selected_id, 1)
                    return
        super().keyPressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        text = event.mimeData().text()

        # Internal reorder
        if text.startswith("step_reorder:"):
            step_id = text.split(":", 1)[1]
            # Find drop position based on mouse Y
            drop_index = self._get_drop_index(event.position().y())
            self._reorder_step(step_id, drop_index)
            return

        # Palette drop (existing logic)
        try:
            from rpa_studio.models import ActionType, LOCKED_ACTIONS, Step
            action_type = ActionType(text)
        except ValueError:
            return
        if action_type in LOCKED_ACTIONS:
            from PyQt6.QtWidgets import QMessageBox
            from rpa_studio.locale_kr import LABELS
            QMessageBox.information(self, "알림", LABELS["locked_msg"])
            return
        step = Step(type=action_type)
        self.add_step(step)

    def _get_drop_index(self, y: float) -> int:
        """Determine insertion index based on drop Y position."""
        for i, w in enumerate(self._widgets):
            widget_center = w.y() + w.height() / 2
            if y < widget_center:
                return i
        return len(self._steps)

    def _reorder_step(self, step_id: str, new_index: int):
        """Move a step to a new position."""
        old_index = None
        for i, s in enumerate(self._steps):
            if s.id == step_id:
                old_index = i
                break
        if old_index is None:
            return
        step = self._steps.pop(old_index)
        if new_index > old_index:
            new_index -= 1
        new_index = max(0, min(new_index, len(self._steps)))
        self._steps.insert(new_index, step)
        self._rebuild()
        self.steps_changed.emit()
