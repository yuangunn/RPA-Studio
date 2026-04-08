from __future__ import annotations
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QListWidget, QListWidgetItem, QPushButton, QLabel,
    QComboBox, QTimeEdit, QSpinBox, QLineEdit, QGroupBox,
    QFormLayout, QCheckBox, QMessageBox, QFileDialog,
)
from PyQt6.QtCore import Qt, QTime
from rpa_studio.locale_kr import LABELS


class ScheduleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(LABELS["schedule_title"])
        self.setMinimumSize(500, 400)
        # Style inherited from global DARK_THEME via parent
        from rpa_studio.gui.style import DARK_THEME
        self.setStyleSheet(DARK_THEME)

        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        tabs.addTab(self._build_schedule_tab(), "\U0001f4c5 \uc2a4\ucf00\uc904")
        tabs.addTab(self._build_trigger_tab(), "\u26a1 \ud2b8\ub9ac\uac70")
        layout.addWidget(tabs)

        close_btn = QPushButton("\ub2eb\uae30")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def _build_schedule_tab(self) -> QWidget:
        w = QWidget()
        layout = QHBoxLayout(w)

        # Left: schedule list
        left = QVBoxLayout()
        self._schedule_list = QListWidget()
        left.addWidget(QLabel("\ub4f1\ub85d\ub41c \uc2a4\ucf00\uc904"))
        left.addWidget(self._schedule_list)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("+ \ucd94\uac00")
        add_btn.clicked.connect(self._add_schedule)
        del_btn = QPushButton("\uc0ad\uc81c")
        del_btn.clicked.connect(self._remove_schedule)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(del_btn)
        left.addLayout(btn_row)
        layout.addLayout(left)

        # Right: schedule form
        right = QVBoxLayout()
        form_group = QGroupBox("\uc0c8 \uc2a4\ucf00\uc904")
        form = QFormLayout(form_group)

        self._sched_name = QLineEdit()
        self._sched_name.setPlaceholderText("\uc2a4\ucf00\uc904 \uc774\ub984")
        form.addRow("\uc774\ub984:", self._sched_name)

        self._sched_type = QComboBox()
        self._sched_type.addItems([LABELS["schedule_daily"], LABELS["schedule_weekly"], LABELS["schedule_monthly"]])
        form.addRow("\uc8fc\uae30:", self._sched_type)

        self._sched_day = QSpinBox()
        self._sched_day.setRange(1, 31)
        self._sched_day.setValue(1)
        form.addRow("\ub0a0\uc9dc (\ub9e4\uc6d4):", self._sched_day)

        self._sched_time = QTimeEdit()
        self._sched_time.setTime(QTime(9, 0))
        self._sched_time.setDisplayFormat("HH:mm")
        form.addRow("\uc2dc\uac04:", self._sched_time)

        self._sched_enabled = QCheckBox("\ud65c\uc131\ud654")
        self._sched_enabled.setChecked(True)
        form.addRow(self._sched_enabled)

        right.addWidget(form_group)
        right.addStretch()
        layout.addLayout(right)

        return w

    def _build_trigger_tab(self) -> QWidget:
        w = QWidget()
        layout = QHBoxLayout(w)

        left = QVBoxLayout()
        self._trigger_list = QListWidget()
        left.addWidget(QLabel("\ub4f1\ub85d\ub41c \ud2b8\ub9ac\uac70"))
        left.addWidget(self._trigger_list)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("+ \ucd94\uac00")
        add_btn.clicked.connect(self._add_trigger)
        del_btn = QPushButton("\uc0ad\uc81c")
        del_btn.clicked.connect(self._remove_trigger)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(del_btn)
        left.addLayout(btn_row)
        layout.addLayout(left)

        right = QVBoxLayout()
        form_group = QGroupBox("\uc0c8 \ud2b8\ub9ac\uac70")
        form = QFormLayout(form_group)

        self._trigger_type = QComboBox()
        self._trigger_type.addItems(["\uc571 \uc2e4\ud589 \uac10\uc9c0", "\ud30c\uc77c \uc0dd\uc131 \uac10\uc9c0"])
        form.addRow("\uc720\ud615:", self._trigger_type)

        self._trigger_value = QLineEdit()
        self._trigger_value.setPlaceholderText("\uc571 \uc774\ub984 \ub610\ub294 \ud30c\uc77c \ud328\ud134")
        form.addRow("\uc870\uac74:", self._trigger_value)

        self._trigger_dir = QLineEdit()
        self._trigger_dir.setPlaceholderText("\uac10\uc2dc\ud560 \ud3f4\ub354 (\ud30c\uc77c \ud2b8\ub9ac\uac70\uc6a9)")
        form.addRow("\ud3f4\ub354:", self._trigger_dir)

        right.addWidget(form_group)
        right.addStretch()
        layout.addLayout(right)

        return w

    def _add_schedule(self):
        name = self._sched_name.text().strip()
        if not name:
            QMessageBox.warning(self, "\uc54c\ub9bc", "\uc2a4\ucf00\uc904 \uc774\ub984\uc744 \uc785\ub825\ud574\uc8fc\uc138\uc694.")
            return
        time_str = self._sched_time.time().toString("HH:mm")
        stype = ["daily", "weekly", "monthly"][self._sched_type.currentIndex()]
        item = QListWidgetItem(f"{name} \u2014 {stype} {time_str}")
        item.setData(Qt.ItemDataRole.UserRole, {
            "name": name, "type": stype,
            "time": time_str, "day": self._sched_day.value(),
            "enabled": self._sched_enabled.isChecked(),
        })
        self._schedule_list.addItem(item)
        self._sched_name.clear()

    def _remove_schedule(self):
        row = self._schedule_list.currentRow()
        if row >= 0:
            self._schedule_list.takeItem(row)

    def _add_trigger(self):
        value = self._trigger_value.text().strip()
        if not value:
            QMessageBox.warning(self, "\uc54c\ub9bc", "\uc870\uac74\uc744 \uc785\ub825\ud574\uc8fc\uc138\uc694.")
            return
        ttype = "app" if self._trigger_type.currentIndex() == 0 else "file"
        label = f"{'\uc571 \uac10\uc9c0' if ttype == 'app' else '\ud30c\uc77c \uac10\uc9c0'}: {value}"
        item = QListWidgetItem(label)
        item.setData(Qt.ItemDataRole.UserRole, {
            "type": ttype, "value": value,
            "watch_dir": self._trigger_dir.text().strip(),
        })
        self._trigger_list.addItem(item)
        self._trigger_value.clear()

    def _remove_trigger(self):
        row = self._trigger_list.currentRow()
        if row >= 0:
            self._trigger_list.takeItem(row)

    def get_schedules(self) -> list[dict]:
        result = []
        for i in range(self._schedule_list.count()):
            data = self._schedule_list.item(i).data(Qt.ItemDataRole.UserRole)
            if data:
                result.append(data)
        return result

    def get_triggers(self) -> list[dict]:
        result = []
        for i in range(self._trigger_list.count()):
            data = self._trigger_list.item(i).data(Qt.ItemDataRole.UserRole)
            if data:
                result.append(data)
        return result
