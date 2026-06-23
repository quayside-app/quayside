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


def next_actions(statuses, tasks, limit=3):
    """The work to surface: tasks in flight (middle columns) and the next ones to start.

    Next-up tasks come from the leftmost (todo) column, ordered by their queue
    priority, preferring leaf tasks over container tasks. With no dependency or
    date data, queue position is the only signal for what comes next.
    """
    ordered = sorted(statuses, key=lambda status: (status["order"], str(status["id"])))
    if not ordered:
        return {"in_flight": [], "next_up": []}

    done_id = str(ordered[-1]["id"])
    middle_ids = {str(status["id"]) for status in ordered[1:-1]}

    in_flight, todo = [], []
    for task in tasks:
        status_id = str(task["status_id"]) if task["status_id"] is not None else ""
        if status_id == done_id:
            continue
        (in_flight if status_id in middle_ids else todo).append(task)

    def rank(task):
        priority = task.get("priority")
        return (priority if priority is not None else float("inf"), str(task["id"]))

    leaves = [task for task in todo if task.get("is_leaf")]
    next_pool = leaves if leaves else todo

    def brief(task):
        return {"id": str(task["id"]), "name": task["name"]}

    return {
        "in_flight": [brief(task) for task in sorted(in_flight, key=rank)],
        "next_up": [brief(task) for task in sorted(next_pool, key=rank)[:limit]],
    }
