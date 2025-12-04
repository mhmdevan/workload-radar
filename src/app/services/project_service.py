from typing import List
from pony.orm import db_session
from ..repositories.project_repo import ProjectRepository
from ..repositories.user_repo import UserRepository
from ..exceptions import ValidationError, NotFoundError


class ProjectService:
    """Business logic for working with projects."""

    def __init__(self, project_repo: ProjectRepository, user_repo: UserRepository) -> None:
        self.project_repo = project_repo
        self.user_repo = user_repo

    @db_session
    def create_project(self, owner_id: int, name: str) -> dict:
        owner = self.user_repo.get(owner_id)
        if owner is None:
            raise NotFoundError("Owner not found")

        if not name or not name.strip():
            raise ValidationError("Project name cannot be empty")

        project = self.project_repo.create(owner=owner, name=name)
        return project.to_dict()

    @db_session
    def list_projects_for_owner(self, owner_id: int, limit: int, offset: int) -> List[dict]:
        owner = self.user_repo.get(owner_id)
        if owner is None:
            raise NotFoundError("Owner not found")

        projects = self.project_repo.list_for_owner(owner, limit=limit, offset=offset)
        return [p.to_dict() for p in projects]
