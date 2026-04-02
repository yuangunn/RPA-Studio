from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from rpa_studio.locale_kr import LABELS


class LogPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        self._log_text.setStyleSheet(
            "QTextEdit { background: #0d1117; color: #c9d1d9; border: none; "
            "font-family: 'Consolas', 'Courier New', monospace; font-size: 12px; }"
        )
        layout.addWidget(self._log_text)

        btn_row = QHBoxLayout()
        clear_btn = QPushButton("지우기")
        clear_btn.clicked.connect(self.clear)
        btn_row.addStretch()
        btn_row.addWidget(clear_btn)
        layout.addLayout(btn_row)

    def append_log(self, message: str):
        self._log_text.append(message)
        sb = self._log_text.verticalScrollBar()
        sb.setValue(sb.maximum())

    def clear(self):
        self._log_text.clear()
