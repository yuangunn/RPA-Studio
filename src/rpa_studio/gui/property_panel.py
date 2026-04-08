# src/rpa_studio/gui/property_panel.py
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
    QComboBox, QPushButton, QFormLayout, QGroupBox, QScrollArea, QFileDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal
from rpa_studio.models import Step, ActionType
from rpa_studio.locale_kr import LABELS, CLICK_TYPES, WINDOW_ACTIONS, OPERATORS


# Property schemas per action type: list of (param_key, label, widget_type, options)
# widget_type: "text", "int", "float", "combo", "file", "element_picker"
PROPERTY_SCHEMAS: dict[ActionType, list[tuple]] = {
    ActionType.APP_OPEN: [
        ("app_name", "앱 이름", "text", {}),
        ("app_path", "실행 경로 (선택)", "file", {}),
    ],
    ActionType.APP_CLOSE: [
        ("app_name", "앱 이름", "text", {}),
    ],
    ActionType.WINDOW_FOCUS: [
        ("window_title", "창 선택", "window_list", {}),
    ],
    ActionType.WINDOW_RESIZE: [
        ("window_title", "창 선택", "window_list", {}),
        ("action", "동작", "combo", {"choices": WINDOW_ACTIONS}),
    ],
    ActionType.UI_CLICK: [
        ("window_title", "대상 앱 창 제목", "text", {}),
        ("element_path", "요소 경로", "text", {}),
        ("click_type", "클릭 방법", "combo", {"choices": CLICK_TYPES}),
        ("_element_picker", LABELS["pick_element"], "element_picker", {}),
    ],
    ActionType.UI_TYPE: [
        ("window_title", "대상 앱 창 제목", "text", {}),
        ("text", "입력할 텍스트", "text", {}),
        ("_element_picker", LABELS["pick_element"], "element_picker", {}),
    ],
    ActionType.HOTKEY: [
        ("keys", "키 조합 (예: Ctrl+C)", "text", {}),
    ],
    ActionType.MOUSE_MOVE: [
        ("x", "X 좌표", "int", {}),
        ("y", "Y 좌표", "int", {}),
    ],
    ActionType.IF_ELSE: [
        ("left", "비교할 저장값 이름", "text", {}),
        ("operator", "조건", "combo", {"choices": OPERATORS}),
        ("right", "비교 값", "text", {}),
    ],
    ActionType.LOOP: [
        ("count", "반복 횟수", "int", {"min": 1, "max": 99999}),
    ],
    ActionType.WAIT: [
        ("seconds", "대기 시간 (초)", "float", {"min": 0, "max": 3600}),
    ],
    ActionType.STOP: [],
    ActionType.EXCEL_OPEN: [
        ("file_path", "엑셀 파일 경로", "file", {}),
    ],
    ActionType.EXCEL_WRITE: [
        ("file_path", "엑셀 파일 경로", "file", {}),
        ("sheet", "시트 이름", "text", {}),
        ("cell", "셀 (예: A1)", "text", {}),
        ("value", "입력할 값", "text", {}),
    ],
    ActionType.EXCEL_READ: [
        ("file_path", "엑셀 파일 경로", "file", {}),
        ("sheet", "시트 이름", "text", {}),
        ("cell", "셀 (예: A1)", "text", {}),
        ("save_as", "저장값 이름", "text", {}),
    ],
    ActionType.FILE_COPY: [
        ("source", "원본 파일 경로", "file", {}),
        ("destination", "대상 경로", "file", {}),
    ],
    ActionType.FOLDER_CREATE: [
        ("path", "폴더 경로", "text", {}),
    ],
    ActionType.BROWSER_OPEN: [
        ("browser", "브라우저", "combo", {"choices": {"chrome": "Chrome", "edge": "Edge"}}),
    ],
    ActionType.BROWSER_URL: [
        ("url", "웹사이트 주소", "text", {}),
        ("browser", "브라우저", "combo", {"choices": {"chrome": "Chrome", "edge": "Edge"}}),
    ],
    ActionType.IMAGE_SEARCH: [
        ("template_path", "찾을 이미지 파일", "file", {}),
        ("confidence", "정확도 (0~1)", "float", {"min": 0.1, "max": 1.0}),
        ("save_as", "결과 저장값 이름", "text", {}),
    ],
    ActionType.OCR_READ: [
        ("lang", "인식 언어", "combo", {"choices": {"kor+eng": "한국어+영어", "eng": "영어만", "kor": "한국어만"}}),
        ("save_as", "결과 저장값 이름", "text", {}),
    ],
    ActionType.NOTIFY: [
        ("message", "알림 메시지", "text", {}),
    ],
}

HELP_TEXTS: dict[ActionType, str] = {
    ActionType.UI_CLICK: "'요소 선택하기'를 클릭하면 대상 앱 위에서 직접 요소를 선택할 수 있어요.",
    ActionType.UI_TYPE: "텍스트를 입력할 요소를 먼저 선택한 후, 입력할 내용을 적어주세요.",
    ActionType.IF_ELSE: "저장값의 이름을 적고, 어떤 조건으로 비교할지 선택하세요.",
    ActionType.LOOP: "반복할 횟수를 정하면 하위 단계들이 그만큼 반복 실행돼요.",
    ActionType.EXCEL_WRITE: "엑셀 파일이 없으면 자동으로 새로 만들어요.",
}


class PropertyPanel(QWidget):
    params_changed = pyqtSignal()
    pick_element_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._step: Step | None = None
        self._widgets: dict[str, QWidget] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self._title = QLabel(LABELS["prop_title"])
        self._title.setStyleSheet("color: #a6adc8; font-size: 12px; font-weight: 700;")
        layout.addWidget(self._title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        self._form_container = QWidget()
        self._form_layout = QVBoxLayout(self._form_container)
        self._form_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self._form_container)
        layout.addWidget(scroll, stretch=1)

        self._help_box = QGroupBox(LABELS["prop_help"])
        self._help_box.setStyleSheet(
            "QGroupBox { color: #cba6f7; background: #1e1e2e; border: 1px solid #45475a; "
            "border-radius: 10px; padding: 14px; margin-top: 12px; }"
            "QGroupBox::title { color: #cba6f7; font-weight: 600; }"
        )
        help_layout = QVBoxLayout(self._help_box)
        self._help_label = QLabel("")
        self._help_label.setWordWrap(True)
        self._help_label.setStyleSheet("color: #a6adc8; font-size: 12px; line-height: 1.4;")
        help_layout.addWidget(self._help_label)
        layout.addWidget(self._help_box)
        self._help_box.hide()

    def set_step(self, step: Step | None):
        self._step = step
        self._clear_form()
        if not step:
            self._title.setText("단계를 선택하세요")
            self._help_box.hide()
            return

        self._title.setText(f"단계 — {step.label}")
        schema = PROPERTY_SCHEMAS.get(step.type, [])

        # Action type (read-only)
        type_label = QLabel(step.label)
        type_label.setStyleSheet("color: #c9d1d9; background: #161b22; border: 1px solid #30363d; border-radius: 4px; padding: 6px;")
        self._add_field(LABELS["prop_action_type"], type_label)

        # Dynamic fields
        for param_key, label, wtype, opts in schema:
            if param_key.startswith("_"):
                # Special widgets like element picker
                if wtype == "element_picker":
                    btn = QPushButton(label)
                    btn.setStyleSheet(
                        "QPushButton { background: #89b4fa22; color: #89b4fa; "
                        "border: 1px solid #89b4fa44; border-radius: 8px; padding: 10px; font-weight: 600; }"
                        "QPushButton:hover { background: #89b4fa33; border-color: #89b4fa; }"
                    )
                    btn.clicked.connect(self.pick_element_requested.emit)
                    self._form_layout.addWidget(btn)
                continue

            current_val = step.params.get(param_key, opts.get("default", ""))

            if wtype == "text":
                w = QLineEdit(str(current_val))
                w.textChanged.connect(lambda val, k=param_key: self._on_param_changed(k, val))
                self._add_field(label, w)
            elif wtype == "int":
                w = QSpinBox()
                w.setMinimum(opts.get("min", 0))
                w.setMaximum(opts.get("max", 99999))
                w.setValue(int(current_val) if current_val else 0)
                w.valueChanged.connect(lambda val, k=param_key: self._on_param_changed(k, val))
                self._add_field(label, w)
            elif wtype == "float":
                w = QDoubleSpinBox()
                w.setMinimum(opts.get("min", 0.0))
                w.setMaximum(opts.get("max", 3600.0))
                w.setDecimals(1)
                w.setValue(float(current_val) if current_val else 0.0)
                w.valueChanged.connect(lambda val, k=param_key: self._on_param_changed(k, val))
                self._add_field(label, w)
            elif wtype == "combo":
                w = QComboBox()
                choices = opts.get("choices", {})
                for k, v in choices.items():
                    w.addItem(v, k)
                idx = w.findData(current_val)
                if idx >= 0:
                    w.setCurrentIndex(idx)
                w.currentIndexChanged.connect(
                    lambda _, k=param_key, combo=w: self._on_param_changed(k, combo.currentData())
                )
                self._add_field(label, w)
            elif wtype == "window_list":
                container = QWidget()
                vl = QVBoxLayout(container)
                vl.setContentsMargins(0, 0, 0, 0)
                combo = QComboBox()
                combo.setEditable(True)  # allow manual input too
                # Populate with running windows
                self._populate_windows(combo)
                if current_val:
                    combo.setCurrentText(str(current_val))
                combo.currentTextChanged.connect(lambda val, k=param_key: self._on_param_changed(k, val))
                refresh_btn = QPushButton("🔄 새로고침")
                refresh_btn.clicked.connect(lambda _, c=combo: self._populate_windows(c))
                vl.addWidget(combo)
                vl.addWidget(refresh_btn)
                self._add_field(label, container)
                w = combo
            elif wtype == "file":
                container = QWidget()
                hl = QVBoxLayout(container)
                hl.setContentsMargins(0, 0, 0, 0)
                le = QLineEdit(str(current_val))
                le.textChanged.connect(lambda val, k=param_key: self._on_param_changed(k, val))
                browse = QPushButton("📂 찾아보기")
                browse.clicked.connect(lambda _, le=le: self._browse_file(le))
                hl.addWidget(le)
                hl.addWidget(browse)
                self._add_field(label, container)

            self._widgets[param_key] = w

        # Wait after
        wait_spin = QDoubleSpinBox()
        wait_spin.setMinimum(0.0)
        wait_spin.setMaximum(300.0)
        wait_spin.setDecimals(1)
        wait_spin.setSuffix(" 초")
        wait_spin.setValue(step.wait_after)
        wait_spin.valueChanged.connect(self._on_wait_changed)
        self._add_field(LABELS["prop_wait_after"], wait_spin)

        # Help text
        help_text = HELP_TEXTS.get(step.type, "")
        if help_text:
            self._help_label.setText(help_text)
            self._help_box.show()
        else:
            self._help_box.hide()

    def _add_field(self, label: str, widget: QWidget):
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #6c7086; font-size: 11px; font-weight: 600; margin-top: 10px;")
        self._form_layout.addWidget(lbl)
        self._form_layout.addWidget(widget)

    def _clear_form(self):
        self._widgets.clear()
        while self._form_layout.count():
            item = self._form_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _on_param_changed(self, key: str, value):
        if self._step:
            self._step.params[key] = value
            self.params_changed.emit()

    def _on_wait_changed(self, value: float):
        if self._step:
            self._step.wait_after = value

    def _populate_windows(self, combo: QComboBox):
        combo.clear()
        try:
            import win32gui
            titles = []
            def enum_cb(hwnd, _):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title and title.strip() and title not in ("Program Manager", ""):
                        titles.append(title)
            win32gui.EnumWindows(enum_cb, None)
            for t in sorted(set(titles)):
                combo.addItem(t)
        except ImportError:
            # win32gui 없으면 psutil 프로세스 이름으로 대체
            try:
                import psutil
                seen = set()
                for proc in psutil.process_iter(["name", "pid"]):
                    name = proc.info["name"]
                    if name and name not in seen and not name.startswith("svc"):
                        seen.add(name)
                        combo.addItem(name)
            except Exception:
                combo.addItem("(창 목록을 가져올 수 없습니다)")
        except Exception as e:
            combo.addItem(f"(오류: {e})")

    def _browse_file(self, line_edit: QLineEdit):
        path, _ = QFileDialog.getOpenFileName(self, "파일 선택")
        if path:
            line_edit.setText(path)

    def update_element_info(self, info: dict):
        """Called by element picker to populate element_info."""
        if self._step:
            self._step.params["element_info"] = info
            self._step.params["element_path"] = info.get("name", "")
            # Update text field if it exists
            w = self._widgets.get("element_path")
            if w and isinstance(w, QLineEdit):
                w.setText(info.get("name", ""))
            self.params_changed.emit()
