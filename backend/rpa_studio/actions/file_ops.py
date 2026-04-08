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
