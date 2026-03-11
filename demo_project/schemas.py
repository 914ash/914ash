from dataclasses import dataclass


@dataclass(frozen=True)
class WorkItem:
    """Validated unit of work accepted by the demo service boundary."""

    name: str
    priority: int
    completed: bool
