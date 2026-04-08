from __future__ import annotations
from typing import Any
from rpa_studio.engine.context import ExecutionContext

OPERATORS = {
    "eq": lambda a, b: a == b,
    "neq": lambda a, b: a != b,
    "gt": lambda a, b: float(a) > float(b),
    "lt": lambda a, b: float(a) < float(b),
    "gte": lambda a, b: float(a) >= float(b),
    "lte": lambda a, b: float(a) <= float(b),
    "contains": lambda a, b: str(b) in str(a),
}

def evaluate_condition(params: dict[str, Any], context: ExecutionContext) -> bool:
    left_key = params.get("left", "")
    left_val = context.variables.get(left_key, left_key)
    operator = params.get("operator", "eq")
    right_val = context.resolve(str(params.get("right", "")))
    fn = OPERATORS.get(operator, OPERATORS["eq"])
    try:
        return fn(left_val, right_val)
    except (ValueError, TypeError):
        return False
