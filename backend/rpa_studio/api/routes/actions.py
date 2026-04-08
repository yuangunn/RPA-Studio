"""Action metadata endpoints — provides palette data for the frontend."""
from fastapi import APIRouter
from rpa_studio.models import ACTION_CATEGORIES, ACTION_LABELS, LOCKED_ACTIONS, ActionType
from rpa_studio.api.schemas import ActionMetadata

router = APIRouter()

# Property schemas for each action type (drives the PropertyPanel in frontend)
ACTION_PARAM_SCHEMAS: dict[str, list[dict]] = {
    "app_open": [
        {"key": "app_name", "label": "앱 이름", "type": "text"},
        {"key": "app_path", "label": "실행 경로 (선택)", "type": "file"},
    ],
    "app_close": [
        {"key": "app_name", "label": "앱 이름", "type": "text"},
    ],
    "window_focus": [
        {"key": "window_title", "label": "창 선택", "type": "window_list"},
    ],
    "window_resize": [
        {"key": "window_title", "label": "창 선택", "type": "window_list"},
        {"key": "action", "label": "동작", "type": "combo",
         "choices": {"maximize": "최대화", "minimize": "최소화", "restore": "복원"}},
    ],
    "ui_click": [
        {"key": "window_title", "label": "대상 앱 창 제목", "type": "window_list"},
        {"key": "element_path", "label": "요소 경로", "type": "text"},
        {"key": "click_type", "label": "클릭 방법", "type": "combo",
         "choices": {"left": "왼쪽 클릭", "right": "오른쪽 클릭", "double": "더블 클릭"}},
        {"key": "_element_picker", "label": "🎯 요소 선택하기", "type": "element_picker"},
    ],
    "ui_type": [
        {"key": "window_title", "label": "대상 앱 창 제목", "type": "window_list"},
        {"key": "text", "label": "입력할 텍스트", "type": "text"},
        {"key": "_element_picker", "label": "🎯 요소 선택하기", "type": "element_picker"},
    ],
    "hotkey": [
        {"key": "keys", "label": "키 조합 (예: Ctrl+C)", "type": "text"},
    ],
    "mouse_move": [
        {"key": "x", "label": "X 좌표", "type": "int"},
        {"key": "y", "label": "Y 좌표", "type": "int"},
    ],
    "if_else": [
        {"key": "left", "label": "비교할 저장값 이름", "type": "text"},
        {"key": "operator", "label": "조건", "type": "combo",
         "choices": {"eq": "과 같으면", "neq": "과 다르면", "gt": "보다 크면",
                     "lt": "보다 작으면", "gte": "이상이면", "lte": "이하이면",
                     "contains": "을 포함하면"}},
        {"key": "right", "label": "비교 값", "type": "text"},
    ],
    "loop": [
        {"key": "count", "label": "반복 횟수", "type": "int", "min": 1, "max": 99999},
    ],
    "wait": [
        {"key": "seconds", "label": "대기 시간 (초)", "type": "float", "min": 0, "max": 3600},
    ],
    "stop": [],
    "excel_open": [
        {"key": "file_path", "label": "엑셀 파일 경로", "type": "file"},
    ],
    "excel_write": [
        {"key": "file_path", "label": "엑셀 파일 경로", "type": "file"},
        {"key": "sheet", "label": "시트 이름", "type": "text"},
        {"key": "cell", "label": "셀 (예: A1)", "type": "text"},
        {"key": "value", "label": "입력할 값", "type": "text"},
    ],
    "excel_read": [
        {"key": "file_path", "label": "엑셀 파일 경로", "type": "file"},
        {"key": "sheet", "label": "시트 이름", "type": "text"},
        {"key": "cell", "label": "셀 (예: A1)", "type": "text"},
        {"key": "save_as", "label": "저장값 이름", "type": "text"},
    ],
    "file_copy": [
        {"key": "source", "label": "원본 파일 경로", "type": "file"},
        {"key": "destination", "label": "대상 경로", "type": "file"},
    ],
    "folder_create": [
        {"key": "path", "label": "폴더 경로", "type": "text"},
    ],
    "image_search": [
        {"key": "template_path", "label": "찾을 이미지 파일", "type": "file"},
        {"key": "confidence", "label": "정확도 (0~1)", "type": "float", "min": 0.1, "max": 1.0},
        {"key": "save_as", "label": "결과 저장값 이름", "type": "text"},
    ],
    "ocr_read": [
        {"key": "lang", "label": "인식 언어", "type": "combo",
         "choices": {"kor+eng": "한국어+영어", "eng": "영어만", "kor": "한국어만"}},
        {"key": "save_as", "label": "결과 저장값 이름", "type": "text"},
    ],
    "browser_open": [
        {"key": "browser", "label": "브라우저", "type": "combo",
         "choices": {"chrome": "Chrome", "edge": "Edge"}},
    ],
    "browser_url": [
        {"key": "url", "label": "웹사이트 주소", "type": "text"},
        {"key": "browser", "label": "브라우저", "type": "combo",
         "choices": {"chrome": "Chrome", "edge": "Edge"}},
    ],
    "notify": [
        {"key": "title", "label": "알림 제목", "type": "text"},
        {"key": "message", "label": "알림 메시지", "type": "text"},
    ],
    # 웹 자동화 (Playwright)
    "web_open": [
        {"key": "url", "label": "시작 URL (비워두면 빈 페이지)", "type": "text"},
        {"key": "headless", "label": "숨김 모드", "type": "combo",
         "choices": {"false": "브라우저 표시", "true": "숨김 (백그라운드)"}},
    ],
    "web_navigate": [
        {"key": "url", "label": "이동할 웹 주소", "type": "text"},
    ],
    "web_click": [
        {"key": "selector", "label": "CSS 선택자 (예: #btn, .class)", "type": "text"},
        {"key": "text", "label": "또는 텍스트로 찾기", "type": "text"},
    ],
    "web_type": [
        {"key": "selector", "label": "CSS 선택자", "type": "text"},
        {"key": "placeholder", "label": "또는 placeholder로 찾기", "type": "text"},
        {"key": "text", "label": "입력할 텍스트", "type": "text"},
        {"key": "clear", "label": "기존 내용 지우기", "type": "combo",
         "choices": {"true": "지우고 입력", "false": "이어서 입력"}},
    ],
    "web_extract": [
        {"key": "selector", "label": "CSS 선택자", "type": "text"},
        {"key": "attribute", "label": "추출 대상", "type": "combo",
         "choices": {"textContent": "텍스트 내용", "innerText": "보이는 텍스트",
                     "value": "입력값", "href": "링크 주소"}},
        {"key": "save_as", "label": "저장값 이름", "type": "text"},
    ],
    "web_wait": [
        {"key": "selector", "label": "CSS 선택자", "type": "text"},
        {"key": "state", "label": "대기 조건", "type": "combo",
         "choices": {"visible": "보일 때까지", "hidden": "숨겨질 때까지",
                     "attached": "DOM에 존재할 때까지"}},
        {"key": "timeout", "label": "최대 대기 (초)", "type": "int", "min": 1, "max": 60},
    ],
    "web_close": [],
}


@router.get("/actions")
async def list_actions():
    """Return all action types with categories, labels, and param schemas."""
    result = []
    for cat_name, action_types in ACTION_CATEGORIES.items():
        icon = cat_name.split()[0]  # emoji
        cat_label = cat_name[len(icon):].strip()
        for at in action_types:
            result.append({
                "type": at.value,
                "label": ACTION_LABELS[at],
                "category": cat_label,
                "category_icon": icon,
                "category_full": cat_name,
                "locked": at in LOCKED_ACTIONS,
                "params_schema": ACTION_PARAM_SCHEMAS.get(at.value, []),
            })
    return result


@router.get("/actions/{action_type}/schema")
async def get_action_schema(action_type: str):
    """Get param schema for a specific action type."""
    schema = ACTION_PARAM_SCHEMAS.get(action_type)
    if schema is None:
        return {"error": f"Unknown action type: {action_type}"}
    return {"type": action_type, "params_schema": schema}


@router.get("/actions/windows")
async def list_windows():
    """Return list of currently open window titles."""
    try:
        import win32gui
        titles = []

        def enum_cb(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and title.strip() and title not in ("Program Manager", ""):
                    titles.append(title)

        win32gui.EnumWindows(enum_cb, None)
        return sorted(set(titles))
    except ImportError:
        import psutil
        names = set()
        for proc in psutil.process_iter(["name"]):
            name = proc.info.get("name", "")
            if name:
                names.add(name)
        return sorted(names)
