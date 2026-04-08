from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QAbstractItemView,
)
from PyQt6.QtCore import Qt, pyqtSignal


class VariablePanel(QWidget):
    """Panel for managing project variables (저장값)."""
    variables_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        header = QLabel("\U0001f4e6 \uc800\uc7a5\uac12 \uad00\ub9ac")
        header.setStyleSheet("color: #a6adc8; font-size: 12px; font-weight: 700;")
        layout.addWidget(header)

        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["이름", "값"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setStyleSheet("""
            QTableWidget { background: #1e1e2e; color: #cdd6f4; border: 1px solid #313244; gridline-color: #313244; }
            QTableWidget::item { color: #cdd6f4; padding: 6px; }
            QTableWidget::item:selected { background: #45475a; color: #cdd6f4; }
            QLineEdit { background: #313244; color: #cdd6f4; border: 1px solid #89b4fa; padding: 4px; }
        """)
        self._table.cellChanged.connect(self._on_cell_changed)
        layout.addWidget(self._table)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("+ \ucd94\uac00")
        add_btn.setStyleSheet(
            "QPushButton { background: #a6e3a1; color: #1e1e2e; border: none; "
            "border-radius: 8px; padding: 6px 14px; font-weight: 600; }"
            "QPushButton:hover { background: #b4f0a8; }"
        )
        add_btn.clicked.connect(self._add_variable)
        del_btn = QPushButton("\uc0ad\uc81c")
        del_btn.setStyleSheet(
            "QPushButton { background: #f38ba8; color: #1e1e2e; border: none; "
            "border-radius: 8px; padding: 6px 14px; font-weight: 600; }"
            "QPushButton:hover { background: #f5a0b8; }"
        )
        del_btn.clicked.connect(self._delete_variable)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(del_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def set_variables(self, variables: dict):
        self._table.blockSignals(True)
        self._table.setRowCount(0)
        for name, value in variables.items():
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(str(name)))
            self._table.setItem(row, 1, QTableWidgetItem(str(value)))
        self._table.blockSignals(False)

    def get_variables(self) -> dict:
        result = {}
        for row in range(self._table.rowCount()):
            name_item = self._table.item(row, 0)
            value_item = self._table.item(row, 1)
            if name_item and name_item.text().strip():
                val = value_item.text() if value_item else ""
                # Auto type inference
                try:
                    val = int(val)
                except ValueError:
                    try:
                        val = float(val)
                    except ValueError:
                        pass
                result[name_item.text().strip()] = val
        return result

    def _add_variable(self):
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.setItem(row, 0, QTableWidgetItem(f"값{row + 1}"))
        self._table.setItem(row, 1, QTableWidgetItem(""))
        self._table.editItem(self._table.item(row, 0))

    def _delete_variable(self):
        rows = set(idx.row() for idx in self._table.selectedIndexes())
        for row in sorted(rows, reverse=True):
            self._table.removeRow(row)
        self._emit_changes()

    def _on_cell_changed(self, row, col):
        self._emit_changes()

    def _emit_changes(self):
        self.variables_changed.emit(self.get_variables())
