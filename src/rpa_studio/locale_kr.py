"""Korean UI text — all user-facing strings live here."""

LABELS = {
    # Toolbar
    "run": "▶ 실행",
    "stop": "⏹ 중지",
    "record": "⏺ 녹화",
    "mode_basic": "기본 모드",
    "mode_advanced": "고급 모드",
    # Step editor
    "add_step": "+ 단계 추가 (드래그 또는 클릭)",
    "step_count": "{n}개 단계",
    # Property panel
    "prop_title": "속성 편집",
    "prop_action_type": "작업 유형",
    "prop_wait_after": "실행 후 대기 (초)",
    "prop_help": "💡 도움말",
    # Element picker
    "pick_element": "🎯 요소 선택하기",
    "pick_element_help": "'요소 선택하기'를 클릭하면 대상 앱 위에 마우스를 올려 원하는 버튼이나 텍스트를 직접 선택할 수 있어요.",
    "element_selected": "✅ 선택 완료",
    "element_not_found": (
        "{step_num}번째 단계의 '{element_name}'을(를) 찾을 수 없어요. "
        "앱 화면이 바뀌었을 수 있습니다. 요소를 다시 선택해주세요."
    ),
    # Categories
    "cat_app": "🖥️ 앱 조작",
    "cat_click": "🖱️ 클릭 & 입력",
    "cat_flow": "🔄 흐름 제어",
    "cat_data": "📁 파일 & 데이터",
    "cat_detect": "🔍 화면 인식",
    "cat_misc": "💬 기타",
    # Locked
    "locked_msg": "이 기능은 업데이트 예정입니다.",
    # Errors
    "err_app_not_found": "앱을 찾을 수 없어요. 앱이 실행 중인지 확인해주세요.",
    "err_step_failed": "{step_num}번째 단계에서 문제가 생겼어요: {message}",
    # Log
    "log_title": "📝 실행 로그",
    "log_expand": "▲ 펼치기",
    "log_collapse": "▼ 접기",
    # Schedule
    "schedule_title": "스케줄 관리",
    "schedule_daily": "매일",
    "schedule_weekly": "매주",
    "schedule_monthly": "매월",
    # Tray
    "tray_open": "열기",
    "tray_schedule": "스케줄 관리",
    "tray_running": "실행 중 작업",
    "tray_quit": "종료",
    # Recorder
    "rec_stop": "⏹ 녹화 중지 (F9)",
    "rec_pause": "⏸ 일시정지",
    "rec_time": "녹화 시간: {time}",
}

# Condition operators — friendly Korean
OPERATORS = {
    "eq": "과 같으면",
    "neq": "과 다르면",
    "gt": "보다 크면",
    "lt": "보다 작으면",
    "gte": "이상이면",
    "lte": "이하이면",
    "contains": "을 포함하면",
}

# Click types
CLICK_TYPES = {
    "left": "왼쪽 클릭",
    "right": "오른쪽 클릭",
    "double": "더블 클릭",
}

# Window actions
WINDOW_ACTIONS = {
    "maximize": "최대화",
    "minimize": "최소화",
    "restore": "복원",
}
