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
