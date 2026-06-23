import re

from bson.errors import InvalidId
from django import template
from mongoengine.errors import OperationError, ValidationError
from pymongo.errors import PyMongoError

from api.models import Project, Task
from api.progress import compute_progress, next_actions

register = template.Library()

HEX_COLOR = re.compile(r"^([0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
FALLBACK_COLOR = "6b7280"


def hex_color(color):
    return color if isinstance(color, str) and HEX_COLOR.match(color) else FALLBACK_COLOR


@register.inclusion_tag("components/whatsnext.html")
def whats_next(project_id):
    try:
        project = Project.objects.get(id=project_id)
        statuses = [
            {"id": status.id, "name": status.name, "color": status.color, "order": status.order}
            for status in project.taskStatuses
        ]
        tasks = list(Task.objects.filter(projectID=project_id).only("name", "statusId", "priority", "parentTaskID"))
    except (Project.DoesNotExist, ValidationError, InvalidId, OperationError, PyMongoError):
        return {"available": False}

    if not statuses:
        return {"available": False}

    parent_ids = {str(task.parentTaskID) for task in tasks if task.parentTaskID}
    task_records = [
        {
            "id": task.id,
            "name": task.name,
            "status_id": task.statusId,
            "priority": task.priority,
            "is_leaf": str(task.id) not in parent_ids,
        }
        for task in tasks
    ]

    progress = compute_progress(statuses, [record["status_id"] for record in task_records])
    actions = next_actions(statuses, task_records)
    segments = [
        {"name": segment["name"], "color": hex_color(segment["color"]), "count": segment["count"]}
        for segment in progress["segments"]
    ]

    return {
        "available": True,
        "total": progress["total"],
        "done": progress["done"],
        "completeness_pct": round(progress["completeness"] * 100),
        "segments": segments,
        "in_flight": actions["in_flight"],
        "next_up": actions["next_up"],
    }
