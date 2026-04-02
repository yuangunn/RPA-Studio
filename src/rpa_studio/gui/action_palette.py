from __future__ import annotations
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDrag
from rpa_studio.models import ACTION_CATEGORIES, ACTION_LABELS, LOCKED_ACTIONS, ActionType


class ActionPalette(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setDragEnabled(True)
        self.setIndentation(16)
        self._build_tree()

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
