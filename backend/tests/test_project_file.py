import json
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
