from .schemas import WorkItem


def quality_points(item: WorkItem) -> int:
    """Compute a deterministic score based on task attributes."""

    base = 10 if item.completed else 0
    return base + (item.priority * 5)
