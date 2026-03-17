from typing import Any

from .domain import quality_points
from .schemas import WorkItem


def _validate_payload(payload: dict[str, Any]) -> WorkItem:
    """Validate and normalize untrusted input at the service boundary."""

    required = {"name", "priority", "completed"}
    missing = required - payload.keys()
    if missing:
        missing_fields = ", ".join(sorted(missing))
        raise ValueError(f"Missing required fields: {missing_fields}")

    name = payload["name"]
    priority = payload["priority"]
    completed = payload["completed"]

    if not isinstance(name, str) or not name.strip():
        raise ValueError("Field 'name' must be a non-empty string")
    if not isinstance(priority, int) or priority < 0 or priority > 5:
        raise ValueError("Field 'priority' must be an integer between 0 and 5")
    if not isinstance(completed, bool):
        raise ValueError("Field 'completed' must be a boolean")

    return WorkItem(name=name.strip(), priority=priority, completed=completed)


def evaluate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Entry-point API for the demo project."""

    item = _validate_payload(payload)
    points = quality_points(item)
    return {
        "name": item.name,
        "priority": item.priority,
        "completed": item.completed,
        "points": points,
        "status": "done" if item.completed else "in_progress",
    }
