import time
import threading
import pytest
from rpa_studio.engine.context import ExecutionContext
from rpa_studio.engine.executor import StepExecutor
from rpa_studio.models import Step, ActionType, Project


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


class TestStepExecutor:
    def test_execute_simple_steps(self):
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
        steps = [
            Step(type=ActionType.WAIT, params={"seconds": 10}),
            Step(type=ActionType.WAIT, params={"seconds": 0}),
        ]
        proj = Project(name="test_stop", steps=steps)
        executor = StepExecutor()
        ctx = ExecutionContext()
        t = threading.Thread(target=executor.run, args=(proj, ctx))
        t.start()
        time.sleep(0.1)
        executor.stop()
        t.join(timeout=2)
        assert not t.is_alive()

    def test_loop_step_executes_children(self):
        child = Step(type=ActionType.WAIT, params={"seconds": 0})
        loop = Step(type=ActionType.LOOP, params={"count": 3}, children=[child])
        proj = Project(name="test_loop", steps=[loop])
        executor = StepExecutor()
        ctx = ExecutionContext()
        count = []
        executor.on_step_exit = lambda step, result: count.append(1)
        executor.run(proj, ctx)
        # loop itself + 3 child executions = 4
        assert len(count) == 4

    def test_max_steps_limit(self):
        child = Step(type=ActionType.WAIT, params={"seconds": 0})
        loop = Step(type=ActionType.LOOP, params={"count": 999999}, children=[child])
        proj = Project(name="test_max", steps=[loop])
        executor = StepExecutor(max_steps=10)
        ctx = ExecutionContext()
        executor.run(proj, ctx)
        assert ctx.error is not None
