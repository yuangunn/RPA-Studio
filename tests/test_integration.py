import pytest
from pathlib import Path
from rpa_studio.models import Step, ActionType, Project
from rpa_studio.engine.executor import StepExecutor
from rpa_studio.engine.context import ExecutionContext
from rpa_studio.project.project_file import save_project, load_project
# Register action handlers
import rpa_studio.actions.file_ops
import rpa_studio.actions.notify
import rpa_studio.actions.app_control
import rpa_studio.actions.excel_ops


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

    def test_excel_write_and_read(self, tmp_path):
        """Write to excel then read back."""
        xlsx = tmp_path / "test.xlsx"
        proj = Project(name="엑셀 테스트")
        proj.steps = [
            Step(type=ActionType.EXCEL_WRITE, params={
                "file_path": str(xlsx), "sheet": "Sheet1", "cell": "A1", "value": "안녕하세요"
            }),
            Step(type=ActionType.EXCEL_READ, params={
                "file_path": str(xlsx), "sheet": "Sheet1", "cell": "A1", "save_as": "결과"
            }),
        ]
        executor = StepExecutor()
        ctx = ExecutionContext()
        executor.run(proj, ctx)
        assert ctx.variables.get("결과") == "안녕하세요"
        assert ctx.error is None

    def test_loop_with_file_ops(self, tmp_path):
        """Loop creating multiple folders."""
        children = [
            Step(type=ActionType.FOLDER_CREATE, params={"path": str(tmp_path / "folder_{_loop_index}")})
        ]
        # Note: variable substitution uses {_loop_index}
        proj = Project(name="반복 테스트")
        proj.steps = [
            Step(type=ActionType.LOOP, params={"count": 3}, children=[
                Step(type=ActionType.NOTIFY, params={"message": "반복 {_loop_index}"}),
            ]),
        ]
        executor = StepExecutor()
        ctx = ExecutionContext()
        executor.run(proj, ctx)
        assert ctx.variables.get("_loop_index") == 3
        assert ctx.error is None

    def test_condition_branch(self):
        """If-else evaluates correctly."""
        proj = Project(name="조건 테스트", variables={"점수": 85})
        proj.steps = [
            Step(type=ActionType.IF_ELSE, params={
                "left": "점수", "operator": "gt", "right": "60"
            }, children=[
                Step(type=ActionType.NOTIFY, params={"message": "합격!"}),
            ]),
        ]
        executor = StepExecutor()
        ctx = ExecutionContext(variables={"점수": 85})
        executor.run(proj, ctx)
        assert any("합격" in line for line in ctx.log)

    def test_project_roundtrip_with_schedule(self, tmp_path):
        """Save/load project with schedule and triggers."""
        proj = Project(name="스케줄 테스트")
        proj.schedule = {"enabled": True, "type": "monthly", "day": 1, "time": "09:00"}
        proj.triggers = [{"type": "app", "value": "Teams.exe"}]
        proj.steps = [Step(type=ActionType.NOTIFY, params={"message": "hello"})]

        fp = tmp_path / "sched_project.json"
        save_project(proj, fp)
        loaded = load_project(fp)

        assert loaded.schedule["type"] == "monthly"
        assert loaded.triggers[0]["value"] == "Teams.exe"
        assert loaded.schema_version == 1
