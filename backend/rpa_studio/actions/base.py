from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional
from rpa_studio.models import ActionType, Step
from rpa_studio.engine.context import ExecutionContext

_REGISTRY: dict[ActionType, "ActionHandler"] = {}

class ActionHandler(ABC):
    action_type: ActionType

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "action_type") and isinstance(getattr(cls, "action_type", None), ActionType):
            _REGISTRY[cls.action_type] = cls()

    @abstractmethod
    def execute(self, step: Step, context: ExecutionContext) -> Any:
        ...

def get_action_handler(action_type: ActionType) -> Optional[ActionHandler]:
    return _REGISTRY.get(action_type)
