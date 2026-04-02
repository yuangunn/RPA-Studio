from __future__ import annotations
import ctypes
import ctypes.wintypes
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen

try:
    import pywinauto
    from pywinauto import Desktop
    HAS_PYWINAUTO = True
except ImportError:
    HAS_PYWINAUTO = False


class ElementPicker(QWidget):
    """Transparent overlay that highlights UI elements under cursor."""
    element_picked = pyqtSignal(dict)  # element info dict
    cancelled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint |
                         Qt.WindowType.WindowStaysOnTopHint |
                         Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.setCursor(Qt.CursorShape.CrossCursor)

        self._highlight_rect = None
        self._current_info = {}

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_highlight)
        self._timer.setInterval(100)

    def start(self):
        self.show()
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self.hide()

    def _update_highlight(self):
        if not HAS_PYWINAUTO:
            return
        try:
            pos = ctypes.wintypes.POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pos))
            x, y = pos.x, pos.y

            desktop = Desktop(backend="uia")
            element = desktop.from_point(x, y)
            if element:
                rect = element.rectangle()
                self._highlight_rect = (rect.left, rect.top, rect.width(), rect.height())
                self._current_info = {
                    "name": element.element_info.name or "",
                    "control_type": element.element_info.control_type or "",
                    "automation_id": element.element_info.automation_id or "",
                    "class_name": element.element_info.class_name or "",
                }
                self.update()
        except Exception:
            pass

    def paintEvent(self, event):
        if self._highlight_rect:
            painter = QPainter(self)
            pen = QPen(QColor(255, 0, 0), 3)
            painter.setPen(pen)
            painter.setBrush(QColor(255, 0, 0, 30))
            x, y, w, h = self._highlight_rect
            painter.drawRect(x, y, w, h)

            # Label
            painter.setPen(QColor(255, 255, 255))
            info = self._current_info
            label = f"{info.get('name', '')} [{info.get('control_type', '')}]"
            painter.drawText(x + 4, y - 4, label)
            painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.stop()
            if self._current_info:
                self.element_picked.emit(self._current_info)
        elif event.button() == Qt.MouseButton.RightButton:
            self.stop()
            self.cancelled.emit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.stop()
            self.cancelled.emit()
