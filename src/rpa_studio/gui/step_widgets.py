from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from rpa_studio.models import Step, ACTION_CATEGORIES, ActionType

_CATEGORY_ICONS = {}
for _cat, _actions in ACTION_CATEGORIES.items():
    _emoji = _cat.split()[0]
    for _a in _actions:
        _CATEGORY_ICONS[_a] = _emoji


class StepWidget(QWidget):
    clicked = pyqtSignal(str)
    delete_requested = pyqtSignal(str)

    def __init__(self, step: Step, index, indent: int = 0, parent=None):
        super().__init__(parent)
        self.step = step
        self._selected = False
        self.setMinimumHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("StepWidget")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12 + indent * 32, 4, 12, 4)

        num_label = QLabel(str(index))
        num_label.setFixedWidth(28)
        num_label.setStyleSheet("color: #58a6ff; font-weight: bold; font-size: 12px;")
        layout.addWidget(num_label)

        icon = QLabel(_CATEGORY_ICONS.get(step.type, "\u2699\ufe0f"))
        icon.setFixedWidth(24)
        layout.addWidget(icon)

        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        name = QLabel(step.label)
        name.setStyleSheet("color: #c9d1d9; font-size: 13px;")
        info_layout.addWidget(name)
        summary = self._make_summary(step)
        if summary:
            s = QLabel(f"\u2014 {summary}")
            s.setStyleSheet("color: #484f58; font-size: 11px;")
            info_layout.addWidget(s)
        info_layout.addStretch()

        info_w = QWidget()
        info_w.setLayout(info_layout)
        layout.addWidget(info_w, stretch=1)

        self._update_style()

    def _make_summary(self, step: Step) -> str:
        p = step.params
        if step.type == ActionType.APP_OPEN:
            return p.get("app_name", "")
        if step.type == ActionType.UI_CLICK:
            return p.get("element_path", "")
        if step.type == ActionType.HOTKEY:
            return p.get("keys", "")
        if step.type == ActionType.WAIT:
            return f"{p.get('seconds', 1)}\ucd08"
        if step.type == ActionType.LOOP:
            return f"{p.get('count', 1)}\ud68c \ubc18\ubcf5"
        if step.type == ActionType.EXCEL_WRITE:
            return p.get("file_path", "")
        if step.type == ActionType.NOTIFY:
            msg = p.get("message", "")
            return msg[:30] if msg else ""
        return ""

    def mousePressEvent(self, event):
        self._drag_start_pos = event.position().toPoint()
        self.clicked.emit(self.step.id)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, '_drag_start_pos'):
            from PyQt6.QtWidgets import QApplication
            if (event.position().toPoint() - self._drag_start_pos).manhattanLength() < QApplication.startDragDistance():
                return  # 최소 이동 거리 미달 — 드래그 시작 안 함
            from PyQt6.QtGui import QDrag
            from PyQt6.QtCore import QMimeData
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(f"step_reorder:{self.step.id}")
            drag.setMimeData(mime)
            drag.exec(Qt.DropAction.MoveAction)
        super().mouseMoveEvent(event)

    def set_selected(self, selected: bool):
        self._selected = selected
        self._update_style()

    def _update_style(self):
        border = "#58a6ff" if self._selected else "#30363d"
        self.setStyleSheet(
            f"#StepWidget {{ background: #161b22; border: 1px solid {border}; border-radius: 6px; }}"
        )
