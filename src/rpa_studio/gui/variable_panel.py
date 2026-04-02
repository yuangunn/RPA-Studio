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

        header = QLabel("📦 저장값 관리")
        header.setStyleSheet("color: #8b949e; font-size: 11px; font-weight: bold;")
        layout.addWidget(header)

        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["이름", "값"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setStyleSheet(
            "QTableWidget { background: #0d1117; color: #c9d1d9; border: 1px solid #30363d; gridline-color: #30363d; }"
            "QHeaderView::section { background: #161b22; color: #8b949e; border: 1px solid #30363d; padding: 4px; }"
            "QTableWidget::item { padding: 4px; }"
            "QTableWidget::item:selected { background: #1f6feb33; }"
        )
        self._table.cellChanged.connect(self._on_cell_changed)
        layout.addWidget(self._table)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("+ 추가")
        add_btn.setStyleSheet("QPushButton { background: #238636; color: white; border-radius: 4px; padding: 4px 12px; }")
        add_btn.clicked.connect(self._add_variable)
        del_btn = QPushButton("삭제")
        del_btn.setStyleSheet("QPushButton { background: #da3633; color: white; border-radius: 4px; padding: 4px 12px; }")
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
