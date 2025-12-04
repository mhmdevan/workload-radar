from flask import Blueprint, request, jsonify
from ..repositories.user_repo import UserRepository
from ..repositories.project_repo import ProjectRepository
from ..services.project_service import ProjectService
from ..pagination import get_pagination_params
from ..exceptions import ValidationError

projects_bp = Blueprint("projects", __name__)

_user_repo = UserRepository()
_project_repo = ProjectRepository()
_project_service = ProjectService(project_repo=_project_repo, user_repo=_user_repo)


@projects_bp.route("", methods=["GET"])
def list_projects():
    """List projects for a given owner id with pagination."""
    owner_id = request.args.get("owner_id", type=int)
    if not owner_id:
        raise ValidationError("owner_id query parameter is required")

    limit, offset = get_pagination_params(request)

    projects = _project_service.list_projects_for_owner(
        owner_id=owner_id,
        limit=limit,
        offset=offset,
    )

    return jsonify(
        {
            "items": projects,
            "limit": limit,
            "offset": offset,
            "count": len(projects),
        }
    )


@projects_bp.route("", methods=["POST"])
def create_project():
    """Create a new project for a given owner."""
    data = request.get_json() or {}
    owner_id = data.get("owner_id")
    name = data.get("name")

    if not owner_id or not name:
        raise ValidationError("owner_id and name are required")

    project = _project_service.create_project(owner_id=int(owner_id), name=name)

    return jsonify(project), 201
