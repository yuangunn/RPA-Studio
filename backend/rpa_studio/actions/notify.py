from __future__ import annotations
from rpa_studio.actions.base import ActionHandler
from rpa_studio.models import ActionType, Step
from rpa_studio.engine.context import ExecutionContext

class NotifyHandler(ActionHandler):
    action_type = ActionType.NOTIFY
    def execute(self, step: Step, context: ExecutionContext):
        message = context.resolve(step.params.get("message", ""))
        context.add_log(f"알림: {message}")
        return {"message": message}
