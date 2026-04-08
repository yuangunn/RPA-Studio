"""FastAPI server entry point for RPA Studio backend."""
from __future__ import annotations

import argparse
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from rpa_studio.api.routes.health import router as health_router
from rpa_studio.api.routes.actions import router as actions_router
from rpa_studio.api.routes.projects import router as projects_router
from rpa_studio.api.routes.execution import router as execution_router
from rpa_studio.api.routes.recorder import router as recorder_router
from rpa_studio.api.routes.scheduler import router as scheduler_router

app = FastAPI(
    title="RPA Studio API",
    version="0.2.0",
    description="Windows Desktop RPA 자동화 도구 백엔드",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Electron loads from file:// or localhost
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api", tags=["System"])
app.include_router(actions_router, prefix="/api", tags=["Actions"])
app.include_router(projects_router, prefix="/api", tags=["Projects"])
app.include_router(execution_router, prefix="/api", tags=["Execution"])
app.include_router(recorder_router, prefix="/api", tags=["Recorder"])
app.include_router(scheduler_router, prefix="/api", tags=["Scheduler"])


def main():
    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8742)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    # Signal to Electron that the server is ready
    print(f"READY:{args.port}", flush=True)

    uvicorn.run(
        "rpa_studio.api.server:app",
        host="127.0.0.1",
        port=args.port,
        reload=args.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
