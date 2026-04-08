from __future__ import annotations
import ctypes
import ctypes.wintypes
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRect
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

try:
    import pywinauto
    from pywinauto import Desktop
    HAS_PYWINAUTO = True
except ImportError:
    HAS_PYWINAUTO = False


class ElementPicker(QWidget):
    """Transparent overlay that highlights UI elements under cursor.

    Covers ALL monitors. Hides itself from UI Automation detection
    by briefly hiding before querying the element.
    """
    element_picked = pyqtSignal(dict)
    cancelled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint |
                         Qt.WindowType.WindowStaysOnTopHint |
                         Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        # Cover ALL monitors
        virtual_geo = self._get_virtual_screen()
        self.setGeometry(virtual_geo)
        self.setCursor(Qt.CursorShape.CrossCursor)

        self._highlight_rect = None
        self._current_info = {}
        self._label_text = ""

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_highlight)
        self._timer.setInterval(150)

    def _get_virtual_screen(self) -> QRect:
        """Get bounding rect of all screens combined."""
        screens = QApplication.screens()
        if not screens:
            return QApplication.primaryScreen().geometry()
        left = min(s.geometry().left() for s in screens)
        top = min(s.geometry().top() for s in screens)
        right = max(s.geometry().right() for s in screens)
        bottom = max(s.geometry().bottom() for s in screens)
        return QRect(left, top, right - left + 1, bottom - top + 1)

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

            # Hide overlay so we don't detect ourselves
            self.hide()
            QApplication.processEvents()

            desktop = Desktop(backend="uia")
            element = desktop.from_point(x, y)

            # Re-show overlay
            self.show()

            if element:
                info = element.element_info
                # Skip if it's our own overlay or empty
                name = info.name or ""
                ctrl = info.control_type or ""
                auto_id = info.automation_id or ""
                class_name = info.class_name or ""

                rect = element.rectangle()
                # Convert to overlay coordinates
                geo = self.geometry()
                self._highlight_rect = (
                    rect.left - geo.x(),
                    rect.top - geo.y(),
                    rect.width(),
                    rect.height(),
                )
                self._current_info = {
                    "name": name,
                    "control_type": ctrl,
                    "automation_id": auto_id,
                    "class_name": class_name,
                }
                self._label_text = f"{name} [{ctrl}]" if name else f"[{ctrl}] {class_name}"
                self.update()
        except Exception:
            self.show()  # ensure we're visible even on error

    def paintEvent(self, event):
        painter = QPainter(self)
        # Semi-transparent dark overlay
        painter.fillRect(self.rect(), QColor(0, 0, 0, 40))

        if self._highlight_rect:
            x, y, w, h = self._highlight_rect
            # Clear the highlight area (make it transparent)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(x, y, w, h, QColor(0, 0, 0, 0))
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

            # Red border around element
            pen = QPen(QColor("#f38ba8"), 3)
            painter.setPen(pen)
            painter.setBrush(QColor(243, 139, 168, 30))
            painter.drawRect(x, y, w, h)

            # Label background
            if self._label_text:
                font = QFont("Segoe UI", 10)
                font.setBold(True)
                painter.setFont(font)
                fm = painter.fontMetrics()
                text_w = fm.horizontalAdvance(self._label_text) + 12
                text_h = fm.height() + 8
                label_y = y - text_h - 4 if y > text_h + 10 else y + h + 4
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor("#1e1e2e"))
                painter.drawRoundedRect(x, label_y, text_w, text_h, 4, 4)
                painter.setPen(QColor("#cdd6f4"))
                painter.drawText(x + 6, label_y + fm.ascent() + 4, self._label_text)

        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.stop()
            if self._current_info and self._current_info.get("name"):
                self.element_picked.emit(self._current_info)
            else:
                self.cancelled.emit()
        elif event.button() == Qt.MouseButton.RightButton:
            self.stop()
            self.cancelled.emit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.stop()
            self.cancelled.emit()
