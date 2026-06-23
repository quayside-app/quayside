import re

from bson import ObjectId
from bson.errors import InvalidId
from django import template
from mongoengine.errors import OperationError, ValidationError
from pymongo.errors import PyMongoError

from api.models import Project, Task
from api.progress import compute_progress, cross_project_next, next_actions

register = template.Library()

HEX_COLOR = re.compile(r"^([0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
FALLBACK_COLOR = "6b7280"
TASK_SCAN_LIMIT = 10000


def hex_color(color):
    return color if isinstance(color, str) and HEX_COLOR.match(color) else FALLBACK_COLOR


def task_records(tasks):
    parent_ids = {str(task.parentTaskID) for task in tasks if task.parentTaskID}
    return [
        {
            "id": task.id,
            "name": task.name,
            "status_id": task.statusId,
            "priority": task.priority,
            "is_leaf": str(task.id) not in parent_ids,
        }
        for task in tasks
    ]


def status_records(statuses):
    return [
        {"id": status.id, "name": status.name, "color": status.color, "order": status.order}
        for status in statuses
    ]


@register.inclusion_tag("components/whatsnext.html")
def whats_next(project_id):
    try:
        project = Project.objects.get(id=project_id)
        statuses = status_records(project.taskStatuses)
        tasks = list(Task.objects.filter(projectID=project_id).only("name", "statusId", "priority", "parentTaskID"))
    except (Project.DoesNotExist, ValidationError, InvalidId, OperationError, PyMongoError):
        return {"available": False}

    if not statuses:
        return {"available": False}

    records = task_records(tasks)
    progress = compute_progress(statuses, [record["status_id"] for record in records])
    actions = next_actions(statuses, records)
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


@register.inclusion_tag("components/whatsnext_all.html")
def whats_next_all(user_id):
    if not user_id:
        return {"available": False}

    try:
        owner = ObjectId(user_id)
        projects = list(Project.objects.filter(userIDs=owner).only("name", "taskStatuses"))
        project_ids = [project.id for project in projects]
        if not project_ids:
            return {"available": True, "projects": [], "more": 0}
        tasks = list(
            Task.objects.filter(projectID__in=project_ids)
            .only("name", "statusId", "priority", "parentTaskID", "projectID")
            .limit(TASK_SCAN_LIMIT)
        )
    except (ValidationError, InvalidId, OperationError, PyMongoError):
        return {"available": False}

    tasks_by_project = {}
    for task in tasks:
        tasks_by_project.setdefault(str(task.projectID), []).append(task)

    project_records = [
        {
            "id": project.id,
            "name": project.name,
            "statuses": status_records(project.taskStatuses),
            "tasks": task_records(tasks_by_project.get(str(project.id), [])),
        }
        for project in projects
    ]

    result = cross_project_next(project_records)
    return {"available": True, "projects": result["projects"], "more": result["more"]}
