def compute_progress(statuses, task_status_ids):
    """Completeness of a project from its own tasks: done-column tasks over total.

    `statuses` are the project's task statuses (id, name, color, order). The
    highest-order status is the done column. Tasks whose status is missing or
    unrecognized fall into the leftmost column, matching the kanban board.
    """
    ordered = sorted(statuses, key=lambda status: (status["order"], str(status["id"])))
    total = len(task_status_ids)

    if not ordered:
        return {"total": total, "done": 0, "completeness": 0.0, "segments": []}

    known = {str(status["id"]) for status in ordered}
    leftmost = str(ordered[0]["id"])

    counts = {str(status["id"]): 0 for status in ordered}
    for status_id in task_status_ids:
        key = str(status_id) if status_id is not None and str(status_id) in known else leftmost
        counts[key] += 1

    segments = [
        {
            "id": str(status["id"]),
            "name": status["name"],
            "color": status["color"],
            "order": status["order"],
            "count": counts[str(status["id"])],
            "fraction": counts[str(status["id"])] / total if total else 0.0,
        }
        for status in ordered
    ]

    done = segments[-1]["count"]
    return {
        "total": total,
        "done": done,
        "completeness": done / total if total else 0.0,
        "segments": segments,
    }
