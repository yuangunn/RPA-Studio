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
