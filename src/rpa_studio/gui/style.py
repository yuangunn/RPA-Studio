"""PAD-inspired dark theme for RPA Studio."""

# Category accent colors (left bar on step cards)
CATEGORY_COLORS = {
    "app": "#5c6bc0",      # 앱 조작 — Indigo
    "click": "#ef6c00",    # 클릭 & 입력 — Orange
    "flow": "#ab47bc",     # 흐름 제어 — Purple
    "data": "#26a69a",     # 파일 & 데이터 — Teal
    "browser": "#42a5f5",  # 브라우저 — Blue
    "detect": "#66bb6a",   # 화면 인식 — Green
    "misc": "#78909c",     # 기타 — Blue Gray
}

# Map ActionType category prefix to color key
ACTION_TYPE_COLORS = {
    "app_": "app", "window_": "app",
    "ui_": "click", "hotkey": "click", "mouse_": "click",
    "if_": "flow", "loop": "flow", "wait": "flow", "stop": "flow",
    "excel_": "data", "file_": "data", "folder_": "data",
    "browser_": "browser",
    "image_": "detect", "ocr_": "detect",
    "notify": "misc",
}


def get_step_color(action_type_value: str) -> str:
    """Get accent color for an action type."""
    for prefix, key in ACTION_TYPE_COLORS.items():
        if action_type_value.startswith(prefix):
            return CATEGORY_COLORS[key]
    return CATEGORY_COLORS["misc"]


DARK_THEME = """
/* === Base === */
* {
    font-family: 'Segoe UI', 'Malgun Gothic', sans-serif;
}

QMainWindow {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

/* === Menu Bar === */
QMenuBar {
    background-color: #181825;
    color: #cdd6f4;
    border-bottom: 1px solid #313244;
    padding: 2px 0;
    font-size: 13px;
}
QMenuBar::item {
    padding: 6px 12px;
    border-radius: 4px;
    margin: 2px 2px;
}
QMenuBar::item:selected {
    background-color: #313244;
}
QMenu {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 4px;
}
QMenu::item {
    padding: 8px 24px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #313244;
}
QMenu::separator {
    height: 1px;
    background-color: #313244;
    margin: 4px 8px;
}

/* === Toolbar === */
QToolBar {
    background-color: #181825;
    border-bottom: 1px solid #313244;
    spacing: 8px;
    padding: 6px 12px;
}
QToolBar QWidget {
    background: transparent;
}

/* === Buttons === */
QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #45475a;
    border-color: #585b70;
}
QPushButton:pressed {
    background-color: #585b70;
}
QPushButton:disabled {
    background-color: #1e1e2e;
    color: #585b70;
    border-color: #313244;
}

/* Run / Stop / Record buttons */
QPushButton#runBtn {
    background-color: #a6e3a1;
    color: #1e1e2e;
    border: none;
    font-weight: 600;
}
QPushButton#runBtn:hover {
    background-color: #b4f0a8;
}
QPushButton#runBtn:disabled {
    background-color: #45475a;
    color: #585b70;
}

QPushButton#stopBtn {
    background-color: #f38ba8;
    color: #1e1e2e;
    border: none;
    font-weight: 600;
}
QPushButton#stopBtn:hover {
    background-color: #f5a0b8;
}
QPushButton#stopBtn:disabled {
    background-color: #45475a;
    color: #585b70;
}

QPushButton#recordBtn {
    background-color: #fab387;
    color: #1e1e2e;
    border: none;
    font-weight: 600;
}
QPushButton#recordBtn:hover {
    background-color: #fcc5a0;
}

/* === Dock Widgets === */
QDockWidget {
    color: #a6adc8;
    font-size: 12px;
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
}
QDockWidget::title {
    background-color: #181825;
    padding: 8px 12px;
    border-bottom: 1px solid #313244;
    font-weight: 600;
    font-size: 12px;
}

/* === Tree (Action Palette) === */
QTreeWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border: none;
    outline: none;
    font-size: 13px;
}
QTreeWidget::item {
    padding: 6px 4px;
    border-radius: 4px;
    margin: 1px 4px;
}
QTreeWidget::item:hover {
    background-color: #313244;
}
QTreeWidget::item:selected {
    background-color: #45475a;
    color: #cdd6f4;
}
QTreeWidget::branch {
    background-color: transparent;
}

/* === Inputs === */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    selection-background-color: #585b70;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border-color: #89b4fa;
}
QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 8px;
    selection-background-color: #45475a;
    padding: 4px;
}
QTimeEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 8px;
    padding: 8px 12px;
}

/* === Text Edit (Log) === */
QTextEdit {
    background-color: #11111b;
    color: #a6adc8;
    border: none;
    border-radius: 8px;
    padding: 8px;
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 12px;
}

/* === Labels === */
QLabel {
    color: #a6adc8;
}

/* === Scroll Bars === */
QScrollBar:vertical {
    background-color: transparent;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background-color: #45475a;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: #585b70;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
    height: 0;
}
QScrollBar:horizontal {
    background-color: transparent;
    height: 8px;
}
QScrollBar::handle:horizontal {
    background-color: #45475a;
    border-radius: 4px;
    min-width: 30px;
}

/* === Checkbox === */
QCheckBox {
    color: #cdd6f4;
    spacing: 8px;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #45475a;
    background-color: #313244;
}
QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
}

/* === Group Box === */
QGroupBox {
    color: #a6adc8;
    border: 1px solid #313244;
    border-radius: 8px;
    margin-top: 12px;
    padding: 16px 12px 12px 12px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}

/* === Table (Variable Panel) === */
QTableWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 8px;
    gridline-color: #313244;
    font-size: 13px;
}
QTableWidget::item {
    padding: 6px 8px;
}
QTableWidget::item:selected {
    background-color: #45475a;
}
QHeaderView::section {
    background-color: #181825;
    color: #a6adc8;
    border: none;
    border-bottom: 1px solid #313244;
    border-right: 1px solid #313244;
    padding: 8px;
    font-weight: 600;
    font-size: 12px;
}

/* === List Widget === */
QListWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 8px;
    outline: none;
}
QListWidget::item {
    padding: 8px;
    border-radius: 4px;
    margin: 2px 4px;
}
QListWidget::item:selected {
    background-color: #45475a;
}
QListWidget::item:hover {
    background-color: #313244;
}

/* === Status Bar === */
QStatusBar {
    background-color: #181825;
    color: #a6adc8;
    border-top: 1px solid #313244;
    font-size: 12px;
}

/* === Scroll Area === */
QScrollArea {
    border: none;
    background: transparent;
}

/* === Tab Widget (Schedule Dialog) === */
QTabWidget::pane {
    border: 1px solid #313244;
    background: #1e1e2e;
    border-radius: 0 0 8px 8px;
}
QTabBar::tab {
    background: #181825;
    color: #a6adc8;
    padding: 10px 20px;
    border: 1px solid #313244;
    border-bottom: none;
    font-size: 13px;
}
QTabBar::tab:selected {
    background: #1e1e2e;
    color: #cdd6f4;
    font-weight: 600;
}
QTabBar::tab:hover {
    background: #313244;
}
"""
