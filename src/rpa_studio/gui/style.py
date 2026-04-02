DARK_THEME = """
QMainWindow, QWidget { background-color: #0d1117; color: #c9d1d9; }
QMenuBar { background-color: #161b22; color: #c9d1d9; }
QMenuBar::item:selected { background-color: #30363d; }
QToolBar { background-color: #161b22; border-bottom: 1px solid #30363d; spacing: 6px; padding: 4px; }
QPushButton { background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px; padding: 5px 14px; }
QPushButton:hover { background-color: #30363d; }
QPushButton#runBtn { background-color: #238636; color: white; }
QPushButton#runBtn:hover { background-color: #2ea043; }
QPushButton#stopBtn { background-color: #da3633; color: white; }
QPushButton#stopBtn:hover { background-color: #f85149; }
QPushButton#recordBtn { background-color: #f85149; color: white; }
QPushButton#recordBtn:hover { background-color: #ff6e6e; }
QDockWidget { color: #8b949e; }
QDockWidget::title { background-color: #161b22; padding: 6px; }
QTreeWidget, QListWidget { background-color: #0d1117; color: #c9d1d9; border: 1px solid #30363d; }
QTreeWidget::item:selected, QListWidget::item:selected { background-color: #1f6feb33; }
QScrollBar:vertical { background-color: #0d1117; width: 8px; }
QScrollBar::handle:vertical { background-color: #30363d; border-radius: 4px; }
QScrollBar:horizontal { background-color: #0d1117; height: 8px; }
QScrollBar::handle:horizontal { background-color: #30363d; border-radius: 4px; }
QLabel { color: #8b949e; }
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #161b22; color: #c9d1d9;
    border: 1px solid #30363d; border-radius: 4px; padding: 6px;
}
QTextEdit { background-color: #0d1117; color: #c9d1d9; border: 1px solid #30363d; }
QCheckBox { color: #c9d1d9; }
QGroupBox { color: #8b949e; border: 1px solid #30363d; border-radius: 4px; margin-top: 8px; padding-top: 16px; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; }
"""
