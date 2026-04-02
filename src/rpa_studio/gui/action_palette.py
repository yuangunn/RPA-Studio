from __future__ import annotations
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMessageBox
from PyQt6.QtCore import Qt, QMimeData, pyqtSignal
from PyQt6.QtGui import QDrag
from rpa_studio.models import ACTION_CATEGORIES, ACTION_LABELS, LOCKED_ACTIONS, ActionType


class ActionPalette(QTreeWidget):
    action_double_clicked = pyqtSignal(str)  # action_type value

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setDragEnabled(True)
        self.setIndentation(16)
        self._build_tree()
        self.itemDoubleClicked.connect(self._on_double_click)

    def _build_tree(self):
        for cat_name, action_types in ACTION_CATEGORIES.items():
            cat_item = QTreeWidgetItem([cat_name])
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemFlag.ItemIsDragEnabled)
            self.addTopLevelItem(cat_item)
            for at in action_types:
                label = ACTION_LABELS[at]
                if at in LOCKED_ACTIONS:
                    label += " \U0001f512"
                child = QTreeWidgetItem([label])
                child.setData(0, Qt.ItemDataRole.UserRole, at.value)
                if at in LOCKED_ACTIONS:
                    child.setFlags(child.flags() & ~Qt.ItemFlag.ItemIsDragEnabled)
                cat_item.addChild(child)
            cat_item.setExpanded(True)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item or not item.data(0, Qt.ItemDataRole.UserRole):
            return
        action_value = item.data(0, Qt.ItemDataRole.UserRole)
        if ActionType(action_value) in LOCKED_ACTIONS:
            return
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(action_value)
        drag.setMimeData(mime)
        drag.exec(Qt.DropAction.CopyAction)

    def _on_double_click(self, item: QTreeWidgetItem, column: int):
        action_value = item.data(0, Qt.ItemDataRole.UserRole)
        if not action_value:
            return
        if ActionType(action_value) in LOCKED_ACTIONS:
            QMessageBox.information(self, "알림", "이 기능은 업데이트 예정입니다.")
            return
        self.action_double_clicked.emit(action_value)
