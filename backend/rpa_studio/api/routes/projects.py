"""Project CRUD endpoints."""
from __future__ import annotations

from pathlib import Path
from fastapi import APIRouter, HTTPException

from rpa_studio.api.schemas import ProjectSchema, ProjectCreateRequest, StepAddRequest, StepUpdateRequest, StepReorderRequest
from rpa_studio.api.state import PROJECTS_DIR
from rpa_studio.models import Project, Step, ActionType
from rpa_studio.project.project_file import save_project, load_project

router = APIRouter()


def _project_path(name: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-_ " else "_" for c in name)
    return PROJECTS_DIR / f"{safe}.json"


@router.get("/projects")
async def list_projects():
    """List all saved projects."""
    projects = []
    for f in PROJECTS_DIR.glob("*.json"):
        try:
            proj = load_project(f)
            projects.append({
                "name": proj.name,
                "version": proj.version,
                "created": proj.created,
                "step_count": len(proj.steps),
                "file_path": str(f),
            })
        except Exception:
            continue
    return projects


@router.post("/projects")
async def create_project(req: ProjectCreateRequest):
    """Create a new empty project. If it already exists, just return it."""
    path = _project_path(req.name)
    if path.exists():
        proj = load_project(path)
        return {"name": proj.name, "file_path": str(path)}
    proj = Project(name=req.name)
    save_project(proj, path)
    return {"name": proj.name, "file_path": str(path)}


@router.get("/projects/{name}")
async def get_project(name: str):
    """Load a project by name."""
    path = _project_path(name)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"프로젝트를 찾을 수 없어요: {name}")
    proj = load_project(path)
    return proj.to_dict()


@router.put("/projects/{name}")
async def save_project_endpoint(name: str, data: ProjectSchema):
    """Save/update a project."""
    proj = Project.from_dict(data.model_dump())
    path = _project_path(name)
    save_project(proj, path)
    return {"name": proj.name, "file_path": str(path)}


@router.delete("/projects/{name}")
async def delete_project(name: str):
    """Delete a project."""
    path = _project_path(name)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"프로젝트를 찾을 수 없어요: {name}")
    path.unlink()
    return {"deleted": name}


# --- Steps within a project ---

@router.get("/projects/{name}/steps")
async def get_steps(name: str):
    """Get all steps for a project."""
    path = _project_path(name)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"프로젝트를 찾을 수 없어요: {name}")
    proj = load_project(path)
    return [s.to_dict() for s in proj.steps]


@router.post("/projects/{name}/steps")
async def add_step(name: str, req: StepAddRequest):
    """Add a step to the project."""
    path = _project_path(name)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"프로젝트를 찾을 수 없어요: {name}")

    proj = load_project(path)
    try:
        action_type = ActionType(req.type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"알 수 없는 액션: {req.type}")

    step = Step(type=action_type, params=req.params)

    if req.parent_id:
        # Add as child of an existing step (loop/if-else)
        parent = _find_step(proj.steps, req.parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail=f"상위 단계를 찾을 수 없어요: {req.parent_id}")
        parent.children.append(step)
    elif req.index is not None:
        proj.steps.insert(req.index, step)
    else:
        proj.steps.append(step)

    save_project(proj, path)
    return step.to_dict()


@router.put("/projects/{name}/steps/{step_id}")
async def update_step(name: str, step_id: str, req: StepUpdateRequest):
    """Update a step's params."""
    path = _project_path(name)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"프로젝트를 찾을 수 없어요: {name}")

    proj = load_project(path)
    step = _find_step(proj.steps, step_id)
    if not step:
        raise HTTPException(status_code=404, detail=f"단계를 찾을 수 없어요: {step_id}")

    if req.params is not None:
        step.params.update(req.params)
    if req.wait_after is not None:
        step.wait_after = req.wait_after
    if req.label is not None:
        step.label = req.label

    save_project(proj, path)
    return step.to_dict()


@router.delete("/projects/{name}/steps/{step_id}")
async def delete_step(name: str, step_id: str):
    """Remove a step from the project."""
    path = _project_path(name)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"프로젝트를 찾을 수 없어요: {name}")

    proj = load_project(path)
    if not _remove_step(proj.steps, step_id):
        raise HTTPException(status_code=404, detail=f"단계를 찾을 수 없어요: {step_id}")

    save_project(proj, path)
    return {"deleted": step_id}


@router.post("/projects/{name}/steps/reorder")
async def reorder_steps(name: str, req: StepReorderRequest):
    """Reorder a step to a new position."""
    path = _project_path(name)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"프로젝트를 찾을 수 없어요: {name}")

    proj = load_project(path)

    # Find and remove the step
    old_index = None
    for i, s in enumerate(proj.steps):
        if s.id == req.step_id:
            old_index = i
            break

    if old_index is None:
        raise HTTPException(status_code=404, detail=f"단계를 찾을 수 없어요: {req.step_id}")

    step = proj.steps.pop(old_index)
    new_idx = req.new_index
    if new_idx > old_index:
        new_idx -= 1
    new_idx = max(0, min(new_idx, len(proj.steps)))
    proj.steps.insert(new_idx, step)

    save_project(proj, path)
    return [s.to_dict() for s in proj.steps]


# --- Variables ---

@router.get("/projects/{name}/variables")
async def get_variables(name: str):
    path = _project_path(name)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"프로젝트를 찾을 수 없어요: {name}")
    proj = load_project(path)
    return proj.variables


@router.put("/projects/{name}/variables")
async def set_variables(name: str, variables: dict):
    path = _project_path(name)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"프로젝트를 찾을 수 없어요: {name}")
    proj = load_project(path)
    proj.variables = variables
    save_project(proj, path)
    return proj.variables


# --- Helpers ---

def _find_step(steps: list[Step], step_id: str) -> Step | None:
    for s in steps:
        if s.id == step_id:
            return s
        found = _find_step(s.children, step_id)
        if found:
            return found
    return None


def _remove_step(steps: list[Step], step_id: str) -> bool:
    for i, s in enumerate(steps):
        if s.id == step_id:
            steps.pop(i)
            return True
        if _remove_step(s.children, step_id):
            return True
    return False
