from typing import Iterable, Optional
from pony.orm import select
from ..models import Project, User


class ProjectRepository:
    """Persistence operations for Project entity."""

    def create(self, owner: User, name: str) -> Project:
        project = Project(owner=owner, name=name)
        return project

    def get(self, project_id: int) -> Optional[Project]:
        return Project.get(id=project_id)

    def list_for_owner(self, owner: User, limit: int, offset: int) -> Iterable[Project]:
        query = select(p for p in Project if p.owner == owner).order_by(lambda p: p.id)
        return query.limit(limit, offset=offset)[:]
