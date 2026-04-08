"""Pydantic schemas for API request/response validation.

These mirror the dataclasses in models.py but add validation,
serialization, and documentation for the REST API.
"""
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any


class StepSchema(BaseModel):
    id: str = ""
    type: str
    label: str = ""
    params: dict[str, Any] = Field(default_factory=dict)
    wait_after: float = 0.0
    children: list[StepSchema] = Field(default_factory=list)


class ProjectSchema(BaseModel):
    schema_version: int = 1
    name: str
    version: str = "1.0"
    created: str = ""
    steps: list[StepSchema] = Field(default_factory=list)
    variables: dict[str, Any] = Field(default_factory=dict)
    schedule: dict[str, Any] = Field(default_factory=dict)
    triggers: list[dict[str, Any]] = Field(default_factory=list)


class ProjectCreateRequest(BaseModel):
    name: str


class StepAddRequest(BaseModel):
    type: str
    params: dict[str, Any] = Field(default_factory=dict)
    index: int | None = None  # None = append at end
    parent_id: str | None = None  # None = root level


class StepUpdateRequest(BaseModel):
    params: dict[str, Any] | None = None
    wait_after: float | None = None
    label: str | None = None


class StepReorderRequest(BaseModel):
    step_id: str
    new_index: int


class ExecutionRequest(BaseModel):
    project_name: str


class ExecutionStatusResponse(BaseModel):
    execution_id: str
    running: bool
    current_step_id: str | None = None
    error: str | None = None
    log_count: int = 0


class ScheduleConfig(BaseModel):
    project_name: str
    type: str  # "daily", "weekly", "monthly"
    time: str = "09:00"
    day_of_week: str | None = None  # for weekly
    day: int | None = None  # for monthly
    enabled: bool = True


class TriggerConfig(BaseModel):
    trigger_type: str  # "app" or "file"
    value: str  # process name or file pattern
    watch_dir: str | None = None  # for file triggers
    project_name: str


class ActionMetadata(BaseModel):
    type: str
    label: str
    category: str
    category_icon: str


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str


class ElementPickerResult(BaseModel):
    name: str = ""
    control_type: str = ""
    automation_id: str = ""
    class_name: str = ""
