"""Recorder endpoints."""
from fastapi import APIRouter
from rpa_studio.api.state import app_state

router = APIRouter()


@router.post("/recorder/start")
async def start_recording():
    """Start recording mouse/keyboard actions."""
    if app_state.recorder.is_running:
        return {"status": "already_recording"}
    app_state.recorder.start()
    return {"status": "recording"}


@router.post("/recorder/stop")
async def stop_recording():
    """Stop recording and return captured steps."""
    if not app_state.recorder.is_running:
        return {"status": "not_recording", "steps": []}
    steps = app_state.recorder.stop()
    return {
        "status": "stopped",
        "step_count": len(steps),
        "steps": [s.to_dict() for s in steps],
    }


@router.post("/recorder/pause")
async def pause_recording():
    """Pause recording."""
    app_state.recorder.pause()
    return {"status": "paused"}


@router.post("/recorder/resume")
async def resume_recording():
    """Resume recording."""
    app_state.recorder.resume()
    return {"status": "recording"}


@router.get("/recorder/status")
async def recorder_status():
    """Get current recorder status."""
    return {
        "is_recording": app_state.recorder.is_running,
    }
