from __future__ import annotations
import threading
from typing import Any, Callable
from rpa_studio.models import Step, ActionType, Project
from rpa_studio.engine.context import ExecutionContext


class StepExecutor:
    _running_projects: dict[str, bool] = {}
    _lock = threading.Lock()

    def __init__(self, max_steps: int = 100_000, max_depth: int = 10,
                 on_error_continue: bool = False):
        self._stop_event = threading.Event()
        self._max_steps = max_steps
        self._max_depth = max_depth
        self._step_count = 0
        self._on_error_continue = on_error_continue
        self.on_step_enter: Callable[[Step], None] = lambda s: None
        self.on_step_exit: Callable[[Step, Any], None] = lambda s, r: None
        self.on_log: Callable[[str], None] = lambda msg: None
        self.on_error: Callable[[str], None] = lambda msg: None

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
