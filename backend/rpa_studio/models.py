from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ActionType(str, Enum):
    # 앱 조작
    APP_OPEN = "app_open"
    APP_CLOSE = "app_close"
    WINDOW_FOCUS = "window_focus"
    WINDOW_RESIZE = "window_resize"
    # 클릭 & 입력
    UI_CLICK = "ui_click"
    UI_TYPE = "ui_type"
    HOTKEY = "hotkey"
    MOUSE_MOVE = "mouse_move"
    # 흐름 제어
    IF_ELSE = "if_else"
    LOOP = "loop"
    WAIT = "wait"
    STOP = "stop"
    # 파일 & 데이터
    EXCEL_OPEN = "excel_open"
    EXCEL_WRITE = "excel_write"
    EXCEL_READ = "excel_read"
    FILE_COPY = "file_copy"
    FOLDER_CREATE = "folder_create"
    # 화면 인식 (2차)
    IMAGE_SEARCH = "image_search"
    OCR_READ = "ocr_read"
    # 브라우저 (기본)
    BROWSER_OPEN = "browser_open"
    BROWSER_URL = "browser_url"
    # 웹 자동화 (Playwright)
    WEB_OPEN = "web_open"
    WEB_CLICK = "web_click"
    WEB_TYPE = "web_type"
    WEB_NAVIGATE = "web_navigate"
    WEB_EXTRACT = "web_extract"
    WEB_WAIT = "web_wait"
    WEB_CLOSE = "web_close"
    # 기타
    NOTIFY = "notify"


ACTION_LABELS: dict[ActionType, str] = {
    ActionType.APP_OPEN: "앱 열기",
    ActionType.APP_CLOSE: "앱 닫기",
    ActionType.WINDOW_FOCUS: "창 전환",
    ActionType.WINDOW_RESIZE: "창 크기 조절",
    ActionType.UI_CLICK: "UI 요소 클릭",
    ActionType.UI_TYPE: "텍스트 입력",
    ActionType.HOTKEY: "단축키 누르기",
    ActionType.MOUSE_MOVE: "마우스 이동",
    ActionType.IF_ELSE: "만약 ~이면",
    ActionType.LOOP: "반복하기",
    ActionType.WAIT: "기다리기",
    ActionType.STOP: "멈추기",
    ActionType.EXCEL_OPEN: "엑셀 열기",
    ActionType.EXCEL_WRITE: "엑셀에 쓰기",
    ActionType.EXCEL_READ: "엑셀에서 읽기",
    ActionType.FILE_COPY: "파일 복사",
    ActionType.FOLDER_CREATE: "폴더 만들기",
    ActionType.IMAGE_SEARCH: "이미지 찾기",
    ActionType.OCR_READ: "텍스트 읽기(OCR)",
    ActionType.BROWSER_OPEN: "브라우저 열기",
    ActionType.BROWSER_URL: "웹사이트 열기",
    ActionType.WEB_OPEN: "웹 브라우저 시작",
    ActionType.WEB_CLICK: "웹 요소 클릭",
    ActionType.WEB_TYPE: "웹 텍스트 입력",
    ActionType.WEB_NAVIGATE: "웹 페이지 이동",
    ActionType.WEB_EXTRACT: "웹 텍스트 추출",
    ActionType.WEB_WAIT: "웹 요소 대기",
    ActionType.WEB_CLOSE: "웹 브라우저 닫기",
    ActionType.NOTIFY: "알림 보내기",
}

LOCKED_ACTIONS = set()  # All actions now implemented

ACTION_CATEGORIES = {
    "🖥️ 앱 조작": [
        ActionType.APP_OPEN, ActionType.APP_CLOSE,
        ActionType.WINDOW_FOCUS, ActionType.WINDOW_RESIZE,
    ],
    "🖱️ 클릭 & 입력": [
        ActionType.UI_CLICK, ActionType.UI_TYPE,
        ActionType.HOTKEY, ActionType.MOUSE_MOVE,
    ],
    "🔄 흐름 제어": [
        ActionType.IF_ELSE, ActionType.LOOP,
        ActionType.WAIT, ActionType.STOP,
    ],
    "📁 파일 & 데이터": [
        ActionType.EXCEL_OPEN, ActionType.EXCEL_WRITE, ActionType.EXCEL_READ,
        ActionType.FILE_COPY, ActionType.FOLDER_CREATE,
    ],
    "🌐 브라우저": [ActionType.BROWSER_OPEN, ActionType.BROWSER_URL],
    "🌍 웹 자동화": [
        ActionType.WEB_OPEN, ActionType.WEB_NAVIGATE, ActionType.WEB_CLICK,
        ActionType.WEB_TYPE, ActionType.WEB_EXTRACT, ActionType.WEB_WAIT,
        ActionType.WEB_CLOSE,
    ],
    "🔍 화면 인식": [ActionType.IMAGE_SEARCH, ActionType.OCR_READ],
    "💬 기타": [ActionType.NOTIFY],
}


@dataclass
class Step:
    type: ActionType
    params: dict[str, Any] = field(default_factory=dict)
    wait_after: float = 0.0
    children: list[Step] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    label: str = ""

    def __post_init__(self):
        if not self.label:
            self.label = ACTION_LABELS.get(self.type, str(self.type))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "label": self.label,
            "params": self.params,
            "wait_after": self.wait_after,
            "children": [c.to_dict() for c in self.children],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Step:
        return cls(
            id=data["id"],
            type=ActionType(data["type"]),
            label=data.get("label", ""),
            params=data.get("params", {}),
            wait_after=data.get("wait_after", 0.0),
            children=[cls.from_dict(c) for c in data.get("children", [])],
        )


@dataclass
class Project:
    name: str
    schema_version: int = 1
    version: str = "1.0"
    created: str = ""
    steps: list[Step] = field(default_factory=list)
    variables: dict[str, Any] = field(default_factory=dict)
    schedule: dict[str, Any] = field(default_factory=dict)
    triggers: list[dict] = field(default_factory=list)

    def __post_init__(self):
        if not self.created:
            from datetime import date
            self.created = date.today().isoformat()

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "name": self.name,
            "version": self.version,
            "created": self.created,
            "steps": [s.to_dict() for s in self.steps],
            "variables": self.variables,
            "schedule": self.schedule,
            "triggers": self.triggers,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Project:
        return cls(
            name=data["name"],
            schema_version=data.get("schema_version", 1),
            version=data.get("version", "1.0"),
            created=data.get("created", ""),
            steps=[Step.from_dict(s) for s in data.get("steps", [])],
            variables=data.get("variables", {}),
            schedule=data.get("schedule", {}),
            triggers=data.get("triggers", []),
        )

    def resolve_variable_refs(self, text: str) -> str:
        """Replace {name} references with variable values."""
        def replace_match(m: re.Match) -> str:
            key = m.group(1)
            return str(self.variables.get(key, m.group(0)))
        return re.sub(r"\{(\w+)\}", replace_match, text)
