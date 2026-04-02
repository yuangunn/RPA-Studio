from __future__ import annotations
import time
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from rpa_studio.locale_kr import LABELS


class RecorderToolbar(QWidget):
    """Floating toolbar shown during recording."""
    stop_requested = pyqtSignal()
    pause_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint |
                         Qt.WindowType.WindowStaysOnTopHint |
                         Qt.WindowType.Tool)
        self.setFixedHeight(40)
        self.setMinimumWidth(350)
        self.setStyleSheet(
            "QWidget { background: rgba(20, 20, 30, 200); border-radius: 8px; }"
            "QPushButton { color: white; border: 1px solid #555; border-radius: 4px; padding: 4px 12px; }"
            "QLabel { color: white; }"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 4)

        stop_btn = QPushButton(LABELS["rec_stop"])
        stop_btn.setStyleSheet("QPushButton { background: #da3633; }")
        stop_btn.clicked.connect(self.stop_requested.emit)
        layout.addWidget(stop_btn)

        pause_btn = QPushButton(LABELS["rec_pause"])
        pause_btn.clicked.connect(self.pause_requested.emit)
        layout.addWidget(pause_btn)

        layout.addStretch()

        self._time_label = QLabel("녹화 시간: 00:00")
        layout.addWidget(self._time_label)

        self._start_time = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_time)
        self._timer.setInterval(1000)

    def start(self):
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() // 2 - self.width() // 2, 10)
        self.show()
        self._start_time = time.time()
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self.hide()

    def _update_time(self):
        elapsed = int(time.time() - self._start_time)
        mins = elapsed // 60
        secs = elapsed % 60
        self._time_label.setText(f"녹화 시간: {mins:02d}:{secs:02d}")
