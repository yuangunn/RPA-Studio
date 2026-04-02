# RPA Studio Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a user-friendly Windows RPA tool with step-list editor, UI Automation, recorder, scheduler, and system tray — targeting non-developer office workers.

**Architecture:** 4-layer Python app: GUI (PyQt6) → Engine → Actions → Scheduler. Step-list based workflow editor (PAD-style), project files in JSON, Korean natural-language UI.

**Tech Stack:** Python 3.11+, PyQt6, pywinauto, pyautogui, pynput, openpyxl, APScheduler, watchdog, pystray, psutil, PyInstaller

**Spec:** `docs/superpowers/specs/2026-04-02-rpa-studio-design.md`

---

## Task 1: Project Scaffolding & Data Models

**Files:**
- Create: `pyproject.toml`
- Create: `src/rpa_studio/__init__.py`
- Create: `src/rpa_studio/models.py`
- Create: `src/rpa_studio/locale_kr.py`
- Create: `tests/__init__.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Create pyproject.toml with all dependencies**

```toml
[project]
name = "rpa-studio"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "PyQt6>=6.6.0",
    "pywinauto>=0.6.8",
    "pyautogui>=0.9.54",
    "pynput>=1.7.6",
    "openpyxl>=3.1.0",
    "APScheduler>=3.10.0",
    "watchdog>=4.0.0",
    "pystray>=0.19.0",
    "psutil>=5.9.0",
    "Pillow>=10.0.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0.0", "pytest-qt>=4.2.0"]

[project.gui-scripts]
rpa-studio = "rpa_studio.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

- [ ] **Step 2: Create package init**

```python
# src/rpa_studio/__init__.py
__version__ = "0.1.0"
```

- [ ] **Step 3: Write failing tests for data models**

```python
# tests/test_models.py
import pytest
from rpa_studio.models import Step, Project, ActionType

class TestStep:
    def test_create_step(self):
        step = Step(type=ActionType.APP_OPEN, params={"app_name": "Notepad"})
        assert step.type == ActionType.APP_OPEN
        assert step.params["app_name"] == "Notepad"
        assert step.wait_after == 0.0
        assert step.children == []
        assert step.id  # auto-generated

    def test_step_with_children(self):
        child = Step(type=ActionType.UI_CLICK, params={"click_type": "left"})
        parent = Step(type=ActionType.LOOP, params={"count": 3}, children=[child])
        assert len(parent.children) == 1

    def test_step_label_auto_generated(self):
        step = Step(type=ActionType.APP_OPEN, params={"app_name": "Teams"})
        assert step.label  # should have Korean label

class TestProject:
    def test_create_project(self):
        proj = Project(name="테스트")
        assert proj.name == "테스트"
        assert proj.schema_version == 1
        assert proj.steps == []
        assert proj.variables == {}

    def test_project_to_dict_and_back(self):
        step = Step(type=ActionType.WAIT, params={"seconds": 2})
        proj = Project(name="테스트", steps=[step])
        data = proj.to_dict()
        restored = Project.from_dict(data)
        assert restored.name == "테스트"
        assert len(restored.steps) == 1
        assert restored.steps[0].type == ActionType.WAIT

    def test_project_variable_reference(self):
        proj = Project(name="t", variables={"폴더": "C:/backup"})
        result = proj.resolve_variable_refs("{폴더}/file.xlsx")
        assert result == "C:/backup/file.xlsx"
```

- [ ] **Step 4: Run tests to verify they fail**

Run: `cd C:/Users/Helios_Neo_18/RPA && python -m pytest tests/test_models.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'rpa_studio.models'`

- [ ] **Step 5: Implement data models**

```python
# src/rpa_studio/models.py
from __future__ import annotations
import uuid
import re
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
    # 기타
    NOTIFY = "notify"


# Korean labels — see locale_kr.py for full mapping
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
    ActionType.NOTIFY: "알림 보내기",
}

# Actions locked for Phase 2
LOCKED_ACTIONS = {ActionType.IMAGE_SEARCH, ActionType.OCR_READ}

# Category grouping
ACTION_CATEGORIES = {
    "🖥️ 앱 조작": [ActionType.APP_OPEN, ActionType.APP_CLOSE, ActionType.WINDOW_FOCUS, ActionType.WINDOW_RESIZE],
    "🖱️ 클릭 & 입력": [ActionType.UI_CLICK, ActionType.UI_TYPE, ActionType.HOTKEY, ActionType.MOUSE_MOVE],
    "🔄 흐름 제어": [ActionType.IF_ELSE, ActionType.LOOP, ActionType.WAIT, ActionType.STOP],
    "📁 파일 & 데이터": [ActionType.EXCEL_OPEN, ActionType.EXCEL_WRITE, ActionType.EXCEL_READ, ActionType.FILE_COPY, ActionType.FOLDER_CREATE],
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
    steps: list[Step] = field(default_factory=list)
    variables: dict[str, Any] = field(default_factory=dict)
    schedule: dict[str, Any] = field(default_factory=dict)
    triggers: list[dict] = field(default_factory=list)

    version: str = "1.0"
    created: str = ""

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
```

- [ ] **Step 6: Create locale file**

```python
# src/rpa_studio/locale_kr.py
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
    "element_not_found": "{step_num}번째 단계의 '{element_name}'을(를) 찾을 수 없어요. 앱 화면이 바뀌었을 수 있습니다. 요소를 다시 선택해주세요.",
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
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `cd C:/Users/Helios_Neo_18/RPA && pip install -e ".[dev]" && python -m pytest tests/test_models.py -v`
Expected: 5 tests PASS

- [ ] **Step 8: Commit**

```bash
git init
git add pyproject.toml src/ tests/
git commit -m "feat: project scaffolding with data models and Korean locale"
```

---

## Task 2: Project File Save/Load

**Files:**
- Create: `src/rpa_studio/project/__init__.py`
- Create: `src/rpa_studio/project/project_file.py`
- Create: `tests/test_project_file.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_project_file.py
import json
import tempfile
from pathlib import Path
import pytest
from rpa_studio.models import Project, Step, ActionType
from rpa_studio.project.project_file import save_project, load_project

class TestProjectFile:
    def test_save_and_load(self, tmp_path):
        proj = Project(name="테스트 프로젝트")
        proj.steps.append(Step(type=ActionType.APP_OPEN, params={"app_name": "Notepad"}))
        proj.variables = {"폴더": "C:/backup"}

        filepath = tmp_path / "test_project.json"
        save_project(proj, filepath)
        assert filepath.exists()

        loaded = load_project(filepath)
        assert loaded.name == "테스트 프로젝트"
        assert len(loaded.steps) == 1
        assert loaded.variables["폴더"] == "C:/backup"

    def test_load_validates_schema_version(self, tmp_path):
        filepath = tmp_path / "bad.json"
        filepath.write_text(json.dumps({"schema_version": 999, "name": "x", "steps": []}), encoding="utf-8")
        with pytest.raises(ValueError, match="schema"):
            load_project(filepath)

    def test_save_creates_parent_dirs(self, tmp_path):
        proj = Project(name="t")
        filepath = tmp_path / "sub" / "dir" / "project.json"
        save_project(proj, filepath)
        assert filepath.exists()
```

- [ ] **Step 2: Run tests — expect FAIL**

Run: `python -m pytest tests/test_project_file.py -v`

- [ ] **Step 3: Implement project file module**

```python
# src/rpa_studio/project/__init__.py
# (empty)

# src/rpa_studio/project/project_file.py
from __future__ import annotations
import json
from pathlib import Path
from rpa_studio.models import Project

CURRENT_SCHEMA_VERSION = 1

def save_project(project: Project, filepath: Path) -> None:
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    data = project.to_dict()
    filepath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def load_project(filepath: Path) -> Project:
    filepath = Path(filepath)
    data = json.loads(filepath.read_text(encoding="utf-8"))
    version = data.get("schema_version", 1)
    if version > CURRENT_SCHEMA_VERSION:
        raise ValueError(
            f"이 프로젝트 파일은 최신 버전(schema v{version})입니다. "
            f"앱을 업데이트해주세요. (현재: v{CURRENT_SCHEMA_VERSION})"
        )
    return Project.from_dict(data)
```

- [ ] **Step 4: Run tests — expect PASS**

Run: `python -m pytest tests/test_project_file.py -v`

- [ ] **Step 5: Commit**

```bash
git add src/rpa_studio/project/ tests/test_project_file.py
git commit -m "feat: project file save/load with schema validation"
```

---

## Task 3: Execution Engine (Core)

**Files:**
- Create: `src/rpa_studio/engine/__init__.py`
- Create: `src/rpa_studio/engine/context.py`
- Create: `src/rpa_studio/engine/executor.py`
- Create: `src/rpa_studio/engine/condition.py`
- Create: `tests/test_engine.py`

- [ ] **Step 1: Write failing tests for ExecutionContext**

```python
# tests/test_engine.py
import pytest
from rpa_studio.engine.context import ExecutionContext

class TestExecutionContext:
    def test_create(self):
        ctx = ExecutionContext()
        assert ctx.variables == {}
        assert ctx.running is True
        assert ctx.log == []

    def test_resolve_refs(self):
        ctx = ExecutionContext(variables={"name": "hello"})
        assert ctx.resolve("{name} world") == "hello world"

    def test_add_log(self):
        ctx = ExecutionContext()
        ctx.add_log("테스트 메시지")
        assert len(ctx.log) == 1
        assert "테스트 메시지" in ctx.log[0]
```

- [ ] **Step 2: Implement ExecutionContext**

```python
# src/rpa_studio/engine/__init__.py
# (empty)

# src/rpa_studio/engine/context.py
from __future__ import annotations
import re
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from rpa_studio.models import Step


@dataclass
class ExecutionContext:
    variables: dict[str, Any] = field(default_factory=dict)
    running: bool = True
    current_step: Optional[Step] = None
    log: list[str] = field(default_factory=list)
    error: Optional[str] = None
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def resolve(self, text: str) -> str:
        def replace_match(m: re.Match) -> str:
            key = m.group(1)
            return str(self.variables.get(key, m.group(0)))
        return re.sub(r"\{(\w+)\}", replace_match, str(text))

    def add_log(self, message: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self.log.append(f"[{ts}] {message}")

    def save_log_to_disk(self, project_name: str) -> Path:
        """Persist execution log to ~/.rpa_studio/logs/"""
        from pathlib import Path
        log_dir = Path.home() / ".rpa_studio" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in project_name)
        log_path = log_dir / f"{ts}_{safe_name}.log"
        log_path.write_text("\n".join(self.log), encoding="utf-8")
        return log_path
```

- [ ] **Step 3: Run context tests — expect PASS**

Run: `python -m pytest tests/test_engine.py::TestExecutionContext -v`

- [ ] **Step 4: Write failing tests for StepExecutor**

```python
# tests/test_engine.py (append)
from rpa_studio.engine.executor import StepExecutor
from rpa_studio.models import Step, ActionType, Project

class TestStepExecutor:
    def test_execute_simple_steps(self):
        """Execute a project with wait steps — verify all run."""
        steps = [
            Step(type=ActionType.WAIT, params={"seconds": 0}),
            Step(type=ActionType.WAIT, params={"seconds": 0}),
        ]
        proj = Project(name="test", steps=steps)
        executor = StepExecutor()
        ctx = ExecutionContext()
        results = []
        executor.on_step_exit = lambda step, result: results.append(step.id)
        executor.run(proj, ctx)
        assert len(results) == 2

    def test_stop_interrupts(self):
        """Calling stop() should halt execution."""
        steps = [
            Step(type=ActionType.WAIT, params={"seconds": 10}),
            Step(type=ActionType.WAIT, params={"seconds": 0}),
        ]
        proj = Project(name="test", steps=steps)
        executor = StepExecutor()
        ctx = ExecutionContext()
        import threading
        t = threading.Thread(target=executor.run, args=(proj, ctx))
        t.start()
        import time; time.sleep(0.1)
        executor.stop()
        t.join(timeout=2)
        assert not t.is_alive()

    def test_loop_step_executes_children(self):
        child = Step(type=ActionType.WAIT, params={"seconds": 0})
        loop = Step(type=ActionType.LOOP, params={"count": 3}, children=[child])
        proj = Project(name="test", steps=[loop])
        executor = StepExecutor()
        ctx = ExecutionContext()
        count = []
        executor.on_step_exit = lambda step, result: count.append(1)
        executor.run(proj, ctx)
        # loop itself + 3 child executions = 4
        assert len(count) == 4

    def test_max_steps_limit(self):
        """Infinite loop protection."""
        child = Step(type=ActionType.WAIT, params={"seconds": 0})
        loop = Step(type=ActionType.LOOP, params={"count": 999999}, children=[child])
        proj = Project(name="test", steps=[loop])
        executor = StepExecutor(max_steps=10)
        ctx = ExecutionContext()
        executor.run(proj, ctx)
        assert ctx.error is not None
```

- [ ] **Step 5: Implement StepExecutor**

```python
# src/rpa_studio/engine/executor.py
from __future__ import annotations
import threading
from typing import Any, Callable, Optional
from rpa_studio.models import Step, ActionType, Project
from rpa_studio.engine.context import ExecutionContext


class StepExecutor:
    def __init__(self, max_steps: int = 100_000, max_depth: int = 10,
                 on_error_continue: bool = False):
        self._stop_event = threading.Event()
        self._max_steps = max_steps
        self._max_depth = max_depth
        self._step_count = 0
        self._on_error_continue = on_error_continue
        # Callbacks
        self.on_step_enter: Callable[[Step], None] = lambda s: None
        self.on_step_exit: Callable[[Step, Any], None] = lambda s, r: None
        self.on_log: Callable[[str], None] = lambda msg: None
        self.on_error: Callable[[str], None] = lambda msg: None

    # Per-project execution lock
    _running_projects: dict[str, bool] = {}
    _lock = threading.Lock()

    def run(self, project: Project, context: ExecutionContext) -> None:
        with self._lock:
            if self._running_projects.get(project.name):
                context.add_log(f"'{project.name}'이(가) 이미 실행 중입니다. 건너뜁니다.")
                return
            self._running_projects[project.name] = True

        self._stop_event.clear()
        self._step_count = 0
        context.running = True
        context.error = None
        try:
            self._run_steps(project.steps, context, depth=0)
        except _StopExecution:
            pass
        finally:
            context.running = False
            with self._lock:
                self._running_projects.pop(project.name, None)
            context.save_log_to_disk(project.name)

    def stop(self) -> None:
        self._stop_event.set()

    def _run_steps(self, steps: list[Step], context: ExecutionContext, depth: int) -> None:
        if depth > self._max_depth:
            msg = f"중첩이 너무 깊어요 (최대 {self._max_depth}단계)"
            context.error = msg
            self.on_error(msg)
            raise _StopExecution()

        for step in steps:
            if self._stop_event.is_set():
                raise _StopExecution()
            self._step_count += 1
            if self._step_count > self._max_steps:
                msg = f"실행 한도 초과 ({self._max_steps}단계). 무한 반복일 수 있어요."
                context.error = msg
                self.on_error(msg)
                raise _StopExecution()

            context.current_step = step
            self.on_step_enter(step)
            try:
                result = self._execute_step(step, context, depth)
            except _StopExecution:
                raise
            except Exception as e:
                msg = f"{step.label}에서 문제가 생겼어요: {e}"
                context.error = msg
                context.add_log(msg)
                self.on_error(msg)
                if not self._on_error_continue:
                    raise _StopExecution()
                # Continue to next step if configured

            self.on_step_exit(step, result)

            if step.wait_after > 0:
                self._stop_event.wait(timeout=step.wait_after)
                if self._stop_event.is_set():
                    raise _StopExecution()

    def _execute_step(self, step: Step, context: ExecutionContext, depth: int) -> Any:
        from rpa_studio.actions.base import get_action_handler

        if step.type == ActionType.LOOP:
            count = int(step.params.get("count", 1))
            for i in range(count):
                if self._stop_event.is_set():
                    raise _StopExecution()
                context.variables["_loop_index"] = i + 1
                self._run_steps(step.children, context, depth + 1)
            return {"iterations": count}

        if step.type == ActionType.IF_ELSE:
            from rpa_studio.engine.condition import evaluate_condition
            result = evaluate_condition(step.params, context)
            if result:
                self._run_steps(step.children, context, depth + 1)
            return {"condition_met": result}

        if step.type == ActionType.WAIT:
            seconds = float(step.params.get("seconds", 1))
            self._stop_event.wait(timeout=seconds)
            return None

        if step.type == ActionType.STOP:
            raise _StopExecution()

        handler = get_action_handler(step.type)
        if handler:
            return handler.execute(step, context)

        context.add_log(f"{step.label} — 핸들러 없음 (건너뜀)")
        return None


class _StopExecution(Exception):
    pass
```

- [ ] **Step 6: Implement condition evaluator**

```python
# src/rpa_studio/engine/condition.py
from __future__ import annotations
from typing import Any
from rpa_studio.engine.context import ExecutionContext

OPERATORS = {
    "eq": lambda a, b: a == b,
    "neq": lambda a, b: a != b,
    "gt": lambda a, b: float(a) > float(b),
    "lt": lambda a, b: float(a) < float(b),
    "gte": lambda a, b: float(a) >= float(b),
    "lte": lambda a, b: float(a) <= float(b),
    "contains": lambda a, b: str(b) in str(a),
}

def evaluate_condition(params: dict[str, Any], context: ExecutionContext) -> bool:
    left_key = params.get("left", "")
    left_val = context.variables.get(left_key, left_key)
    operator = params.get("operator", "eq")
    right_val = context.resolve(str(params.get("right", "")))
    fn = OPERATORS.get(operator, OPERATORS["eq"])
    try:
        return fn(left_val, right_val)
    except (ValueError, TypeError):
        return False
```

- [ ] **Step 7: Create action base (minimal stub so executor imports work)**

```python
# src/rpa_studio/actions/__init__.py
# (empty)

# src/rpa_studio/actions/base.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional
from rpa_studio.models import ActionType, Step
from rpa_studio.engine.context import ExecutionContext

_REGISTRY: dict[ActionType, ActionHandler] = {}

class ActionHandler(ABC):
    action_type: ActionType

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "action_type"):
            _REGISTRY[cls.action_type] = cls()

    @abstractmethod
    def execute(self, step: Step, context: ExecutionContext) -> Any:
        ...

def get_action_handler(action_type: ActionType) -> Optional[ActionHandler]:
    return _REGISTRY.get(action_type)
```

- [ ] **Step 8: Run all engine tests — expect PASS**

Run: `python -m pytest tests/test_engine.py -v`

- [ ] **Step 9: Commit**

```bash
git add src/rpa_studio/engine/ src/rpa_studio/actions/ tests/test_engine.py
git commit -m "feat: execution engine with context, step executor, conditions"
```

---

## Task 4: Action Handlers

**Files:**
- Create: `src/rpa_studio/actions/ui_auto.py`
- Create: `src/rpa_studio/actions/keyboard_mouse.py`
- Create: `src/rpa_studio/actions/file_ops.py`
- Create: `src/rpa_studio/actions/excel_ops.py`
- Create: `src/rpa_studio/actions/app_control.py`
- Create: `src/rpa_studio/actions/notify.py`
- Create: `src/rpa_studio/actions/image_match.py` (stub)
- Create: `src/rpa_studio/actions/ocr.py` (stub)
- Create: `tests/test_actions.py`

- [ ] **Step 1: Write tests for file operations (testable without GUI)**

```python
# tests/test_actions.py
import pytest
from pathlib import Path
from rpa_studio.models import Step, ActionType
from rpa_studio.engine.context import ExecutionContext
from rpa_studio.actions.file_ops import FileCopyHandler, FolderCreateHandler

class TestFileOps:
    def test_file_copy(self, tmp_path):
        src = tmp_path / "source.txt"
        src.write_text("hello")
        dst = tmp_path / "dest.txt"
        step = Step(type=ActionType.FILE_COPY, params={"source": str(src), "destination": str(dst)})
        ctx = ExecutionContext()
        handler = FileCopyHandler()
        handler.execute(step, ctx)
        assert dst.read_text() == "hello"

    def test_folder_create(self, tmp_path):
        target = tmp_path / "new_folder"
        step = Step(type=ActionType.FOLDER_CREATE, params={"path": str(target)})
        ctx = ExecutionContext()
        handler = FolderCreateHandler()
        handler.execute(step, ctx)
        assert target.is_dir()
```

- [ ] **Step 2: Run tests — expect FAIL**

- [ ] **Step 3: Implement all action handlers**

```python
# src/rpa_studio/actions/app_control.py
from __future__ import annotations
import subprocess
import psutil
from rpa_studio.actions.base import ActionHandler
from rpa_studio.models import ActionType, Step
from rpa_studio.engine.context import ExecutionContext

# Known app name → executable mapping
APP_NAME_MAP = {
    "microsoft teams": "Teams.exe",
    "teams": "Teams.exe",
    "메모장": "notepad.exe",
    "notepad": "notepad.exe",
    "계산기": "calc.exe",
    "calculator": "calc.exe",
    "excel": "EXCEL.EXE",
    "엑셀": "EXCEL.EXE",
    "word": "WINWORD.EXE",
    "워드": "WINWORD.EXE",
    "chrome": "chrome.exe",
    "크롬": "chrome.exe",
    "edge": "msedge.exe",
}

class AppOpenHandler(ActionHandler):
    action_type = ActionType.APP_OPEN
    def execute(self, step: Step, context: ExecutionContext):
        app_input = context.resolve(step.params.get("app_path", step.params.get("app_name", "")))
        # Resolve friendly name to executable
        app = APP_NAME_MAP.get(app_input.lower(), app_input)
        context.add_log(f"앱 열기: {app}")
        try:
            subprocess.Popen(app)
        except FileNotFoundError:
            # Fallback: try via start command for registered apps
            subprocess.Popen(["cmd", "/c", "start", "", app])
        return {"app": app}

class AppCloseHandler(ActionHandler):
    action_type = ActionType.APP_CLOSE
    def execute(self, step: Step, context: ExecutionContext):
        app_name = context.resolve(step.params.get("app_name", ""))
        context.add_log(f"앱 닫기: {app_name}")
        for proc in psutil.process_iter(["name"]):
            if app_name.lower() in proc.info["name"].lower():
                proc.terminate()
                return {"terminated": proc.info["name"]}
        return {"terminated": None}

class WindowFocusHandler(ActionHandler):
    action_type = ActionType.WINDOW_FOCUS
    def execute(self, step: Step, context: ExecutionContext):
        import pywinauto
        title = context.resolve(step.params.get("window_title", ""))
        context.add_log(f"창 전환: {title}")
        app = pywinauto.Application(backend="uia").connect(title_re=f".*{title}.*")
        win = app.top_window()
        win.set_focus()
        return {"focused": title}

class WindowResizeHandler(ActionHandler):
    action_type = ActionType.WINDOW_RESIZE
    def execute(self, step: Step, context: ExecutionContext):
        import pywinauto
        title = context.resolve(step.params.get("window_title", ""))
        action = step.params.get("action", "maximize")
        context.add_log(f"창 크기 조절: {title} → {action}")
        app = pywinauto.Application(backend="uia").connect(title_re=f".*{title}.*")
        win = app.top_window()
        if action == "maximize": win.maximize()
        elif action == "minimize": win.minimize()
        elif action == "restore": win.restore()
        return {"action": action}
```

```python
# src/rpa_studio/actions/ui_auto.py
from __future__ import annotations
from rpa_studio.actions.base import ActionHandler
from rpa_studio.models import ActionType, Step
from rpa_studio.engine.context import ExecutionContext

class UIClickHandler(ActionHandler):
    action_type = ActionType.UI_CLICK
    def execute(self, step: Step, context: ExecutionContext):
        import pywinauto
        element_info = step.params.get("element_info", {})
        window_title = context.resolve(step.params.get("window_title", ""))
        click_type = step.params.get("click_type", "left")
        context.add_log(f"UI 요소 클릭: {step.params.get('element_path', '')}")

        app = pywinauto.Application(backend="uia").connect(title_re=f".*{window_title}.*")
        win = app.top_window()
        element = self._find_element(win, element_info)
        if click_type == "left": element.click_input()
        elif click_type == "right": element.click_input(button="right")
        elif click_type == "double": element.double_click_input()
        return {"clicked": True}

    def _find_element(self, window, info: dict):
        # Tier 1: AutomationId
        auto_id = info.get("automation_id", "")
        if auto_id:
            try:
                return window.child_window(auto_id=auto_id).wrapper_object()
            except Exception:
                pass
        # Tier 2: Name + ControlType
        name = info.get("name", "")
        ctrl = info.get("control_type", "")
        if name:
            try:
                return window.child_window(title=name, control_type=ctrl).wrapper_object()
            except Exception:
                pass
        # Tier 3: fall through
        raise RuntimeError(f"요소를 찾을 수 없어요: {info}")

class UITypeHandler(ActionHandler):
    action_type = ActionType.UI_TYPE
    def execute(self, step: Step, context: ExecutionContext):
        import pywinauto
        text = context.resolve(step.params.get("text", ""))
        window_title = context.resolve(step.params.get("window_title", ""))
        element_info = step.params.get("element_info", {})
        context.add_log(f"텍스트 입력: {text[:20]}...")

        app = pywinauto.Application(backend="uia").connect(title_re=f".*{window_title}.*")
        win = app.top_window()
        handler = UIClickHandler()
        element = handler._find_element(win, element_info)
        element.set_text(text)
        return {"typed": text}
```

```python
# src/rpa_studio/actions/keyboard_mouse.py
from __future__ import annotations
from rpa_studio.actions.base import ActionHandler
from rpa_studio.models import ActionType, Step
from rpa_studio.engine.context import ExecutionContext

class HotkeyHandler(ActionHandler):
    action_type = ActionType.HOTKEY
    def execute(self, step: Step, context: ExecutionContext):
        import pyautogui
        keys = step.params.get("keys", "")
        context.add_log(f"단축키: {keys}")
        parts = [k.strip().lower() for k in keys.split("+")]
        pyautogui.hotkey(*parts)
        return {"keys": keys}

class MouseMoveHandler(ActionHandler):
    action_type = ActionType.MOUSE_MOVE
    def execute(self, step: Step, context: ExecutionContext):
        import pyautogui
        x = int(step.params.get("x", 0))
        y = int(step.params.get("y", 0))
        context.add_log(f"마우스 이동: ({x}, {y})")
        pyautogui.moveTo(x, y)
        return {"x": x, "y": y}
```

```python
# src/rpa_studio/actions/file_ops.py
from __future__ import annotations
import shutil
from pathlib import Path
from rpa_studio.actions.base import ActionHandler
from rpa_studio.models import ActionType, Step
from rpa_studio.engine.context import ExecutionContext

class FileCopyHandler(ActionHandler):
    action_type = ActionType.FILE_COPY
    def execute(self, step: Step, context: ExecutionContext):
        src = Path(context.resolve(step.params.get("source", "")))
        dst = Path(context.resolve(step.params.get("destination", "")))
        context.add_log(f"파일 복사: {src.name} → {dst}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return {"source": str(src), "destination": str(dst)}

class FolderCreateHandler(ActionHandler):
    action_type = ActionType.FOLDER_CREATE
    def execute(self, step: Step, context: ExecutionContext):
        path = Path(context.resolve(step.params.get("path", "")))
        context.add_log(f"폴더 만들기: {path}")
        path.mkdir(parents=True, exist_ok=True)
        return {"path": str(path)}
```

```python
# src/rpa_studio/actions/excel_ops.py
from __future__ import annotations
from pathlib import Path
from rpa_studio.actions.base import ActionHandler
from rpa_studio.models import ActionType, Step
from rpa_studio.engine.context import ExecutionContext

class ExcelOpenHandler(ActionHandler):
    action_type = ActionType.EXCEL_OPEN
    def execute(self, step: Step, context: ExecutionContext):
        import openpyxl
        filepath = Path(context.resolve(step.params.get("file_path", "")))
        context.add_log(f"엑셀 열기: {filepath.name}")
        wb = openpyxl.load_workbook(filepath)
        context.variables["_excel_wb"] = wb
        context.variables["_excel_path"] = str(filepath)
        return {"file": str(filepath)}

class ExcelWriteHandler(ActionHandler):
    action_type = ActionType.EXCEL_WRITE
    def execute(self, step: Step, context: ExecutionContext):
        import openpyxl
        filepath = Path(context.resolve(step.params.get("file_path", context.variables.get("_excel_path", ""))))
        sheet_name = step.params.get("sheet", "Sheet1")
        cell = step.params.get("cell", "A1")
        value = context.resolve(str(step.params.get("value", "")))
        context.add_log(f"엑셀에 쓰기: {filepath.name} [{sheet_name}]{cell} = {value[:20]}")

        if filepath.exists():
            wb = openpyxl.load_workbook(filepath)
        else:
            wb = openpyxl.Workbook()
        ws = wb[sheet_name] if sheet_name in wb.sheetnames else wb.create_sheet(sheet_name)
        ws[cell] = value
        wb.save(filepath)
        return {"cell": cell, "value": value}

class ExcelReadHandler(ActionHandler):
    action_type = ActionType.EXCEL_READ
    def execute(self, step: Step, context: ExecutionContext):
        import openpyxl
        filepath = Path(context.resolve(step.params.get("file_path", context.variables.get("_excel_path", ""))))
        sheet_name = step.params.get("sheet", "Sheet1")
        cell = step.params.get("cell", "A1")
        var_name = step.params.get("save_as", "엑셀값")
        context.add_log(f"엑셀에서 읽기: {filepath.name} [{sheet_name}]{cell}")

        wb = openpyxl.load_workbook(filepath)
        ws = wb[sheet_name] if sheet_name in wb.sheetnames else wb.create_sheet(sheet_name)
        value = ws[cell].value
        context.variables[var_name] = value
        return {"cell": cell, "value": value}
```

```python
# src/rpa_studio/actions/notify.py
from __future__ import annotations
from rpa_studio.actions.base import ActionHandler
from rpa_studio.models import ActionType, Step
from rpa_studio.engine.context import ExecutionContext

class NotifyHandler(ActionHandler):
    action_type = ActionType.NOTIFY
    def execute(self, step: Step, context: ExecutionContext):
        message = context.resolve(step.params.get("message", ""))
        context.add_log(f"알림: {message}")
        # Will integrate with GUI notification / tray notification later
        return {"message": message}
```

```python
# src/rpa_studio/actions/image_match.py (stub)
# Phase 2 — not implemented

# src/rpa_studio/actions/ocr.py (stub)
# Phase 2 — not implemented
```

- [ ] **Step 4: Run tests — expect PASS**

Run: `python -m pytest tests/test_actions.py -v`

- [ ] **Step 5: Commit**

```bash
git add src/rpa_studio/actions/ tests/test_actions.py
git commit -m "feat: all action handlers — app, ui, keyboard, file, excel, notify"
```

---

## Task 5: GUI — Main Window Shell

**Files:**
- Create: `src/rpa_studio/main.py`
- Create: `src/rpa_studio/gui/__init__.py`
- Create: `src/rpa_studio/gui/main_window.py`
- Create: `src/rpa_studio/gui/style.py`

- [ ] **Step 1: Create style module**

```python
# src/rpa_studio/gui/__init__.py
# (empty)

# src/rpa_studio/gui/style.py
DARK_THEME = """
QMainWindow, QWidget { background-color: #0d1117; color: #c9d1d9; }
QMenuBar { background-color: #161b22; color: #c9d1d9; }
QMenuBar::item:selected { background-color: #30363d; }
QToolBar { background-color: #161b22; border-bottom: 1px solid #30363d; spacing: 6px; padding: 4px; }
QPushButton { background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px; padding: 5px 14px; }
QPushButton:hover { background-color: #30363d; }
QPushButton#runBtn { background-color: #238636; color: white; }
QPushButton#stopBtn { background-color: #da3633; color: white; }
QPushButton#recordBtn { background-color: #f85149; color: white; }
QDockWidget { color: #8b949e; }
QDockWidget::title { background-color: #161b22; padding: 6px; }
QTreeWidget, QListWidget { background-color: #0d1117; color: #c9d1d9; border: 1px solid #30363d; }
QTreeWidget::item:selected, QListWidget::item:selected { background-color: #1f6feb33; }
QScrollBar:vertical { background-color: #0d1117; width: 8px; }
QScrollBar::handle:vertical { background-color: #30363d; border-radius: 4px; }
QLabel { color: #8b949e; }
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox { background-color: #161b22; color: #c9d1d9; border: 1px solid #30363d; border-radius: 4px; padding: 6px; }
"""
```

- [ ] **Step 2: Create main window skeleton**

```python
# src/rpa_studio/gui/main_window.py
from __future__ import annotations
from PyQt6.QtWidgets import (
    QMainWindow, QToolBar, QPushButton, QWidget, QLabel,
    QDockWidget, QVBoxLayout, QHBoxLayout, QSplitter,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QKeySequence, QUndoStack
from rpa_studio.gui.style import DARK_THEME
from rpa_studio.locale_kr import LABELS


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🤖 RPA Studio")
        self.setMinimumSize(1100, 700)
        self.setStyleSheet(DARK_THEME)
        self._undo_stack = QUndoStack(self)
        self._advanced_mode = False

        self._setup_toolbar()
        self._setup_central()
        self._setup_docks()
        self._setup_shortcuts()

    def _setup_toolbar(self):
        tb = QToolBar("Main")
        tb.setMovable(False)
        tb.setIconSize(QSize(16, 16))
        self.addToolBar(tb)

        self._run_btn = QPushButton(LABELS["run"])
        self._run_btn.setObjectName("runBtn")
        self._stop_btn = QPushButton(LABELS["stop"])
        self._stop_btn.setObjectName("stopBtn")
        self._stop_btn.setEnabled(False)
        self._record_btn = QPushButton(LABELS["record"])
        self._record_btn.setObjectName("recordBtn")

        tb.addWidget(self._run_btn)
        tb.addWidget(self._stop_btn)
        tb.addWidget(self._record_btn)
        tb.addSeparator()

        self._mode_label = QLabel(LABELS["mode_basic"])
        tb.addWidget(self._mode_label)

    def _setup_central(self):
        # Placeholder — will be replaced by StepEditor in Task 6
        self._central = QWidget()
        layout = QVBoxLayout(self._central)
        layout.addWidget(QLabel("📋 스텝 에디터 (Task 6에서 구현)"))
        self.setCentralWidget(self._central)

    def _setup_docks(self):
        # Left: Action Palette (placeholder)
        self._palette_dock = QDockWidget("작업 추가", self)
        self._palette_dock.setWidget(QLabel("팔레트 (Task 6)"))
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self._palette_dock)

        # Right: Property Panel (placeholder)
        self._property_dock = QDockWidget(LABELS["prop_title"], self)
        self._property_dock.setWidget(QLabel("속성 (Task 7)"))
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._property_dock)

        # Bottom: Log Panel (placeholder)
        self._log_dock = QDockWidget(LABELS["log_title"], self)
        self._log_dock.setWidget(QLabel("로그 (Task 8)"))
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self._log_dock)
        self._log_dock.hide()

    def _setup_shortcuts(self):
        QAction("Run", self, shortcut=QKeySequence("F5"), triggered=self._on_run).setParent(self)
        QAction("Stop", self, shortcut=QKeySequence("F6"), triggered=self._on_stop).setParent(self)
        QAction("Record", self, shortcut=QKeySequence("F9"), triggered=self._on_record).setParent(self)
        QAction("Undo", self, shortcut=QKeySequence.StandardKey.Undo, triggered=self._undo_stack.undo).setParent(self)
        QAction("Redo", self, shortcut=QKeySequence.StandardKey.Redo, triggered=self._undo_stack.redo).setParent(self)
        QAction("Save", self, shortcut=QKeySequence.StandardKey.Save, triggered=self._on_save).setParent(self)
        QAction("New", self, shortcut=QKeySequence.StandardKey.New, triggered=self._on_new).setParent(self)

    # Slots — will be connected in later tasks
    def _on_run(self): pass
    def _on_stop(self): pass
    def _on_record(self): pass
    def _on_save(self): pass
    def _on_new(self): pass
```

- [ ] **Step 3: Create app entry point**

```python
# src/rpa_studio/main.py
import sys
from PyQt6.QtWidgets import QApplication
from rpa_studio.gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("RPA Studio")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Manual test — launch the app**

Run: `cd C:/Users/Helios_Neo_18/RPA && python -m rpa_studio.main`
Expected: Window opens with toolbar (실행/중지/녹화), 3 dock panels, dark theme

- [ ] **Step 5: Commit**

```bash
git add src/rpa_studio/main.py src/rpa_studio/gui/
git commit -m "feat: main window shell with toolbar, docks, dark theme"
```

---

## Task 6: GUI — Step Editor & Action Palette

**Files:**
- Create: `src/rpa_studio/gui/step_editor.py`
- Create: `src/rpa_studio/gui/step_widgets.py`
- Create: `src/rpa_studio/gui/action_palette.py`
- Modify: `src/rpa_studio/gui/main_window.py`

- [ ] **Step 1: Implement Action Palette (left panel)**

```python
# src/rpa_studio/gui/action_palette.py
from __future__ import annotations
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDrag
from rpa_studio.models import ACTION_CATEGORIES, ACTION_LABELS, LOCKED_ACTIONS, ActionType
from rpa_studio.locale_kr import LABELS


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
                    label += " 🔒"
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
```

- [ ] **Step 2: Implement Step Widgets (individual step display)**

```python
# src/rpa_studio/gui/step_widgets.py
from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal
from rpa_studio.models import Step, ACTION_LABELS, ACTION_CATEGORIES, ActionType

# Map action types to category emojis
_CATEGORY_ICONS = {}
for cat, actions in ACTION_CATEGORIES.items():
    emoji = cat.split()[0]
    for a in actions:
        _CATEGORY_ICONS[a] = emoji


class StepWidget(QWidget):
    clicked = pyqtSignal(str)  # step.id
    delete_requested = pyqtSignal(str)

    def __init__(self, step: Step, index: int, indent: int = 0, parent=None):
        super().__init__(parent)
        self.step = step
        self._selected = False
        self.setMinimumHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12 + indent * 32, 4, 12, 4)

        num_label = QLabel(str(index))
        num_label.setFixedWidth(28)
        num_label.setStyleSheet("color: #58a6ff; font-weight: bold; font-size: 12px;")
        layout.addWidget(num_label)

        icon = QLabel(_CATEGORY_ICONS.get(step.type, "⚙️"))
        icon.setFixedWidth(24)
        layout.addWidget(icon)

        info = QWidget()
        info_layout = QHBoxLayout(info)
        info_layout.setContentsMargins(0, 0, 0, 0)
        name = QLabel(step.label)
        name.setStyleSheet("color: #c9d1d9; font-size: 13px;")
        info_layout.addWidget(name)
        summary = self._make_summary(step)
        if summary:
            s = QLabel(f"— {summary}")
            s.setStyleSheet("color: #484f58; font-size: 11px;")
            info_layout.addWidget(s)
        info_layout.addStretch()
        layout.addWidget(info, stretch=1)

        self.setStyleSheet(
            "StepWidget { background: #161b22; border: 1px solid #30363d; border-radius: 6px; }"
            "StepWidget:hover { border-color: #58a6ff; }"
        )

    def _make_summary(self, step: Step) -> str:
        p = step.params
        if step.type == ActionType.APP_OPEN:
            return p.get("app_name", "")
        if step.type == ActionType.UI_CLICK:
            return p.get("element_path", "")
        if step.type == ActionType.HOTKEY:
            return p.get("keys", "")
        if step.type == ActionType.WAIT:
            return f"{p.get('seconds', 1)}초"
        if step.type == ActionType.LOOP:
            return f"{p.get('count', 1)}회 반복"
        if step.type == ActionType.EXCEL_WRITE:
            return p.get("file_path", "")
        if step.type == ActionType.NOTIFY:
            return p.get("message", "")[:30]
        return ""

    def mousePressEvent(self, event):
        self.clicked.emit(self.step.id)
        super().mousePressEvent(event)

    def set_selected(self, selected: bool):
        self._selected = selected
        border = "#58a6ff" if selected else "#30363d"
        self.setStyleSheet(
            f"StepWidget {{ background: #161b22; border: 1px solid {border}; border-radius: 6px; }}"
        )
```

- [ ] **Step 3: Implement Step Editor (central panel)**

```python
# src/rpa_studio/gui/step_editor.py
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel, QPushButton,
)
from PyQt6.QtCore import Qt, pyqtSignal
from rpa_studio.models import Step, ActionType, LOCKED_ACTIONS
from rpa_studio.gui.step_widgets import StepWidget
from rpa_studio.locale_kr import LABELS


class StepEditor(QWidget):
    step_selected = pyqtSignal(str)  # step.id
    steps_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._steps: list[Step] = []
        self._widgets: list[StepWidget] = []
        self._selected_id: str | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)

        # Header
        self._header = QLabel("📋 새 프로젝트")
        self._header.setStyleSheet("color: #c9d1d9; font-size: 14px; font-weight: bold;")
        layout.addWidget(self._header)

        # Scroll area for steps
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self._step_container = QWidget()
        self._step_layout = QVBoxLayout(self._step_container)
        self._step_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._step_layout.setSpacing(4)
        scroll.setWidget(self._step_container)
        layout.addWidget(scroll, stretch=1)

        # Add step button
        add_btn = QPushButton(LABELS["add_step"])
        add_btn.setStyleSheet("QPushButton { border: 2px dashed #30363d; padding: 12px; color: #484f58; }")
        layout.addWidget(add_btn)

        # Accept drops from palette
        self.setAcceptDrops(True)

    def set_project_name(self, name: str):
        self._header.setText(f"📋 {name}")

    def set_steps(self, steps: list[Step]):
        self._steps = steps
        self._rebuild()

    def add_step(self, step: Step, index: int | None = None):
        if index is None:
            self._steps.append(step)
        else:
            self._steps.insert(index, step)
        self._rebuild()
        self.steps_changed.emit()

    def remove_step(self, step_id: str):
        self._steps = [s for s in self._steps if s.id != step_id]
        self._rebuild()
        self.steps_changed.emit()

    def move_step(self, step_id: str, direction: int):
        for i, s in enumerate(self._steps):
            if s.id == step_id:
                new_i = i + direction
                if 0 <= new_i < len(self._steps):
                    self._steps[i], self._steps[new_i] = self._steps[new_i], self._steps[i]
                    self._rebuild()
                    self.steps_changed.emit()
                return

    def get_steps(self) -> list[Step]:
        return self._steps

    def _rebuild(self):
        # Clear existing widgets
        for w in self._widgets:
            self._step_layout.removeWidget(w)
            w.deleteLater()
        self._widgets.clear()

        idx = 1
        for step in self._steps:
            self._add_step_widget(step, idx, indent=0)
            idx += 1
            for ci, child in enumerate(step.children):
                self._add_step_widget(child, f"{idx-1}-{ci+1}", indent=1)

    def _add_step_widget(self, step: Step, index, indent: int):
        w = StepWidget(step, index, indent=indent)
        w.clicked.connect(self._on_step_clicked)
        self._step_layout.addWidget(w)
        self._widgets.append(w)

    def _on_step_clicked(self, step_id: str):
        self._selected_id = step_id
        for w in self._widgets:
            w.set_selected(w.step.id == step_id)
        self.step_selected.emit(step_id)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        action_value = event.mimeData().text()
        try:
            action_type = ActionType(action_value)
        except ValueError:
            return
        if action_type in LOCKED_ACTIONS:
            return
        step = Step(type=action_type)
        self.add_step(step)
```

- [ ] **Step 4: Wire palette and editor into main window**

Update `main_window.py` to replace placeholders with real widgets. Import `ActionPalette` and `StepEditor`, set them as dock/central widgets.

Also add keyboard shortcuts for step editor:
- `Delete` → remove selected step
- `Ctrl+Up` → move selected step up
- `Ctrl+Down` → move selected step down

Wire the basic/advanced mode toggle as a `QCheckBox` or `QPushButton` in the toolbar. In basic mode, hide advanced-only fields in property panel. In advanced mode, show all fields. The `_advanced_mode` flag on `MainWindow` is toggled and a signal `mode_changed(bool)` is emitted.

- [ ] **Step 5: Manual test — launch app, drag actions to step list**

Run: `python -m rpa_studio.main`
Expected: Left panel shows categories, drag an action → appears in center step list

- [ ] **Step 6: Commit**

```bash
git add src/rpa_studio/gui/step_editor.py src/rpa_studio/gui/step_widgets.py src/rpa_studio/gui/action_palette.py src/rpa_studio/gui/main_window.py
git commit -m "feat: step editor, action palette, step widgets — core editor UI"
```

---

## Task 7: GUI — Property Panel

**Files:**
- Create: `src/rpa_studio/gui/property_panel.py`
- Modify: `src/rpa_studio/gui/main_window.py`

- [ ] **Step 1: Implement property panel with dynamic form generation**

Property panel generates input widgets based on `ActionType`. Each action type has a schema of fields (label, widget type, default). Widget types: text input, number spinner, combo box, file picker, element picker button.

- [ ] **Step 2: Wire property panel to step editor selection signal**

When step is selected in editor → property panel shows that step's params. When params change in property panel → step is updated.

- [ ] **Step 3: Manual test — select a step, edit properties**

- [ ] **Step 4: Commit**

```bash
git add src/rpa_studio/gui/property_panel.py src/rpa_studio/gui/main_window.py
git commit -m "feat: property panel with dynamic forms per action type"
```

---

## Task 8: GUI — Log Panel & Execution Wiring

**Files:**
- Create: `src/rpa_studio/gui/log_panel.py`
- Modify: `src/rpa_studio/gui/main_window.py`

- [ ] **Step 1: Implement log panel**

Collapsible text area that shows execution log messages. Auto-scrolls to bottom. Timestamp per line.

- [ ] **Step 2: Wire Run/Stop buttons to executor**

Run button: create `ExecutionThread(QThread)`, pass current project steps to `StepExecutor`. Stop button: call `executor.stop()`. Update step highlighting as each step executes (via signals).

- [ ] **Step 3: Wire save/load with Ctrl+S / Ctrl+N / file dialog**

- [ ] **Step 4: Manual test — create steps, click Run, see log output**

- [ ] **Step 5: Commit**

```bash
git add src/rpa_studio/gui/log_panel.py src/rpa_studio/gui/main_window.py
git commit -m "feat: log panel, execution wiring, save/load"
```

---

## Task 9: UI Automation Element Picker

**Files:**
- Create: `src/rpa_studio/gui/element_picker.py`
- Modify: `src/rpa_studio/gui/property_panel.py`

- [ ] **Step 1: Implement element picker overlay**

When "🎯 요소 선택하기" is clicked: minimize RPA Studio, start a transparent overlay that highlights UI elements under the mouse cursor using `pywinauto.uia_element_info`. On click, capture element info (AutomationId, Name, ControlType, parent path). On ESC, cancel. Return to RPA Studio with captured info.

- [ ] **Step 2: Wire picker result to property panel**

The captured element info populates the property panel fields for ui_click / ui_type actions.

- [ ] **Step 3: Manual test — pick an element from Notepad**

Run app, add "UI 요소 클릭" step, click element picker, hover over Notepad's menu, click → element info should appear in property panel.

- [ ] **Step 4: Commit**

```bash
git add src/rpa_studio/gui/element_picker.py src/rpa_studio/gui/property_panel.py
git commit -m "feat: UI Automation element picker with highlight overlay"
```

---

## Task 10: Recorder

**Files:**
- Create: `src/rpa_studio/engine/recorder.py`
- Create: `src/rpa_studio/gui/recorder_toolbar.py`
- Modify: `src/rpa_studio/gui/main_window.py`

- [ ] **Step 1: Implement recorder engine**

Uses `pynput` listeners for mouse clicks and keyboard events. Identifies UI element at click position via `pywinauto`. Generates Step objects. Detects pauses > 3 seconds → "기다리기" step.

- [ ] **Step 2: Implement floating recorder toolbar**

Frameless, always-on-top, semi-transparent QWidget showing: stop button (F9), pause button, elapsed time. F9 global hotkey via pynput to toggle recording.

- [ ] **Step 3: Wire recorder to main window**

Record button → minimize window, show floating toolbar, start recording. Stop → restore window, populate step editor with recorded steps.

- [ ] **Step 4: Manual test — record opening Notepad, typing text**

- [ ] **Step 5: Commit**

```bash
git add src/rpa_studio/engine/recorder.py src/rpa_studio/gui/recorder_toolbar.py src/rpa_studio/gui/main_window.py
git commit -m "feat: action recorder with floating toolbar and F9 hotkey"
```

---

## Task 11: Scheduler & Triggers

**Files:**
- Create: `src/rpa_studio/scheduler/__init__.py`
- Create: `src/rpa_studio/scheduler/cron.py`
- Create: `src/rpa_studio/scheduler/triggers.py`
- Create: `tests/test_scheduler.py`

- [ ] **Step 1: Write failing tests for scheduler**

```python
# tests/test_scheduler.py
from rpa_studio.scheduler.cron import ScheduleManager

class TestScheduler:
    def test_add_schedule(self):
        mgr = ScheduleManager()
        mgr.add_schedule("test_job", {"type": "daily", "time": "09:00"}, callback=lambda: None)
        assert "test_job" in mgr.list_schedules()

    def test_remove_schedule(self):
        mgr = ScheduleManager()
        mgr.add_schedule("test_job", {"type": "daily", "time": "09:00"}, callback=lambda: None)
        mgr.remove_schedule("test_job")
        assert "test_job" not in mgr.list_schedules()
```

- [ ] **Step 2: Implement ScheduleManager (APScheduler wrapper)**

- [ ] **Step 3: Implement TriggerManager (app detection via psutil polling, file detection via watchdog)**

- [ ] **Step 4: Run tests — expect PASS**

- [ ] **Step 5: Commit**

```bash
git add src/rpa_studio/scheduler/ tests/test_scheduler.py
git commit -m "feat: scheduler with cron and app/file triggers"
```

---

## Task 12: Schedule Management UI

**Files:**
- Create: `src/rpa_studio/gui/schedule_view.py`
- Modify: `src/rpa_studio/gui/main_window.py`

- [ ] **Step 1: Implement schedule management dialog**

Dialog with: list of schedules (name, project, schedule type, next run, toggle on/off), add/edit/delete buttons. "New schedule" form: project selector, frequency (daily/weekly/monthly), time picker.

- [ ] **Step 2: Implement trigger management in same dialog**

Tab or section for triggers: list, add trigger (app detection / file detection), remove.

- [ ] **Step 3: Wire to main window menu**

- [ ] **Step 4: Manual test — open schedule dialog, add/remove a schedule**

Run: `python -m rpa_studio.main`
Expected: Menu → 스케줄 관리 → Dialog opens. Can add daily schedule, toggle on/off, remove.

- [ ] **Step 5: Commit**

```bash
git add src/rpa_studio/gui/schedule_view.py src/rpa_studio/gui/main_window.py
git commit -m "feat: schedule and trigger management UI"
```

---

## Task 13: System Tray

**Files:**
- Create: `src/rpa_studio/gui/tray.py`
- Modify: `src/rpa_studio/main.py`

- [ ] **Step 1: Implement system tray with pystray**

Tray icon with menu: 열기, 스케줄 관리, 실행 중 작업, 종료. Close window = minimize to tray (override `closeEvent`). Tray notifications on schedule/trigger execution.

- [ ] **Step 2: Wire tray to main window lifecycle**

Window close → hide to tray. Tray "열기" → show window. Tray "종료" → quit app. Start scheduler on app launch.

- [ ] **Step 3: Manual test — close window, verify tray icon, reopen**

- [ ] **Step 4: Commit**

```bash
git add src/rpa_studio/gui/tray.py src/rpa_studio/main.py
git commit -m "feat: system tray with minimize-on-close and background scheduling"
```

---

## Task 14: Integration Test & Polish

**Files:**
- Modify: various files for bug fixes
- Create: `tests/test_integration.py`

- [ ] **Step 1: Write integration test — full scenario**

```python
# tests/test_integration.py
from rpa_studio.models import Step, ActionType, Project
from rpa_studio.engine.executor import StepExecutor
from rpa_studio.engine.context import ExecutionContext
from rpa_studio.project.project_file import save_project, load_project
import rpa_studio.actions.file_ops  # register handlers
import rpa_studio.actions.notify
import rpa_studio.actions.app_control

class TestIntegration:
    def test_full_workflow(self, tmp_path):
        """Build a project, save, load, execute."""
        proj = Project(name="통합 테스트")
        proj.steps = [
            Step(type=ActionType.FOLDER_CREATE, params={"path": str(tmp_path / "output")}),
            Step(type=ActionType.NOTIFY, params={"message": "폴더 생성 완료!"}),
        ]
        # Save & load
        fp = tmp_path / "project.json"
        save_project(proj, fp)
        loaded = load_project(fp)

        # Execute
        executor = StepExecutor()
        ctx = ExecutionContext()
        executor.run(loaded, ctx)

        assert (tmp_path / "output").is_dir()
        assert any("폴더 생성 완료" in line for line in ctx.log)
        assert ctx.error is None
```

- [ ] **Step 2: Run all tests**

Run: `python -m pytest tests/ -v`

- [ ] **Step 3: Fix any failures**

- [ ] **Step 4: Manual end-to-end test**

Launch app → create a simple workflow (open Notepad, wait 2s, close) → save → reload → run → verify it works.

- [ ] **Step 5: Commit**

```bash
git add tests/test_integration.py
git commit -m "feat: integration tests and end-to-end verification"
```
