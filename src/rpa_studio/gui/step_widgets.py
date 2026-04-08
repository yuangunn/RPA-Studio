from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from rpa_studio.models import Step, ACTION_CATEGORIES, ActionType
from rpa_studio.gui.style import get_step_color

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
        self._accent = get_step_color(step.type.value)
        self.setMinimumHeight(48)
        self.setMaximumHeight(56)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("StepWidget")

        outer = QHBoxLayout(self)
        outer.setContentsMargins(indent * 28, 2, 0, 2)
        outer.setSpacing(0)

        # Left color bar
        self._color_bar = QFrame()
        self._color_bar.setFixedWidth(4)
        self._color_bar.setStyleSheet(f"background-color: {self._accent}; border-radius: 2px;")
        outer.addWidget(self._color_bar)

        # Main content area
        content = QWidget()
        content.setObjectName("StepContent")
        layout = QHBoxLayout(content)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(10)

        # Step number badge
        num_label = QLabel(str(index))
        num_label.setFixedSize(26, 26)
        num_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        num_label.setStyleSheet(
            f"background-color: {self._accent}22; color: {self._accent}; "
            f"border-radius: 13px; font-size: 11px; font-weight: 700;"
        )
        layout.addWidget(num_label)

        # Icon
        icon = QLabel(_CATEGORY_ICONS.get(step.type, "\u2699\ufe0f"))
        icon.setFixedWidth(20)
        icon.setStyleSheet("font-size: 14px;")
        layout.addWidget(icon)

        # Text info (stacked: name on top, summary below)
        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(1)

        name = QLabel(step.label)
        name.setStyleSheet("color: #cdd6f4; font-size: 13px; font-weight: 600;")
        text_col.addWidget(name)

        summary = self._make_summary(step)
        if summary:
            s = QLabel(summary)
            s.setStyleSheet("color: #6c7086; font-size: 11px;")
            s.setMaximumWidth(400)
            text_col.addWidget(s)

        layout.addLayout(text_col, stretch=1)

        # Drag handle
        handle = QLabel("\u2261")  # ≡
        handle.setStyleSheet("color: #45475a; font-size: 18px;")
        handle.setCursor(Qt.CursorShape.OpenHandCursor)
        layout.addWidget(handle)

        outer.addWidget(content, stretch=1)
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
            return f"{p.get('seconds', 1)}\ucd08 \ub300\uae30"
        if step.type == ActionType.LOOP:
            return f"{p.get('count', 1)}\ud68c \ubc18\ubcf5"
        if step.type == ActionType.EXCEL_WRITE:
            return p.get("file_path", "")
        if step.type == ActionType.NOTIFY:
            msg = p.get("message", "")
            return msg[:30] if msg else ""
        if step.type == ActionType.BROWSER_URL:
            return p.get("url", "")
        if step.type == ActionType.BROWSER_OPEN:
            return p.get("browser", "chrome")
        return ""

    def mousePressEvent(self, event):
        self._drag_start_pos = event.position().toPoint()
        self.clicked.emit(self.step.id)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, '_drag_start_pos'):
            from PyQt6.QtWidgets import QApplication
            if (event.position().toPoint() - self._drag_start_pos).manhattanLength() < QApplication.startDragDistance():
                return
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
        if self._selected:
            bg = "#313244"
            border = self._accent
        else:
            bg = "#181825"
            border = "#313244"
        self.setStyleSheet(
            f"#StepContent {{ background: {bg}; border: 1px solid {border}; "
            f"border-radius: 10px; }}"
        )
