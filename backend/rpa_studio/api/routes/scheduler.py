"""Schedule and trigger management endpoints."""
from fastapi import APIRouter, HTTPException
from rpa_studio.api.schemas import ScheduleConfig, TriggerConfig
from rpa_studio.api.state import app_state

router = APIRouter()


# --- Schedules ---

@router.get("/schedules")
async def list_schedules():
    """List all registered schedules."""
    return app_state.schedule_manager.list_schedules()


@router.post("/schedules")
async def add_schedule(config: ScheduleConfig):
    """Add a new schedule for a project."""
    job_id = f"sched_{config.project_name}_{config.type}"

    def _execute_scheduled():
        # TODO: load and execute project
        pass

    app_state.schedule_manager.start()
    app_state.schedule_manager.add_schedule(
        job_id=job_id,
        config=config.model_dump(),
        callback=_execute_scheduled,
    )
    return {"job_id": job_id, "status": "scheduled"}


@router.delete("/schedules/{job_id}")
async def remove_schedule(job_id: str):
    """Remove a schedule."""
    app_state.schedule_manager.remove_schedule(job_id)
    return {"deleted": job_id}


@router.put("/schedules/{job_id}/enabled")
async def toggle_schedule(job_id: str, enabled: bool):
    """Enable or disable a schedule."""
    app_state.schedule_manager.set_enabled(job_id, enabled)
    return {"job_id": job_id, "enabled": enabled}


# --- Triggers ---

@router.get("/triggers")
async def list_triggers():
    """List active triggers."""
    return list(app_state.trigger_manager._triggers.keys())


@router.post("/triggers")
async def add_trigger(config: TriggerConfig):
    """Add a new trigger."""
    trigger_id = f"trig_{config.project_name}_{config.trigger_type}"

    def _on_trigger(*args):
        # TODO: load and execute project
        pass

    if config.trigger_type == "app":
        app_state.trigger_manager.add_app_trigger(
            trigger_id=trigger_id,
            process_name=config.value,
            callback=_on_trigger,
        )
    elif config.trigger_type == "file":
        if not config.watch_dir:
            raise HTTPException(status_code=400, detail="파일 트리거에는 감시할 폴더가 필요해요.")
        app_state.trigger_manager.add_file_trigger(
            trigger_id=trigger_id,
            watch_dir=config.watch_dir,
            pattern=config.value,
            callback=_on_trigger,
        )
    else:
        raise HTTPException(status_code=400, detail=f"알 수 없는 트리거 유형: {config.trigger_type}")

    return {"trigger_id": trigger_id, "status": "active"}


@router.delete("/triggers/{trigger_id}")
async def remove_trigger(trigger_id: str):
    """Remove a trigger."""
    app_state.trigger_manager.remove_trigger(trigger_id)
    return {"deleted": trigger_id}
