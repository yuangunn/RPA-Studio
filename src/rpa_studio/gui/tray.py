from __future__ import annotations
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import pyqtSignal, QObject
from rpa_studio.locale_kr import LABELS


def _create_default_icon() -> QIcon:
    """Create a simple colored icon since we don't have an icon file."""
    pixmap = QPixmap(32, 32)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    painter.setBrush(QColor("#58a6ff"))
    painter.setPen(QColor("#58a6ff"))
    painter.drawEllipse(2, 2, 28, 28)
    painter.setPen(QColor("white"))
    painter.drawText(pixmap.rect(), 0x0084, "R")  # AlignCenter
    painter.end()
    return QIcon(pixmap)


class SystemTray(QObject):
    open_requested = pyqtSignal()
    schedule_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tray = QSystemTrayIcon(_create_default_icon(), parent)
        self._tray.setToolTip("RPA Studio")

        menu = QMenu()
        open_action = menu.addAction(LABELS["tray_open"])
        open_action.triggered.connect(self.open_requested.emit)

        schedule_action = menu.addAction(LABELS["tray_schedule"])
        schedule_action.triggered.connect(self.schedule_requested.emit)

        menu.addSeparator()

        quit_action = menu.addAction(LABELS["tray_quit"])
        quit_action.triggered.connect(self.quit_requested.emit)

        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_activated)

    def show(self):
        self._tray.show()

    def hide(self):
        self._tray.hide()

    def show_message(self, title: str, message: str):
        self._tray.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 3000)

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.open_requested.emit()
