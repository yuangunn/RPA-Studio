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
