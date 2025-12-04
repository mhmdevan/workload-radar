from flask import Blueprint, request, jsonify
from ..repositories.task_repo import TaskRepository
from ..repositories.project_repo import ProjectRepository
from ..repositories.user_repo import UserRepository
from ..services.task_service import TaskService
from ..pagination import get_pagination_params
from ..exceptions import ValidationError

tasks_bp = Blueprint("tasks", __name__)

_task_repo = TaskRepository()
_project_repo = ProjectRepository()
_user_repo = UserRepository()
_task_service = TaskService(
    task_repo=_task_repo,
    project_repo=_project_repo,
    user_repo=_user_repo,
)


@tasks_bp.route("/project/<int:project_id>", methods=["GET"])
def list_tasks_for_project(project_id: int):
    """List tasks for a given project with pagination."""
    limit, offset = get_pagination_params(request)

    tasks = _task_service.list_tasks_for_project(
        project_id=project_id,
        limit=limit,
        offset=offset,
    )

    return jsonify(
        {
            "items": tasks,
            "limit": limit,
            "offset": offset,
            "count": len(tasks),
        }
    )


@tasks_bp.route("/project/<int:project_id>", methods=["POST"])
def create_task_for_project(project_id: int):
    """Create a new task under the given project."""
    data = request.get_json() or {}

    title = data.get("title")
    description = data.get("description")
    assignee_id = data.get("assignee_id")

    if not title:
        raise ValidationError("title is required")

    task = _task_service.create_task(
        project_id=project_id,
        title=title,
        description=description,
        assignee_id=int(assignee_id) if assignee_id is not None else None,
    )

    return jsonify(task), 201


@tasks_bp.route("/<int:task_id>/status", methods=["PATCH"])
def update_task_status(task_id: int):
    """Update the status of a task."""
    data = request.get_json() or {}
    new_status = data.get("status")

    if not new_status:
        raise ValidationError("status is required")

    task = _task_service.update_status(task_id=task_id, new_status=new_status)

    return jsonify(task)
