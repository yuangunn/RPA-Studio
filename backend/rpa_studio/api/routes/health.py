"""Health check and system endpoints."""
from fastapi import APIRouter
from rpa_studio.api.schemas import HealthResponse
from rpa_studio.api.state import app_state
from rpa_studio.locale_kr import LABELS, OPERATORS, CLICK_TYPES, WINDOW_ACTIONS

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok", version="0.2.0")


@router.get("/locale")
async def get_locale():
    """Return all Korean UI strings as JSON."""
    return {
        "labels": LABELS,
        "operators": OPERATORS,
        "click_types": CLICK_TYPES,
        "window_actions": WINDOW_ACTIONS,
    }


@router.post("/shutdown")
async def shutdown():
    """Graceful shutdown — called by Electron on app quit."""
    app_state.shutdown()
    return {"status": "shutting_down"}
