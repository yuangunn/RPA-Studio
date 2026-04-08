"""Execution endpoints + WebSocket for real-time updates."""
from __future__ import annotations

import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException

from rpa_studio.api.schemas import ExecutionRequest, ExecutionStatusResponse
from rpa_studio.api.state import app_state, PROJECTS_DIR
from rpa_studio.project.project_file import load_project

router = APIRouter()


@router.post("/execution/run")
async def start_execution(req: ExecutionRequest):
    """Start executing a project. Returns execution_id for WebSocket connection."""
    from rpa_studio.api.routes.projects import _project_path
    path = _project_path(req.project_name)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"프로젝트를 찾을 수 없어요: {req.project_name}")

    project = load_project(path)
    if not project.steps:
        raise HTTPException(status_code=400, detail="실행할 단계가 없습니다.")

    loop = asyncio.get_event_loop()
    exec_id = app_state.start_execution(project, loop)
    return {"execution_id": exec_id, "project_name": req.project_name}


@router.post("/execution/stop/{exec_id}")
async def stop_execution(exec_id: str):
    """Stop a running execution."""
    if not app_state.stop_execution(exec_id):
        raise HTTPException(status_code=404, detail=f"실행을 찾을 수 없어요: {exec_id}")
    return {"stopped": exec_id}


@router.get("/execution/status/{exec_id}", response_model=ExecutionStatusResponse)
async def execution_status(exec_id: str):
    """Get current execution status (fallback for WebSocket)."""
    info = app_state.get_execution(exec_id)
    if not info:
        raise HTTPException(status_code=404, detail=f"실행을 찾을 수 없어요: {exec_id}")
    ctx = info.context
    return ExecutionStatusResponse(
        execution_id=exec_id,
        running=ctx.running,
        current_step_id=ctx.current_step.id if ctx.current_step else None,
        error=ctx.error,
        log_count=len(ctx.log),
    )


@router.websocket("/ws/execution/{exec_id}")
async def execution_ws(websocket: WebSocket, exec_id: str):
    """WebSocket for real-time execution updates.

    The executor callbacks push messages to an asyncio.Queue.
    This handler reads from that queue and forwards to the WebSocket client.
    """
    await websocket.accept()

    info = app_state.get_execution(exec_id)
    if not info:
        await websocket.send_json({"type": "error", "message": "실행을 찾을 수 없어요"})
        await websocket.close()
        return

    try:
        while True:
            try:
                msg = await asyncio.wait_for(info.queue.get(), timeout=1.0)
                await websocket.send_json(msg)

                if msg.get("type") == "execution_complete":
                    break
            except asyncio.TimeoutError:
                # Check if execution is still alive
                if not info.thread.is_alive():
                    break
                # Send heartbeat
                await websocket.send_json({"type": "heartbeat"})
    except WebSocketDisconnect:
        pass
    finally:
        app_state.cleanup_execution(exec_id)
